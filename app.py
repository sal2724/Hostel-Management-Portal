from flask import Flask, render_template, request, redirect, session, flash, url_for
# from admission import get_data
from sqlalchemy import create_engine
from sqlalchemy.exc import DatabaseError
import re
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import sessionmaker
from models import St_Accounts
import logging
import sqlite3

app = Flask(__name__) 

# Create a custom logger
logger = logging.getLogger(__name__)
  
logging.basicConfig(filename='file.log', encoding='utf-8', level=logging.DEBUG, filemode='w', format="%(asctime)s - %(levelname)s - %(message)s")

bcrypt = Bcrypt(app)

#Setting up sql for models
SQLALCHEMY_DATABASE_URL = "mysql+mysqldb://root:1234@localhost/hostel_management"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Base = declarative_base()
Session = sessionmaker(bind=engine)
dbsession = Session()


app.secret_key = 'your secret key'
users = {} 

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# route to display home page of the web application

@app.route("/", methods = ['GET', 'POST'])
def front():
    logger.info("User is logged in")

    is_logged_in = session.get('loggedin')
    if (is_logged_in is None or is_logged_in is False):
        return redirect("/login")
    return render_template("index.html")

@app.route("/committee", methods = ['GET', 'POST'] )
def comm():
    return render_template("committee.html")

@app.route("/warden", methods = ['GET', 'POST'] )
def warden():
    return render_template("warden_info.html")

@app.route("/caretaker_info", methods = ['GET', 'POST'] )
def caretaker():
    return render_template("caretaker_info.html")

@app.route("/anti_ragging", methods = ['GET', 'POST'] )
def ragging():
    return render_template("anti_ragging.html")

@app.route('/login', methods =['GET', 'POST'])
def login():
    logger.info("Started Login")
    if (request.method == "GET"):
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return render_template("login.html", msg = "Incorrect username / password !")
        
        # Query for f'SELECT * FROM accounts WHERE username = "{username}"')).fetchone()
        account = dbsession.query(St_Accounts).filter_by(username = username).one_or_none()
        if not account:
            flash(f'Incorrect username / password !', 'error')
            return render_template("login.html")
        correct_password = bcrypt.check_password_hash(account.password, password  )
        if not correct_password:
            logger.error("Incorrect password")
            flash(f'Incorrect username / password !', 'error')
            return render_template("login.html")
        else:
            session['loggedin'] = True
            session['id'] = account.id
            session['username'] = account.username
            flash(f'Welcome, {username}! You have successfully logged in.')
            return redirect("/")

@app.route('/logout', methods =['GET', 'POST'])
def logout():
        logger.info("User is logged out")
        session.clear()
        return redirect("/login")

    

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'room_no' in request.form and 'roll_no' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        room_no = request.form['room_no']
        roll_no = request.form['roll_no']
        hashed_password = bcrypt.generate_password_hash(password.encode())
        users[username] = {'password': hashed_password}
        
        desired_username = {username}
        # Query for SELECT * FROM accounts WHERE username = "{username}"
        account = dbsession.query(St_Accounts).filter(St_Accounts.username == desired_username).all() 

        if account:
            msg = 'Account already exists !'
            logger.warning("Account already exists !")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
            logger.error("Invalid email address !")
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
            logger.warning("Username must contain only characters and numbers !")
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
            logger.warning("Please fill out the form !")
        else:
            #Query for INSERT INTO accounts VALUES (NULL, "{username}","{hashed_password.decode()}", "{email}"
            new_account = St_Accounts(username=username, password=hashed_password.decode(), email=email, room_no=room_no, roll_no=roll_no)
            # Add the new Account object to the session
            dbsession.add(new_account)

            # Commit the transaction to save the new record to the database
            dbsession.commit()

            msg = "You have successfully  registered"
            logger.info("New user has registered")
            flash(f'Welcome, {username}! You have successfully  registered')
            return redirect("/login")

    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template("register.html", msg = msg)

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'loggedin' in session:
        if request.method == 'POST':
            user_id = session['id']
            date = request.form['date']

            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('''INSERT INTO attendance (student_id, date) VALUES (?, ?)''', (user_id, date))
            conn.commit()
            conn.close()

            flash('Attendance recorded successfully!', 'success')
            return redirect(url_for('front'))
        return render_template('attendance.html')
    else:
        return redirect('/login')

@app.route('/mess_entry', methods=['GET', 'POST'])
def mess_entry():
    # Fetch student data from your database or any other source
    students = [
        {"id": 1, "name": "Saloni Jain"},
        {"id": 2, "name": "Kirti Panchal"},
        {"id": 3, "name": "Harsh Gujjar"}
    ]
    
    meals = {student['id']: 0 for student in students}  # Initialize meals count as 0 for all students
    
    if request.method == 'POST':
        for student in students:
            student_id = str(student['id'])
            meals[student_id] = int(request.form.get(student_id, 0))
        # Logic to update the meals count in your database can be added here
        
        flash('Meals recorded successfully!', 'success')
        # return redirect(url_for('index'))  # Redirect to the main page or another suitable page

    return render_template('mess_entry.html', students=students, meals=meals)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Here you can perform actions with the submitted data, such as sending emails, storing in the database, etc.

        # For demonstration, let's print the received data
        print(f"Name: {name}, Email: {email}, Subject: {subject}, Message: {message}")

        # Redirect to a thank you page or any other suitable page
        return render_template('thank_you.html', name=name)  # Replace 'thank_you.html' with your desired thank you page

    return render_template('contact_us.html')  # Render the contact form


def get_app():
    return app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81) 
    
