"""Validate the generated locale database and the new RHMI action/model wiring."""
from pathlib import Path
import subprocess,zipfile,xml.etree.ElementTree as ET,tempfile,shutil,sys

root=Path(__file__).resolve().parents[1]
generator=root/'rhmiapp/make_db.py'
def definitions(source):
    scope={'__file__':str(generator)}
    exec(compile(source.split('with zipfile.ZipFile(',1)[0],str(generator),'exec'),scope)
    return scope
current=definitions(generator.read_text(encoding='utf-8'))
baseline=subprocess.check_output(['git','show','HEAD:milestone-7/rhmiapp/make_db.py'],cwd=root).decode('utf-8')
# Accept the historical pre-repair baseline as well as the repaired upstream generator.
baseline=baseline.replace('"pl": "Polski"}}','"pl": "Polski"}')
previous=definitions(baseline)
assert current['LANGS']==previous['LANGS']
assert set(current['BT_AUTO_SOURCE_TEXTS'])==set(current['LANGS'])
temporary=tempfile.TemporaryDirectory()
fixture=Path(temporary.name)
(fixture/'rhmiapp').mkdir()
shutil.copy2(generator,fixture/'rhmiapp/make_db.py')
shutil.copytree(root/'plugin/res',fixture/'plugin/res')
subprocess.run([sys.executable,str(fixture/'rhmiapp/make_db.py')],check=True,capture_output=True)
with zipfile.ZipFile(fixture/'rhmiapp/NbtAad_ALL_Texts.zip') as z:
    assert z.testzip() is None
    assert set(z.namelist())=={lang+'.txt' for lang in current['LANGS']}
    for lang in current['LANGS']:
        before=dict(previous['TEXTS']);before.update(previous['LANG_TEXTS'].get(lang,{}))
        actual=dict(line.split('=',1) for line in z.read(lang+'.txt').decode('utf-8').splitlines())
        assert all(actual[str(key)]==value for key,value in before.items()),lang
        assert actual['49']==current['BT_AUTO_SOURCE_TEXTS'][lang],lang
assert current['BT_AUTO_SOURCE_TEXTS']['pl']=='Automatycznie przełączaj źródło na Bluetooth po połączeniu Android Auto'
xml_path=root/'rhmiapp/NbtAad.xml'
assert b'\r' not in xml_path.read_bytes(), 'RHMI XML must retain LF endings'
app=ET.parse(xml_path).getroot().find('pluginApp')
assert len(app.findall("actions/raAction[@id='181']"))==1
assert len(app.findall("models/raBoolModel[@id='182']"))==1
assert len(app.findall("models/textIdModel[@id='183'][@textId='49']"))==1
box=app.find("hmiStates/hmiState[@id='14']/components/checkbox[@id='184']")
assert box is not None and box.attrib['action']=='181' and box.attrib['model']=='182' and box.attrib['textModel']=='183'
# Preserve the new upstream gauge-cluster controls and text IDs.
assert app.find("hmiStates/hmiState[@id='54']") is not None
for tid in [400,404,405,406]: assert tid in current['TEXTS']
all_ids=[n.attrib['id'] for n in app.iter() if 'id' in n.attrib and n.tag!='property']
for value in ['181','182','183','184']:assert all_ids.count(value)==1,value
source=(root/'rhmiapp/nbt_aad_app.cpp').read_text(encoding='utf-8')
assert 'addAction(self, kActBtAutoSource, &onBtAutoSourceToggle)' in source
assert 'showBtAutoSource(g_app)' in source
assert 'kSpeechBtFlag, kNoBtAutoSourceFlag, kWarnFlag' in source
print('PASS: all 11 locales, exact Polish wording, all previous labels preserved, ZIP CRC, RHMI IDs and wiring.')
temporary.cleanup()
