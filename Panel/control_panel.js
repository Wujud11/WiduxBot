// تبويبات
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
  })
    .then(res => res.json())
    .then(() => alert("تم تحديث إعدادات المنشن!"))
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

// ========== الردود العامة ==========
let currentResponses = [];

function loadResponses() {
  const type = document.getElementById("response-type").value;
  fetch(`/api/responses/${type}`)
    .then(res => res.json())
    .then(data => {
      currentResponses = data;
      const list = document.getElementById("responses-list");
      list.innerHTML = "";
      data.forEach((response, index) => {
        const li = document.createElement("li");

        const span = document.createElement("span");
        span.textContent = response;
        span.style.flex = "1";

        const btnGroup = document.createElement("div");
        btnGroup.className = "btn-group";

        const edit = document.createElement("button");
        edit.textContent = "تعديل";
        edit.className = "edit-btn";
        edit.onclick = () => editResponse(index, response);

        const del = document.createElement("button");
        del.textContent = "حذف";
        del.className = "del-btn";
        del.onclick = () => deleteResponse(index);

        btnGroup.appendChild(edit);
        btnGroup.appendChild(del);
        li.appendChild(span);
        li.appendChild(btnGroup);
        list.appendChild(li);
      });
    })
    .catch(err => console.error("خطأ تحميل الردود:", err));
}

function addResponse() {
  const input = document.getElementById("new-response-input");
  const value = input.value.trim();
  if (!value) return;

  const type = document.getElementById("response-type").value;
  const updated = [...currentResponses, value];

  fetch(`/api/responses/${type}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ responses: updated }),
  })
    .then(() => {
      input.value = "";
      loadResponses();
    })
    .catch(err => console.error("خطأ إضافة رد:", err));
}

function deleteResponse(index) {
  const type = document.getElementById("response-type").value;
  const updated = [...currentResponses];
  updated.splice(index, 1);

  fetch(`/api/responses/${type}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ responses: updated }),
  })
    .then(() => loadResponses())
    .catch(err => console.error("خطأ حذف رد:", err));
}

function editResponse(index, oldValue) {
  const li = document.getElementById("responses-list").children[index];
  li.innerHTML = "";

  const input = document.createElement("input");
  input.value = oldValue;
  input.style.flex = "1";

  const save = document.createElement("button");
  save.textContent = "حفظ";
  save.className = "save-btn";
  save.onclick = () => {
    const type = document.getElementById("response-type").value;
    currentResponses[index] = input.value.trim();
    fetch(`/api/responses/${type}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ responses: currentResponses }),
    })
      .then(() => loadResponses())
      .catch(err => console.error("خطأ الحفظ:", err));
  };

  li.appendChild(input);
  li.appendChild(save);
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
  })
    .then(res => res.json())
    .then(() => {
      alert("تمت إضافة السؤال!");
      loadQuestions();
    })
    .catch(err => console.error("خطأ:", err));
}

function deleteQuestion(id) {
  fetch(`/api/questions/${id}`, { method: "DELETE" })
    .then(() => {
      alert("تم حذف السؤال!");
      loadQuestions();
    })
    .catch(err => console.error("خطأ:", err));
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
    .catch(err => console.error("فشل تحميل الأسئلة:", err));
}

// ========== القنوات ==========
function addChannel() {
  const name = document.getElementById("channel-name").value;
  fetch("/api/channels", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  })
    .then(() => {
      alert("تمت إضافة القناة!");
      loadChannels();
    })
    .catch(err => console.error("خطأ:", err));
}

function deleteChannel(name) {
  fetch(`/api/channels/${name}`, { method: "DELETE" })
    .then(() => {
      alert("تم حذف القناة!");
      loadChannels();
    })
    .catch(err => console.error("خطأ:", err));
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
    .catch(err => console.error("فشل تحميل القنوات:", err));
}

// ========== الردود الخاصة ==========
function addSpecialUser() {
  const user = document.getElementById("special-user-id").value.trim();
  if (!user) return alert("رجاءً أدخل اسم المستخدم أولاً");

  const responses = document.getElementById("special-responses-box").value.split("\n").filter(Boolean);
  if (responses.length === 0) return alert("أضف رد واحد على الأقل");

  fetch("/api/special", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user, responses }),
  })
    .then(() => {
      alert("تمت الإضافة!");
      loadSpecials();
    })
    .catch(err => console.error("خطأ:", err));
}

function deleteSpecialUser() {
  const user = document.getElementById("special-user-id").value;
  if (!user) return alert("أدخل اسم المستخدم أولاً");

  fetch(`/api/special/${user}`, { method: "DELETE" })
    .then(() => {
      alert("تم حذف المستخدم!");
      loadSpecials();
    })
    .catch(err => console.error("خطأ:", err));
}

function updateSpecialResponses() {
  addSpecialUser();
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
    .catch(err => console.error("فشل تحميل الردود الخاصة:", err));
}

function cleanupSpecials() {
  if (!confirm("هل أنت متأكد من حذف الردود التالفة؟")) return;

  fetch("/api/special/cleanup", {
    method: "POST",
  })
    .then(res => res.json())
    .then(data => {
      alert(`تم حذف ${data.count} رد خاص تالف!`);
      loadSpecials();
    })
    .catch(err => console.error("خطأ التنظيف:", err));
}

// ========== تحميل تلقائي ==========
window.onload = () => {
  loadMentionSettings();
  loadQuestions();
  loadChannels();
  loadSpecials();
  loadResponses();
};
