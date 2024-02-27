import unittest
from unittest.mock import MagicMock, patch
from drive_service import DriveService

class TestDriveService(unittest.TestCase):

    @patch('drive_service.build')
    def test_autenticar(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        drive_service = DriveService()

        servicio_drive = drive_service.autenticar()

        mock_build.assert_called_once()


