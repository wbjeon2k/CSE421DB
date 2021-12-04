import json

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, url_for
from jinja2 import Template
from flask import session, request
from psycopg2 import sql
from psycopg2.sql import SQL
from database import Connection
from models import *
from datetime import datetime, timezone
from database import Connection
from models import *
import hashlib

# logout blueprint
bp = Blueprint('logout', __name__, url_prefix='/logout')

@bp.route('/', methods=['GET'])
def logout_main():
    if 'user' in session:
	    del session['user']
        
    return redirect(url_for('main'))