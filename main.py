import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session
#from wtforms import StringField,SubmitField, DateField, EmailField, SelectField
import bcrypt
import string
import random
import re

#funzione che controlla se la password ha raggiunto i requisiti minimi per essere sicura
def requirements_pass(NewPassword):

    length_error = len(NewPassword) < 8
    num_error = re.search(r"\d", NewPassword) is None
    uppercase_error = re.search(r"[A-Z]", NewPassword) is None
    lowercase_error = re.search(r"[a-z]", NewPassword) is None
    symbol_error = re.search(r"\W", NewPassword) is None

    password_ok = not ( length_error or num_error or uppercase_error or lowercase_error or symbol_error )
    
    if password_ok:
        return True
    else:
        return False    

#funzione che serve nel caso di eventuali cambiamenti dei dati va ad aggiornare lo specifico campo
def update_user(row,form,olduser):
    error_exist = False # serve nel caso in cui vogliamo cambaire il username e quello è gia in uso

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    session['username'] = form['FormUsername']
    if form['FormUsername'] != row[0][0]:
        cur.execute("UPDATE users SET username = ? WHERE username=?", (form['FormUsername'],olduser))
        conn.commit()
    else:
        error_exist = True
        return render_template("info.html", error_exist=error_exist, global_username=row[0][0], global_email=row[0][1], global_fullname=row[0][2], global_age=row[0][3], global_gender=row[0][4])
    if form['email'] != row[0][1]:
        cur.execute("UPDATE users SET email = ? WHERE username=?", (form['email'],form['FormUsername']))
        conn.commit()
    if form['fullname'] != row[0][2]:
        cur.execute("UPDATE users SET fullname = ? WHERE username=?", (form['fullname'],form['FormUsername']))
        conn.commit()
    if form['age'] != row[0][3]:
        cur.execute("UPDATE users SET age = ? WHERE username=?", (form['age'],form['FormUsername']))
        conn.commit()
    if form['gender'] != row[0][4]:
        cur.execute("UPDATE users SET gender = ? WHERE username=?", (form['gender'],form['FormUsername']))
        conn.commit()

    conn.close()
    
    
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

#ritorno tutti i dati dell'utente
def retrieve_all(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))  

    result = cur.fetchall()
    return result

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
        not_hashed_psw = password
        #procedimento per encodare e "salare" la password
        password = password.encode('utf-8')
        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())

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
        if requirements_pass(not_hashed_psw):
            register_user_to_db(username,email,fullname,age,gender,hashed_pw)
            return redirect(url_for('login'))
        else:
            req_psw = True
            return render_template('register.html', req_psw=req_psw)
    
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

    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
        else:
            username = "Guest"
        
        #  PER INVIARE UN MESSAGGIO NON è NECCESSARIO ESSERE LOGGATI SUL SITO
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        print(message)
        # se almeno un campo non è completato allora mi uscirà un alert con l'errore e mi riporterà successivamente alla stessa pagina
        if not name or not email or not subject or not message:
            requirements = True
            return render_template('contact.html', requirements=requirements, global_username=username)

        #se tutto viene soddisfatto allora mi salva nel DB tutte le informazioni dal contact.html
        create_message(name,email,subject,message)

    if 'username' in session:
        username = session['username']
    else:
        username = "Guest"

    

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
@app.route('/info', methods=['GET', 'POST'])
def info():
    checkpwd = False # errore nel caso in cui le password corrispondano, si sbloccano altri due form
    error_match1 = False #error se non corrisponde la password del Db con quella inserita dall'utente
    error_match = False #errore se non metchano la NewPassword e ConfirmNewPassword
    requirements = False #nel caso in cui non vengano rispettati i requisiti minimi
    success = False

    if 'username' in session:
        if session['logged_in'] == True and session['username']:
            row = retrieve_all(session['username']) #passo il username presente nella sessione e recupero tutti i dati dell'utente dal DB

            if request.method == "POST":
                FormUsername = request.form['FormUsername']
                #bottone per commettere cambio di (username,email,fullnam,age,gender)
                if request.form['action'] == "one":
                    print(session['username'])
                    row = retrieve_all(session['username'])
                    print(row)
                    update_user(row,request.form, FormUsername) 
                    update_user(row,request.form, row[0][0]) 
                    row = retrieve_all(session['username'])
                    success = True
                    print(row) 
                
                #bottone per controllare se la password del DB corrisponda con quella inserita dall'utente e sblocco gli altri 2 form
                if request.form['action'] == "two":
                    YourPassword = request.form['YourPassword']
                    hashed_psw = retrieve_password(session['username'])
                    if bcrypt.checkpw(YourPassword.encode('utf-8'), hashed_psw):
                        checkpwd = True
                    # se no mi rimanda alla stessa pagina con un errore che le password non corrispondano
                    else:
                        error_match1 = True
                        #in questo caso visto che richiediamo tutti i valori della riga, c'è lo passa come una matrice quindi è necessario l'utilizzo di 2 indic
                        return render_template('info.html', error_match1=error_match1, global_username=row[0][0], global_email=row[0][1], global_fullname=row[0][2], global_age=row[0][3], global_gender=row[0][4], global_checkpwd= checkpwd)
                
                #bottone per controllare se la nuova password è accettabile e se uguali
                if request.form['action'] == "three":
                    NewPassword = request.form['NewPassword']
                    ConfirmNewPassword = request.form['ConfirmNewPassword']
                    #mi salvo la password non heshata per poi vedere se soddisfa i requisiti minimi
                    NewPassword_not_hash = NewPassword
                    #se le passsword corrispondano e soddisfa i requisiti allora me la salva nel Db e mi slogga portando alla pagina index
                    if NewPassword == ConfirmNewPassword:
                        if requirements_pass(NewPassword_not_hash):
                            insert_rec_psw(session['username'], bcrypt.hashpw(NewPassword.encode('utf-8'), bcrypt.gensalt()))
                            return redirect(url_for('logout'))
                        else:
                            checkpwd = True
                            requirements = True
                            return render_template('info.html', requirements=requirements, global_username=row[0][0], global_email=row[0][1], global_fullname=row[0][2], global_age=row[0][3], global_gender=row[0][4], global_checkpwd=checkpwd)
                
                    else:
                        error_match = True
                        checkpwd = True
                        return render_template('info.html', error_match=error_match, global_username=row[0][0], global_email=row[0][1], global_fullname=row[0][2], global_age=row[0][3], global_gender=row[0][4], global_checkpwd=checkpwd)
            print(row)
            return render_template('info.html',success=success, global_username=row[0][0], global_email=row[0][1], global_fullname=row[0][2], global_age=row[0][3], global_gender=row[0][4], global_checkpwd= checkpwd)
    #se l'utente non è loggato, non sarà in grado di accedere a questa pagina
    else:
        username = "Guest"
        requirements = True
        return render_template('index.html', requirements=requirements, global_username=username)


#Edit Account if the User is a

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