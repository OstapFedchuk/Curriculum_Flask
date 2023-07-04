import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session
import bcrypt
import string
import random

#password generator for recovery password
def password_generator():
    recovery_psw = ""
    string.letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890\|!"£$%&/()=?*[]@#§-_:.;,'
    
    for x in range(10):
        recovery_psw += random.choice(string.letters)
    
    return recovery_psw


#funzione che serve per settare nel Db la recovery_psw
def insert_rec_psw(username,password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = ? WHERE username=?", (password,username))
    conn.commit()
    conn.close()

#funzione che va a recuperare la password heshed dal DB
def retrieve_password(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    #inserendo il username dell'utente andiamo a recuperare la passsword dal DB
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    
    result = cur.fetchone()
    return result[0]     

#funzione che memorizza il username e password nel database
def register_user_to_db(username,email,fullname,age,gender,password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username,email,fullname,age,gender,password) VALUES (?, ?, ?, ?, ?, ?)", (username,email,fullname,age,gender,password))
    conn.commit()
    conn.close()

#funzione che serve per salvare i dati del client del contact.html form
def create_message(name,email,subject,message):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (name,email,subject,message) VALUES (?, ?, ?, ?)", (name,email,subject,message))
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
# configuriamo la secret key situata nel 'config.py' per tenere in sicurezza la sessione del utente
app.config.from_pyfile('config.py')


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
    error = False #serve se il username è gia esistente
    requirements = False # serve quando tutti campi non sono compilati
    #permetto di ottenere l'accesso ai dati inseriti e li memorizzo in un database
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        fullname = request.form['fullname']
        age = request.form['age']
        gender = request.form['gender']
        password = request.form['password']
        
        #procedimento per encodare e "salare" la password
        password = password.encode('utf-8')
        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        print(hashed_pw)

        # controlla se tutti i campi sono stati inseriti
        if not username or not email or not fullname or not age or not gender or not password:
            requirements = True
            return render_template('register.html', requirements=requirements)

        #controla se nel database è gia presente un'utente loggato con quel username
        # se esite allota errore diventa True e ti riporta sulla stessa pagina 
        if check_user_exist(username,):
            error = True
            return render_template("register.html", error=error)
        
        # altrimenti salva tutti i dati nel DB e ti porta nella pagina del login
        else:
            register_user_to_db(username,email,fullname,age,gender,hashed_pw)
            return redirect(url_for('login'))
    
    else:
        return render_template('register.html')

#LOGIN   
@app.route('/login', methods=["GET", "POST"])
def login():
    error = False # errore se username o password sono errati
    
    #permetto di ottenere l'accesso ai dati inseriti, controllo se esiste tra quelli gia loggati e riporto sulla pagina home
    if request.method == 'POST':
        username = request.form['username']
        UserPassword = request.form['UserPassword']
        
        #controllo l'esistenza del username
        if check_user_exist(username):
            #recupero dal DB la password hashed
            hashed_psw = retrieve_password(username)
            #controllo se la PSW recuperata è uguale a quella inserita
            if bcrypt.checkpw(UserPassword.encode('utf-8'), hashed_psw):
                #salvo nella sessione il username e riporto nella pagina index
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('index'))
            # se username non esiste mi ritorna al login.html con un errore visivo
            else:
                error = True
                return render_template('login.html', error=error)

        # se password non esiste mi ritorna al login.html con un errore visivo    
        else:
            error = True
            return render_template('login.html', error=error)
 
    return render_template('login.html')

#GitHub Status Page
@app.route('/gitstatus')
def gitstatus():
    return render_template('gitstatus.html')

#Contact Page
@app.route('/contact', methods=["GET", "POST"])
def contact():
    requirements = False # errore che serve per far comparire il messaggio nel caso in cui non vengano riempiti tutti i form

    if 'username' in session:
        return render_template('contact.html', global_username=session['username'])
    else:
        username = "Guest"
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        if not name or not email or not subject or not message:
            requirements = True
            return render_template('contact.html', requirements=requirements, global_username=username)

        create_message(name,email,subject,message)

    return render_template("contact.html", global_username=username)

#About Page, with my Curriculum Vitae
@app.route('/about')
def about():
    if 'username' in session:
        return render_template('about.html', global_username=session['username'])
    else:
        username = "Guest"
    return render_template("about.html", global_username=username)

# user info Page
@app.route('/info')
def info():
    if 'username' in session:
        return render_template('info.html', global_username=session['username'])
    else:
        username = "Guest"
    return render_template("info.html", global_username=username)

#Password Recovery Page
@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    error = False

    if request.method == 'POST':
        username = request.form['username']
        
        if check_user_exist(username):
            #genero la password temporanea senza encoddarla
            clear_psw = password_generator()
            #encoddo la password generata
            rec_psw = clear_psw.encode('utf-8')
            #hesho la password encoddata
            hashed_rec_psw = bcrypt.hashpw(rec_psw, bcrypt.gensalt())
            #recupero la password dal DB
            password = retrieve_password(username)
            # la password viene sostituita
            password = hashed_rec_psw

            #inserisco la nuova password all'interno del DB
            insert_rec_psw(username,password)
            return render_template('recovery.html', rec_psw=clear_psw) #passo all'utente la password generata senza il sale
        
        else:
            error = True
            return render_template('recovery.html', error=error)


    return render_template('recovery.html')

#LogOut Page      
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#esecuzione dell'applicazione
if __name__ == "__main__":
    app.run(debug=True)