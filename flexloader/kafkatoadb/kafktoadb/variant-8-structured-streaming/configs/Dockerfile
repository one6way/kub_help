FROM apache/spark:3.3.0

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install pyspark==3.3.0 psycopg2-binary

# Копирование приложения
COPY structured-streaming-app.py /app/

# Настройка рабочей директории
WORKDIR /app

# Настройка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Добавление пользователя с ограниченными правами
USER 185 