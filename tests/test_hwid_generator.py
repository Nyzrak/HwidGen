from hashlib import sha256
from src.HwidGenerator import HWIDGenerator, HWIDError
from unittest import TestCase
from unittest.mock import patch, MagicMock
from subprocess import CalledProcessError


class TestHwidGeneratorWindows(TestCase):
    @patch("platform.system", return_value="Windows")
    @patch("subprocess.check_output", return_value=b"CPU123\nVOL456")
    def test_get_hwid(self, mock_check_output, _mock_platform):
        mock_winreg = MagicMock()
        mock_winreg.QueryValueEx.return_value = ("GUID789", 1)

        with patch.dict("sys.modules", {"winreg": mock_winreg}):
            hwid = HWIDGenerator.get_hwid()

        expected = sha256(b"CPU123" + b"VOL456" + b"GUID789").hexdigest()

        mock_check_output.assert_called_once()
        mock_winreg.OpenKey.assert_called_once()
        mock_winreg.QueryValueEx.assert_called_once()
        self.assertEqual(len(hwid), 64)
        self.assertRegex(hwid, r"^[0-9a-f]{64}$")
        self.assertEqual(expected, hwid)


class TestHwidGeneratorMac(TestCase):
    IOREG_OUTPUT = (
        b'      "IOPlatformUUID" = "UUID-1234"\n'
        b'      "IOPlatformSerialNumber" = "SN-ABCD"\n'
    )
    VOLUME_UUID_LINE = b"   Volume UUID:               VOL-UUID-5678"

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.check_output")
    def test_get_hwid(self, mock_check_output, _mock_platform):
        mock_check_output.side_effect = [
            self.IOREG_OUTPUT,
            self.VOLUME_UUID_LINE,
        ]

        hwid = HWIDGenerator.get_hwid()
        expected = sha256(
            b"UUID-1234" + b"SN-ABCD" + b"VOL-UUID-5678"
        ).hexdigest()

        self.assertEqual(mock_check_output.call_count, 2)
        self.assertEqual(len(hwid), 64)
        self.assertRegex(hwid, r"^[0-9a-f]{64}$")
        self.assertEqual(expected, hwid)


class TestHwidGeneratorLinux(TestCase):
    @patch("platform.system", return_value="Linux")
    @patch("subprocess.check_output")
    def test_disk_detection_uses_root_mountpoint(self, mock_check_output, _mock_platform):
        # Verifies the disk detection command finds the disk via root mountpoint,
        # not by picking the first disk alphabetically
        mock_check_output.side_effect = [
            b"abcdef1234567890abcdef1234567890",  # /etc/machine-id
            b"/dev/nvme0n1",                       # disk detection
            b"SERIALXYZ",                          # lsblk SERIAL
            b"ptuuid-0000-1111",                   # lsblk PTUUID
        ]
        HWIDGenerator.get_hwid()
        disk_detection_cmd = mock_check_output.call_args_list[1][0][0]
        self.assertIn("findmnt", disk_detection_cmd)

    @patch("platform.system", return_value="Linux")
    @patch("subprocess.check_output")
    def test_get_hwid(self, mock_check_output, _mock_platform):
        mock_check_output.side_effect = [
            b"abcdef1234567890abcdef1234567890",  # /etc/machine-id
            b"/dev/nvme0n1",  # lsblk primary disk detection
            b"SERIALXYZ",  # lsblk SERIAL
            b"ptuuid-0000-1111",  # lsblk PTUUID
        ]

        hwid = HWIDGenerator.get_hwid()
        expected = sha256(
            b"abcdef1234567890abcdef1234567890" + b"ptuuid-0000-1111" + b"SERIALXYZ"
        ).hexdigest()

        self.assertEqual(mock_check_output.call_count, 4)
        self.assertEqual(len(hwid), 64)
        self.assertRegex(hwid, r"^[0-9a-f]{64}$")
        self.assertEqual(expected, hwid)


class TestHwidGeneratorMacFailures(TestCase):
    IOREG_OUTPUT = (
        b'      "IOPlatformUUID" = "UUID-1234"\n'
        b'      "IOPlatformSerialNumber" = "SN-ABCD"\n'
    )

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.check_output")
    def test_ioreg_missing_uuid_field_raises(self, mock_check_output, _mock_platform):
        # ioreg output lacks IOPlatformUUID — regex returns None, .group(1) crashes
        mock_check_output.side_effect = [
            b'      "IOPlatformSerialNumber" = "SN-ABCD"\n',
            b"   Volume UUID:               VOL-UUID-5678",
        ]
        with self.assertRaises(AttributeError):
            HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.check_output")
    def test_ioreg_missing_serial_field_raises(self, mock_check_output, _mock_platform):
        # ioreg output lacks IOPlatformSerialNumber — same crash
        mock_check_output.side_effect = [
            b'      "IOPlatformUUID" = "UUID-1234"\n',
            b"   Volume UUID:               VOL-UUID-5678",
        ]
        with self.assertRaises(AttributeError):
            HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.check_output")
    def test_diskutil_empty_output_raises(self, mock_check_output, _mock_platform):
        # diskutil returns nothing (e.g. encrypted volume, edge case hardware)
        # .split()[-1] on an empty list raises IndexError
        mock_check_output.side_effect = [
            self.IOREG_OUTPUT,
            b"",
        ]
        with self.assertRaises(IndexError):
            HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.check_output", side_effect=CalledProcessError(1, "ioreg"))
    def test_ioreg_command_failure_raises(self, _mock_check_output, _mock_platform):
        with self.assertRaises(CalledProcessError):
            HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.check_output")
    def test_diskutil_command_failure_raises(self, mock_check_output, _mock_platform):
        mock_check_output.side_effect = [
            self.IOREG_OUTPUT,
            CalledProcessError(1, "diskutil"),
        ]
        with self.assertRaises(CalledProcessError):
            HWIDGenerator.get_hwid()


class TestHwidGeneratorWindowsFailures(TestCase):
    @patch("platform.system", return_value="Windows")
    @patch("subprocess.check_output", return_value=b"ONLY_ONE_LINE")
    def test_powershell_truncated_output_raises(self, _mock_check_output, _mock_platform):
        # PowerShell returns fewer lines than expected — output[1] raises IndexError
        mock_winreg = MagicMock()
        with patch.dict("sys.modules", {"winreg": mock_winreg}):
            with self.assertRaises(IndexError):
                HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Windows")
    @patch("subprocess.check_output", side_effect=CalledProcessError(1, "powershell"))
    def test_powershell_command_failure_raises(self, _mock_check_output, _mock_platform):
        mock_winreg = MagicMock()
        with patch.dict("sys.modules", {"winreg": mock_winreg}):
            with self.assertRaises(CalledProcessError):
                HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Windows")
    @patch("subprocess.check_output", return_value=b"CPU123\nVOL456")
    def test_registry_open_key_failure_raises(self, _mock_check_output, _mock_platform):
        # Registry key doesn't exist (e.g. non-standard Windows install)
        mock_winreg = MagicMock()
        mock_winreg.OpenKey.side_effect = OSError("Registry key not found")
        with patch.dict("sys.modules", {"winreg": mock_winreg}):
            with self.assertRaises(OSError):
                HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Windows")
    @patch("subprocess.check_output", return_value=b"CPU123\nVOL456")
    def test_registry_query_failure_raises(self, _mock_check_output, _mock_platform):
        # Key opens but MachineGuid value is missing
        mock_winreg = MagicMock()
        mock_winreg.QueryValueEx.side_effect = OSError("Value not found")
        with patch.dict("sys.modules", {"winreg": mock_winreg}):
            with self.assertRaises(OSError):
                HWIDGenerator.get_hwid()


class TestHwidGeneratorLinuxFailures(TestCase):
    @patch("platform.system", return_value="Linux")
    @patch(
        "subprocess.check_output",
        side_effect=CalledProcessError(1, "cat /etc/machine-id"),
    )
    def test_machine_id_missing_raises(self, _mock_check_output, _mock_platform):
        with self.assertRaises(CalledProcessError):
            HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Linux")
    @patch("subprocess.check_output")
    def test_lsblk_command_failure_raises(self, mock_check_output, _mock_platform):
        mock_check_output.side_effect = [
            b"abcdef1234567890abcdef1234567890",  # machine-id succeeds
            CalledProcessError(1, "lsblk"),       # disk detection fails
        ]
        with self.assertRaises(CalledProcessError):
            HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Linux")
    @patch("subprocess.check_output")
    def test_no_primary_disk_raises_hwid_error(self, mock_check_output, _mock_platform):
        # lsblk finds no disk (e.g. inside a container with no block devices)
        mock_check_output.side_effect = [
            b"abcdef1234567890abcdef1234567890",  # machine-id
            b"",                                   # no disk found
        ]
        with self.assertRaises(HWIDError):
            HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Linux")
    @patch("subprocess.check_output")
    def test_empty_serial_raises_hwid_error(self, mock_check_output, _mock_platform):
        # lsblk returns empty serial (common without root on many drivers)
        mock_check_output.side_effect = [
            b"abcdef1234567890abcdef1234567890",  # machine-id
            b"/dev/sda",                           # disk found
            b"",                                   # serial empty
            b"ptuuid-0000-1111",                  # ptuuid fine
        ]
        with self.assertRaises(HWIDError):
            HWIDGenerator.get_hwid()

    @patch("platform.system", return_value="Linux")
    @patch("subprocess.check_output")
    def test_empty_ptuuid_raises_hwid_error(self, mock_check_output, _mock_platform):
        # lsblk returns empty PTUUID (e.g. LVM, loop devices, some VM configs)
        mock_check_output.side_effect = [
            b"abcdef1234567890abcdef1234567890",  # machine-id
            b"/dev/sda",                           # disk found
            b"SERIALXYZ",                          # serial fine
            b"",                                   # ptuuid empty
        ]
        with self.assertRaises(HWIDError):
            HWIDGenerator.get_hwid()


class TestHwidGeneratorUnsupportedOS(TestCase):
    @patch("platform.system", return_value="FreeBSD")
    def test_raises_not_implemented(self, _mock_platform):
        with self.assertRaises(NotImplementedError):
            HWIDGenerator.get_hwid()


class TestHwidGeneratorMain(TestCase):
    @patch("platform.system", return_value="Linux")
    @patch("subprocess.check_output")
    def test_main_prints_hwid(self, mock_check_output, _mock_platform):
        mock_check_output.side_effect = [
            b"abcdef1234567890abcdef1234567890",
            b"/dev/nvme0n1",
            b"SERIALXYZ",
            b"ptuuid-0000-1111",
        ]
        import io
        import runpy
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            runpy.run_path("src/HwidGenerator.py", run_name="__main__")
        output = mock_stdout.getvalue().strip()
        self.assertRegex(output, r"^[0-9a-f]{64}$")
