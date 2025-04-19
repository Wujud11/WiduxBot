// حفظ القسم
async function saveSection(sectionId) {
  const textarea = document.querySelector(`#${sectionId} textarea`);
  if (!textarea) {
    alert("لم يتم العثور على خانة النص!");
    return;
  }

  const content = textarea.value.trim();
  if (!content) {
    alert("الرجاء كتابة شيء قبل الحفظ!");
    return;
  }

  const response = await fetch('/api/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ section: sectionId, content })
  });

  if (response.ok) {
    alert("تم حفظ البيانات بنجاح!");
  } else {
    alert("حدث خطأ أثناء الحفظ!");
  }
}

// تحميل البيانات القديمة عند فتح الصفحة
async function loadSettings() {
  try {
    const response = await fetch('/api/get-settings');
    if (!response.ok) throw new Error("فشل في تحميل الإعدادات");

    const data = await response.json();
    for (const [sectionId, content] of Object.entries(data)) {
      const textarea = document.querySelector(`#${sectionId} textarea`);
      if (textarea) {
        textarea.value = content;
      }
    }
  } catch (error) {
    console.error(error);
    alert("فشل الاتصال بالسيرفر لتحميل الإعدادات");
  }
}

// تنفيذ التحميل تلقائياً عند فتح الصفحة
document.addEventListener("DOMContentLoaded", loadSettings);
