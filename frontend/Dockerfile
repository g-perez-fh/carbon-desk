FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 FRONTEND_HOST=0.0.0.0
WORKDIR /app
COPY requirements/frontend.txt /app/requirements/frontend.txt
RUN pip install --no-cache-dir -r requirements/frontend.txt
COPY frontend /app/frontend
EXPOSE 8080
CMD ["python", "-m", "frontend.main"]
