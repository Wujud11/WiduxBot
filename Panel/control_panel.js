
const API_BASE_URL = "http://128.199.217.221:9200";

async function fetchSettings() {
    const res = await fetch(API_BASE_URL + "/settings");
    const data = await res.json();
    document.getElementById("settings-container").innerText = JSON.stringify(data, null, 2);
}

async function fetchGameResponses() {
    const res = await fetch(API_BASE_URL + "/game-responses");
    const data = await res.json();
    document.getElementById("game-responses-container").innerText = JSON.stringify(data, null, 2);
}

async function fetchMentionReplies() {
    const res = await fetch(API_BASE_URL + "/mention-replies");
    const data = await res.json();
    document.getElementById("mention-replies-container").innerText = JSON.stringify(data, null, 2);
}

async function fetchQuestions() {
    const res = await fetch(API_BASE_URL + "/questions");
    const data = await res.json();
    document.getElementById("questions-container").innerText = JSON.stringify(data, null, 2);
}

async function fetchChannels() {
    const res = await fetch(API_BASE_URL + "/channels");
    const data = await res.json();
    document.getElementById("channels-container").innerText = JSON.stringify(data, null, 2);
}

async function fetchSpecialResponses() {
    const res = await fetch(API_BASE_URL + "/special-responses");
    const data = await res.json();
    document.getElementById("special-responses-container").innerText = JSON.stringify(data, null, 2);
}

// دوال الإضافة
function showAddResponseForm() {
    document.getElementById("form-container").innerHTML = `
        <input id="new-response" placeholder="نص الرد الجديد">
        <button onclick="addGameResponse()">حفظ</button>
    `;
}

async function addGameResponse() {
    const newValue = document.getElementById("new-response").value;
    const responses = await fetch(API_BASE_URL + "/game-responses").then(r => r.json());
    responses.push(newValue);
    await fetch(API_BASE_URL + "/import-game-responses", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(responses)
    });
    alert("تمت إضافة الرد!");
    fetchGameResponses();
}

function showAddMentionForm() {
    document.getElementById("form-container").innerHTML = `
        <input id="new-mention" placeholder="نص المنشن الجديد">
        <button onclick="addMentionReply()">حفظ</button>
    `;
}

async function addMentionReply() {
    const newValue = document.getElementById("new-mention").value;
    const replies = await fetch(API_BASE_URL + "/mention-replies").then(r => r.json());
    replies.push(newValue);
    await fetch(API_BASE_URL + "/import-mention-replies", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(replies)
    });
    alert("تمت إضافة الرد على المنشن!");
    fetchMentionReplies();
}

function showAddQuestionForm() {
    document.getElementById("form-container").innerHTML = `
        <input id="new-question" placeholder="السؤال الجديد">
        <button onclick="addQuestion()">حفظ</button>
    `;
}

async function addQuestion() {
    const newValue = document.getElementById("new-question").value;
    const questions = await fetch(API_BASE_URL + "/questions").then(r => r.json());
    questions.push(newValue);
    await fetch(API_BASE_URL + "/import-questions", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(questions)
    });
    alert("تمت إضافة السؤال!");
    fetchQuestions();
}

function showAddChannelForm() {
    document.getElementById("form-container").innerHTML = `
        <input id="new-channel" placeholder="اسم القناة الجديدة">
        <button onclick="addChannel()">حفظ</button>
    `;
}

async function addChannel() {
    const newValue = document.getElementById("new-channel").value;
    const channels = await fetch(API_BASE_URL + "/channels").then(r => r.json());
    channels.push(newValue);
    await fetch(API_BASE_URL + "/import-channels", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(channels)
    });
    alert("تمت إضافة القناة!");
    fetchChannels();
}

function showAddSpecialUserForm() {
    document.getElementById("form-container").innerHTML = `
        <input id="new-special-user" placeholder="رد خاص جديد">
        <button onclick="addSpecialResponse()">حفظ</button>
    `;
}

async function addSpecialResponse() {
    const newValue = document.getElementById("new-special-user").value;
    const users = await fetch(API_BASE_URL + "/special-responses").then(r => r.json());
    users.push(newValue);
    await fetch(API_BASE_URL + "/import-special-responses", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(users)
    });
    alert("تمت إضافة الرد الخاص!");
    fetchSpecialResponses();
}
