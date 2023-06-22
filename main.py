import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session

global_username = ""

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
#funzione che andrà a controllare solo il username
def check_user_exist(username):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE username = ?", (username,))

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
    return render_template("index.html")
    

#pagina della registrazione
@app.route('/register', methods=["POST", "GET"])
def register():
    error = False
    #permetto di ottenere l'accesso ai dati inseriti e li memorizzo in un database
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if check_user_exist(username,):
            error = True
            
        else:
            register_user_to_db(username,password)
            return redirect(url_for('index'))
    
    else:
        return render_template('register.html')

#pagina del login    
@app.route('/login', methods=["POST", "GET"])
def login():
    #permetto di ottenere l'accesso ai dati inseriti, controllo se esiste tra quelli gia loggati e riporto sulla pagina home
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = False

        if check_user(username, password):
            global_username = username
            return redirect(url_for('index'))
        else:
            error = True
            #return render_template("login.html")
    
    else:
        return render_template('login.html')

#per il controllo durante il login
@app.route("/home", methods=["POST", "GET"])
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return render_template("errore.html")
    
#per il controllo durante la registrazione
@app.route('/home1', methods=["POST", "GET"])
def home1():
    if username in session:
        return render_template("home1.html", username=session['username'])
    else:
        return render_template("user_taken.html")
        
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/tabella")
def tabella():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute("SELECT * from users")

    rows = cur.fetchall()
    return render_template("tabella.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)