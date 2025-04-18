// control_panel.js

async function fetchData(url) {
  const response = await fetch(url);
  return response.json();
}

async function postData(url, data) {
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}

async function putData(url, data) {
  await fetch(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}

async function deleteData(url) {
  await fetch(url, {
    method: "DELETE"
  });
}

// Tabs switching
function showTab(id) {
  document.querySelectorAll(".section").forEach(section => {
    section.classList.remove("active");
  });
  document.getElementById(id).classList.add("active");

  // Load section data when shown
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

/* ----------------- ردود اللعبة ----------------- */
async function loadGameResponses() {
  const list = document.getElementById("game-responses-list");
  list.innerHTML = "";
  const data = await fetchData("/game-responses");
  data.forEach((response, index) => {
    const div = createItemDiv(response, index, "game");
    list.appendChild(div);
  });
}

/* ----------------- ردود المنشن العامة ----------------- */
async function loadMentionReplies() {
  const list = document.getElementById("mention-replies-list");
  list.innerHTML = "";
  const data = await fetchData("/mention-replies");
  data.forEach((response, index) => {
    const div = createItemDiv(response, index, "mention");
    list.appendChild(div);
  });
}

/* ----------------- الأسئلة ----------------- */
async function loadQuestions() {
  const list = document.getElementById("questions-list");
  list.innerHTML = "";
  const data = await fetchData("/questions");
  data.forEach((question, index) => {
    const div = createQuestionDiv(question, index);
    list.appendChild(div);
  });
}

/* ----------------- القنوات ----------------- */
async function loadChannels() {
  const list = document.getElementById("channels-list");
  list.innerHTML = "";
  const data = await fetchData("/channels");
  data.forEach((channel, index) => {
    const div = createItemDiv(channel, index, "channel");
    list.appendChild(div);
  });
}

/* ----------------- الردود الخاصة ----------------- */
async function loadSpecialResponses() {
  const list = document.getElementById("special-users-list");
  list.innerHTML = "";
  const data = await fetchData("/special-responses");
  data.forEach((user, index) => {
    const div = createSpecialUserDiv(user, index);
    list.appendChild(div);
  });
}
