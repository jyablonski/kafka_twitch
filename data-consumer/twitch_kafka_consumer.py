from datetime import datetime, timedelta
import logging
import os
import json

from confluent_kafka import Consumer, KafkaError, KafkaException
import pandas as pd
from sqlalchemy import exc, create_engine

# https://docs.confluent.io/clients-confluent-kafka-python/current/overview.html

def sql_connection(rds_schema: str):
    """
    SQL Connection function connecting to my postgres db with schema = nba_source where initial data in ELT lands
    Args:
        None
    Returns:
        SQL Connection variable to schema: nba_source in my PostgreSQL DB
    """
    RDS_USER = os.environ.get('RDS_USER')
    RDS_PW = os.environ.get('RDS_PW')
    RDS_IP = os.environ.get('IP')
    RDS_DB = os.environ.get('RDS_DB')
    try:
        connection = create_engine(
            f"postgresql+psycopg2://{RDS_USER}:{RDS_PW}@{RDS_IP}:5432/{RDS_DB}",
            connect_args={"options": f"-csearch_path={rds_schema}"},
            # defining schema to connect to
            echo=False,
        )
        logging.info(f"SQL Connection to schema: {rds_schema} Successful")
        return connection
    except exc.SQLAlchemyError as e:
        logging.error(f"SQL Connection to schema: {rds_schema} Failed, Error: {e}")
        return e

def write_to_sql(con, data, table_type):
    """
    SQL Table function to write a pandas data frame in aws_dfname_source format
    Args:
        data: The Pandas DataFrame to store in SQL
        table_type: Whether the table should replace or append to an existing SQL Table under that name
    Returns:
        Writes the Pandas DataFrame to a Table in Snowflake in the {nba_source} Schema we connected to.
    """
    try:
        data_name = [k for k, v in globals().items() if v is data][0]
        # ^ this disgusting monstrosity is to get the name of the -fucking- dataframe lmfao
        if len(data) == 0:
            logging.info(f"{data_name} is empty, not writing to SQL")
        else:
            data.to_sql(
                con=con,
                name=f"twitch_{data_name}_source",
                index=False,
                if_exists=table_type,
            )
            logging.info(f"Writing twitch_{data_name}_source to SQL")
    except BaseException as error:
        logging.error(f"SQL Write Script Failed, {error}")
        return error


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    handlers=[logging.FileHandler("python_logs/example.log"), logging.StreamHandler()],
)

logging.info('STARTING TWITCH KAFKA CONSUMER')

consumer = Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'jacobsgroup',
        'auto.offset.reset': 'earliest',
        'session.timeout.ms': 20000
})


consumer.subscribe(['twitch-streams'])
logging.info('CONNECTING TO TOPIC twitch_streams')

kafka_data = []
conn = sql_connection(os.environ.get())

end_time = datetime.now() + timedelta(minutes=1)
logging.info(f"Current Time is {datetime.now()}, End time is {end_time} (60 s)")

while True:
    msg = consumer.poll(1.0)
    current_time = datetime.now()

    if msg is None:
        continue
    if msg.error():
        logging.info("Consumer error: {}".format(msg.error()))
        continue
    
    # the str json loads is to convert false and true booleans to False and True which you need for python dict.
    msg_clean = json.loads(str(msg.value().decode('utf-8')))
    logging.info(f'Received message: {msg_clean}')
    kafka_data.append(msg_clean)

    if current_time > end_time:
        print(f"Proccessed {len(kafka_data)} total messages after 60 seconds")
        kafka_df = pd.DataFrame(kafka_data)
        write_to_sql(conn, kafka_df, "append")
        logging.info('FINISHING TWITCH KAFKA CONSUMER')
        break  
    else:
        continue

consumer.close()
