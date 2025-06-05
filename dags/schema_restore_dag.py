from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
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

# Получаем список пар база-схема для восстановления
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

def restore_schema_from_s3(conn_id, db_name, schema_name, backup_date, **context):
    """Restore a single schema from S3 backup"""
    hook = PostgresHook(postgres_conn_id=conn_id)
    s3_hook = S3Hook(aws_conn_id=AWS_CONN_ID)
    
    # Формируем путь в S3
    s3_key = f"postgres_backups/{db_name}/{schema_name}/{backup_date}/{schema_name}.sql"
    
    # Создаем временный файл для дампа
    with tempfile.NamedTemporaryFile(suffix='.sql', delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
    
    try:
        # Проверяем существование бэкапа в S3
        if not s3_hook.check_for_key(s3_key, bucket_name=S3_BUCKET):
            raise Exception(f"Backup not found in S3: {s3_key}")
        
        # Скачиваем файл из S3
        s3_hook.download_file(
            key=s3_key,
            bucket_name=S3_BUCKET,
            local_path=tmp_file_path
        )
        
        # Формируем команду pg_restore
        pg_restore_cmd = (
            f"pg_restore -h {hook.get_conn().info.host} "
            f"-p {hook.get_conn().info.port} "
            f"-U {hook.get_conn().info.user} "
            f"-d {db_name} "
            f"-n {schema_name} "
            f"-c "  # Очищать объекты перед созданием
            f"-v "  # Подробный вывод
            f"{tmp_file_path}"
        )
        
        # Устанавливаем переменную окружения с паролем
        os.environ['PGPASSWORD'] = hook.get_conn().info.password
        
        # Выполняем pg_restore
        result = os.system(pg_restore_cmd)
        
        if result != 0:
            raise Exception(f"pg_restore failed with exit code {result}")
        
        logging.info(f"Successfully restored schema {schema_name} in database {db_name} from backup: {s3_key}")
        
    except Exception as e:
        logging.error(f"Error restoring schema {schema_name} in database {db_name}: {str(e)}")
        raise
    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        # Очищаем переменную окружения
        if 'PGPASSWORD' in os.environ:
            del os.environ['PGPASSWORD']

with DAG(
    'postgres_schema_restore',
    default_args=default_args,
    description='Restore PostgreSQL schemas from S3 backups',
    schedule_interval=None,  # Запускается только вручную
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['postgres', 'restore'],
) as dag:

    def restore_all_schemas(**context):
        """Restore all configured schemas from S3"""
        # Получаем дату бэкапа из параметров запуска
        backup_date = context['dag_run'].conf.get('backup_date')
        if not backup_date:
            raise ValueError("backup_date parameter is required")
        
        # Проверяем формат даты
        try:
            datetime.strptime(backup_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("backup_date must be in YYYY-MM-DD format")
        
        # Получаем список пар для восстановления
        pairs_to_restore = context['dag_run'].conf.get('pairs', DB_SCHEMA_PAIRS)
        
        for pair in pairs_to_restore:
            if pair not in DB_SCHEMA_PAIRS:
                logging.warning(f"Skipping unknown pair: {pair}")
                continue
            restore_schema_from_s3(
                POSTGRES_CONN_ID,
                pair['database'],
                pair['schema'],
                backup_date,
                **context
            )

    restore_schemas_task = PythonOperator(
        task_id='restore_all_schemas',
        python_callable=restore_all_schemas,
    )

    restore_schemas_task 