from flask import Flask, request, jsonify, send_file, render_template_string
from instagrapi import Client
import threading
import time
import os

app = Flask(__name__)
client = Client()
messaging_active = False

# HTML Frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Messenger By Hater</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            width: 300px;
        }
        .container h2 {
            text-align: center;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
        }
        .form-group input {
            width: 100%;
            padding: 8px;
            border: none;
            border-radius: 4px;
            margin-top: 5px;
        }
        .form-group input[type="file"] {
            background-color: #ecf0f1;
            color: #2c3e50;
        }
        .form-group input[type="text"],
        .form-group input[type="password"],
        .form-group input[type="number"] {
            background-color: #34495e;
            color: #ecf0f1;
        }
        .buttons {
            display: flex;
            justify-content: space-between;
        }
        .buttons button {
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .start {
            background-color: #27ae60;
            color: white;
        }
        .stop {
            background-color: #c0392b;
            color: white;
        }
        .start:hover {
            background-color: #2ecc71;
        }
        .stop:hover {
            background-color: #e74c3c;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Hater Papa On Top</h2>
        <form id="messengerForm" method="POST" enctype="multipart/form-data" action="/start">
            <div class="form-group">
                <label for="username">Instagram Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Instagram Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="haterName">Hater's Name:</label>
                <input type="text" id="haterName" name="haterName">
            </div>
            <div class="form-group">
                <label for="groupIds">Target Group IDs (comma-separated):</label>
                <input type="text" id="groupIds" name="groupIds" required>
            </div>
            <div class="form-group">
                <label for="messageFile">Message File (TXT):</label>
                <input type="file" id="messageFile" name="messageFile" accept=".txt" required>
            </div>
            <div class="form-group">
                <label for="delay">Delay (seconds):</label>
                <input type="number" id="delay" name="delay" required>
            </div>
            <div class="buttons">
                <button type="submit" class="start">Start Messaging</button>
                <button type="button" class="stop" onclick="stopMessaging()">Stop Messaging</button>
            </div>
        </form>
    </div>
    <script>
        function stopMessaging() {
            fetch('/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => alert(data.message))
                .catch(error => console.error('Error:', error));
        }
    </script>
</body>
</html>
"""

# Route to serve the frontend
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# Route to start messaging
@app.route('/start', methods=['POST'])
def start_messaging():
    global messaging_active
    if messaging_active:
        return jsonify({"message": "Messaging already in progress."})

    username = request.form.get('username')
    password = request.form.get('password')
    hater_name = request.form.get('haterName')
    group_ids = request.form.get('groupIds').split(',')
    delay = int(request.form.get('delay'))
    message_file = request.files.get('messageFile')

    if not username or not password or not group_ids or not message_file:
        return jsonify({"message": "Missing required fields!"})

    messages = message_file.read().decode('utf-8').splitlines()

    def send_messages():
        global messaging_active
        messaging_active = True

        try:
            client.login(username, password)
            for group_id in group_ids:
                if not messaging_active:
                    break
                for message in messages:
                    client.direct_send(message, group_id)
                    time.sleep(delay)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            messaging_active = False

    threading.Thread(target=send_messages).start()
    return jsonify({"message": "Messaging started."})

# Route to stop messaging
@app.route('/stop', methods=['POST'])
def stop_messaging():
    global messaging_active
    messaging_active = False
    return jsonify({"message": "Messaging stopped."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
