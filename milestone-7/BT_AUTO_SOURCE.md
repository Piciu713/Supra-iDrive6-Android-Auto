# Optional automatic Bluetooth media source selection

Based on upstream `f288ab949e52827bf2afd867e59e2b4bebe0769b` (v1.9.111-cluster / rhmiapp-85-cluster).
Preserves the author's gauge cluster selection and Polish support.

Settings adds **Automatically switch audio source to Bluetooth when Android Auto connects**.
Polish: **Automatycznie przełączaj źródło na Bluetooth po połączeniu Android Auto**.
All 11 supported locales have a translation for text ID 49.

The default stays **on**. Unticking stores `no-bt-auto-source` in the existing settings
directory. `NBT_BT_AUTO_SOURCE=0` / `off` / `no` / `false` forces manual selection;
`1` / `on` / `yes` / `true` forces automatic selection, overriding the checkbox.
An unset, empty or unrecognised value follows the checkbox. The existing Settings
restart mechanism notices the flag; otherwise use Restart for it to take effect.

In Bluetooth audio mode, manual selection suppresses the daemon's A2DP source request
at session start and after Assistant microphone closure. No source request means no
associated retries or PLAY callback. Optional A2DP release/STOP at session end is also
suppressed, preserving a source manually selected by the driver. Guidance handling
is unchanged. Other audio backends are unchanged.

Factory HFP call routing and call-screen handling are unchanged. This does not
guarantee radio restoration after calls on every car. Test incoming, outgoing,
rejected and ended calls from radio and manually selected Bluetooth on the vehicle.
The new flag only controls media requests made by nbt-aad; phone/iDrive behaviour
outside those requests remains independent.

## Build and validation

`make check` includes `test_bt_auto_source` (actual BtAudio/config with hardware-port
test doubles) and `test_bt_auto_source_resources.py` (generated locale ZIP, old labels,
XML IDs and registration). Test doubles do not verify hardware, asynchronous routing
workers, filesystem checkbox changes, or HFP audio. Existing config tests should pass.

The author's generator repair, cluster labels and existing Polish labels are preserved. Regenerate resources with
`python3 rhmiapp/make_db.py` before building. Older checked-in generated ZIPs can differ
from the generator (e.g. German About line breaks); this source patch does not replace
them with a hand-edited binary archive.

Build **both** `nbt-aad` and `rhmiapp/libNbtAad.so` using QNX SDP 6.5.0 / qcc GCC 4.4.2
for ARMv7 little endian, with a valid licence, following the upstream Makefile/build.sh.
Distribute the matching daemon, plugin, XML and regenerated text database together.
Do not install this source patch or only the new text database as a binary release.
Both programs were compiled with the installed QNX SDP 6.5.0 Windows toolchain.
The experimental builds carry the suffix `+bt-source2`. In-car testing has not been performed.
