import socket
import os
from utils.responses import get_response

# إعدادات Twitch
HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = os.getenv("TWITCH_BOT_USERNAME")  # اسم حساب البوت
TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")  # يبدأ بـ oauth:
CHANNEL = os.getenv("TWITCH_CHANNEL")    # اسم القناة بدون #

def connect():
    sock = socket.socket()
    sock.connect((HOST, PORT))
    sock.send(f"PASS {TOKEN}\n".encode("utf-8"))
    sock.send(f"NICK {NICK}\n".encode("utf-8"))
    sock.send(f"JOIN #{CHANNEL}\n".encode("utf-8"))
    print(f"Connected to channel: #{CHANNEL}")
    return sock

def listen(sock):
    while True:
        response = sock.recv(2048).decode("utf-8")
        if response.startswith("PING"):
            sock.send("PONG\n".encode("utf-8"))
        elif "PRIVMSG" in response:
            username = response.split("!", 1)[0][1:]
            message = response.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
            print(f"{username}: {message}")

            # رد تلقائي لو أحد كتب "وج؟"
            if message == "وج؟":
                reply = get_response("solo_win_responses", {"player": username})
                if reply:
                    send_message(sock, reply)

def send_message(sock, message):
    sock.send(f"PRIVMSG #{CHANNEL} :{message}\n".encode("utf-8"))

if __name__ == "__main__":
    sock = connect()
    listen(sock)