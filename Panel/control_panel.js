<script>
// تحميل الداتا عند فتح الصفحة
window.addEventListener('DOMContentLoaded', loadData);

function loadData() {
  fetch('/api/load') // أو المسار الصحيح عندك
    .then(response => response.json())
    .then(data => {
      for (const section in data) {
        const textarea = document.querySelector(`#${section} textarea`);
        if (textarea) {
          textarea.value = data[section];
        }
      }
    })
    .catch(error => {
      console.error(error);
      showToast('خطأ في تحميل البيانات', 'error');
    });
}

// حفظ داتا قسم معين
function saveSection(sectionId) {
  const textarea = document.querySelector(`#${sectionId} textarea`);
  if (!textarea) return;

  const data = textarea.value.trim();

  if (!data) {
    showToast('لا يمكن حفظ نص فارغ!', 'error');
    return;
  }

  fetch('/api/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ section: sectionId, content: data })
  })
  .then(response => response.json())
  .then(result => {
    if (result.success) {
      showToast('تم حفظ البيانات بنجاح', 'success');
    } else {
      showToast('خطأ أثناء الحفظ', 'error');
    }
  })
  .catch(error => {
    console.error(error);
    showToast('فشل الاتصال بالخادم', 'error');
  });
}

// عرض إشعارات (توستات) احترافية
function showToast(message, type) {
  const toast = document.createElement('div');
  toast.textContent = message;
  toast.style.position = 'fixed';
  toast.style.bottom = '20px';
  toast.style.left = '50%';
  toast.style.transform = 'translateX(-50%)';
  toast.style.padding = '12px 24px';
  toast.style.backgroundColor = type === 'success' ? '#4caf50' : '#e53935';
  toast.style.color = 'white';
  toast.style.borderRadius = '8px';
  toast.style.fontWeight = 'bold';
  toast.style.opacity = '0';
  toast.style.transition = 'opacity 0.5s';
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '1';
  }, 100);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => {
      toast.remove();
    }, 500);
  }, 3000);
}

// التنقل الناعم بالسلاسة للأقسام
document.querySelectorAll('aside a').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});
</script>
