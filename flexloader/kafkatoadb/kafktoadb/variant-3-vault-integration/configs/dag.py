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
    'kafka_to_adb_spark_vault',
    default_args=default_args,
    description='Transfer data from Kafka to ADB using Spark with HashiCorp Vault integration',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['spark', 'kafka', 'adb', 'vault'],
)

# Функция для создания задачи KubernetesPodOperator
def create_spark_task():
    return KubernetesPodOperator(
        task_id='spark_kafka_to_adb',
        namespace='spark-namespace',  # Замените на ваш namespace
        image='apache/spark:3.3.0',  # Базовый образ Spark
        arguments=[
            "spark-submit",
            "--master", "k8s://https://kubernetes.default.svc:443",
            "--deploy-mode", "cluster",
            "--conf", "spark.kubernetes.container.image=apache/spark:3.3.0",
            "--conf", "spark.kubernetes.authenticate.driver.serviceAccountName=spark-vault-auth",
            "--conf", "spark.executor.instances=2",
            "--conf", "spark.jars.packages=org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,org.postgresql:postgresql:42.2.23",
            # Добавим конфигурацию для логирования Spark
            "--conf", "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:///log4j.properties",
            "--conf", "spark.executor.extraJavaOptions=-Dlog4j.configuration=file:///log4j.properties",
            "/opt/spark/work-dir/sparkapp.py"  # Путь к приложению
        ],
        env_vars={
            "ADB_URL": "{{ conn.adb_con.host }}",  # URL ADB из коннектора
            "ADB_USER": "{{ conn.adb_con.login }}",  # Логин ADB из коннектора
            "ADB_PASSWORD": "{{ conn.adb_con.password }}",  # Пароль ADB из коннектора
            "KAFKA_BOOTSTRAP_SERVERS": "{{ var.value.kafka_bootstrap_servers }}",
            "KAFKA_TOPIC": "{{ var.value.kafka_topic }}",
            "VAULT_ADDR": "{{ conn.vault.host }}",  # Адрес Vault сервера
            "VAULT_SECRET_PATH": "secret/data/kafka-certs",  # Путь к секретам в Vault
            "KAFKA_KEYSTORE_PATH": "/vault/secrets/kafka-keystore.jks",
            "KAFKA_TRUSTSTORE_PATH": "/vault/secrets/kafka-truststore.jks"
        },
        # Аннотации для Vault Agent Injector
        annotations={
            "vault.hashicorp.com/agent-inject": "true",
            "vault.hashicorp.com/role": "spark-app",
            "vault.hashicorp.com/agent-inject-secret-kafka-keystore.jks": "secret/data/kafka-certs",
            "vault.hashicorp.com/agent-inject-template-kafka-keystore.jks": """{{- with secret "secret/data/kafka-certs" -}}
            {{- .Data.data.keystore_content | base64Decode -}}
            {{- end -}}""",
            "vault.hashicorp.com/agent-inject-secret-kafka-truststore.jks": "secret/data/kafka-certs",
            "vault.hashicorp.com/agent-inject-template-kafka-truststore.jks": """{{- with secret "secret/data/kafka-certs" -}}
            {{- .Data.data.truststore_content | base64Decode -}}
            {{- end -}}""",
            "vault.hashicorp.com/agent-inject-secret-kafka-passwords": "secret/data/kafka-certs",
            "vault.hashicorp.com/agent-inject-template-kafka-passwords": """{{- with secret "secret/data/kafka-certs" -}}
            export KAFKA_KEYSTORE_PASSWORD={{ .Data.data.keystore_password }}
            export KAFKA_TRUSTSTORE_PASSWORD={{ .Data.data.truststore_password }}
            {{- end -}}""",
            "prometheus.io/scrape": "true",
            "prometheus.io/port": "8080"
        },
        # Добавим обработку ошибок и мониторинг
        on_failure_callback=handle_task_failure,
        get_logs=True,  # Получать логи пода
        is_delete_operator_pod=True,  # Удалять под после выполнения
        startup_timeout_seconds=600,  # Таймаут запуска пода
        # Добавим ресурсные ограничения
        resources={
            'request_cpu': '1',
            'request_memory': '2Gi',
            'limit_cpu': '2',
            'limit_memory': '4Gi'
        },
        # Добавим метки для лучшей идентификации подов
        labels={
            "app": "spark-kafka-adb",
            "component": "data-transfer",
            "environment": "{{ var.value.environment }}",
            "cert-type": "vault"
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