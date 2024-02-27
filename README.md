### Prerrequisitos

1. Python 3.12.2 o superior

2. Motor de base de datos MySQL


3. Instalar todas las dependencias 'requirements.txt' ejecutando pip install -r requirements.txt

	
4. Guarda el archivo de credenciales y cambiar el nombre del. JSON descargado a “**credentials.json**”. Luego colocarlo en la misma dirección que los '.py'. https://cloud.google.com/bigquery/docs/authentication/end-user-installed?hl=es-419#client-credentials

	
5. Agregar lo siguientes permisos a la APP
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/drive.file
https://www.googleapis.com/auth/drive.metadata
https://www.googleapis.com/auth/drive.metadata.readonly

	
6. Generar un archivo “**config.json**” con los siguientes datos: ( Se podrán modificar según su preferencia en el mismo archivo)

### BaseDeDatos

-	Host: Host de la base de datos

-	User: Usuario de la base de datos

-	database: Nombre de la base de datos

-	password: Contraseña del usuario

### Drive

-	smtp_server: Es la dirección del servidor SMTP de Gmail. En este caso, es smtp.gmail.com

-	puerto: Es el puerto utilizado para la comunicación SMTP. Es el 587

-	usuario: dirección de correo electrónico desde la cual se enviarán los correos electrónicos

-	password: Contraseña de la dirección de correo electrónico

### Instrucciones



Para ejecutar el programa: **python main.py**

Para ejecutar los test: **pytest**
