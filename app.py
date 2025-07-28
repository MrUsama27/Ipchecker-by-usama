from flask import Flask, render_template, request, jsonify
import hashlib
import psycopg2
import os

app = Flask(__name__)

# Database connection config
DB_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DB_URL)

def hash_ip(ip):
    return hashlib.sha256(ip.encode()).hexdigest()

def is_duplicate(ip_hash):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM used_ips WHERE ip_hash = %s", (ip_hash,))
            return cur.fetchone() is not None

def save_ip(ip_hash):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO used_ips (ip_hash) VALUES (%s)", (ip_hash,))
            conn.commit()

def get_recent_ips(limit=10):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ip_hash FROM used_ips ORDER BY id DESC LIMIT %s", (limit,))
            return [row[0] for row in cur.fetchall()]

@app.route('/')
def index():
    recent = get_recent_ips()
    return render_template('index.html', recent=recent)

@app.route('/check', methods=['POST'])
def check():
    ip = request.form.get('ip')
    if not ip:
        return jsonify({'status': 'error', 'message': 'No IP provided'})

    ip_hash = hash_ip(ip)

    if is_duplicate(ip_hash):
        return jsonify({'status': 'duplicate', 'message': '❌ Duplicate IP! Already used.'})
    else:
        save_ip(ip_hash)
        return jsonify({'status': 'new', 'message': '✅ New IP added successfully!'})

import os
if __name__ == "__main__":
   port = int(os.environ.get("PORT", 5000)) 
   app.run(host="0.0.0.0", port=port)
