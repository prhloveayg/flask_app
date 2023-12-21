import paho.mqtt.client as mqtt
import json
import pymysql.cursors
from datetime import datetime

# Callback when a message is received
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    # Store the received data in the database
    store_in_database(payload)

def store_in_database(data):
    try:
        # Connect to MySQL database
        conn = pymysql.connect(
            host='mysql',
            user='houpr',
            password="houpr1013",
            database='IoT'
        )

        # Insert the received data into the database
        cur = conn.cursor()
        sql = 'insert into data values(%s, %s, %s, %s, %s, %s, %s)'

        timestamp_seconds = int(data['timestamp']) / 1000
        datetime_value = datetime.fromtimestamp(timestamp_seconds)
        cur.execute(sql, (
                            data['clientId'][-1],
                            datetime_value,
                            data['lng'],
                            data['lat'],
                            data['info'],
                            data['value'],
                            data['alert']
                        ))

        conn.commit()

    except Exception as e:
        print(f"Error storing data in the database: {e}")

    finally:
        # Close the database connection
        conn.close()

if __name__ == "__main__":
    # Set up the MQTT client
    mqttClient = mqtt.Client()
    mqttClient.on_message = on_message
    
    # Connect to the MQTT broker
    if mqttClient.connect('mqtt', 1883, 60) == 0:
        pass
    else:
        print("Failed to connect to MQTT broker")

    # Subscribe to the specified topic
    mqttClient.subscribe("testapp")
    # Start the MQTT client loop to receive messages
    #print("subcribed")
    mqttClient.loop_forever()
