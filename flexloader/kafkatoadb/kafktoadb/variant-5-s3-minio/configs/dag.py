from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.exceptions import AirflowException
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Функция для обработки ошибок
def handle_task_failure(context):
    """Обработчик ошибок для задачи."""
    task_instance = context['task_instance']
    logger.error(f"Задача {task_instance.task_id} завершилась с ошибкой!")
    logger.error(f"Execution date: {context['execution_date']}")
    logger.error(f"DAG ID: {task_instance.dag_id}")
    logger.error(f"Task state: {task_instance.state}")
    
    # Получаем информацию об ошибке
    if 'exception' in context:
        logger.error(f"Error: {str(context['exception'])}")
    
    # Логируем дополнительную информацию о поде Kubernetes
    if hasattr(task_instance, 'xcom_pull'):
        pod_name = task_instance.xcom_pull(key='pod_name')
        pod_namespace = task_instance.xcom_pull(key='pod_namespace')
        logger.error(f"Pod name: {pod_name}")
        logger.error(f"Pod namespace: {pod_namespace}")

# Параметры по умолчанию для DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,  # Увеличим количество попыток
    'retry_delay': timedelta(minutes=5),  # Задержка между попытками
    'retry_exponential_backoff': True,  # Экспоненциальное увеличение времени между попытками
    'max_retry_delay': timedelta(minutes=30),  # Максимальная задержка между попытками
}

# Инициализация DAG
dag = DAG(
    'kafka_to_adb_spark_s3_minio',
    default_args=default_args,
    description='Transfer data from Kafka to ADB using Spark with certificates from S3/MinIO',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['spark', 'kafka', 'adb', 's3', 'minio'],
)

# Функция для создания задачи KubernetesPodOperator
def create_spark_task():
    return KubernetesPodOperator(
        task_id='spark_kafka_to_adb',
        namespace='spark-namespace',  # Замените на ваш namespace
        image='apache/spark:3.3.0',  # Базовый образ Spark
        cmds=["sh", "-c"],
        arguments=[
            """
            # Ожидание инициализации init-контейнера
            echo "Ожидание инициализации сертификатов и приложения..."
            while [ ! -f /etc/kafka/certs/initialized ] || [ ! -f /opt/spark/work-dir/sparkapp.py ]; do
                sleep 2
            done
            echo "Сертификаты и приложение готовы, запуск Spark-приложения..."
            
            # Запуск Spark-приложения
            spark-submit \
            --master k8s://https://kubernetes.default.svc:443 \
            --deploy-mode cluster \
            --conf spark.kubernetes.container.image=apache/spark:3.3.0 \
            --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark-sa \
            --conf spark.executor.instances=2 \
            --conf spark.jars.packages=org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,org.postgresql:postgresql:42.2.23,com.amazonaws:aws-java-sdk:1.12.1,org.apache.hadoop:hadoop-aws:3.3.1 \
            --conf spark.driver.extraJavaOptions=-Dlog4j.configuration=file:///log4j.properties \
            --conf spark.executor.extraJavaOptions=-Dlog4j.configuration=file:///log4j.properties \
            /opt/spark/work-dir/sparkapp.py
            """
        ],
        env_vars={
            # Подключение к ADB
            "ADB_URL": "{{ conn.adb_con.host }}",  # URL ADB из коннектора
            "ADB_USER": "{{ conn.adb_con.login }}",  # Логин ADB из коннектора
            "ADB_PASSWORD": "{{ conn.adb_con.password }}",  # Пароль ADB из коннектора
            
            # Подключение к Kafka
            "KAFKA_BOOTSTRAP_SERVERS": "{{ var.value.kafka_bootstrap_servers }}",
            "KAFKA_TOPIC": "{{ var.value.kafka_topic }}",
            
            # Настройки сертификатов
            "KAFKA_KEYSTORE_PATH": "/etc/kafka/certs/keystore.jks",
            "KAFKA_TRUSTSTORE_PATH": "/etc/kafka/certs/truststore.jks",
            "KAFKA_KEYSTORE_PASSWORD": "{{ conn.kafka_secrets.password }}",
            "KAFKA_TRUSTSTORE_PASSWORD": "{{ conn.kafka_secrets.extra_dejson.truststore_password }}",
            
            # Настройки S3/MinIO
            "S3_ENDPOINT": "{{ var.value.s3_endpoint }}",
            "S3_ACCESS_KEY": "{{ conn.minio.login }}",
            "S3_SECRET_KEY": "{{ conn.minio.password }}",
            "S3_BUCKET": "{{ var.value.s3_certs_bucket }}",
            "S3_KEYSTORE_KEY": "certs/keystore.jks",
            "S3_TRUSTSTORE_KEY": "certs/truststore.jks",
            "S3_SPARKAPP_KEY": "apps/sparkapp.py"  # Путь к приложению в S3/MinIO
        },
        # Инициализация: контейнер, который загружает сертификаты из S3/MinIO перед запуском основного контейнера
        init_containers=[
            {
                "name": "init-certs",
                "image": "minio/mc:latest",
                "command": [
                    "/bin/sh",
                    "-c",
                    """
                    # Установка AWS CLI
                    apk add --no-cache aws-cli

                    # Создание директорий
                    mkdir -p /etc/kafka/certs
                    mkdir -p /opt/spark/work-dir

                    # Загрузка сертификатов и приложения из S3/MinIO
                    if [ -n "$S3_ENDPOINT" ]; then
                        # Использование MinIO Client при наличии эндпоинта
                        mc alias set minio $S3_ENDPOINT $S3_ACCESS_KEY $S3_SECRET_KEY
                        mc cp minio/$S3_BUCKET/$S3_KEYSTORE_KEY /etc/kafka/certs/keystore.jks
                        mc cp minio/$S3_BUCKET/$S3_TRUSTSTORE_KEY /etc/kafka/certs/truststore.jks
                        mc cp minio/$S3_BUCKET/$S3_SPARKAPP_KEY /opt/spark/work-dir/sparkapp.py
                    else
                        # Использование AWS CLI для AWS S3
                        aws s3 cp s3://$S3_BUCKET/$S3_KEYSTORE_KEY /etc/kafka/certs/keystore.jks --region $AWS_REGION
                        aws s3 cp s3://$S3_BUCKET/$S3_TRUSTSTORE_KEY /etc/kafka/certs/truststore.jks --region $AWS_REGION
                        aws s3 cp s3://$S3_BUCKET/$S3_SPARKAPP_KEY /opt/spark/work-dir/sparkapp.py --region $AWS_REGION
                    fi

                    # Проверка успешной загрузки файлов
                    if [ -f /etc/kafka/certs/keystore.jks ] && [ -f /etc/kafka/certs/truststore.jks ] && [ -f /opt/spark/work-dir/sparkapp.py ]; then
                        echo "Сертификаты и приложение успешно загружены"
                        chmod +x /opt/spark/work-dir/sparkapp.py
                        touch /etc/kafka/certs/initialized
                    else
                        echo "Ошибка при загрузке файлов из S3/MinIO"
                        exit 1
                    fi
                    """
                ],
                "env": [
                    {"name": "S3_ENDPOINT", "value": "{{ var.value.s3_endpoint }}"},
                    {"name": "S3_ACCESS_KEY", "value": "{{ conn.minio.login }}"},
                    {"name": "S3_SECRET_KEY", "value": "{{ conn.minio.password }}"},
                    {"name": "S3_BUCKET", "value": "{{ var.value.s3_certs_bucket }}"},
                    {"name": "S3_KEYSTORE_KEY", "value": "certs/keystore.jks"},
                    {"name": "S3_TRUSTSTORE_KEY", "value": "certs/truststore.jks"},
                    {"name": "S3_SPARKAPP_KEY", "value": "apps/sparkapp.py"},
                    {"name": "AWS_REGION", "value": "{{ var.value.aws_region | default('us-east-1') }}"}
                ],
                "volume_mounts": [
                    {
                        "name": "cert-volume",
                        "mountPath": "/etc/kafka/certs"
                    },
                    {
                        "name": "app-volume",
                        "mountPath": "/opt/spark/work-dir"
                    }
                ]
            }
        ],
        # Настройка общих томов для init-контейнера и основного контейнера
        volumes=[
            {
                "name": "cert-volume",
                "emptyDir": {}
            },
            {
                "name": "app-volume",
                "emptyDir": {}
            }
        ],
        volume_mounts=[
            {
                "name": "cert-volume",
                "mountPath": "/etc/kafka/certs"
            },
            {
                "name": "app-volume",
                "mountPath": "/opt/spark/work-dir"
            }
        ],
        # Обработка ошибок и мониторинг
        on_failure_callback=handle_task_failure,
        get_logs=True,  # Получать логи пода
        is_delete_operator_pod=True,  # Удалять под после выполнения
        startup_timeout_seconds=600,  # Таймаут запуска пода
        # Ресурсные ограничения
        resources={
            'request_cpu': '1',
            'request_memory': '2Gi',
            'limit_cpu': '2',
            'limit_memory': '4Gi'
        },
        # Метки для лучшей идентификации подов
        labels={
            "app": "spark-kafka-adb",
            "component": "data-transfer",
            "environment": "{{ var.value.environment }}",
            "cert-type": "s3-minio"
        },
        # Аннотации для дополнительной информации
        annotations={
            "prometheus.io/scrape": "true",
            "prometheus.io/port": "8080"
        },
        # Настройки для повторных попыток
        retries=default_args['retries'],
        retry_delay=default_args['retry_delay'],
        execution_timeout=timedelta(hours=2),  # Максимальное время выполнения
        dag=dag,
        do_xcom_push=True  # Включаем передачу информации через XCom
    )

# Функция для проверки статуса выполнения
def check_spark_status(**context):
    task_instance = context['task_instance']
    pod_name = task_instance.xcom_pull(task_ids='spark_kafka_to_adb', key='pod_name')
    if not pod_name:
        raise AirflowException("Не удалось получить имя пода Spark")
    logger.info(f"Spark pod name: {pod_name}")
    return "Spark job completed successfully"

# Создание задач
transfer_task = create_spark_task()
status_check = PythonOperator(
    task_id='check_spark_status',
    python_callable=check_spark_status,
    provide_context=True,
    dag=dag
)

# Установка порядка выполнения
transfer_task >> status_check 