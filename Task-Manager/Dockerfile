FROM python:3.13-slim
WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
