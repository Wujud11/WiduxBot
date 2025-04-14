from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__, template_folder=".")
SETTINGS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bot_settings.json'))

@app.route('/')
def home():
    try:
        return render_template("control_panel.html")
    except Exception as e:
        return f"حدث خطأ: {e}"

@app.route('/responses', methods=['GET'])
def get_responses():
    response_type = request.args.get('type')
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data.get(response_type, []))

@app.route('/responses', methods=['POST'])
def add_response():
    payload = request.json
    with open(SETTINGS_FILE, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        data.setdefault(payload['type'], []).append(payload['response'])
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()
    return jsonify({"status": "added"})

@app.route('/responses', methods=['DELETE'])
def delete_response():
    payload = request.json
    with open(SETTINGS_FILE, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        if payload['response'] in data.get(payload['type'], []):
            data[payload['type']].remove(payload['response'])
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()
            return jsonify({"status": "deleted"})
    return jsonify({"status": "not found"}), 404

@app.route('/mention-settings', methods=['GET'])
def get_mention_settings():
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    keys = [
        "mention_limit", "mention_guard_warn_msg", "mention_guard_timeout_msg",
        "mention_guard_duration", "mention_cooldown", "mention_daily_cooldown"
    ]
    return jsonify({k: data.get(k) for k in keys})

@app.route('/mention-settings', methods=['PUT'])
def update_mention_settings():
    payload = request.json
    with open(SETTINGS_FILE, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        for key, value in payload.items():
            data[key] = value
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()
    return jsonify({"status": "updated", "settings": payload})

@app.route('/special-responses', methods=['GET'])
def get_special_responses():
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data.get('special_responses', {}))

@app.route('/special-responses', methods=['PUT'])
def update_special_responses():
    payload = request.json
    with open(SETTINGS_FILE, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        data['special_responses'] = payload
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()
    return jsonify({"status": "updated"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
