# Greenhouse Monitoring Project

This project is a greenhouse monitoring system that collects, processes, and visualizes sensor data (temperature, humidity, and growth rate) for a single greenhouse. The project uses **Kafka** for real-time data streaming, **SQLite** for storage, and **Dash** for data visualization.

---

## **Features**
- Collects data from sensors and streams it using Kafka.
- Stores aggregated data in SQLite with a 2-hour interval.
- Provides interactive dashboards to visualize:
  - Temperature
  - Humidity
  - Growth rate
- Automatically updates every minute.

---

## **Requirements**

### **System**
- Python 3.8+
- SQLite
- Kafka

### **Python Libraries**
Install the following Python libraries:
```bash
pip install dash sqlalchemy pandas plotly kafka-python
```

Setup
1. Clone the Repository
bash
Copy code
git clone https://github.com/username/repo-name.git
cd repo-name
2. Set Up Kafka
Download and start Kafka on your system. Follow the instructions on the official Kafka documentation.
Create the required Kafka topics:
bash
Copy code
kafka-topics.sh --create --topic sensor_temperature --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
kafka-topics.sh --create --topic sensor_humidity --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
kafka-topics.sh --create --topic sensor_light --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
3. Initialize SQLite
The SQLite database will be automatically created when you run the consume_and_process.py script.

How to Run
1. Start Kafka
Make sure Kafka is running:

bash
Copy code
kafka-server-start.sh config/server.properties
2. Start the Sensor Data Generator
Run the script to simulate sensor data:

bash
Copy code
python sensorData.py
3. Process Data with Kafka Consumer
Run the consumer to process and store data in SQLite:

bash
Copy code
python consume_and_process.py
4. Start the Dash App
Run the Dash application to visualize the data:

bash
Copy code
python app.py
Open your browser and navigate to: http://127.0.0.1:8050

Project Structure
graphql
Copy code
project/
│
├── sensorData.py            # Generates and streams sensor data to Kafka topics
├── consume_and_process.py   # Consumes Kafka data, processes it, and stores it in SQLite
├── app2.py                   # Dash application for data visualization
├── greenhouse_data.db       # SQLite database (auto-created)
├── templates/               # Dash HTML templates (if used)
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
└── .gitignore               # Git ignored files
Future Improvements
Add support for multiple greenhouses with a dropdown selector.
Include real-time updates for more granular timeframes.
Integrate with a cloud database for scalable storage.
