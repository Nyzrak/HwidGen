from hashlib import sha256
import platform
import re
import subprocess


class HWIDGenerator:
    @staticmethod
    def get_hwid() -> str:
        system = platform.system()
        if "Windows" == system:
            return HWIDGenerator._get_windows_hwid()
        elif "Darwin" == system:
            return HWIDGenerator._get_mac_hwid()
        elif "Linux" == system:
            return HWIDGenerator._get_linux_hwid()
        else:
            raise NotImplementedError(f"Unsupported OS: {system}")

    @staticmethod
    def _get_windows_hwid() -> str:
        import winreg

        script = (
            "$cpu = (Get-CimInstance Win32_Processor).ProcessorId;"
            "$vol = (Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\").VolumeSerialNumber;"
            'Write-Output "$cpu`n$vol"'
        )
        output = (
            subprocess.check_output(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            )
            .decode()
            .strip()
            .splitlines()
        )
        cpu_id = output[0].strip().encode()
        drive_serial = output[1].strip().encode()

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
        )
        machine_guid = winreg.QueryValueEx(key, "MachineGuid")[0].encode()
        winreg.CloseKey(key)

        return sha256(cpu_id + drive_serial + machine_guid).hexdigest()

    @staticmethod
    def _get_mac_hwid() -> str:
        ioreg_out = subprocess.check_output(
            "ioreg -rd1 -c IOPlatformExpertDevice", shell=True
        ).decode()
        platform_uuid = (
            re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', ioreg_out).group(1).encode()
        )
        platform_serial = (
            re.search(r'"IOPlatformSerialNumber"\s*=\s*"([^"]+)"', ioreg_out)
            .group(1)
            .encode()
        )
        volume_uuid = subprocess.check_output(
            'diskutil info / | grep "Volume UUID"', shell=True
        ).strip()

        return sha256(platform_uuid + platform_serial + volume_uuid).hexdigest()

    @staticmethod
    def _get_linux_hwid() -> str:
        cpu_id = subprocess.check_output("cat /etc/machine-id", shell=True).strip()

        primary_disk = (
            subprocess.check_output(
                'lsblk -o NAME,TYPE -dn | awk \'$2=="disk" {print "/dev/"$1; exit}\'',
                shell=True,
            )
            .strip()
            .decode()
        )

        disk_serial = subprocess.check_output(
            ["lsblk", "-o", "SERIAL", "-d", "-n", primary_disk]
        ).strip()
        drive_serial = subprocess.check_output(
            ["lsblk", "-o", "PTUUID", "-d", "-n", primary_disk]
        ).strip()

        return sha256(cpu_id + drive_serial + disk_serial).hexdigest()
