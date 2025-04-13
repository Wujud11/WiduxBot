from flask import Flask, request, jsonify, send_file
import json
import os

app = Flask(__name__)
SETTINGS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bot_settings.json'))

# تحميل الإعدادات من JSON
def load_settings():
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# حفظ الإعدادات
def save_settings(data):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def home():
    return send_file('control_panel.html')

@app.route('/responses', methods=['GET'])
def get_responses():
    response_type = request.args.get('type')
    data = load_settings()
    return jsonify(data.get(response_type, []))

@app.route('/responses', methods=['POST'])
def add_response():
    payload = request.json
    rtype = payload['type']
    reply = payload['response']
    data = load_settings()
    data.setdefault(rtype, []).append(reply)
    save_settings(data)
    return jsonify({"status": "added", "response": reply})

@app.route('/responses', methods=['DELETE'])
def delete_response():
    payload = request.json
    rtype = payload['type']
    reply = payload['response']
    data = load_settings()
    if rtype in data and reply in data[rtype]:
        data[rtype].remove(reply)
        save_settings(data)
        return jsonify({"status": "deleted"})
    return jsonify({"status": "not found"}), 404

@app.route('/mention-settings', methods=['GET'])
def get_mention_settings():
    data = load_settings()
    keys = [
        "mention_limit",
        "mention_guard_warn_msg",
        "mention_guard_timeout_msg",
        "mention_guard_duration",
        "mention_cooldown",
        "mention_daily_cooldown"
    ]
    return jsonify({k: data.get(k) for k in keys})

@app.route('/mention-settings', methods=['PUT'])
def update_mention_settings():
    payload = request.json
    data = load_settings()
    for key, value in payload.items():
        data[key] = value
    save_settings(data)
    return jsonify({"status": "updated", "settings": payload})

@app.route('/special-responses', methods=['GET'])
def get_special_responses():
    data = load_settings()
    return jsonify(data.get('special_responses', {}))

@app.route('/special-responses', methods=['PUT'])
def update_special_responses():
    payload = request.json  # {"user_id": [...responses]}
    data = load_settings()
    data['special_responses'] = payload
    save_settings(data)
    return jsonify({"status": "updated"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
