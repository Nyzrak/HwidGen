from hashlib import sha256
from src.HwidGenerator import HWIDGenerator
from unittest import TestCase
from unittest.mock import patch, MagicMock


class TestHwidGeneratorWindows(TestCase):
    @patch("platform.system", return_value="Windows")
    def test_get_hwid(self, _mock_platform):
        mock_wmi_instance = MagicMock()
        mock_wmi_instance.Win32_Processor.return_value = [MagicMock(ProcessorId="CPU123")]
        mock_wmi_instance.Win32_LogicalDisk.return_value = [MagicMock(VolumeSerialNumber="VOL456")]
        mock_wmi_instance.Win32_PhysicalMedia.return_value = [MagicMock(SerialNumber="DISK789")]

        mock_wmi_module = MagicMock(WMI=MagicMock(return_value=mock_wmi_instance))

        with patch.dict("sys.modules", {"wmi": mock_wmi_module}):
            hwid = HWIDGenerator.get_hwid()

        expected = sha256(b"CPU123" + b"VOL456" + b"DISK789").hexdigest()

        mock_wmi_instance.Win32_Processor.assert_called_once()
        mock_wmi_instance.Win32_LogicalDisk.assert_called_once()
        mock_wmi_instance.Win32_PhysicalMedia.assert_called_once()
        self.assertEqual(len(hwid), 64)
        self.assertRegex(hwid, r"^[0-9a-f]{64}$")
        self.assertEqual(expected, hwid)


class TestHwidGeneratorMac(TestCase):
    IOREG_OUTPUT = (
        b'      "IOPlatformUUID" = "UUID-1234"\n'
        b'      "IOPlatformSerialNumber" = "SN-ABCD"\n'
    )
    VOLUME_UUID_LINE = b'   Volume UUID:               VOL-UUID-5678'

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.check_output")
    def test_get_hwid(self, mock_check_output, _mock_platform):
        mock_check_output.side_effect = [
            self.IOREG_OUTPUT,
            self.VOLUME_UUID_LINE,
        ]

        hwid = HWIDGenerator.get_hwid()
        expected = sha256(b"UUID-1234" + b"SN-ABCD" + self.VOLUME_UUID_LINE.strip()).hexdigest()

        self.assertEqual(mock_check_output.call_count, 2)
        self.assertEqual(len(hwid), 64)
        self.assertRegex(hwid, r"^[0-9a-f]{64}$")
        self.assertEqual(expected, hwid)


class TestHwidGeneratorLinux(TestCase):
    @patch("platform.system", return_value="Linux")
    @patch("subprocess.check_output")
    def test_get_hwid(self, mock_check_output, _mock_platform):
        mock_check_output.side_effect = [
            b"abcdef1234567890abcdef1234567890",  # /etc/machine-id
            b"SERIALXYZ",                          # lsblk SERIAL
            b"uuid-0000-1111",                     # lsblk UUID
        ]

        hwid = HWIDGenerator.get_hwid()
        expected = sha256(b"abcdef1234567890abcdef1234567890" + b"uuid-0000-1111" + b"SERIALXYZ").hexdigest()

        self.assertEqual(mock_check_output.call_count, 3)
        self.assertEqual(len(hwid), 64)
        self.assertRegex(hwid, r"^[0-9a-f]{64}$")
        self.assertEqual(expected, hwid)


class TestHwidGeneratorUnsupportedOS(TestCase):
    @patch("platform.system", return_value="FreeBSD")
    def test_raises_not_implemented(self, _mock_platform):
        with self.assertRaises(NotImplementedError):
            HWIDGenerator.get_hwid()