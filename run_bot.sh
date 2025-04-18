#!/bin/bash

# ننتقل لمجلد السكربت الحالي تلقائيًا (حتى لو شغلته من مكان ثاني)
cd "$(dirname "$0")"

echo "تشغيل WiduxBot مع مراقبة تلقائية..."

while true; do
    python3 main.py
    echo "البوت توقف فجأة... إعادة تشغيل خلال 5 ثواني."
    sleep 5
done
