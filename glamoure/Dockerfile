# Imagen base de Python
FROM python:3.11-slim

# Carpeta de trabajo en el contenedor
WORKDIR /app

# Evitar archivos .pyc y mejorar logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copiar archivo de dependencias
COPY requirements.txt /app/

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto dentro del contenedor
COPY . /app/

# Exponer el puerto donde correrá Django
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
