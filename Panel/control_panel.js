// تشغيل التبويبات
function showTab(id) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
  document.querySelector(`.tab[onclick="showTab('${id}')"]`).classList.add("active");
  document.getElementById(id).classList.add("active");
}

// إعدادات المنشن
function updateMentionSettings() {
  const data = {
    mention_limit: document.getElementById("mention_limit").value,
    mention_guard_warn_msg: document.getElementById("mention_guard_warn_msg").value,
    mention_guard_timeout_msg: document.getElementById("mention_guard_timeout_msg").value,
    mention_guard_duration: document.getElementById("mention_guard_duration").value,
    mention_cooldown: document.getElementById("mention_cooldown").value,
    mention_daily_cooldown: document.getElementById("mention_daily_cooldown").checked,
  };
  fetch("/api/settings/mention", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  .then(() => alert("تم تحديث إعدادات المنشن!"))
  .catch(err => alert("فشل في تحديث إعدادات المنشن: " + err));
}

// الردود العامة
function replaceResponses() {
  const type = document.getElementById("response-type").value;
  const lines = document.getElementById("new-response-box").value.split("\n").filter(Boolean);
  fetch(`/api/responses/${type}`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ responses: lines }),
  })
  .then(() => alert("تم تحديث الردود!"))
  .catch(err => alert("فشل في تحديث الردود: " + err));
}

// الأسئلة
function addQuestion() {
  const question = document.getElementById("question-text").value;
  const correct = document.getElementById("correct-answer").value;
  const alts = document.getElementById("alt-answers").value.split(",").map(a => a.trim()).filter(Boolean);
  const category = document.getElementById("question-category").value;
  const type = document.getElementById("question-type").value;

  if (!question || !correct || !type) return alert("يرجى ملء الحقول المطلوبة.");

  const payload = {
    question, correct_answer: correct, alt_answers: alts, category, q_type: type,
  };

  fetch("/api/questions", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  .then(() => {
    alert("تمت إضافة السؤال!");
    loadQuestions();
  })
  .catch(err => alert("فشل في إضافة السؤال: " + err));
}

function deleteQuestion(id) {
  fetch(`/api/questions/${id}`, { method: "DELETE" })
    .then(() => {
      alert("تم حذف السؤال!");
      loadQuestions();
    })
    .catch(err => alert("فشل في حذف السؤال: " + err));
}

function loadQuestions() {
  fetch("/api/questions")
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById("questions-list");
      list.innerHTML = "";
      data.forEach(q => {
        const li = document.createElement("li");
        li.textContent = `${q.question} (${q.q_type})`;
        const del = document.createElement("button");
        del.textContent = "حذف";
        del.className = "del-btn";
        del.onclick = () => deleteQuestion(q.id);
        li.appendChild(del);
        list.appendChild(li);
      });
    })
    .catch(err => console.error("فشل في تحميل الأسئلة:", err));
}

// القنوات
function addChannel() {
  const name = document.getElementById("channel-name").value;
  if (!name) return alert("يرجى إدخال اسم القناة.");
  fetch("/api/channels", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  })
  .then(() => {
    alert("تمت إضافة القناة!");
    loadChannels();
  })
  .catch(err => alert("فشل في إضافة القناة: " + err));
}

function deleteChannel(name) {
  fetch(`/api/channels/${name}`, { method: "DELETE" })
    .then(() => {
      alert("تم حذف القناة!");
      loadChannels();
    })
    .catch(err => alert("فشل في حذف القناة: " + err));
}

function loadChannels() {
  fetch("/api/channels")
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById("channels-list");
      list.innerHTML = "";
      data.forEach(ch => {
        const li = document.createElement("li");
        li.textContent = ch;
        const del = document.createElement("button");
        del.textContent = "حذف";
        del.className = "del-btn";
        del.onclick = () => deleteChannel(ch);
        li.appendChild(del);
        list.appendChild(li);
      });
    })
    .catch(err => console.error("فشل في تحميل القنوات:", err));
}

// الردود الخاصة
function addSpecialUser() {
  const user = document.getElementById("special-user-id").value;
  const responses = document.getElementById("special-responses-box").value.split("\n").filter(Boolean);
  if (!user || responses.length === 0) return alert("يرجى ملء اسم المستخدم والردود.");
  fetch("/api/special", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user, responses }),
  })
  .then(() => {
    alert("تمت الإضافة!");
    loadSpecials();
  })
  .catch(err => alert("فشل في الإضافة: " + err));
}

function deleteSpecialUser() {
  const user = document.getElementById("special-user-id").value;
  if (!user) return alert("يرجى إدخال اسم المستخدم.");
  fetch(`/api/special/${user}`, { method: "DELETE" })
    .then(() => {
      alert("تم حذف المستخدم!");
      loadSpecials();
    })
    .catch(err => alert("فشل في الحذف: " + err));
}

function loadSpecials() {
  fetch("/api/special")
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById("special-users-list");
      list.innerHTML = "";
      Object.entries(data).forEach(([user, responses]) => {
        const li = document.createElement("li");
        li.textContent = `${user} (${responses.length} رد)`;
        list.appendChild(li);
      });
    })
    .catch(err => console.error("فشل في تحميل الردود الخاصة:", err));
}

// تحميل تلقائي عند الفتح
window.onload = () => {
  loadQuestions();
  loadChannels();
  loadSpecials();
};
