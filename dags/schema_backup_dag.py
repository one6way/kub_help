from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable
import logging
import os
import tempfile
import json
from pathlib import Path

# Получаем настройки из переменных Airflow
POSTGRES_CONN_ID = Variable.get('postgres_conn_id', default_var='postgres_default')
AWS_CONN_ID = Variable.get('aws_conn_id', default_var='aws_default')
S3_BUCKET = Variable.get('s3_backup_bucket', default_var='your-backup-bucket')

# Получаем список пар база-схема для бэкапа
DB_SCHEMA_PAIRS = Variable.get('db_schema_pairs', default_var=json.dumps([]))

# Парсим конфигурацию
DB_SCHEMA_PAIRS = json.loads(DB_SCHEMA_PAIRS)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def get_db_name(conn_id):
    """Get database name from connection"""
    hook = PostgresHook(postgres_conn_id=conn_id)
    conn = hook.get_conn()
    return conn.info.dbname

def backup_schema_to_s3(conn_id, db_name, schema_name, execution_date, **context):
    """Backup a single schema to S3"""
    hook = PostgresHook(postgres_conn_id=conn_id)
    s3_hook = S3Hook(aws_conn_id=AWS_CONN_ID)
    
    # Создаем временный файл для дампа
    with tempfile.NamedTemporaryFile(suffix='.sql', delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
    
    try:
        # Формируем команду pg_dump для схемы
        pg_dump_cmd = f"pg_dump -h {hook.get_conn().info.host} " \
                     f"-p {hook.get_conn().info.port} " \
                     f"-U {hook.get_conn().info.user} " \
                     f"-d {db_name} " \
                     f"-n {schema_name} " \
                     f"-F c " \
                     f"-f {tmp_file_path}"
        
        # Устанавливаем переменную окружения с паролем
        os.environ['PGPASSWORD'] = hook.get_conn().info.password
        
        # Выполняем pg_dump
        os.system(pg_dump_cmd)
        
        # Формируем путь в S3
        date_str = execution_date.strftime('%Y-%m-%d')
        s3_key = f"postgres_backups/{db_name}/{schema_name}/{date_str}/{schema_name}.sql"
        
        # Загружаем файл в S3
        s3_hook.load_file(
            filename=tmp_file_path,
            key=s3_key,
            bucket_name=S3_BUCKET,
            replace=True
        )
        
        logging.info(f"Successfully backed up schema {schema_name} from database {db_name} to S3: {s3_key}")
        
    except Exception as e:
        logging.error(f"Error backing up schema {schema_name} from database {db_name}: {str(e)}")
        raise
    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        # Очищаем переменную окружения
        if 'PGPASSWORD' in os.environ:
            del os.environ['PGPASSWORD']

with DAG(
    'postgres_schema_backup',
    default_args=default_args,
    description='Backup PostgreSQL schemas to S3',
    schedule_interval='0 20 * * *',  # Run at 20:00 UTC (23:00 MSK)
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['postgres', 'backup'],
) as dag:

    def backup_all_schemas(**context):
        """Backup all configured schemas to S3"""
        execution_date = context['execution_date']
        
        # Перебираем все пары база-схема из конфигурации
        for pair in DB_SCHEMA_PAIRS:
            backup_schema_to_s3(
                POSTGRES_CONN_ID,
                pair['database'],
                pair['schema'],
                execution_date,
                **context
            )

    backup_schemas_task = PythonOperator(
        task_id='backup_all_schemas',
        python_callable=backup_all_schemas,
    )

    backup_schemas_task 