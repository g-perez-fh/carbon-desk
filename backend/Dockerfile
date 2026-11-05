FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements/backend.txt /app/requirements/backend.txt
RUN pip install --no-cache-dir -r requirements/backend.txt
COPY backend /app/backend
WORKDIR /app/backend
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
