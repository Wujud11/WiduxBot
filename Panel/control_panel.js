// ---------------- تبويبات ----------------
function showTab(id) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
  document.querySelector(`.tab[onclick="showTab('${id}')"]`).classList.add("active");
  document.getElementById(id).classList.add("active");
}

// ---------------- إعدادات المنشن ----------------
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
    .then(() => alert("تم تحديث إعدادات المنشن!"))
    .catch(err => console.error("خطأ تحديث إعدادات المنشن:", err));
}

// ---------------- ردود اللعبة ----------------
function updateResponse() {
  const type = document.getElementById("response-type").value;
  const responses = document.getElementById("new-response-textarea").value
    .split("\n")
    .map(x => x.trim())
    .filter(x => x);

  fetch(`/api/responses/${type}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(responses),
  })
    .then(() => alert("تم تحديث الردود بنجاح!"))
    .catch(err => console.error("خطأ تحديث الردود:", err));
}

function importResponses() {
  const fileInput = document.getElementById("import-responses-file");
  const file = fileInput.files[0];
  if (!file) return alert("اختر ملف JSON أولاً.");

  const reader = new FileReader();
  reader.onload = function (e) {
    const content = e.target.result;
    try {
      const imported = JSON.parse(content);
      const type = document.getElementById("response-type").value;
      fetch(`/api/responses/${type}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(imported),
      })
        .then(() => alert("تم استيراد الردود بنجاح!"))
        .catch(err => console.error("خطأ استيراد الردود:", err));
    } catch (err) {
      alert("ملف JSON غير صالح.");
    }
  };
  reader.readAsText(file);
}

// ---------------- ردود المنشن العامة ----------------
function updateMentionReplies() {
  const responses = document.getElementById("mention-general-responses").value
    .split("\n")
    .map(x => x.trim())
    .filter(x => x);

  fetch("/api/mention_responses", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(responses),
  })
    .then(() => alert("تم تحديث ردود المنشن العامة!"))
    .catch(err => console.error("خطأ تحديث ردود المنشن:", err));
}

function importMentionReplies() {
  const fileInput = document.getElementById("import-mention-file");
  const file = fileInput.files[0];
  if (!file) return alert("اختر ملف JSON أولاً.");

  const reader = new FileReader();
  reader.onload = function (e) {
    const content = e.target.result;
    try {
      const imported = JSON.parse(content);
      fetch("/api/mention_responses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(imported),
      })
        .then(() => alert("تم استيراد ردود المنشن العامة!"))
        .catch(err => console.error("خطأ استيراد المنشن:", err));
    } catch (err) {
      alert("ملف JSON غير صالح.");
    }
  };
  reader.readAsText(file);
}

// ---------------- إدارة الأسئلة ----------------
function addBulkQuestions() {
  const raw = document.getElementById("bulk-questions").value;
  if (!raw.trim()) return;

  const lines = raw.split("\n").map(x => x.trim()).filter(x => x);
  const questions = lines.map(line => {
    const [q, correct, alts, qtype, category] = line.split("|").map(x => x.trim());
    return {
      question: q,
      correct_answer: correct,
      alt_answers: (alts || "").split(",").map(a => a.trim()).filter(a => a),
      q_type: qtype || "Normal",
      category: category || "عام"
    };
  });

  fetch("/api/questions/bulk", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(questions),
  })
    .then(() => alert("تمت إضافة الأسئلة بنجاح!"))
    .catch(err => console.error("خطأ إضافة الأسئلة:", err));
}

function importQuestions() {
  const fileInput = document.getElementById("import-questions-file");
  const file = fileInput.files[0];
  if (!file) return alert("اختر ملف JSON أولاً.");

  const reader = new FileReader();
  reader.onload = function (e) {
    const content = e.target.result;
    try {
      const imported = JSON.parse(content);
      fetch("/api/questions/bulk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(imported),
      })
        .then(() => alert("تم استيراد الأسئلة بنجاح!"))
        .catch(err => console.error("خطأ استيراد الأسئلة:", err));
    } catch (err) {
      alert("ملف JSON غير صالح.");
    }
  };
  reader.readAsText(file);
}

// ---------------- إدارة القنوات ----------------
function addChannel() {
  const name = document.getElementById("channel-name").value.trim();
  if (!name) return;

  fetch("/api/channels", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  })
    .then(() => {
      alert("تمت إضافة القناة!");
      loadChannels();
    })
    .catch(err => console.error("خطأ إضافة القناة:", err));
}

function loadChannels() {
  fetch("/api/channels")
    .then(res => res.json())
    .then(channels => {
      const ul = document.getElementById("channels-list");
      ul.innerHTML = "";
      channels.forEach(ch => {
        const li = document.createElement("li");
        li.textContent = ch;
        ul.appendChild(li);
      });
    });
}

// ---------------- إدارة الردود الخاصة ----------------
function addSpecialUser() {
  const user = document.getElementById("special-user-id").value.trim();
  const responses = document.getElementById("special-responses-box").value
    .split("\n")
    .map(x => x.trim())
    .filter(x => x);

  if (!user || !responses.length) return alert("الرجاء تعبئة اسم المستخدم والردود");

  fetch("/api/special", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: user, responses }),
  })
    .then(() => {
      alert("تمت إضافة المستخدم!");
      loadSpecials();
    })
    .catch(err => console.error("خطأ إضافة خاص:", err));
}

function updateSpecialResponses() {
  addSpecialUser(); // نفس دالة الإضافة تحدث الردود
}

function deleteSpecialUser() {
  const user = document.getElementById("special-user-id").value.trim();
  if (!user) return;

  fetch(`/api/special/${user}`, {
    method: "DELETE",
  })
    .then(() => {
      alert("تم حذف المستخدم!");
      loadSpecials();
    })
    .catch(err => console.error("خطأ حذف خاص:", err));
}

function cleanupSpecials() {
  fetch("/api/special/cleanup", { method: "POST" })
    .then(() => {
      alert("تم تنظيف الردود التالفة!");
      loadSpecials();
    })
    .catch(err => console.error("خطأ تنظيف:", err));
}

function importSpecials() {
  const fileInput = document.getElementById("import-special-file");
  const file = fileInput.files[0];
  if (!file) return alert("اختر ملف JSON أولاً.");

  const reader = new FileReader();
  reader.onload = function (e) {
    const content = e.target.result;
    try {
      const imported = JSON.parse(content);
      for (const [user, responses] of Object.entries(imported)) {
        fetch("/api/special", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: user, responses }),
        });
      }
      alert("تم استيراد الردود الخاصة!");
      loadSpecials();
    } catch (err) {
      alert("ملف JSON غير صالح.");
    }
  };
  reader.readAsText(file);
}

function loadSpecials() {
  fetch("/api/special")
    .then(res => res.json())
    .then(data => {
      const ul = document.getElementById("special-users-list");
      ul.innerHTML = "";
      for (const user of Object.keys(data)) {
        const li = document.createElement("li");
        li.textContent = user;
        ul.appendChild(li);
      }
    });
}

// ---------------- تحميل البيانات تلقائي ----------------
window.onload = () => {
  loadChannels();
  loadSpecials();
};
