import requests
TOKEN = "7651482274:AAG-uHgPUybye0koU24ClffXxarv3VzjfLw"

def echo(update):
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"]
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": f"You said: {text}"}
    )

response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates").json()
for update in response.get("result", []):
    echo(update)