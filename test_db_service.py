import unittest
from unittest.mock import MagicMock, patch
from db_service import BaseDeDatosService

class TestBaseDeDatosService(unittest.TestCase):

    @patch('db_service.mysql.connector.connect')
    def test_conectar_bd(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        database = BaseDeDatosService()
        assert database

    def test_crear_tablas(self):
        mock_cursor = MagicMock()
        base_de_datos_service = BaseDeDatosService()
        base_de_datos_service.cursor = mock_cursor

        base_de_datos_service.crear_tablas()

        mock_cursor.execute.assert_any_call('''
            CREATE TABLE IF NOT EXISTS archivos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_archivo VARCHAR(255),
                nombre_archivo VARCHAR(255),
                tipo_archivo VARCHAR(255),
                owner VARCHAR(255),
                visibilidad ENUM('Público', 'Privado'),
                fecha_modificacion TIMESTAMP
            )
        ''')
        mock_cursor.execute.assert_any_call('''
            CREATE TABLE IF NOT EXISTS archivos_publicos_historial (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_archivo VARCHAR(255),
                nombre_archivo VARCHAR(255),
                tipo_archivo VARCHAR(255),
                owner VARCHAR(255),
                fecha_modificacion TIMESTAMP,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    @patch('db_service.mysql.connector.connect')
    def test_guardar_archivo_en_base_de_datos(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        base_de_datos_service = BaseDeDatosService()

        id_archivo = '123456'
        nombre_archivo = 'archivo_prueba.txt'
        tipo_archivo = 'txt'
        owner = 'usuario1'
        visibilidad = 'Público'
        fecha_modificacion = '2024-02-18 16:29:24'

        base_de_datos_service.guardar_archivo(nombre_archivo, tipo_archivo, owner, visibilidad, fecha_modificacion, id_archivo)

        self.assertEqual(mock_connection.commit.call_count, 1)


