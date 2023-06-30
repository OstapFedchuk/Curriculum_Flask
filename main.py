import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session
import bcrypt

#funzione che memorizza il username e password nel database
def register_user_to_db(username,email,fullname,age,gender,password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username,email,fullname,age,gender,password) VALUES (?, ?, ?, ?, ?, ?)", (username,email,fullname,age,gender,password))
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
    
def hash_function(password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE password = ?", (password,))

    password = request.form['password']
    password = password.encode('utf-8')
    hash_pw = bcrypt.hashpw(password, bcrypt.gensalt())

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

#pagina iniziale del sito
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', global_username=session['username'])
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
        gender = request.form['gender']
        password = request.form['password']
        
        password = password.encode('utf-8')
        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        print(hashed_pw)

         #controla se nel database è gia presente un'utente loggato con quel username
        if check_user_exist(username,):
            error = True
            return render_template("register.html", error=error)
 
        else:
            register_user_to_db(username,email,fullname,age,gender,hashed_pw)
            return redirect(url_for('login'))
    
    else:
        return render_template('register.html')

#LOGIN   
@app.route('/login', methods=["GET", "POST"])
def login():
    error = False # errore se username o password sono errati
    error_pw = False # errore se password non corrispondono
    
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    #permetto di ottenere l'accesso ai dati inseriti, controllo se esiste tra quelli gia loggati e riporto sulla pagina home
    if request.method == 'POST':
        username = request.form['username']
        UserPassword = request.form['UserPassword']
        
        if check_user_exist(username):
            error = True
            return redirect(url_for('login', error=error))
        
        if bcrypt.checkpw(UserPassword, hash_function(UserPassword)):
            return redirect(url_for('index'))
        else:
            error_pw = True
            return render_template('login.html', error_pw=error_pw)
 
    return render_template('login.html')

#GitHub Status Page
@app.route('/gitstatus')
def gitstatus():
    return render_template('gitstatus.html')

#Contact Page
@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        if request.args.get('username'):
            username = request.args.get('username')
        else:
            username = "Guest"
    return render_template("contact.html", global_username=username)

#About Page, with my Curriculum Vitae
@app.route('/about')
def about():
    return render_template("about.html")

#LogOut Page      
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#esecuzione dell'applicazione
if __name__ == "__main__":
    app.run(debug=True)