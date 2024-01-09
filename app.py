from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://kngpxbrvuuxqie:59500891407391f315c217ae7af60713cb5fca7e74e4239291ae0cbd0cedebcc@ec2-54-164-138-85.compute-1.amazonaws.com:5432/d8aple15ssibb5'
db = SQLAlchemy(app)
app.app_context().push()

@app.route('/', methods = ["POST", "GET"])
def index():
    return render_template("index.html",)


if __name__ == '__main__':
    app.run(debug=True)
