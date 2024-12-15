import flask
from flask import Flask, jsonify, render_template
import requests
from time import time

app = Flask(__name__)

# Configuration
MINECRAFT_SERVER_IP = "urns.zapto.org"  # Replace with your server's IP or hostname

# To store player logs temporarily
player_logs = []

@app.route("/api/status", methods=["GET"])
def get_server_status():
    try:
        response = requests.get(f"https://api.mcsrvstat.us/3/{MINECRAFT_SERVER_IP}")
        if response.status_code == 200:
            data = response.json()
            online_players = data.get("players", {}).get("online", 0)
            players_list = data.get("players", {}).get("list", [])
            current_players = set(players_list)

            # Detect join/leave events
            new_logs = []

            for player in current_players:
                if player not in player_logs:
                    new_logs.append(f"{player} joined at {time()}")
                    player_logs.append(player)

            for player in player_logs:
                if player not in current_players:
                    new_logs.append(f"{player} left at {time()}")
                    player_logs.remove(player)

            return jsonify({
                "success": True,
                "online": data.get("online", False),
                "players": online_players,
                "max_players": data.get("players", {}).get("max", 0),
                "version": data.get("version", "Unknown"),
                "motd": data.get("motd", {}).get("clean", []),
                "player_logs": new_logs  # Add new logs to the response
            })
        else:
            return jsonify({"success": False, "error": "Failed to fetch server status"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
