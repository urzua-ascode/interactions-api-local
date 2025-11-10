# Usar una imagen base de Python delgada
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto 8080 (donde Uvicorn se ejecutará)
EXPOSE 8080

# Comando para ejecutar la aplicación
# Uvicorn es el servidor ASGI que ejecutará FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]