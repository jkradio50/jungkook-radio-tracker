FROM python:3.9-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y wget gnupg curl unzip fonts-liberation libglib2.0-0 libnss3 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libatk-bridge2.0-0 libgtk-3-0 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m playwright install --with-deps

# Copy code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
