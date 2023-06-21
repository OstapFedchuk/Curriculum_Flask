import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session

#funzione che memorizza il username e password nel database
def register_user_to_db(username, password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

#funzione che controlla se sono stati inseriti il username e la password nel database
def check_user(username,password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT username,password FROM users WHERE username = ? AND password = ?", (username, password))
    
    result = cur.fetchone()
    if result:
        return True
    else:
        return False

#inizio programma   
app = Flask(__name__)
app.secret_key = '2006'

#pagina iniziale del sito
@app.route('/')
def index():
    return render_template("login.html")

#pagina della registrazione
@app.route('/register', methods=["POST", "GET"])
def register():
    #permetto di ottenere l'accesso ai dati inseriti e li memorizzo in un database
    if request.method == 'POST':
        username = request.form('username')
        password = request.form('password') 

        register_user_to_db(username, password)
        return redirect(url_for('index'))
    
    else:
        return render_template('register.html')

#pagina del login    
@app.route('/login', methods=["POST", "GET"])
def login():
    #permetto di ottenere l'accesso ai dati inseriti, controllo se esiste tra quelli gia loggati e riporto sulla pagina home
    if request.method == 'POST':
        username = request.form('username')
        password = request.form('password') 

        if check_user(username, password):
            session['username'] = username

        return redirect(url_for('home'))
    
    else:
        return redirect(url_for('index'))

@app.route("/home", methods=["POST", "GET"])
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return "Username or password è sbagliata"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/tabella")
def tabella():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute("SELECT * from persone")

    rows = cur.fetchall()
    return render_template("tabella.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)