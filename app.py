from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    surveys = db.relationship('Survey', backref='author', lazy=True)

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    questions = db.relationship('Question', backref='survey', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer = db.Column(db.String(200), nullable=False)

    user = db.relationship('User', backref='responses')
    question = db.relationship('Question', backref='responses')

# Routes
@app.route('/')
def index():
    surveys = Survey.query.all()
    return render_template('index.html', surveys=surveys)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            process_csv(filename)
            flash('Survey uploaded and processed!')
            return redirect(url_for('index'))
    
    return render_template('upload.html')

def process_csv(filepath):
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)
        survey_title, survey_description = header[0], header[1]
        
        survey = Survey(title=survey_title, description=survey_description, author=current_user)
        db.session.add(survey)
        db.session.commit()
        
        for row in reader:
            question_text = row[0]
            question = Question(text=question_text, survey_id=survey.id)
            db.session.add(question)
        
        db.session.commit()

@app.route('/survey/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    if request.method == 'POST':
        # Process user responses
        for question in survey.questions:
            answer = request.form.get(f'question_{question.id}')
            if answer:
                response = Response(user_id=current_user.id, question_id=question.id, answer=answer)
                db.session.add(response)
        
        db.session.commit()
        flash('Survey completed!', 'success')
        return redirect(url_for('index'))

    return render_template('survey.html', survey=survey)




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/survey/new', methods=['GET', 'POST'])
@login_required
def new_survey():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        survey = Survey(title=title, description=description, author=current_user)
        db.session.add(survey)
        db.session.commit()
        flash('Survey created!', 'success')
        return redirect(url_for('index'))
    return render_template('survey.html')

if __name__ == '__main__':
    app.run(debug=True)
