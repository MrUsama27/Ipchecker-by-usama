
from flask import Flask, render_template, request
import hashlib
import psycopg2
import os

app = Flask(__name__)

def connect_db():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    return psycopg2.connect(DATABASE_URL)

# 🔧 Create table if it doesn't exist
def create_table():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS used_ips (
                id SERIAL PRIMARY KEY,
                ip_hash TEXT NOT NULL UNIQUE
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Table created successfully or already exists.")
    except Exception as e:
        print("❌ Table creation failed:", e)

# Call the table creation on app start
create_table()

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        ip = request.form['ip']
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM used_ips WHERE ip_hash = %s", (ip_hash,))
        if cur.fetchone():
            message = "❌ Duplicate IP: Already Used"
        else:
            cur.execute("INSERT INTO used_ips (ip_hash) VALUES (%s)", (ip_hash,))
            conn.commit()
            message = "✅ IP Added Successfully"
        cur.close()
        conn.close()
    return render_template('index.html', message=message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
