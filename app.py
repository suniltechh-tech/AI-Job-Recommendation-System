from flask import Flask
from database import mysql
import config
from MySQLdb.cursors import DictCursor
import os
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import PyPDF2
from model import recommend_jobs

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.secret_key = "job_ai_secret_key_2026"

app.config["MYSQL_HOST"] = config.MYSQL_HOST
app.config["MYSQL_USER"] = config.MYSQL_USER
app.config["MYSQL_PASSWORD"] = config.MYSQL_PASSWORD
app.config["MYSQL_DB"] = config.MYSQL_DB

print("MYSQL_USER:", app.config["MYSQL_USER"])
print("MYSQL_HOST:", app.config["MYSQL_HOST"])
print("MYSQL_DB:", app.config["MYSQL_DB"])

mysql.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':

        skills = request.form['skills']

        results = recommend_jobs(skills)

        return render_template(
            'result.html',
            jobs=results
        )

    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def recommend():

    skills = request.form['skills']

    results = recommend_jobs(skills)

    return render_template('result.html', jobs=results)


@app.route('/upload', methods=['POST'])
def upload():

    file = request.files['resume']

    if file:

        pdf_reader = PyPDF2.PdfReader(file)

        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text()

        results = recommend_jobs(text)

        return render_template('result.html', jobs=results)


@app.route('/jobs')
def jobs():
    return render_template('jobs.html')

@app.route('/profile')
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    print("Profile loaded for user_id:", session["user_id"])


    cur = mysql.connection.cursor(DictCursor)

    cur.execute(
        "SELECT * FROM users WHERE user_id=%s",
        (session["user_id"],)
    )

    user = cur.fetchone()

    cur.close()
    print("Profile loaded for user_id:", session["user_id"])
    return render_template(
        "profile.html",
        user=user
    )
@app.route('/update_profile', methods=['POST'])
def update_profile():

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    print("Logged in user_id:", session["user_id"])

    # Get form data
    full_name = request.form["full_name"]
    phone = request.form["phone"]
    skills = request.form["skills"]
    education = request.form["education"]
    about = request.form["about"]

    # Get uploaded profile image
    profile_image = request.files["profile_image"]

    print(profile_image)
    print(profile_image.filename)

    filename = None

    # Save image if selected
    if profile_image and profile_image.filename != "":
        filename = secure_filename(profile_image.filename)

        profile_image.save(
            os.path.join(app.config["UPLOAD_FOLDER"], filename)
        )

    # Connect to database
    cur = mysql.connection.cursor()

    # Update profile with image
    if filename:

        cur.execute("""
            UPDATE users
            SET
                full_name = %s,
                phone = %s,
                skills = %s,
                education = %s,
                about = %s,
                profile_image = %s
            WHERE user_id = %s
        """, (
            full_name,
            phone,
            skills,
            education,
            about,
            filename,
            session["user_id"]
        ))

    # Update profile without changing image
    else:

        cur.execute("""
            UPDATE users
            SET
                full_name = %s,
                phone = %s,
                skills = %s,
                education = %s,
                about = %s
            WHERE user_id = %s
        """, (
            full_name,
            phone,
            skills,
            education,
            about,
            session["user_id"]
        ))

    # Save changes
    mysql.connection.commit()

    print("Filename saved:", filename)
    print("Rows updated:", cur.rowcount)

    cur.close()

    flash("Profile updated successfully!")

    return redirect(url_for("profile"))


@app.route('/dashboard')
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

# ---------- Register Route ----------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        password_hash = generate_password_hash(password)

        try:
           cur = mysql.connection.cursor()
           print("✅ Flask MySQL Connected")
        except Exception as e:
           print("❌ Flask Connection Error:", e)
           raise

        # Check if email already exists
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
         flash("Email already registered!")
         cur.close()
         return redirect(url_for('register'))

       # Save new user
        cur.execute("""
        INSERT INTO users(full_name, email, password_hash, phone)
        VALUES (%s, %s, %s, %s)
        """, (full_name, email, password_hash, phone))
        mysql.connection.commit()

        cur.close()

        flash("Registration Successful!")

        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cur.fetchone()

        cur.close()

        if user:

            if check_password_hash(user[3], password):

                session["user_id"] = user[0]
                session["full_name"] = user[1]

                flash("Login Successful!")

                return redirect(url_for("home"))

        flash("Invalid Email or Password")

    return render_template("login.html")
@app.route('/logout')
def logout():

    session.clear()

    flash("Logged out successfully!")

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)





