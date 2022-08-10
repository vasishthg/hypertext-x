from flask import Flask, render_template, request, session, url_for, redirect
import mysql.connector
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.config['SECRET_KEY'] = "c073d0ed65f33a257b57c0df4d20e6865ef479e3d81ee95b124aeb60f5518484"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'toor'
app.config['MYSQL_DB'] = 'projectbeta'
db = mysql.connector.connect(host='localhost', user='root', password = 'toor', database = 'projectbeta')
mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    errmsg = ''
    if 'loggedin' in session:
        return redirect('/portal')
    if request.method == "POST" and 'admno' in request.form and 'password' in request.form:
        admno = request.form['admno']
        password = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM users WHERE admno = %s AND password = %s', (admno, password))
        account = cur.fetchone()
        if account:
            role = account['role']
            session['loggedin'] = True
            session['id'] = account['id']
            session['admno'] = account['admno']
            session['name'] = account['name']
            session['section'] = account['section']
            if role == 'admin':
                return redirect('/admin')
            return redirect("/portal")
    else:
        errmsg= 'Invalid Data'
    return render_template("login.html", errmsg = errmsg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('admno', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/portal')
def portal():
    if 'loggedin' in session:
        secret = ''
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE admno = %s", [session['admno']])
        details = cur.fetchall()
        role = details[0]['role']
        if role == 'admin':
            return redirect('/admin')
        if details[0]['section'] == "D" or details[0]['section'] == "d":
            secret = 'eez nuts'
        return render_template('portal.html', admno=session['admno'], details = details, secret = secret)
    return redirect('/login')

if "__main__" == __name__:
    app.run(debug=True)