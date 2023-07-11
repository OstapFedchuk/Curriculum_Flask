import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session
#from wtforms import StringField,SubmitField, DateField, EmailField, SelectField
import bcrypt
import string
import random
import re

#funzione che controlla se la password ha raggiunto i requisiti minimi per essere sicuri
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

    if not check_user_exist(form['FormUsername']):
        if form['FormUsername'] != row[0][0]:
            cur.execute("UPDATE users SET username = ? WHERE username=?", (form['FormUsername'],olduser))
            conn.commit()
            session['username'] = form['FormUsername']
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
    cur.execute("SELECT password FROM users WHERE username = ? OR email = ?", (username,username))
    
    result = cur.fetchone()
    return result[0]   

#ritorno tutti i dati dell'utente
def retrieve_all(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))  

    result = cur.fetchall()
    return result

#funzione ch emi ritorna l mail dal DB
def retrieve_email(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE username = ?", (username,))  

    result = cur.fetchone()
    return result

#funzione che recupera il username basandosi sull'email
def retrieve_user(User):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE username = ? OR email = ?", (User,User))

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
    
#funzione che andrà a controllare solo il username
def check_email_exist(email):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE email = ?", (email,))

    result = cur.fetchone()
    if result:
        return True
    else: 
        return False