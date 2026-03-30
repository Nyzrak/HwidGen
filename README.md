# HWIDGenerator

A lightweight Python utility that generates a unique hardware fingerprint for Windows machines.

## How It Works

Collects three hardware identifiers via WMI (Windows Management Instrumentation) and combines them into a single SHA-256 hash:

| Source | WMI Class | Property |
|--------|-----------|----------|
| CPU | `Win32_Processor` | `ProcessorId` |
| C: Drive (logical) | `Win32_LogicalDisk` | `VolumeSerialNumber` |
| Physical Disk | `Win32_PhysicalMedia` | `SerialNumber` |

The three values are concatenated and hashed with SHA-256, returning a 64-character hex string.

## Requirements

- Windows only (WMI is Windows-specific)
- Python 3.x

Install production dependencies:

```
pip install -r requirements/requirements.txt
```

Install development dependencies (testing, linting):

```
pip install -r requirements/requirements_dev.txt
```

## Usage

```python
from src.HwidGenerator import HWIDGenerator

hwid = HWIDGenerator.get_hwid()
print(hwid)  # e.g. 3b4c1a9f2e...
```

## Example Output

```
a3f1d9c72e4b08f6a1c3e5d7b9f2a4c6e8d0b2f4a6c8e0d2b4f6a8c0e2d4f6b8
```

## For what is this useful?

If you need some kind of verification you can use this HardwareId Generator as a device verification.
You can safely keep them in your db for example since they are already SHA256 hashed.

## Notes

- The HWID will change if you replace your CPU, reformat your C: drive, or swap your physical disk.
- `VolumeSerialNumber` is a Windows-assigned partition ID and can change on reformat. `SerialNumber` from `Win32_PhysicalMedia` is the hardware serial burned into the drive.
