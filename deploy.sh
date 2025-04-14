#!/bin/bash

cd /root/widuxBot || exit 1
echo "[Webhook] تم استلام تحديث من GitHub!" >> /root/webhook_log.txt

git reset --hard
git pull origin main

# إغلاق أي نسخة سابقة من البوت
pkill -f "python3 main.py"

# تشغيل البوت من جديد
nohup python3 main.py > /dev/null 2>&1 &
