import boto3
import time
from datetime import datetime, timedelta

# Configurar cliente para DynamoDB Local
# Se conecta al puerto 8000 expuesto en docker-compose
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:8000',
    region_name='us-east-1',
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy'
)

TABLE_NAME = "Interactions"

def create_interactions_table():
    """Crea la tabla 'Interactions' si no existe."""
    try:
        print(f"Creando la tabla '{TABLE_NAME}'...")
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'account_number',
                    'KeyType': 'HASH'  # Clave de partición
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'  # Clave de ordenación
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'account_number',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Esperar a que la tabla esté activa
        table.wait_until_exists()
        print(f"Tabla '{TABLE_NAME}' creada exitosamente.")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f"La tabla '{TABLE_NAME}' ya existe.")
        return dynamodb.Table(TABLE_NAME)

def load_sample_data(table):
    """Carga datos de muestra en la tabla."""
    print("Cargando datos de muestra...")
    
    base_time = datetime.now()
    account_1 = "123456789"
    account_2 = "987654321"

    items = [
        # Interacciones para la cuenta 1
        {
            'account_number': account_1,
            'timestamp': (base_time - timedelta(days=1)).isoformat(),
            'interaction_id': 'int-001',
            'reason': 'billing',
            'solution': 'invoice resent to email',
            'summary': 'Customer called about missing invoice; agent verified account and resent it.',
            'channel': 'voice'
        },
        {
            'account_number': account_1,
            'timestamp': (base_time - timedelta(days=5)).isoformat(),
            'interaction_id': 'int-002',
            'reason': 'technical support',
            'solution': 'Wi-Fi password reset',
            'summary': 'Customer reported no internet. Agent guided through router reboot and Wi-Fi password reset.',
            'channel': 'chat'
        },
        {
            'account_number': account_1,
            'timestamp': (base_time - timedelta(days=10)).isoformat(),
            'interaction_id': 'int-003',
            'reason': 'cancellations',
            'solution': 'Retention offer applied',
            'summary': 'Customer called to cancel service. Agent offered a 20% discount for 6 months, customer accepted.',
            'channel': 'voice'
        },
        # Interacción para la cuenta 2
        {
            'account_number': account_2,
            'timestamp': (base_time - timedelta(days=2)).isoformat(),
            'interaction_id': 'int-004',
            'reason': 'billing',
            'solution': 'Payment plan setup',
            'summary': 'Customer requested extension for bill payment. Agent set up a 3-month payment plan.',
            'channel': 'WhatsApp'
        }
    ]

    # Usar Batch Writer para eficiencia
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
            
    print(f"Se cargaron {len(items)} items de muestra.")

if __name__ == "__main__":
    # Esperar a que DynamoDB Local esté listo
    print("Esperando a DynamoDB Local (puede tomar unos segundos)...")
    time.sleep(5) 
    
    table = create_interactions_table()
    load_sample_data(table)