# HWIDGenerator

A Python utility that generates a unique hardware ID (HWID) for a device. It works on Windows, macOS and Linux! The HWID is a SHA-256 hash made from hardware-specific values so it's unique per machine.

## How It Works

It collects some hardware info depending on your OS and hashes it all together with SHA-256. The result is always a 64-character hex string.

### Windows
Uses WMI to grab three things:

| Source | WMI Class | Property |
|--------|-----------|----------|
| CPU | `Win32_Processor` | `ProcessorId` |
| C: Drive (logical) | `Win32_LogicalDisk` | `VolumeSerialNumber` |
| Physical Disk | `Win32_PhysicalMedia` | `SerialNumber` |

### macOS
Uses `ioreg` and `diskutil` to get:
- `IOPlatformUUID`
- `IOPlatformSerialNumber`
- Volume UUID

### Linux
Uses `/etc/machine-id` and `lsblk` to get:
- Machine ID from `/etc/machine-id`
- Disk serial number
- Partition table UUID (PTUUID)

It automatically detects your primary disk so it works with both SATA (`/dev/sda`) and NVMe (`/dev/nvme0n1`) drives. No sudo needed!

## Requirements

- Python 3.x
- On Linux and macOS no extra packages are needed, everything uses the Python standard library
- On Windows the `wmi` package is required:

```
pip install wmi
```

Install development dependencies (testing, linting):

```
pip install -r requirements/requirements_dev.txt
```

## Usage

```python
from src.HwidGenerator import HWIDGenerator

hwid = HWIDGenerator.get_hwid()
print(hwid)  # e.g. 884618235043ffce89d87862abf8882e...
```

## Example Output

```
884618235043ffce89d87862abf8882eb5294517f107f0f980bec789258e8a98
```

## What is this useful for?

If you want to verify that a user is running your software on the same machine (like a license check), you can generate their HWID and store it in your database. Since it's already hashed you don't expose any raw hardware info.

## Notes

- The HWID will change if you replace major hardware components (CPU, disk, etc.)
- On Windows, `VolumeSerialNumber` can change if you reformat your C: drive. `SerialNumber` from `Win32_PhysicalMedia` is the actual hardware serial burned into the drive.
- On Linux, `lsblk` is used without sudo — this works on most systems but on some hardware the serial might be empty depending on the driver.
