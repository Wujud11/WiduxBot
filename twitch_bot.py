import os, sys, datetime
if os.path.exists("log.txt") and os.path.getsize("log.txt") > 1 * 1024 * 1024:
    os.remove("log.txt")
class Logger:
    def write(self, msg):
        if msg.strip():
            with open("log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now()}] {msg}\n")
    def flush(self): pass
sys.stdout = Logger()
sys.stderr = open("error.log", "a", encoding="utf-8")
import os, sys, datetime
