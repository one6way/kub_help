FROM apache/spark:3.3.0

# Метаданные образа
LABEL maintainer="DevOps Team"
LABEL description="Spark image with embedded Kafka certificates"
LABEL version="1.0"

# Установка необходимых пакетов
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    python3-pip \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

# Создание директории для сертификатов
RUN mkdir -p /opt/spark/conf/certs

# Копирование сертификатов и keystore/truststore в образ
COPY certs/kafka.client.keystore.jks /opt/spark/conf/certs/
COPY certs/kafka.client.truststore.jks /opt/spark/conf/certs/

# Установка прав доступа
RUN chmod 400 /opt/spark/conf/certs/kafka.client.keystore.jks && \
    chmod 400 /opt/spark/conf/certs/kafka.client.truststore.jks && \
    chown -R spark:spark /opt/spark/conf/certs

# Копирование Spark-приложения
COPY sparkapp.py /opt/spark/work-dir/

# Копирование log4j.properties
COPY log4j.properties /opt/spark/conf/

# Установка дополнительных Python-пакетов
RUN pip3 install --no-cache-dir \
    numpy \
    pandas \
    pyarrow

# Переключаемся на пользователя spark для безопасного запуска
USER spark

# Настройка рабочей директории
WORKDIR /opt/spark/work-dir

# Точка входа для запуска (будет использоваться значение из родительского образа)
# ENTRYPOINT ["/opt/spark/bin/spark-submit"]

# Команда по умолчанию (запуск Spark приложения)
CMD ["sparkapp.py"] 