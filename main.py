from flask import Flask, render_template, request
import sqlite3 as sql

app = Flask(__name__)


#esecuzione del sito
@app.route("/")
def home():
    title = "Home"
    return render_template("home.html", title=title)

#Visualizzazione della parte di login
@app.route("/login")
def login():
    return render_template("login.html")

#Aggiunta dei record
@app.route("/addrec", methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            email = request.form['email']
            citta = request.form['citta']

            with sql.connect("database.db") as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO persone (nome,email,citta) VALUES(?,?,?)", (nome,email,citta) )

                conn.commit()
                messaggio = "Record Aggiunti con Successo"
        except:
            conn.rollback()
            messaggio = "Errore nell'inserzione"

        finally: 
            return render_template("risultato.html", messaggio=messaggio)
            conn.close()


@app.route("/tabella")
def tabella():
    conn = sql.connect("database.db")
    conn.row_factory = sql.Row

    cur = conn.cursor()
    cur.execute("SELECT * from persone")

    rows = cur.fetchall()
    return render_template("tabella.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)