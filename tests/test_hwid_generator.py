from hashlib import sha256
from src.HwidGenerator import HWIDGenerator
from unittest import TestCase
from unittest.mock import patch, MagicMock


class TestHwidGenerator(TestCase):
    @patch("src.HwidGenerator.WMI")
    def test_get_hwid(self, mock_wmi):
        mock = MagicMock()
        mock_wmi.return_value = mock

        mock.Win32_Processor.return_value = [MagicMock(ProcessorId="CPU123")]
        mock.Win32_LogicalDisk.return_value = [MagicMock(VolumeSerialNumber="VOL456")]
        mock.Win32_PhysicalMedia.return_value = [MagicMock(SerialNumber="DISK789")]

        hwid = HWIDGenerator.get_hwid()
        expected = sha256(b"CPU123" + b"VOL456" + b"DISK789").hexdigest()

        mock.Win32_Processor.assert_called_once()
        mock.Win32_LogicalDisk.assert_called_once()
        mock.Win32_PhysicalMedia.assert_called_once()
        self.assertEqual(len(hwid), 64)
        self.assertRegex(hwid, r"^[0-9a-f]{64}$")
        self.assertEqual(expected, hwid)
