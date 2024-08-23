import flask

app = flask.Flask(__name__)

@app.route('/<path>')
def home(path):
    return flask.render_template("index.html", path = path)

app.run()