from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# ربط مجلد Panel كـ static files
app.mount("/Panel", StaticFiles(directory="Panel"), name="panel")

# الصفحة الرئيسية تفتح لوحة التحكم مباشرة
@app.get("/")
def root():
    return FileResponse("Panel/control_panel.html")

