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
// ----------------------------
// الردود العامة للمنشن
// ----------------------------

// حفظ الردود العامة
async function saveGeneralReplies() {
  const textarea = document.getElementById('general-replies-textarea');
  const replies = textarea.value.split('\n').filter(line => line.trim() !== '');

  try {
    const response = await fetch('/api/mention_replies', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mention_general_responses: replies })
    });
    const result = await response.json();
    if (result.success) {
      alert('تم حفظ الردود العامة بنجاح!');
    } else {
      alert('خطأ أثناء حفظ الردود العامة!');
    }
  } catch (error) {
    alert('حدث خطأ أثناء الاتصال بالسيرفر.');
    console.error(error);
  }
}

// تحميل الردود العامة وعرضها تلقائيًا
async function loadGeneralReplies() {
  try {
    const response = await fetch('/api/mention_replies');
    const data = await response.json();
    const textarea = document.getElementById('general-replies-textarea');
    textarea.value = data.mention_general_responses.join('\n');
  } catch (error) {
    console.error('فشل في تحميل الردود العامة:', error);
  }
}

// لما الصفحة تجهز، نحمل الردود العامة بعد ما نحمل القنوات
document.addEventListener('DOMContentLoaded', () => {
  loadGeneralReplies();
});
// ----------------------------
// الردود الخاصة
// ----------------------------

// إضافة أو تعديل ردود مستخدم خاص
async function addSpecialReply() {
  const username = document.getElementById('special-username').value.trim();
  const repliesText = document.getElementById('special-replies-textarea').value.trim();
  const replies = repliesText.split('\n').filter(line => line.trim() !== '');

  if (!username || replies.length === 0) {
    alert('الرجاء إدخال اسم مستخدم ورد واحد على الأقل.');
    return;
  }

  try {
    const response = await fetch('/api/special_replies/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, replies })
    });
    const result = await response.json();
    if (result.success) {
      alert('تمت إضافة أو تعديل الردود الخاصة لهذا المستخدم!');
      loadSpecialReplies();
    } else {
      alert('خطأ أثناء حفظ الردود الخاصة.');
    }
  } catch (error) {
    alert('حدث خطأ أثناء الاتصال بالسيرفر.');
    console.error(error);
  }
}

// تحميل جميع الردود الخاصة
async function loadSpecialReplies() {
  try {
    const response = await fetch('/api/special_replies');
    const data = await response.json();
    const list = document.getElementById('special-replies-list');
    list.innerHTML = '';

    for (const username in data.special_mentions) {
      const li = document.createElement('li');
      li.textContent = username;
      const deleteButton = document.createElement('button');
      deleteButton.textContent = 'حذف';
      deleteButton.style.marginRight = '10px';
      deleteButton.onclick = () => deleteSpecialReply(username);
      li.appendChild(deleteButton);
      list.appendChild(li);
    }
  } catch (error) {
    console.error('فشل في تحميل الردود الخاصة:', error);
  }
}

// حذف ردود مستخدم كامل
async function deleteSpecialReply(username) {
  if (!confirm(`متأكد أنك تريد حذف الردود الخاصة بالمستخدم: ${username} ؟`)) return;

  try {
    const response = await fetch('/api/special_replies/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username })
    });
    const result = await response.json();
    if (result.success) {
      alert('تم حذف الردود الخاصة بالمستخدم!');
      loadSpecialReplies();
    } else {
      alert('خطأ أثناء حذف الردود الخاصة.');
    }
  } catch (error) {
    alert('حدث خطأ أثناء الاتصال بالسيرفر.');
    console.error(error);
  }
}

// تحميل الردود الخاصة تلقائيًا
document.addEventListener('DOMContentLoaded', () => {
  loadSpecialReplies();
});
// ----------------------------
// إدارة الأسئلة
// ----------------------------

// إضافة سؤال جديد
async function addQuestion() {
  const questionText = document.getElementById('question-text').value.trim();
  const answerText = document.getElementById('answer-text').value.trim();
  const alternativesText = document.getElementById('alternatives-text').value.trim();
  const questionType = document.getElementById('question-type').value.trim();

  if (!questionText || !answerText || !questionType) {
    alert('الرجاء تعبئة كل الحقول المطلوبة (سؤال، إجابة، نوع).');
    return;
  }

  const alternatives = alternativesText
    ? alternativesText.split(',').map(alt => alt.trim()).filter(alt => alt)
    : [];

  const data = {
    question: questionText,
    answer: answerText,
    alternatives,
    type: questionType
  };

  try {
    const response = await fetch('/api/questions/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await response.json();
    if (result.success) {
      alert('تمت إضافة السؤال بنجاح!');
      loadQuestions();
    } else {
      alert('خطأ أثناء إضافة السؤال!');
    }
  } catch (error) {
    alert('حدث خطأ أثناء الاتصال بالسيرفر.');
    console.error(error);
  }
}

// تحميل جميع الأسئلة
async function loadQuestions() {
  try {
    const response = await fetch('/api/questions');
    const data = await response.json();
    const list = document.getElementById('questions-list');
    list.innerHTML = '';

    data.forEach((q, index) => {
      const li = document.createElement('li');
      li.innerHTML = `<strong>س:</strong> ${q.question} <br> <strong>الإجابة:</strong> ${q.answer} <br> <strong>البدائل:</strong> ${q.alternatives.join(', ')} <br> <strong>النوع:</strong> ${q.type}`;
      const deleteButton = document.createElement('button');
      deleteButton.textContent = 'حذف';
      deleteButton.style.marginTop = '5px';
      deleteButton.onclick = () => deleteQuestion(index);
      li.appendChild(deleteButton);
      list.appendChild(li);
    });
  } catch (error) {
    console.error('فشل في تحميل الأسئلة:', error);
  }
}

// حذف سؤال معين
async function deleteQuestion(index) {
  if (!confirm('متأكد أنك تريد حذف هذا السؤال؟')) return;

  try {
    const response = await fetch('/api/questions/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ index })
    });
    const result = await response.json();
    if (result.success) {
      alert('تم حذف السؤال بنجاح!');
      loadQuestions();
    } else {
      alert('خطأ أثناء حذف السؤال.');
    }
  } catch (error) {
    alert('حدث خطأ أثناء الاتصال بالسيرفر.');
    console.error(error);
  }
}

// تحميل الأسئلة تلقائيًا لما تجهز الصفحة
document.addEventListener('DOMContentLoaded', () => {
  loadQuestions();
});
// ----------------------------
// ردود اللعبة والطقطقة
// ----------------------------

// أنواع الردود المتاحة
const responseTypes = [
  'solo_win_responses',
  'team_win_responses',
  'golden_question_responses',
  'steal_success_responses',
  'steal_fail_responses',
  'doom_question_responses',
  'sabotage_success_responses',
  'sabotage_fail_responses',
  'test_of_fate_success_responses',
  'test_of_fate_fail_responses',
  'boost_success_responses'
];

// حفظ ردود اللعبة حسب النوع
async function saveGameResponses() {
  const selectedType = document.getElementById('response-type-selector').value;
  const textarea = document.getElementById('game-responses-textarea');
  const responses = textarea.value.split('\n').filter(line => line.trim() !== '');

  if (!selectedType) {
    alert('الرجاء اختيار نوع الرد.');
    return;
  }

  try {
    const response = await fetch('/api/game_responses/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: selectedType, responses })
    });
    const result = await response.json();
    if (result.success) {
      alert('تم حفظ الردود بنجاح!');
    } else {
      alert('خطأ أثناء حفظ الردود.');
    }
  } catch (error) {
    alert('حدث خطأ أثناء الاتصال بالسيرفر.');
    console.error(error);
  }
}

// تحميل الردود حسب النوع المختار
async function loadGameResponses() {
  const selectedType = document.getElementById('response-type-selector').value;
  if (!selectedType) return;

  try {
    const response = await fetch(`/api/game_responses/get?type=${selectedType}`);
    const data = await response.json();
    const textarea = document.getElementById('game-responses-textarea');
    textarea.value = data.responses.join('\n');
  } catch (error) {
    console.error('فشل في تحميل الردود:', error);
  }
}

// تعبئة Dropdown بأنواع الردود
function setupResponseTypeSelector() {
  const selector = document.getElementById('response-type-selector');
  responseTypes.forEach(type => {
    const option = document.createElement('option');
    option.value = type;
    option.textContent = type;
    selector.appendChild(option);
  });

  selector.addEventListener('change', loadGameResponses);
}

// تحميل أنواع الردود لما الصفحة تجهز
document.addEventListener('DOMContentLoaded', () => {
  setupResponseTypeSelector();
  loadGameResponses();
});
