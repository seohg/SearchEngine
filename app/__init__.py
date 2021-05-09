from flask import Flask
 
app = Flask(__name__)
from app.main.index import main as main
from app.test.test import test as test

app.register_blueprint(test)
app.register_blueprint(main)