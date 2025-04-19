function showSection(sectionId) {
  const sections = document.querySelectorAll('.section');
  sections.forEach(section => {
    section.classList.remove('active');
  });
  document.getElementById(sectionId).classList.add('active');
}

// حفظ إعدادات المنشن
async function saveMentionSettings() {
  const mentionLimit = document.getElementById('mention-limit').value;
  const timeoutDuration = document.getElementById('timeout-duration').value;
  const warningMessage = document.getElementById('warning-message').value;
  const timeoutMessage = document.getElementById('timeout-message').value;
  const cooldownPeriod = document.getElementById('cooldown-period').value;

  const data = {
    mention_limit: Number(mentionLimit),
    timeout_duration: Number(timeoutDuration),
    warning_message: warningMessage,
    timeout_message: timeoutMessage,
    cooldown_period: Number(cooldownPeriod)
  };

  try {
    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await response.json();
    if (result.success) {
      alert('تم حفظ إعدادات المنشن بنجاح!');
    } else {
      alert('خطأ أثناء حفظ الإعدادات!');
    }
  } catch (error) {
    alert('حدث خطأ أثناء الاتصال بالسيرفر');
    console.error(error);
  }
}
