from hashlib import sha256
from wmi import WMI


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
        command = 'sysctl -n machdep.cpu.brand_string'

    @staticmethod
    def _get_linux_hwid() -> str:
        pass