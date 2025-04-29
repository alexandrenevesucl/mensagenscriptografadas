# Programa principal

from flask import Flask, render_template, request, redirect, session
import sqlite3
from crypto_utils import cipher, encrypt_message, decrypt_message
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave-super-secreta'

# Banco de dados inicial
def init_db():
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
init_db()

@app.route('/')
def index():
    if 'user' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                return redirect('/login')
            except:
                return 'Usuário já existe!'
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[2], password):
                session['user'] = username
                return redirect('/dashboard')
            else:
                return 'Login inválido!'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages WHERE receiver = ?', (session['user'],))
        messages = [(m[1], decrypt_message(m[3])) for m in cursor.fetchall()]

    return render_template('dashboard.html', messages=messages)

@app.route('/send', methods=['GET', 'POST'])
def send():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        receiver = request.form['receiver']
        content = request.form['content']
        encrypted = encrypt_message(content)

        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO messages (sender, receiver, content) VALUES (?, ?, ?)',
                           (session['user'], receiver, encrypted))
            conn.commit()
            return redirect('/dashboard')
    return render_template('message.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
