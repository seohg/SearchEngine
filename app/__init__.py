from flask import Flask, render_template, request

app = Flask(__name__)
from app.main.index import main as main
from app.test.test import test as test

app.register_blueprint(test)
app.register_blueprint(main)

@app.route('/')
def first():
    return render_template('first.html')

@app.route('/website')
def website():
    return render_template('website.html')

@app.route('/search',methods=['POST','GET'])
def search():
    title = request.form
    return render_template("search.html", value = title)

@app.route('/info',methods=['POST','GET'])
def info():
    ti = request.form
    return render_template("info.html", val = ti)