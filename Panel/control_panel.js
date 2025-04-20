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
// ----------------------------
// إدارة القنوات
// ----------------------------

// إضافة قناة جديدة
async function addChannel() {
  const channelName = document.getElementById('new-channel').value.trim();
  if (!channelName) {
    alert('الرجاء كتابة اسم القناة.');
    return;
  }

  try {
    const response = await fetch('/api/channels/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ channel: channelName })
    });
    const result = await response.json();
    if (result.success) {
      alert('تمت إضافة القناة بنجاح!');
      loadChannels();
    } else {
      alert('خطأ أثناء إضافة القناة!');
    }
  } catch (error) {
    alert('حدث خطأ أثناء الاتصال بالسيرفر.');
    console.error(error);
  }
}

// تحميل القنوات الحالية وعرضها
async function loadChannels() {
  try {
    const response = await fetch('/api/channels');
    const data = await response.json();
    const list = document.getElementById('channels-list');
    list.innerHTML = '';
    data.channels.forEach(channel => {
      const li = document.createElement('li');
      li.textContent = channel;
      const deleteButton = document.createElement('button');
      deleteButton.textContent = 'حذف';
      deleteButton.style.marginRight = '10px';
      deleteButton.onclick = () => deleteChannel(channel);
      li.appendChild(deleteButton);
      list.appendChild(li);
    });
  } catch (error) {
    console.error('فشل في تحميل القنوات:', error);
  }
}

// حذف قناة
async function deleteChannel(channelName) {
  if (!confirm(`متأكد أنك تريد حذف القناة: ${channelName} ؟`)) return;

  try {
    const response = await fetch('/api/channels/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ channel: channelName })
    });
    const result = await response.json();
    if (result.success) {
      alert('تم حذف القناة بنجاح!');
      loadChannels();
    } else {
      alert('خطأ أثناء حذف القناة!');
    }
  } catch (error) {
    alert('حدث خطأ أثناء الاتصال بالسيرفر.');
    console.error(error);
  }
}

// تحميل القنوات تلقائي لما تفتح القسم
document.addEventListener('DOMContentLoaded', () => {
  loadChannels();
});
