from hashlib import sha256
import os, platform, subprocess, re


class HWIDGenerator:
    @staticmethod
    def get_hwid() -> str:
        os = platform.system()
        if 'Windows' == os:
            return HWIDGenerator._get_windows_hwid()
        elif 'Darwin' == os:
            return HWIDGenerator._get_mac_hwid()
        elif 'Linux' == os:
            return HWIDGenerator._get_linux_hwid()
        else:
            raise NotImplementedError(f'Unsupported OS: {os}')

    @staticmethod
    def _get_windows_hwid() -> str:
        from wmi import WMI
        wmi_data = WMI()
        cpu_id = wmi_data.Win32_Processor()[0].ProcessorId.strip().encode("utf-8")
        drive_serial = (
            wmi_data.Win32_LogicalDisk(DeviceID="C:")[0]
            .VolumeSerialNumber.strip()
            .encode("utf-8")
        )
        disk_serial = (
            wmi_data.Win32_PhysicalMedia()[0].SerialNumber.strip().encode("utf-8")
        )

        return sha256(cpu_id + drive_serial + disk_serial).hexdigest()

    @staticmethod
    def _get_mac_hwid() -> str:
        cpu_id = (
            subprocess.check_output(
                'ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID',
                shell=True
            ).strip()
        )
        disk_serial = subprocess.check_output(['diskutil', 'info', '/']).strip()
        drive_serial = (
            subprocess.check_output(
                'system_profiler SPStorageDataType | grep "Serial Number"',
                shell=True).strip()
        )

        return sha256(cpu_id + drive_serial + disk_serial).hexdigest()

    @staticmethod
    def _get_linux_hwid() -> str:
        cpu_id = subprocess.check_output('cat /etc/machine-id', shell=True).strip()
        disk_serial = subprocess.check_output('lsblk -o SERIAL -d -n /dev/sda', shell=True).strip()
        drive_serial = subprocess.check_output(' lsblk -o UUID -d -n /dev/sda', shell=True).strip()

        return sha256(cpu_id + drive_serial + disk_serial).hexdigest()