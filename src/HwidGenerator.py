from hashlib import sha256
from wmi import WMI


class HWIDGenerator:
    @staticmethod
    def get_hwid() -> str:
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
