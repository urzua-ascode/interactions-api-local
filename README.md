# API de Analíticas de Interacciones de Clientes

Este repositorio contiene la implementación del "Hands-On Technical Exercise" para el desafío de Arquitecto de Soluciones.
Proporciona una API (GET /interactions/{account_number}) que consulta un historial de interacciones desde DynamoDB, con soporte para paginación y filtrado por fecha.

El proyecto incluye dos formas de ejecución:
- Localmente (usando Docker, FastAPI y DynamoDB Local)
- En AWS (usando AWS CDK para desplegar API Gateway, Lambda y DynamoDB)

# 1. Ejecución Local (Docker)
Esta configuración es ideal para desarrollo y pruebas rápidas.
Prerrequisitos
Docker y Docker Compose instalados y en ejecución.
Python 3.10+ (para ejecutar el script de carga de datos).

Pasos
1. Construir y Ejecutar Contenedores:
*Esto levantará la API en el puerto 8080 y DynamoDB Local en el 8000

docker-compose up --build


2. Cargar Datos de Prueba (en otra terminal):
Asegúrate de tener las dependencias de Python instaladas (pip install boto3).

python load_data.py


3. Probar la API:
Prueba básica

curl -X GET "http://localhost:8080/interactions/123456789"

*Prueba de paginación

curl -X GET "http://localhost:8080/interactions/123456789?limit=2"

*Prueba de filtro de fecha (desde el 7 de Nov de 2025)

curl -G --data-urlencode "from=2025-11-07T00:00:00Z" "http://localhost:8080/interactions/123456789"


# 2. Despliegue en AWS (AWS CDK)
Esta implementación despliega la infraestructura serverless en tu cuenta de AWS.
Prerrequisitos
AWS CLI configurada (aws configure)
Node.js y npm
AWS CDK (npm install -g aws-cdk)
Python 3.10+

Pasos
1. Mover al directorio de CDK:

cd cdk-interactions-api


2. Instalar dependencias y activar entorno virtual:

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


3. Bootstrap (Solo la primera vez):

cdk bootstrap


4. Desplegar el Stack:

cdk deploy


5. Cargar Datos de Prueba:
Una vez desplegado, ve a la consola de AWS -> DynamoDB -> Tablas -> Interactions.
Crea manualmente los elementos de prueba (ver load_data.py como referencia).

6. Probar la API Desplegada:
Obtén la URL de la API de la salida de cdk deploy.

API_URL="<pega_tu_url_de_api_gateway_aqui>"

curl -X GET "$API_URL/interactions/123456789"


