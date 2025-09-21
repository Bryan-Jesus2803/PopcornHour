# PopcornHour

Este es un proyecto escolar el cual consiste en la elaboracion de un portal web para recomendar, calificar y discutir sobre películas y series.
Proyecto para la materia: Programación Avanzada.    

## Instalación del entorno

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tu_usuario/popcornhour.git
   cd popcornhour

## Requisitos 
Los requisitos para este proyecto son:
- flask
- flask_login
- supabase
- python-dotenv
- werkzeug
Para instalar los requisitos de manera más comoda se recomienda ejecutar el archivo "requeriments.txt", con el comando ``` pip install -r requirements.txt ```

## Ejecutar la aplicacion
Para esto basta con ejecutar el comando
``` python run.py ```
dentro de la consola.

Como prueba para poblar la base de datos y tener algo de contenido al iniciar se agregó un script "seed_data.py", el cual cumple la funcion de poblar datos de prueba y se ejecuta antes de iniciar la aplicacion con el comando:
``` python seed_data.py ```

## Licencia
Este proyecto está licenciado bajo los términos de la Licencia MIT.  
Consulta el archivo [LICENSE](LICENSE) para más información.