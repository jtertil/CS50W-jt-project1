import os

from flask import Flask
from logging import FileHandler, WARNING
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DEBUG'] = True

# Error Log:
if not app.debug:
    f_handler = FileHandler('error_log.txt')
    f_handler.setLevel(WARNING)
    app.logger.addHandler(f_handler)

# Change in production
app.secret_key = 'secret'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

import views  # noqa: F401
