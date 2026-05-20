from flask import Flask, render_template, request
import PyPDF2
from model import recommend_jobs

app = Flask(__name__)

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
    return render_template('profile.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)





