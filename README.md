# hwidgen

Generates a unique hardware ID (HWID) for Windows, macOS and Linux. The result is always a 64-character SHA-256 hex string.

## Install

```bash
pip install hwidgen
```

## Usage

```python
from hwidgen import HWIDGenerator, HWIDError

try:
    hwid = HWIDGenerator.get_hwid()
    print(hwid)  # e.g. 884618235043ffce89d87862abf8882eb5294517f107f0f980bec789258e8a98
except HWIDError as e:
    print(f"Could not generate HWID: {e}")
```

Or just run it from the terminal:

```bash
hwidgen
```

## How it works

Collects a few hardware-specific values depending on your OS and hashes them together with SHA-256.

| OS | What it uses |
|----|-------------|
| Windows | CPU ProcessorId, C: VolumeSerialNumber, MachineGuid |
| macOS | IOPlatformUUID, IOPlatformSerialNumber, Volume UUID |
| Linux | `/etc/machine-id`, disk serial, PTUUID |

No external dependencies. No admin rights needed.

## Notes

- HWID changes if you replace major hardware (CPU, disk, etc.)
- On Windows, MachineGuid resets if Windows is reinstalled. VolumeSerialNumber resets if you reformat C:
- On Linux, disk serial may be unavailable on some hardware without root — a `HWIDError` is raised in that case
- On Linux, the primary disk is detected via the root mountpoint so it works correctly with LUKS, NVMe and SATA

## Dev setup

```bash
pip install -r requirements/requirements_dev.txt
make test
```
