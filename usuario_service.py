import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

class UsuarioService:
    def enviar_correo(self, destinatario, asunto, cuerpo):
        with open('config.json') as f:
            config = json.load(f)
        remitente = config["Drive"]["usuario"]
        password = config["Drive"]["password"]

        mensaje = MIMEMultipart()
        mensaje['From'] = remitente
        mensaje['To'] = destinatario
        mensaje['Subject'] = asunto
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        servidor_smtp = smtplib.SMTP(config["Drive"]["smtp_server"], int(config["Drive"]["puerto"]))
        servidor_smtp.starttls()
        servidor_smtp.login(remitente, password)
        texto = mensaje.as_string()
        servidor_smtp.sendmail(remitente, destinatario, texto)
        servidor_smtp.quit()
    
    def convertir_a_privado(self, servicio_drive, id_archivo, owner_email):
        try:
            archivo_info = servicio_drive.files().get(fileId=id_archivo, fields='name, mimeType, owners, modifiedTime').execute()
            nombre_archivo = archivo_info.get('name', 'Nombre no disponible')
            tipo_archivo = archivo_info.get('mimeType', 'Tipo no disponible')
            owner = archivo_info['owners'][0]['displayName'] if 'owners' in archivo_info and archivo_info['owners'] else 'Owner no disponible'
            fecha_modificacion_str = archivo_info.get('modifiedTime', None)
            from db_service import BaseDeDatosService
            fecha_modificacion = BaseDeDatosService().convertir_a_zona_horaria_local(fecha_modificacion_str) if fecha_modificacion_str else None

            permisos_actuales = servicio_drive.permissions().list(fileId=id_archivo).execute()
            
            for permiso in permisos_actuales.get('permissions', []):
                if permiso['type'] == 'anyone':
                    servicio_drive.permissions().delete(fileId=id_archivo, permissionId=permiso['id']).execute()
            
            print("Los permisos públicos para el archivo con ID", id_archivo, "han sido revocados.")
            
            servicio_drive.files().update(fileId=id_archivo, body={'visibility': 'private'}).execute()
            
            print("El archivo con ID", id_archivo, "ahora es privado.")
            
            BaseDeDatosService().guardar_archivo(nombre_archivo, tipo_archivo, owner, 'Privado', fecha_modificacion, id_archivo=id_archivo)
            
            self.enviar_correo(owner_email, "Cambio de configuración de archivo",
                        f"Estimado {owner_email},\n\nLe informamos que su archivo '{nombre_archivo}' con ID {id_archivo} ha sido cambiado a privado.\n\nAtentamente,\nEl equipo de soporte")
            
            print("Se ha enviado un correo electrónico al propietario del archivo para notificar el cambio.")

        except Exception as e:
            print("Se produjo un error al convertir el archivo a privado:", str(e))
            self.enviar_correo(owner_email, "Error al cambiar la configuración de archivo",
                        f"Estimado {owner_email},\n\nSe produjo un error al intentar cambiar su archivo '{nombre_archivo}' con ID {id_archivo} a privado. Por favor, póngase en contacto con el soporte técnico para obtener ayuda.\n\nAtentamente,\nEl equipo de soporte")
