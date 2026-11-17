FROM python:3.12-slim

WORKDIR /srv/shopzone

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . .

RUN mkdir -p data

EXPOSE 8000

WORKDIR /srv/shopzone/backend
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
