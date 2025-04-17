// ========== تبويبات ==========
function showTab(id) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
  document.querySelector(`.tab[onclick="showTab('${id}')"]`).classList.add("active");
  document.getElementById(id).classList.add("active");
}

// ========== إعدادات المنشن ==========
function updateMentionSettings() {
  const data = {
    mention_limit: parseInt(document.getElementById("mention_limit").value) || 0,
    mention_guard_warn_msg: document.getElementById("mention_guard_warn_msg").value,
    mention_guard_timeout_msg: document.getElementById("mention_guard_timeout_msg").value,
    mention_guard_duration: parseInt(document.getElementById("mention_guard_duration").value) || 0,
    mention_guard_cooldown: parseInt(document.getElementById("mention_guard_cooldown").value) || 0,
    mention_daily_cooldown: document.getElementById("mention_daily_cooldown").checked
  };
  fetch("/api/settings/mention", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }).then(() => alert("تم تحديث إعدادات المنشن!"))
    .catch(err => console.error("خطأ:", err));
}

function loadMentionSettings() {
  fetch("/api/settings/mention")
    .then(res => res.json())
    .then(data => {
      document.getElementById("mention_limit").value = data.mention_limit || 0;
      document.getElementById("mention_guard_warn_msg").value = data.mention_guard_warn_msg || "";
      document.getElementById("mention_guard_timeout_msg").value = data.mention_guard_timeout_msg || "";
      document.getElementById("mention_guard_duration").value = data.mention_guard_duration || 0;
      document.getElementById("mention_guard_cooldown").value = data.mention_guard_cooldown || 0;
      document.getElementById("mention_daily_cooldown").checked = data.mention_daily_cooldown || false;
    })
    .catch(err => console.error("فشل تحميل إعدادات المنشن:", err));
}

// ========== ردود اللعبة ==========
function loadGameResponses() {
  const type = document.getElementById("game-response-type").value;
  fetch(`/api/responses/${type}`)
    .then(res => res.json())
    .then(data => {
      document.getElementById("game-response-textarea").value = data.join("\n");
    });
}

function saveGameResponses() {
  const type = document.getElementById("game-response-type").value;
  const lines = document.getElementById("game-response-textarea").value.split("\n").filter(Boolean);
  fetch(`/api/responses/${type}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ responses: lines }),
  }).then(() => alert("تم الحفظ"));
}

function importGameResponses(event) {
  const file = event.target.files[0];
  if (!file) return alert("اختر ملف JSON");
  const reader = new FileReader();
  reader.onload = function (e) {
    try {
      const data = JSON.parse(e.target.result);
      Object.entries(data).forEach(([key, responses]) => {
        fetch(`/api/responses/${key}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ responses }),
        });
      });
      alert("تم استيراد الردود!");
    } catch {
      alert("ملف غير صالح");
    }
  };
  reader.readAsText(file);
}

// ========== ردود المنشن ==========
function loadMentionResponses() {
  fetch("/api/responses/mention_responses")
    .then(res => res.json())
    .then(data => {
      document.getElementById("mention-responses-box").value = data.join("\n");
    });
}

function saveMentionResponses() {
  const lines = document.getElementById("mention-responses-box").value.split("\n").filter(Boolean);
  fetch("/api/responses/mention_responses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ responses: lines }),
  }).then(() => alert("تم حفظ ردود المنشن"));
}

function importMentionResponses(event) {
  const file = event.target.files[0];
  if (!file) return alert("اختر ملف");
  const reader = new FileReader();
  reader.onload = function (e) {
    try {
      const responses = JSON.parse(e.target.result);
      fetch("/api/responses/mention_responses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ responses }),
      }).then(() => alert("تم الاستيراد"));
    } catch {
      alert("ملف غير صالح");
    }
  };
  reader.readAsText(file);
}

// ========== الردود الخاصة ==========
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
    });
}

function addSpecialUser() {
  const user = document.getElementById("special-user-id").value.trim();
  const responses = document.getElementById("special-responses-box").value.split("\n").filter(Boolean);
  fetch("/api/special", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user, responses }),
  }).then(() => {
    alert("تمت الإضافة!");
    loadSpecials();
  });
}

function deleteSpecialUser() {
  const user = document.getElementById("special-user-id").value.trim();
  fetch(`/api/special/${user}`, { method: "DELETE" })
    .then(() => {
      alert("تم الحذف!");
      loadSpecials();
    });
}

function cleanupSpecials() {
  fetch("/api/special/cleanup", { method: "POST" })
    .then(res => res.json())
    .then(data => {
      alert(`تم تنظيف ${data.count} رد تالف`);
      loadSpecials();
    });
}

// ========== الأسئلة ==========
function addQuestion() {
  const question = document.getElementById("question-text").value;
  const correct = document.getElementById("correct-answer").value;
  const alts = document.getElementById("alt-answers").value.split(",").map(a => a.trim());
  const category = document.getElementById("question-category").value;
  const type = document.getElementById("question-type").value;

  const payload = { question, correct_answer: correct, alt_answers: alts, category, q_type: type };

  fetch("/api/questions", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then(() => {
    alert("تمت إضافة السؤال!");
    loadQuestions();
  });
}

function deleteQuestion(id) {
  fetch(`/api/questions/${id}`, { method: "DELETE" })
    .then(() => loadQuestions());
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
    });
}

function importQuestions() {
  const file = document.getElementById("import-questions-file").files[0];
  const reader = new FileReader();
  reader.onload = function (e) {
    try {
      const questions = JSON.parse(e.target.result);
      questions.forEach(q => {
        fetch("/api/questions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(q),
        });
      });
      alert("تم استيراد الأسئلة!");
      loadQuestions();
    } catch {
      alert("ملف JSON غير صالح");
    }
  };
  reader.readAsText(file);
}

// ========== القنوات ==========
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
    });
}

function addChannel() {
  const name = document.getElementById("channel-name").value;
  fetch("/api/channels", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  }).then(() => {
    alert("تمت الإضافة!");
    loadChannels();
  });
}

function deleteChannel(name) {
  fetch(`/api/channels/${name}`, { method: "DELETE" })
    .then(() => {
      alert("تم الحذف!");
      loadChannels();
    });
}

// ========== تحميل تلقائي ==========
window.onload = () => {
  loadMentionSettings();
  loadGameResponses();
  loadMentionResponses();
  loadQuestions();
  loadChannels();
  loadSpecials();
};
