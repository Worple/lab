import json
import random
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer

# Кількість теплиць
NUM_GREENHOUSES = 5

# Ініціалізація початкових параметрів
start_time = datetime.now().replace(hour=6, minute=0, second=0)  # Початок дня
current_time = start_time

# Параметр для вибору швидкості симуляції
SIMULATION_SPEED = 10.0  # 1.0 = реальний час, 10.0 = пришвидшена симуляція

# Функція для симуляції природної зміни освітлення
def simulate_light_level(current_time):
    sunrise = start_time
    sunset = start_time + timedelta(hours=12)  # Захід через 12 годин
    max_light = 1000  # Максимальна освітленість, люкс

    if sunrise <= current_time <= sunset:
        elapsed_hours = (current_time - sunrise).seconds / 3600
        if elapsed_hours <= 6:  # До полудня
            return max_light * (elapsed_hours / 6) + random.uniform(-50, 50)
        else:  # Після полудня
            return max_light * (1 - ((elapsed_hours - 6) / 6)) + random.uniform(-50, 50)
    else:
        # Ніч: мінімальне освітлення
        return random.uniform(0, 10)

# Функція для симуляції температури
def simulate_temperature(current_time):
    sunrise = start_time
    sunset = start_time + timedelta(hours=12)
    max_temp = 30  # Максимальна температура вдень
    min_temp = 15  # Мінімальна температура вночі

    if sunrise <= current_time <= sunset:
        elapsed_hours = (current_time - sunrise).seconds / 3600
        if elapsed_hours <= 6:  # До полудня
            return min_temp + (max_temp - min_temp) * (elapsed_hours / 6) + random.uniform(-1, 1)
        else:  # Після полудня
            return max_temp - (max_temp - min_temp) * ((elapsed_hours - 6) / 6) + random.uniform(-1, 1)
    else:
        return min_temp + random.uniform(-1, 1)

# Функція для симуляції вологості (випадкові коливання)
def simulate_humidity():
    return random.uniform(30, 70)  # Відсотки вологості

# Функція для серіалізації JSON
def json_serializer(data):
    return json.dumps(data).encode('utf-8')

# Налаштування Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],  # Адреса Kafka брокера
    value_serializer=json_serializer
)

# Топіки для кожного датчика
topics = {
    "temperature": "sensor_temperature",
    "humidity": "sensor_humidity",
    "light_level": "sensor_light"
}

# Основний цикл імітації
try:
    print("Починаємо імітацію роботи датчиків для 5 теплиць...")
    while True:
        current_time += timedelta(seconds=10 * SIMULATION_SPEED)  # Швидкість симуляції

        for greenhouse_id in range(1, NUM_GREENHOUSES + 1):
            # Генерація значень для кожного датчика
            light_level = simulate_light_level(current_time)
            temperature = simulate_temperature(current_time)
            humidity = simulate_humidity()

            # Створення JSON для кожного датчика
            temperature_data = {
                "greenhouse_id": greenhouse_id,
                "sensor": "temperature",
                "value": round(temperature, 2),
                "timestamp": current_time.isoformat()
            }
            humidity_data = {
                "greenhouse_id": greenhouse_id,
                "sensor": "humidity",
                "value": round(humidity, 2),
                "timestamp": current_time.isoformat()
            }
            light_level_data = {
                "greenhouse_id": greenhouse_id,
                "sensor": "light_level",
                "value": round(light_level, 2),
                "timestamp": current_time.isoformat()
            }

            # Надсилання в Kafka
            producer.send(topics["temperature"], temperature_data)
            producer.send(topics["humidity"], humidity_data)
            producer.send(topics["light_level"], light_level_data)

            # Логування у консоль
            print(f"Greenhouse {greenhouse_id} - Temperature: {temperature_data}")
            print(f"Greenhouse {greenhouse_id} - Humidity: {humidity_data}")
            print(f"Greenhouse {greenhouse_id} - Light Level: {light_level_data}")

        # Інтервал між ітераціями
        time.sleep(2 / SIMULATION_SPEED)  # Інтервал залежить від швидкості симуляції
except KeyboardInterrupt:
    print("Зупинка програми.")
finally:
    producer.close()
