from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('vault.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS buckets 
                 (id INTEGER PRIMARY KEY, name TEXT, target REAL, balance REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, user TEXT, amount REAL, date TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('vault.db')
    c = conn.cursor()
    c.execute("SELECT * FROM buckets")
    buckets = c.fetchall()
    total_balance = sum(b[3] for b in buckets)
    # Simulated 5% Annual Yield shown as daily growth for demo
    yield_earned = total_balance * 0.05 
    
    c.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 6")
    recent_tx = c.fetchall()
    conn.close()
    return render_template('index.html', buckets=buckets, total=total_balance, yield_earned=yield_earned, transactions=recent_tx)

@app.route('/deposit', methods=['POST'])
def deposit():
    bucket_id = request.form['bucket_id']
    user = request.form['user']
    amount = float(request.form['amount'])
    conn = sqlite3.connect('vault.db')
    c = conn.cursor()
    c.execute("UPDATE buckets SET balance = balance + ? WHERE id = ?", (amount, bucket_id))
    c.execute("INSERT INTO transactions (user, amount, date) VALUES (?, ?, ?)",
              (user, amount, datetime.now().strftime("%d %b, %H:%M")))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
