# File: backend/ws_server.py

import asyncio
import websockets
import random
import json

# Dummy packet count generator for now
def generate_stats():
    return {
        "h1": random.randint(10, 300),
        "h2": random.randint(10, 300),
        "h3": random.randint(10, 300),
    }

async def stats_sender(websocket, path):
    while True:
        stats = generate_stats()
        await websocket.send(json.dumps(stats))
        await asyncio.sleep(2)

async def main():
    async with websockets.serve(stats_sender, "0.0.0.0", 8765):
        print("[WebSocket] Server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())


# File: backend/api_server.py (optional)

from flask import Flask, jsonify, request

app = Flask(__name__)

# Dummy network state
network_state = {
    "hosts": {
        "h1": "s1",
        "h2": "s1",
        "h3": "s2"
    }
}

@app.route("/status", methods=["GET"])
def status():
    return jsonify(network_state)

@app.route("/migrate", methods=["POST"])
def migrate():
    data = request.get_json()
    host = data.get("host")
    target_switch = data.get("switch")
    if host in network_state["hosts"]:
        network_state["hosts"][host] = target_switch
        return jsonify({"message": f"Host {host} migrated to {target_switch}"})
    else:
        return jsonify({"error": "Host not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

