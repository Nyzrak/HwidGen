from hashlib import sha256
from src.HwidGenerator import HWIDGenerator
from unittest import TestCase
from unittest.mock import patch, MagicMock


class TestHwidGenerator(TestCase):
    def test_get_hwid_returns_valid_sha256(self):
        hwid = HWIDGenerator.get_hwid()
        self.assertEqual(len(hwid), 64)
        self.assertRegex(hwid, r"^[0-9a-f]{64}$")

    @patch("src.HwidGenerator.WMI")
    def test_get_hwid_expected_hash(self, mock_wmi):
        mock = MagicMock()
        mock_wmi.return_value = mock

        mock.Win32_Processor.return_value = [MagicMock(ProcessorId="ABCD1234")]
        mock.Win32_LogicalDisk.return_value = [MagicMock(VolumeSerialNumber="5678EFGH")]
        mock.Win32_PhysicalMedia.return_value = [MagicMock(SerialNumber="IJKL9012")]

        hwid = HWIDGenerator.get_hwid()
        expected = sha256(b"ABCD1234" + b"5678EFGH" + b"IJKL9012").hexdigest()
        self.assertEqual(expected, hwid)
