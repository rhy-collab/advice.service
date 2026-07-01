FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e . email-validator
ENV PORT=8080
EXPOSE 8080
# Migrations run on startup (RUN_MIGRATIONS_ON_STARTUP=true by default)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
