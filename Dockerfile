FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .


RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "vocali_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]