from flask import Flask, render_template, flash, redirect, url_for, request, session, json, jsonify
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from dbconnect import connection
from content_management import Content
import gc
from functools import wraps

TOPIC_DICT = Content()

app = Flask(__name__)




@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html', TOPIC_DICT = TOPIC_DICT)




@app.route('/login/',methods=['GET', 'POST'])
def login_page():
    print "login page"
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":
	    print "login POST"
            data = c.execute("SELECT * FROM user WHERE email = (%s)",
                             [thwart(request.form['email'])] )
	    
            if not data:
		flash('email does not exist')
            data = c.fetchone()[2]
	    print "data fetchone"
            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['email'] = request.form['email']

                flash('You are now logged in')
                return redirect(url_for("dashboard"))

            else:
		flash('incorrect password')
                e = "Invalid credentials, try again."

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        print e
        error = "EXCEPTIONInvalid credentials, try again."
        return render_template("login.html", error = error)  
		 
    
class RegistrationForm(Form):

    email = TextField('email', [validators.Length(min=6, max=50)])
    firstname = TextField('firstname', [validators.Length(min=2, max=20)])
    lastname = TextField('lastname', [validators.Length(min=2, max=20)])
    university = TextField('university', [validators.Length(min=2, max=20)])
    department = TextField('department', [validators.Length(min=2, max=20)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirmpassword', message='Passwords must match')
    ])
    confirmpassword = PasswordField('Repeat Password')
    token = TextField('token', [validators.Length(min=2, max=100)])
     
		   

@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            
            email = form.email.data
            firstname  = form.firstname.data
            lastname  = form.lastname.data
            university  = form.university.data
            department  = form.department.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            token  = form.token.data
            c, conn = connection()

            x = c.execute("SELECT * FROM user WHERE email = (%s)",
                          [thwart(email)])

            if int(x) > 0:
                flash("That email is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO user (email, firstname, lastname, university, department, password, token) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                          (thwart(email), thwart(firstname), thwart(lastname), thwart(university), thwart(department), thwart(password), thwart(token)))
                
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['email'] = email

                return redirect(url_for("dashboard"))

        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))
    
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for("login_page"))

    return wrap

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for["dashboard"])

@app.route('/interactive/')
def interactive():
	return render_template('interactive.html')


@app.route('/background_process')
def background_process():
	try:
		lang = request.args.get('proglang', 0, type=str)
		if lang.lower() == 'jerry':
			return jsonify(result='That is my name indeed!')
		else:
			return jsonify(result='Try again.')
	except Exception as e:
		return str(e)

@app.route('/github/')
def github():
    return redirect("http://github.com/jk34")

@app.route('/linkedin/')
def linkedin():
    return redirect("http://linkedin.com/in/jerrykim12")


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
