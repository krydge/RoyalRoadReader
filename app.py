from flask import Flask


app = Flask(__name__)

@app.route("/")
def getCompletedBooksList():
    return "<p>Hello, World!</p>"