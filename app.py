from flask import Flask, render_template, request, session, url_for, redirect
import mysql.connector
from flask_mysqldb import MySQL
import MySQLdb.cursors
import datetime

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
        admno = request.form.get('admno')
        password = request.form.get('password')
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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM notices ORDER BY date DESC")
        notices = cursor.fetchall()
        cur.execute("SELECT * FROM homework")
        homework = cur.fetchall()
        return render_template('portal.html', admno=session['admno'], details = details, secret = secret, notices = notices, homework = homework)
    return redirect('/login')

@app.route('/admin', methods=["GET", "POST"])
def admin():
    msg = ''
    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE admno = %s", [session['admno']])
        details = cur.fetchall()
        role = details[0]['role']
        if role == 'admin':
            if request.method == "POST" and 'title' and 'content' in request.form:
                title = request.form.get('title')
                msg = 'Published Notice'
                content = request.form.get('content')
                cur.execute("INSERT INTO notices VALUES(NULL, %s, %s, %s)", (title, content, datetime.date.today()))
                mysql.connection.commit()
            if request.method == "POST" and 'hw-title' in request.form and "hw-sub" in request.form:
                msg = 'Published Homework'
                hw = request.form.get('hw-title')
                subject = request.form.get('hw-sub')
                cur.execute("INSERT into homework VALUES(NULL, %s, %s, %s)", (hw, subject, datetime.date.today()))
                mysql.connection.commit()
            cur.execute("SELECT * FROM users")
            udata = cur.fetchall()
            if request.method == "POST" and "user-admno" in request.form and "user-pass" in request.form and "user-name" in request.form and "user-class" in request.form and "user-section" in request.form:
                admno = request.form.get("user-admno")
                password = request.form.get("user-pass")
                name = request.form.get("user-name")
                msg = 'Created New Account'
                clas = request.form.get("user-class")
                section = request.form.get("user-section")
                cur.execute("INSERT INTO users VALUES(NULL, %s, %s, 'user', %s, %s, %s)", (admno, password, name, clas, section))
                mysql.connection.commit()
                return redirect("/admin")
            return render_template("admin.html", admno=session['admno'], details = details, data = udata, msg = msg)
        else:
            return redirect("/")
    return redirect('/login')

@app.route("/notices/<int:id>")
def notice(id):
    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM notices WHERE id = %s", [id])
        content = cur.fetchone()
        return render_template("notice.html", admno=session['admno'], content = content, id = id)
    return redirect('/login')

@app.route("/manage/<int:admno>", methods=["GET", "POST"])
def manage(admno):
    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE admno = %s", [session['admno']])
        details = cur.fetchall()
        role = details[0]['role']
        if role == 'admin':
            cur.execute("SELECT * FROM users WHERE admno = %s", [admno])
            content = cur.fetchone()
            if request.method == "POST" and 'update-pass' in request.form and "update-role" in request.form and "update-name" in request.form and "update-class" in request.form and "update-section" in request.form:
                upassword = request.form.get("update-pass")
                urole = request.form.get("update-role")
                uname = request.form.get("update-name")
                uclass = request.form.get("update-class")
                usection = request.form.get("update-section")
                cur.execute("UPDATE users SET password = %s, role = %s, name = %s, class = %s, section = %s WHERE id = %s", (upassword, urole, uname, uclass, usection, content['id']))
                mysql.connection.commit()
                return redirect("/manage/<int:admno>")
            return render_template("manage.html", admno = session['admno'], content = content)
        return redirect('/portal')
    return redirect('/login')

if "__main__" == __name__:
    app.run(debug=True)