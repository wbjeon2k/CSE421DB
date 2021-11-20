from flask import Flask, render_template
from flask import Blueprint, redirect, url_for
#from models import db, testModel
from models import TestModel, db
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

app = Flask(__name__)
#db = SQLAlchemy()

POSTGRES = {
    'user': 'postgres',
    'pw': 'password',
    'db': 'my_database',
    'host': 'localhost',
    'port': '5432',
}

def default_config():
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES)
    app.app_context().push()
    db.init_app(app)

# main homepage blueprint
bp = Blueprint('main', __name__, url_prefix='/main')

def dummy_gen():
    for i in range(300):
        obj = TestModel(id= i, msg = "%d th object generated"%i)
        db.session.add(obj)
    db.session.commit()

@app.route("/")
def main():
    return 'This is main page'

@app.route("/test/generate")
def testgen():
    dummy_gen()
    return 'Generated 300 dummy contents.'

@app.route("/test")
def test_main():
    test_list = TestModel.query.order_by(TestModel.id.desc())
    print(test_list)
    return render_template('testlist.html', test_list = test_list)

@app.route("/jinja2/base")
def page_jinja2_base():
    return render_template("base.html")

if __name__ == '__main__':
    default_config()
    app.run()
