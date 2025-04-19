
// إعدادات المنشن
async function saveMentionSettings() {
  const data = {
    limit: parseInt(document.getElementById('mentionLimit').value),
    duration: parseInt(document.getElementById('timeoutDuration').value),
    cooldown: parseInt(document.getElementById('cooldownPeriod').value),
    warn_msg: document.getElementById('warnMessage').value,
    timeout_msg: document.getElementById('timeoutMessage').value
  };

  const response = await fetch('/api/mention-settings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const result = await response.json();
  alert(result.message || 'تم حفظ إعدادات المنشن بنجاح');
}

// إضافة رد لعبة
async function addResponse() {
  const type = document.getElementById('responseType').value;
  const message = document.getElementById('newResponse').value;

  const data = { type, message };

  const response = await fetch('/api/responses', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const result = await response.json();
  alert(result.message || 'تمت إضافة الرد بنجاح');
}

// إدارة الأسئلة
async function addQuestion() {
  const type = document.getElementById('questionType').value;
  const text = document.getElementById('questionText').value;
  const correct = document.getElementById('correctAnswer').value;
  const alternatives = document.getElementById('alternativeAnswers').value.split('\n').map(x => x.trim());

  const data = { type, text, correct_answer: correct, alternative_answers: alternatives };

  const response = await fetch('/api/questions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const result = await response.json();
  alert(result.message || 'تمت إضافة السؤال بنجاح');
}

async function editQuestion(id) {
  const type = document.getElementById('questionType').value;
  const text = document.getElementById('questionText').value;
  const correct = document.getElementById('correctAnswer').value;
  const alternatives = document.getElementById('alternativeAnswers').value.split('\n').map(x => x.trim());

  const data = { type, text, correct_answer: correct, alternative_answers: alternatives };

  const response = await fetch(`/api/questions/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const result = await response.json();
  alert(result.message || 'تم تعديل السؤال بنجاح');
}

async function deleteQuestion(id) {
  const response = await fetch(`/api/questions/${id}`, {
    method: 'DELETE'
  });
  const result = await response.json();
  alert(result.message || 'تم حذف السؤال');
}

// إضافة قناة
async function addChannel() {
  const name = document.getElementById('channelName').value;

  const data = { name };

  const response = await fetch('/api/channels', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const result = await response.json();
  alert(result.message || 'تمت إضافة القناة');
}

// إضافة رد خاص
async function addSpecialResponse() {
  const username = document.getElementById('specialUser').value;
  const message = document.getElementById('specialResponse').value;

  const data = { username, message };

  const response = await fetch('/api/special-responses', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  const result = await response.json();
  alert(result.message || 'تمت إضافة الرد الخاص');
}
