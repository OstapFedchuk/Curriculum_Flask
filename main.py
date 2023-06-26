import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta

#funzione che memorizza il username e password nel database
def register_user_to_db(username,email,fullname,age,password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username,email,fullname,age,password) VALUES (?, ?, ?, ?, ?)", (username,email,fullname,age,password))
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
    if request.method == "GET":
        if request.args.get('username'):
            username = request.args.get('username')
        else:
            username = "Guest"
    return render_template("index.html", global_username=username)
    

#REGISTRAZIONE
@app.route('/register', methods=["POST", "GET"])
def register():
    error = False
    #permetto di ottenere l'accesso ai dati inseriti e li memorizzo in un database
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        fullname = request.form['fullname']
        age = request.form['age']
        password = request.form['password']

        if check_user_exist(username,):
            error = True
            return render_template("register.html", error=error)
            
        else:
            register_user_to_db(username,email,fullname,age,password)
            return redirect(url_for('index'))
    
    else:
        return render_template('register.html')

#LOGIN   
@app.route('/login', methods=["POST", "GET"])
def login():
    #permetto di ottenere l'accesso ai dati inseriti, controllo se esiste tra quelli gia loggati e riporto sulla pagina home
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = False

        if username:
            session['username'] = username[1]

        if check_user(username, password):
            return redirect(url_for('index', username=username))
        else:
            error = True
            return render_template("login.html", error=error)
    
    else:
        return render_template('login.html')


@app.route('/about')
def about():
    return render_template("about.html")
           
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