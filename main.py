import os
import boto3
import json
import base64
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

# Cargar variables de entorno (para DYNAMODB_ENDPOINT_URL)
load_dotenv()

# --- Modelos Pydantic ---

class InteractionItem(BaseModel):
    """Modelo para un item de interacción individual."""
    interaction_id: str
    timestamp: str
    reason: str
    solution: str
    summary: str
    channel: str

class ApiResponse(BaseModel):
    """Modelo para la respuesta de la API, incluyendo paginación."""
    account_number: str
    items: List[InteractionItem]
    next_cursor: Optional[str] = Field(None, description="Token para la siguiente página de resultados")

# --- Configuración de la App ---

app = FastAPI(
    title="Interactions API",
    description="API para consultar historial de interacciones de clientes (Ejercicio Técnico)",
    version="1.0.0"
)

# --- Configuración de DynamoDB ---

def get_dynamodb_resource():
    """
    Crea un recurso de DynamoDB.
    Si DYNAMODB_ENDPOINT_URL está en .env, se conecta localmente.
    De lo contrario, se conecta a AWS.
    """
    endpoint_url = os.getenv("DYNAMODB_ENDPOINT_URL")
    if endpoint_url:
        # Conexión local (para Docker)
        return boto3.resource(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name='us-east-1',
            aws_access_key_id='dummy',
            aws_secret_access_key='dummy'
        )
    else:
        # Conexión a AWS (para Lambda)
        return boto3.resource('dynamodb')

def get_interactions_table():
    """Obtiene la tabla de DynamoDB."""
    dynamodb = get_dynamodb_resource()
    # Usamos un nombre de tabla de una variable de entorno,
    # con un valor por defecto para local.
    table_name = os.getenv("INTERACTIONS_TABLE_NAME", "Interactions")
    return dynamodb.Table(table_name)

# --- Endpoint de la API ---

@app.get(
    "/interactions/{account_number}",
    response_model=ApiResponse,
    summary="Obtener historial de interacciones por cuenta"
)
def get_interactions(
    account_number: str,
    limit: int = Query(10, ge=1, le=100, description="Número de items por página"),
    cursor: Optional[str] = Query(None, description="Cursor de paginación (Base64)"),
    from_date: Optional[str] = Query(None, alias="from", description="Fecha de inicio (ISO 8601)"),
    to_date: Optional[str] = Query(None, alias="to", description="Fecha de fin (ISO 8601)")
):
    """
    Recupera el historial de interacciones para un `account_number` específico.

    - Soporta **paginación** usando `limit` y `cursor`.
    - Soporta **filtrado por rango de fechas** usando `from` y `to`.
    """
    table = get_interactions_table()
    
    # --- Lógica de Consulta ---
    
    # Parámetros base de la consulta
    query_params = {
        'Limit': limit,
        'ScanIndexForward': False  # Ordenar descendente (más reciente primero)
    }

    # Construir la expresión de clave (PK y SK)
    key_condition = Key('account_number').eq(account_number)

    if from_date and to_date:
        # Filtrar por PK y rango de SK (timestamp)
        key_condition = key_condition & Key('timestamp').between(from_date, to_date)
    elif from_date:
        key_condition = key_condition & Key('timestamp').gte(from_date)
    elif to_date:
        key_condition = key_condition & Key('timestamp').lte(to_date)

    query_params['KeyConditionExpression'] = key_condition

    # --- Lógica de Paginación ---
    
    if cursor:
        try:
            # Decodificar el cursor para obtener el ExclusiveStartKey
            decoded_key = base64.urlsafe_b64decode(cursor.encode('utf-8'))
            query_params['ExclusiveStartKey'] = json.loads(decoded_key.decode('utf-8'))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Cursor de paginación inválido: {e}")

    # --- Ejecutar Consulta ---
    
    try:
        response = table.query(**query_params)
    except Exception as e:
        print(f"Error al consultar DynamoDB: {e}")
        raise HTTPException(status_code=500, detail="Error interno al consultar la base de datos")

    items = response.get('Items', [])

    # --- Preparar Siguiente Cursor ---
    
    next_cursor = None
    if 'LastEvaluatedKey' in response:
        # Codificar LastEvaluatedKey como un cursor opaco en Base64
        next_cursor = base64.urlsafe_b64encode(
            json.dumps(response['LastEvaluatedKey']).encode('utf-8')
        ).decode('utf-8')

    return ApiResponse(
        account_number=account_number,
        items=items,
        next_cursor=next_cursor
    )

# --- Punto de entrada para Uvicorn (si se ejecuta localmente) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)