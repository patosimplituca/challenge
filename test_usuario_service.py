import unittest
from unittest.mock import MagicMock, patch
from usuario_service import UsuarioService

class TestUsuarioService(unittest.TestCase):

    @patch('usuario_service.smtplib.SMTP')
    def test_enviar_correo(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        usuario_service = UsuarioService()

        usuario_service.enviar_correo('usuario@ejemplo.com', 'Asunto', 'Cuerpo del correo')

        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()


