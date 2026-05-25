FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e "." && pip install --no-cache-dir uvicorn
COPY src/ src/
COPY main.py .

EXPOSE 8000
CMD ["python", "main.py"]
