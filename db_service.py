import mysql.connector
from datetime import datetime
import pytz
import json

from usuario_service import UsuarioService

class BaseDeDatosService:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.connection, self.cursor = self.conectar_bd()

    def load_config(self, config_file):
        with open(config_file) as f:
            config = json.load(f)
        return config

    def conectar_bd(self):
        conexion = mysql.connector.connect(
            host=self.config["BaseDeDatos"]["Host"],
            user=self.config["BaseDeDatos"]["User"],
            password=self.config["BaseDeDatos"]["password"],
            database=self.config["BaseDeDatos"]["database"]
        )
        cursor = conexion.cursor()
        return conexion, cursor

    def crear_tablas(self):
        self.cursor.execute('''
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
        self.connection.commit()

        self.cursor.execute('''
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
        self.connection.commit()

    def guardar_archivo(self, nombre_archivo, tipo_archivo, owner, visibilidad, fecha_modificacion, id_archivo):
        self.cursor.execute('SELECT * FROM archivos WHERE id_archivo = %s', (id_archivo,))
        resultado = self.cursor.fetchone()

        if resultado:  
            self.cursor.execute('''
                UPDATE archivos 
                SET nombre_archivo = %s, tipo_archivo = %s, owner = %s, visibilidad = %s, fecha_modificacion = %s 
                WHERE id_archivo = %s
            ''', (nombre_archivo, tipo_archivo, owner, visibilidad, fecha_modificacion, id_archivo))
        else:  
            self.cursor.execute('''
                INSERT INTO archivos (id_archivo, nombre_archivo, tipo_archivo, owner, visibilidad, fecha_modificacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (id_archivo, nombre_archivo, tipo_archivo, owner, visibilidad, fecha_modificacion))

        self.connection.commit()
        
    
    def guardar_archivo_historial(self, nombre_archivo, tipo_archivo, owner, fecha_modificacion, id_archivo):
        self.cursor.execute('SELECT * FROM archivos_publicos_historial WHERE id_archivo = %s', (id_archivo,))
        resultado = self.cursor.fetchone()
        if resultado:
            self.cursor.execute('''
                UPDATE archivos_publicos_historial
                SET tipo_archivo = %s, owner = %s, fecha_modificacion = %s
                WHERE id_archivo = %s
            ''', (tipo_archivo, owner, fecha_modificacion, id_archivo))
        else:
            self.cursor.execute('''
                INSERT INTO archivos_publicos_historial (id_archivo, nombre_archivo, tipo_archivo, owner, fecha_modificacion)
                VALUES (%s, %s, %s, %s, %s)
            ''', (id_archivo, nombre_archivo, tipo_archivo, owner, fecha_modificacion))
        self.connection.commit()

    def obtener_visibilidad(self, archivo):
        shared = archivo.get('shared', False)
        return 'Público' if shared else 'Privado'

    def obtener_archivos(self, servicio_drive):
        try:
            resultados = servicio_drive.files().list(
                pageSize=10,
                q="'root' in parents",
                fields="nextPageToken, files(id, name, mimeType, owners, shared, permissions, modifiedTime)"
            ).execute()

            archivos = resultados.get('files', [])

            if not archivos:
                print('No se encontraron archivos en tu unidad.')
            else:
                self.crear_tablas()
                
                for archivo in archivos:
                    id_archivo = archivo.get('id', 'ID no disponible')
                    nombre = archivo.get('name', 'Nombre no disponible')
                    tipo_archivo = archivo.get('mimeType', 'Tipo no disponible')
                    owner = archivo['owners'][0]['displayName'] if 'owners' in archivo and archivo['owners'] else 'Owner no disponible'
                    owner_email = archivo['owners'][0]['emailAddress'] if 'owners' in archivo and archivo['owners'] else 'owner@example.com'
                    visibilidad = self.obtener_visibilidad(archivo)
                    fecha_modificacion_str = archivo.get('modifiedTime', 'Fecha de Modificación no disponible')
                    fecha_modificacion = self.convertir_a_zona_horaria_local(fecha_modificacion_str)

                    self.guardar_archivo(nombre, tipo_archivo, owner, visibilidad, fecha_modificacion, id_archivo)

                    if visibilidad == 'Público':
                        self.guardar_archivo_historial(nombre, tipo_archivo, owner, fecha_modificacion, id_archivo)
                        UsuarioService().convertir_a_privado(servicio_drive, id_archivo, owner_email)

                print("Datos de archivos en tu unidad guardados en la base de datos.")

        except Exception as e:
            print("Error al obtener la lista de archivos en tu unidad o al guardar los datos en la base de datos:", e)


    #La aPI de Drive devuelve el horario en otro HUSO, lo modifco para la hora de Argentina
    def convertir_a_zona_horaria_local(self, fecha_modificacion_str):
        zona_horaria_local = pytz.timezone('America/Buenos_Aires')
        fecha_modificacion_utc = datetime.strptime(fecha_modificacion_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        fecha_modificacion_local = fecha_modificacion_utc.replace(tzinfo=pytz.utc).astimezone(zona_horaria_local)
        return fecha_modificacion_local.strftime('%Y-%m-%d %H:%M:%S')
