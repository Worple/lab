from kafka import KafkaConsumer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime
from datetime import datetime
import json

# SQLite Configuration
SQLITE_DB = "/home/worpl/lab/greenhouse_data.db"
engine = create_engine(f"sqlite:///{SQLITE_DB}")
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()

# Define Tables
greenhouse_data_table = Table(
    "greenhouse_data", metadata,
    Column("id", Integer, primary_key=True),
    Column("greenhouse_id", Integer),
    Column("sensor_type", String(50)),
    Column("value", Float),
    Column("timestamp", DateTime),
    Column("growth_rate", Float)
)

logs_table = Table(
    "logs", metadata,
    Column("id", Integer, primary_key=True),
    Column("greenhouse_id", Integer),
    Column("sensor_type", String(50)),
    Column("value", Float),
    Column("timestamp", DateTime)
)

# Create Tables if they don't exist
metadata.create_all(engine)

# Kafka Consumer Configuration
consumer = KafkaConsumer(
    "sensor_temperature",
    "sensor_humidity",
    "sensor_light",
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='greenhouse-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def calculate_growth_rate(data):
    # Example logic for growth rate calculation
    temp = data.get("value") if data.get("sensor") == "temperature" else 25  # Default to optimal temp
    optimal_temp = 25
    return max(0, min(100, 100 - abs(optimal_temp - temp) * 5))

def process_and_save_data(data):
    try:
        print(f"Processing data: {data}")

        # Record for greenhouse_data
        greenhouse_record = {
            "greenhouse_id": data["greenhouse_id"],
            "sensor_type": data["sensor"],
            "value": data["value"],
            "timestamp": datetime.fromisoformat(data["timestamp"]),
            "growth_rate": calculate_growth_rate(data)
        }

        # Record for logs
        log_record = {
            "greenhouse_id": data["greenhouse_id"],
            "sensor_type": data["sensor"],
            "value": data["value"],
            "timestamp": datetime.fromisoformat(data["timestamp"])
        }

        # Save to greenhouse_data table
        session.execute(greenhouse_data_table.insert(), greenhouse_record)

        # Save to logs table
        session.execute(logs_table.insert(), log_record)

        # Commit both operations
        session.commit()
        print(f"Inserted records: greenhouse_data={greenhouse_record}, logs={log_record}")
    except Exception as e:
        print(f"Error inserting records: {e}")
        session.rollback()  # Rollback transaction on error
    finally:
        session.close()  # Close session to release resources


# Main Consumer Loop
try:
    print("Starting Kafka Consumer...")
    for message in consumer:
        data = message.value
        process_and_save_data(data)
except KeyboardInterrupt:
    print("\nStopping Consumer... Cleaning up resources.")
finally:
    consumer.close()
    print("Consumer stopped. Goodbye!")

