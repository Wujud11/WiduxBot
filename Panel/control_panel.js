// control_panel.js

const API_BASE_URL = "http://128.199.217.221:9200"; // IP السيرفر مع المنفذ

async function fetchData(url) {
  const response = await fetch(API_BASE_URL + url);
  return response.json();
}

async function postData(url, data) {
  await fetch(API_BASE_URL + url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}

async function putData(url, data) {
  await fetch(API_BASE_URL + url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}

async function deleteData(url) {
  await fetch(API_BASE_URL + url, {
    method: "DELETE"
  });
}

// Tabs switching
function showTab(id) {
  document.querySelectorAll(".section").forEach(section => {
    section.classList.remove("active");
  });
  document.getElementById(id).classList.add("active");

  if (id === "game-responses") loadGameResponses();
  else if (id === "mention-replies") loadMentionReplies();
  else if (id === "questions") loadQuestions();
  else if (id === "channels") loadChannels();
  else if (id === "special") loadSpecialResponses();
  else if (id === "settings") loadMentionSettings();
}

/* ----------------- إعدادات المنشن ----------------- */
async function loadMentionSettings() {
  const data = await fetchData("/settings");
  document.getElementById("mention_limit").value = data.mention_limit;
  document.getElementById("mention_guard_warn_msg").value = data.mention_guard_warn_msg;
  document.getElementById("mention_guard_timeout_msg").value = data.mention_guard_timeout_msg;
  document.getElementById("mention_guard_duration").value = data.mention_guard_duration;
  document.getElementById("mention_guard_cooldown").value = data.mention_guard_cooldown;
  document.getElementById("mention_daily_cooldown").checked = data.mention_daily_cooldown;
}

async function updateMentionSettings() {
  const settings = {
    mention_limit: parseInt(document.getElementById("mention_limit").value),
    mention_guard_warn_msg: document.getElementById("mention_guard_warn_msg").value,
    mention_guard_timeout_msg: document.getElementById("mention_guard_timeout_msg").value,
    mention_guard_duration: parseInt(document.getElementById("mention_guard_duration").value),
    mention_guard_cooldown: parseInt(document.getElementById("mention_guard_cooldown").value),
    mention_daily_cooldown: document.getElementById("mention_daily_cooldown").checked
  };
  await postData("/settings", settings);
  alert("تم تحديث إعدادات المنشن!");
}

/* ----------------- رسم العناصر ----------------- */
function createItemDiv(text, index, type) {
  const div = document.createElement("div");
  div.className = "item";
  div.innerHTML = `
    <input type="text" id="${type}-edit-${index}" value="${text}" style="width:80%;">
    <div class="item-buttons">
      <button onclick="updateItem('${type}', ${index})">تعديل</button>
      <button onclick="deleteItem('${type}', ${index})">حذف</button>
    </div>
  `;
  return div;
}

function createQuestionDiv(question, index) {
  const div = document.createElement("div");
  div.className = "item";
  div.innerHTML = `
    <input type="text" id="question-${index}" value="${question.question}" placeholder="السؤال">
    <input type="text" id="answer-${index}" value="${question.answer}" placeholder="الإجابة الصحيحة">
    <input type="text" id="alternatives-${index}" value="${question.alternatives.join(',')}" placeholder="بدائل الإجابة">
    <input type="text" id="type-${index}" value="${question.type}" placeholder="نوع السؤال">
    <input type="text" id="category-${index}" value="${question.category}" placeholder="تصنيف السؤال">
    <div class="item-buttons">
      <button onclick="updateQuestion(${index})">تعديل</button>
      <button onclick="deleteQuestion(${index})">حذف</button>
    </div>
  `;
  return div;
}

function createSpecialUserDiv(user, index) {
  const div = document.createElement("div");
  div.className = "item";
  div.innerHTML = `
    <input type="text" id="special-user-${index}" value="${user.username}" placeholder="اسم المستخدم">
    <textarea id="special-responses-${index}" placeholder="ردود خاصة (كل سطر رد)">${user.responses.join('\n')}</textarea>
    <div class="item-buttons">
      <button onclick="updateSpecialUser(${index})">تعديل</button>
      <button onclick="deleteSpecialUser(${index})">حذف</button>
    </div>
  `;
  return div;
}

/* ----------------- تحميل البيانات ----------------- */
async function loadGameResponses() {
  const list = document.getElementById("game-responses-list");
  list.innerHTML = "";
  const data = await fetchData("/game-responses");
  data.forEach((response, index) => {
    const div = createItemDiv(response, index, "game");
    list.appendChild(div);
  });
}

async function loadMentionReplies() {
  const list = document.getElementById("mention-replies-list");
  list.innerHTML = "";
  const data = await fetchData("/mention-replies");
  data.forEach((response, index) => {
    const div = createItemDiv(response, index, "mention");
    list.appendChild(div);
  });
}

async function loadQuestions() {
  const list = document.getElementById("questions-list");
  list.innerHTML = "";
  const data = await fetchData("/questions");
  data.forEach((question, index) => {
    const div = createQuestionDiv(question, index);
    list.appendChild(div);
  });
}

async function loadChannels() {
  const list = document.getElementById("channels-list");
  list.innerHTML = "";
  const data = await fetchData("/channels");
  data.forEach((channel, index) => {
    const div = createItemDiv(channel, index, "channel");
    list.appendChild(div);
  });
}

async function loadSpecialResponses() {
  const list = document.getElementById("special-users-list");
  list.innerHTML = "";
  const data = await fetchData("/special-responses");
  data.forEach((user, index) => {
    const div = createSpecialUserDiv(user, index);
    list.appendChild(div);
  });
}

/* ----------------- تعديل وحذف ----------------- */
async function updateItem(type, index) {
  const value = document.getElementById(`${type}-edit-${index}`).value;
  await putData(`/${type}/${index}`, { value });
  alert("تم تعديل العنصر!");
  showTab(`${type === "game" ? "game-responses" : type === "mention" ? "mention-replies" : "channels"}`);
}

async function deleteItem(type, index) {
  await deleteData(`/${type}/${index}`);
  alert("تم حذف العنصر!");
  showTab(`${type === "game" ? "game-responses" : type === "mention" ? "mention-replies" : "channels"}`);
}

async function updateQuestion(index) {
  const data = {
    question: document.getElementById(`question-${index}`).value,
    answer: document.getElementById(`answer-${index}`).value,
    alternatives: document.getElementById(`alternatives-${index}`).value.split(','),
    type: document.getElementById(`type-${index}`).value,
    category: document.getElementById(`category-${index}`).value
  };
  await putData(`/questions/${index}`, data);
  alert("تم تعديل السؤال!");
  showTab("questions");
}

async function deleteQuestion(index) {
  await deleteData(`/questions/${index}`);
  alert("تم حذف السؤال!");
  showTab("questions");
}

async function updateSpecialUser(index) {
  const data = {
    username: document.getElementById(`special-user-${index}`).value,
    responses: document.getElementById(`special-responses-${index}`).value.split('\n')
  };
  await putData(`/special-responses/${index}`, data);
  alert("تم تعديل المستخدم!");
  showTab("special");
}

async function deleteSpecialUser(index) {
  await deleteData(`/special-responses/${index}`);
  alert("تم حذف المستخدم!");
  showTab("special");
}

/* ----------------- استيراد ملفات JSON ----------------- */
async function importGameResponses() {
  const fileInput = document.getElementById("import-game-responses-file");
  const file = fileInput.files[0];
  if (!file) return;
  const text = await file.text();
  const data = JSON.parse(text);
  await postData("/import-game-responses", data);
  alert("تم استيراد الردود!");
  showTab("game-responses");
}

async function importMentionReplies() {
  const fileInput = document.getElementById("import-mention-replies-file");
  const file = fileInput.files[0];
  if (!file) return;
  const text = await file.text();
  const data = JSON.parse(text);
  await postData("/import-mention-replies", data);
  alert("تم استيراد ردود المنشن!");
  showTab("mention-replies");
}

async function importQuestions() {
  const fileInput = document.getElementById("import-questions-file");
  const file = fileInput.files[0];
  if (!file) return;
  const text = await file.text();
  const data = JSON.parse(text);
  await postData("/import-questions", data);
  alert("تم استيراد الأسئلة!");
  showTab("questions");
}

async function importSpecialResponses() {
  const fileInput = document.getElementById("import-special-responses-file");
  const file = fileInput.files[0];
  if (!file) return;
  const text = await file.text();
  const data = JSON.parse(text);
  await postData("/import-special-responses", data);
  alert("تم استيراد الردود الخاصة!");
  showTab("special");
}
