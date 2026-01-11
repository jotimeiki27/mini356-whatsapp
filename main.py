import os
import time
import requests
import paho.mqtt.client as mqtt

# ===== MQTT CONFIG =====
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

TOPIC_LOG     = "mini356/door/log"
TOPIC_STATUS  = "mini356/door/status"
TOPIC_ONLINE  = "mini356/door/online"

# ===== WHATSAPP CONFIG (ENV) =====
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
TARGET_PHONE    = os.getenv("TARGET_PHONE")

WA_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def send_whatsapp(message):
    if not PHONE_NUMBER_ID or not ACCESS_TOKEN or not TARGET_PHONE:
        print("❌ WhatsApp ENV not set")
        return

    payload = {
        "messaging_product": "whatsapp",
        "to": TARGET_PHONE,
        "type": "text",
        "text": {"body": message}
    }

    r = requests.post(WA_URL, headers=HEADERS, json=payload)
    print("📨 WhatsApp:", r.text)

# ===== MQTT CALLBACK =====
def on_connect(client, userdata, flags, rc):
    print("✅ MQTT Connected")
    client.subscribe([
        (TOPIC_LOG, 0),
        (TOPIC_STATUS, 0),
        (TOPIC_ONLINE, 0)
    ])

def on_message(client, userdata, msg):
    text = msg.payload.decode()
    topic = msg.topic
    print(f"📩 {topic}: {text}")

    if topic == TOPIC_LOG:
        send_whatsapp(f"🚪 Door Log:\n{text}")

    elif topic == TOPIC_STATUS:
        send_whatsapp(f"🔐 Door Status:\n{text}")

    elif topic == TOPIC_ONLINE:
        send_whatsapp(f"📡 Device:\n{text}")

# ===== START =====
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
