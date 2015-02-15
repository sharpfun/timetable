from .entities import *
from wtforms import *
from flask_wtf import Form
from wtforms.validators import *
from flask import Flask, request, render_template, render_template_string, abort, flash, redirect
from pony.orm import db_session
import jinja2

app = Flask(__name__)
app.secret_key = "Vor einem etwaigen Deployment unbedingt verbessern!"
app.jinja_loader = jinja2.FileSystemLoader('./templates')


