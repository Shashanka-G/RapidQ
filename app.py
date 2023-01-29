from flask import Flask, render_template, request
from haystack.utils import launch_es, clean_wiki_text, convert_files_to_docs, fetch_archive_from_http
import os
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import BM25Retriever, FARMReader, TransformersReader
from haystack.pipelines import ExtractiveQAPipeline
from pprint import pprint
from haystack.utils import print_answers
from werkzeug.utils import secure_filename
from transformers import pipeline
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import torch

UPLOAD_FOLDER = './data'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)


def generate_answer(plain_text, ques_text):
    nlp = pipeline('question-answering', model='deepset/roberta-base-squad2',
                   tokenizer='deepset/roberta-base-squad2')
    question_set = {
        'question': ques_text,
        'context': plain_text
    }
    results = nlp(question_set)
    return results['answer']


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute(
            "INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
            (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s",
                             [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('login'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):

    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/TryRapid')
@is_logged_in
def TryRapid():
    return render_template('nlp.html')


@app.route('/TryRapid', methods=["POST"])
def insurance():
    file = request.files['txt_file']
    query = request.form.get('input')

    if file.filename != '':
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        import logging
        torch.cuda.is_available()
        logging.basicConfig(
            format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
        logging.getLogger("haystack").setLevel(logging.INFO)

        launch_es()

        host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
        document_store = ElasticsearchDocumentStore(
            host=host, username="", password="", index="document")
        doc_dir = "data"

        docs = convert_files_to_docs(
            dir_path=doc_dir, clean_func=clean_wiki_text, split_paragraphs=True)

        # print(docs[:3])

        document_store.write_documents(docs)

        retriever = BM25Retriever(document_store=document_store)

        reader = FARMReader(
            model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

        # ans = generate_answer(str(document_store), query)
        pipe = ExtractiveQAPipeline(reader, retriever)
        prediction = pipe.run(
            query=query, params={"Retriever": {
                "top_k": 2}, "Reader": {"top_k": 1}}
        )

        data = prediction["answers"]
        data1 = data[0].answer

        return render_template('output.html', dataoutput=data1, outputquery=query)

        # print_answers(prediction, details="minimum")
    else:
        return render_template('nlp.html', PageTitle="Landing page")


if __name__ == "__main__":
    app.secret_key = 'secrets123'
    app.run(debug=True)
