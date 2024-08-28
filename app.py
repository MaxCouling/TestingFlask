from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Sample data (you'd typically use a database)
user_data = {
    "name": "Sam",
    "balance": 8.80,
    "total_earned": 27.80,
    "total_withdrawn": 19.00
}

@app.route('/')
def home():
    return render_template('index.html', user=user_data)

@app.route('/profile')
def profile():
    return render_template('index.html', user=user_data)

@app.route('/claim_rewards')
def claim_rewards():
    return render_template('index.html', user=user_data)

@app.route('/survey_history')
def survey_history():
    return render_template('index.html', user=user_data)

@app.route('/survey/<int:question_number>')
def survey(question_number):
    questions = [
        {"id": 1, "text": "How many hours sleep did you get last night?", "options": ["1-4 Hours", "4-8 Hours", "8-12 Hours"]},
        {"id": 2, "text": "What mattress do you sleep on?", "options": ["Single", "Double", "Queen", "King"]},
        {"id": 3, "text": "What time do you wake up?", "options": ["4-6am", "6-8am", "8-10am", "10+ am"]}
    ]
    if 1 <= question_number <= len(questions):
        return render_template('survey_question.html', question=questions[question_number-1], user=user_data)
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)