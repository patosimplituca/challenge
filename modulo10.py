import mysql.connector
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def convertir_a_zona_horaria_local(fecha_modificacion_str):
    zona_horaria_local = pytz.timezone('America/Buenos_Aires')
    fecha_modificacion_utc = datetime.strptime(fecha_modificacion_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    fecha_modificacion_local = fecha_modificacion_utc.replace(tzinfo=pytz.utc).astimezone(zona_horaria_local)
    return fecha_modificacion_local.strftime('%Y-%m-%d %H:%M:%S')

def autenticar():
    scopes = ['https://www.googleapis.com/auth/drive.readonly']
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": "552311329490-qfgph5ui26m503sfocnvovdhl10h683g.apps.googleusercontent.com",
                "project_id": "proyecto-para-meli-414519",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "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",
                "redirect_uris": ["http://localhost"]
            }
        },
        scopes=scopes
    )
    credenciales = flow.run_local_server()
    servicio_drive = build('drive', 'v3', credentials=credenciales)
    return servicio_drive

def conectar_bd():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="simpli94",
        database="db_inventario"
    )
    cursor = conexion.cursor()
    return conexion, cursor

def crear_tabla(conexion):
    cursor = conexion.cursor()
    cursor.execute('''
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
    conexion.commit()
    cursor.close()

def guardar_archivo(nombre_archivo, tipo_archivo, owner, visibilidad, fecha_modificacion, id_archivo):
    conexion, cursor = conectar_bd()

    # Verificar si el archivo ya existe en la base de datos
    cursor.execute('SELECT * FROM archivos WHERE id_archivo = %s', (id_archivo,))
    resultado = cursor.fetchone()

    if resultado:  # Si el archivo ya existe, actualizar sus datos
        id_archivo = resultado[1]  # Aquí ajustamos el índice para el ID del archivo
        cursor.execute('''
            UPDATE archivos 
            SET nombre_archivo = %s, tipo_archivo = %s, owner = %s, visibilidad = %s, fecha_modificacion = %s 
            WHERE id_archivo = %s
        ''', (nombre_archivo, tipo_archivo, owner, visibilidad, fecha_modificacion, id_archivo))
    else:  # Si el archivo no existe, insertarlo en la base de datos
        cursor.execute('''
            INSERT INTO archivos (id_archivo, nombre_archivo, tipo_archivo, owner, visibilidad, fecha_modificacion)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (id_archivo, nombre_archivo, tipo_archivo, owner, visibilidad, fecha_modificacion))

    conexion.commit()
    conexion.close()

def crear_tabla_archivos_publicos_historial(conexion):
    cursor = conexion.cursor()
    cursor.execute('''
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
    conexion.commit()
    cursor.close()

def guardar_archivo_historial(nombre_archivo, tipo_archivo, owner, fecha_modificacion, id_archivo):
    conexion, cursor = conectar_bd()
    cursor.execute('SELECT * FROM archivos_publicos_historial WHERE id_archivo = %s', (id_archivo,))
    resultado = cursor.fetchone()
    if resultado:
        cursor.execute('''
            UPDATE archivos_publicos_historial
            SET tipo_archivo = %s, owner = %s, fecha_modificacion = %s
            WHERE id_archivo = %s
        ''', (tipo_archivo, owner, fecha_modificacion, id_archivo))
    else:
        cursor.execute('''
            INSERT INTO archivos_publicos_historial (id_archivo, nombre_archivo, tipo_archivo, owner, fecha_modificacion)
            VALUES (%s, %s, %s, %s, %s)
        ''', (id_archivo, nombre_archivo, tipo_archivo, owner, fecha_modificacion))
    conexion.commit()
    conexion.close()

def convertir_a_privado(servicio_drive, id_archivo, owner_email):
    try:
        permiso = {
            'role': 'reader',
            'type': 'anyone',
            'allowFileDiscovery': False
        }
        servicio_drive.permissions().create(fileId=id_archivo, body=permiso).execute()
        print("El archivo con ID", id_archivo, "ahora es privado.")
        enviar_correo(owner_email, "Cambio de configuración de archivo",
                     f"Estimado {owner_email},\n\nLe informamos que su archivo con ID {id_archivo} ha sido cambiado a privado.\n\nAtentamente,\nEl equipo de soporte")
    except Exception as e:
        print("Error al convertir el archivo a privado:", e)

def enviar_correo(destinatario, asunto, mensaje):
    # Configuración del servidor SMTP
    smtp_server = "smtp.gmail.com"
    puerto = 587
    usuario = "psimplituca@pioix.edu.ar"
    password = "simpli94"

    # Crear instancia del objeto MIMEMultipart
    msg = MIMEMultipart()

    # Configurar los parámetros del mensaje
    msg['From'] = usuario
    msg['To'] = destinatario
    msg['Subject'] = asunto

    # Adjuntar el cuerpo del mensaje
    msg.attach(MIMEText(mensaje, 'plain'))

    # Establecer conexión con el servidor SMTP
    server = smtplib.SMTP(smtp_server, puerto)
    server.starttls()

    # Iniciar sesión en el servidor SMTP y enviar correo electrónico
    server.login(usuario, password)
    server.send_message(msg)
    server.quit()

def obtener_archivos(servicio_drive):
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
            conexion, cursor = conectar_bd()
            crear_tabla(conexion)
            crear_tabla_archivos_publicos_historial(conexion)

            for archivo in archivos:
                id_archivo = archivo.get('id', 'ID no disponible')
                nombre = archivo.get('name', 'Nombre no disponible')
                tipo_archivo = archivo.get('mimeType', 'Tipo no disponible')
                owner = archivo['owners'][0]['displayName'] if 'owners' in archivo and archivo['owners'] else 'Owner no disponible'
                owner_email = archivo['owners'][0]['emailAddress'] if 'owners' in archivo and archivo['owners'] else 'owner@example.com'
                visibilidad = obtener_visibilidad(archivo)
                fecha_modificacion_str = archivo.get('modifiedTime', 'Fecha de Modificación no disponible')
                fecha_modificacion = convertir_a_zona_horaria_local(fecha_modificacion_str)

                guardar_archivo(nombre, tipo_archivo, owner, visibilidad, fecha_modificacion, id_archivo)

                if visibilidad == 'Público':
                    guardar_archivo_historial(nombre, tipo_archivo, owner, fecha_modificacion, id_archivo)
                    convertir_a_privado(servicio_drive, id_archivo, owner_email)

            print("Datos de archivos en tu unidad guardados en la base de datos.")

    except Exception as e:
        print("Error al obtener la lista de archivos en tu unidad o al guardar los datos en la base de datos:", e)

def obtener_visibilidad(archivo):
    shared = archivo.get('shared', False)
    return 'Público' if shared else 'Privado'

def main():
    servicio_drive = autenticar()
    obtener_archivos(servicio_drive)

if __name__ == "__main__":
    main()
