from db_service import BaseDeDatosService
from drive_service import DriveService
from usuario_service import UsuarioService

def main():
    db_service = BaseDeDatosService()
    drive_service = DriveService()
    servicio_drive = drive_service.autenticar()
    db_service.obtener_archivos(servicio_drive)

if __name__ == "__main__":
    main()
