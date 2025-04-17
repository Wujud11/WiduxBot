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

// ========== استيراد الأسئلة ==========
function importQuestions() {
  const fileInput = document.getElementById("import-questions-file");
  const file = fileInput.files[0];
  if (!file) return alert("اختر ملف JSON أولاً");

  const reader = new FileReader();
  reader.onload = function (e) {
    const content = e.target.result;
    try {
      const questions = JSON.parse(content);
      fetch("/api/questions/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ questions }),
      })
        .then(res => res.json())
        .then(() => {
          alert("تم استيراد الأسئلة بنجاح!");
          loadQuestions();
        })
        .catch(err => console.error("فشل رفع الملف:", err));
    } catch (err) {
      alert("ملف JSON غير صالح");
    }
  };
  reader.readAsText(file);
}

// ========== تحميل تلقائي ==========
window.onload = () => {
  loadMentionSettings();
  loadResponses();
  loadQuestions();
  loadChannels();
  loadSpecials();
};
