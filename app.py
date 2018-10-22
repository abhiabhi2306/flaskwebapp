from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import datetime

app = Flask(__name__,static_url_path='/static')

#mysql
mysql = MySQL()
mysql.init_app(app)
# Config MySQL
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'flask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'



TEMPLATES_AUTO_RELOAD=True

@app.route("/")
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

    

        conn = mysql.connect()
        cursor = conn.cursor()

        result = cursor.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cursor.fetchone()
            password = data[2]

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                return render_template('wrong_credentials.html')
            cursor.close()
        else:
            return render_template('wrong_credentials.html')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session['logged_in'] != True:
       return render_template('index.html')
    else:
       conn = mysql.connect()
       cursor = conn.cursor()

       result = cursor.execute("SELECT * FROM threads")
       threads = cursor.fetchall()
       if result > 0:
          return render_template('dashboard.html',threads=threads)
       else:
          return render_template('dashboardempty.html')
    # Close connection
    #cur.close()


class ThreadForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/create_thread', methods=['GET', 'POST'])
def add_thread():
    if session['logged_in'] == True:
        form = ThreadForm(request.form)
        if request.method == 'POST' and form.validate():
           title = form.title.data
           body = form.body.data

           conn = mysql.connect()
           cursor = conn.cursor()

           # Execute
           cursor.execute("INSERT INTO threads(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

            # Commit to DB
           conn.commit()
           #Close connection
           conn.close()

           return render_template('thread_success.html')

        return render_template('create_thread.html', form=form)
    else:
        return render_template('login.html')



@app.route('/edit_thread/<string:id>', methods=['GET', 'POST'])
def edit_thread(id):
    if session['logged_in'] != True:
       return render_template('index.html')
    else:
        # Create cursor
        conn = mysql.connect()
        cursor = conn.cursor()
        # Get article by id
        result = cursor.execute("SELECT * FROM threads WHERE id = %s", [id])

        thread = cursor.fetchone()
        cursor.close()
         # Get form
        form = ThreadForm(request.form)

        # Populate article form fields
        form.title.data = thread[1]
        form.body.data = thread[2]

        if request.method == 'POST' and form.validate():
            title = request.form['title']
            body = request.form['body']

            # Create Cursor
            conn = mysql.connect()
            cursor = conn.cursor()
            app.logger.info(title)
            # Execute
            cursor.execute ("UPDATE threads SET title=%s, body=%s WHERE id=%s",(title, body, id))
            # Commit to DB
            conn.commit()

            #Close connection
            cursor.close()

            return render_template('threadupdated.html')

        return render_template('edit_thread.html', form=form)

@app.route('/delete_thread/<string:id>', methods=['POST'])
def delete_thread(id):
    if session['logged_in'] != True:
       return render_template('index.html')
    else:
        # Create cursor
        conn = mysql.connect()
        cursor = conn.cursor()
       # Execute
        cursor.execute("DELETE FROM threads WHERE id = %s", [id])
        conn.commit()

        #Close connection
        cursor.close()
    
        return render_template('threaddeleted.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

def current_time():
    return {'now': datetime.utcnow()}

@app.route('/threads')
def threads():
    conn = mysql.connect()
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM threads")

    threads = cursor.fetchall()

    if result > 0:
        return render_template('threads.html', threads=threads)
    else:
        return render_template('dashboardempty.html')
    # Close connection
    cursor.close()


@app.route('/thread/<string:id>/')
def thread(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM threads WHERE id = %s", [id])

    threads = cursor.fetchone()

    return render_template('thread.html', threads=threads)





class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))


        # Create cursor
        conn = mysql.connect()
        cursor = conn.cursor()

        # Execute query
        cursor.execute("INSERT INTO users(username, email, password) VALUES(%s, %s, %s)", (username, email, password))

        #commit

        conn.commit()

        flash('You are now registered and can log in', 'success')

        return redirect('/login')
    return render_template('signup.html', form=form)

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.run(Debug=True)



