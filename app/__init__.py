from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = "KJGHJG^&*%&*^T&*(IGFG%ERFTGHCFHGFasdasIU"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/flightdb?charset=utf8mb4" % quote('admin123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 4

db = SQLAlchemy(app)
login = LoginManager(app)

cloudinary.config(
    cloud_name="dd1frsvzk",
    api_key="172266497937733",
    api_secret="W_FvA2NSah3Jlv8cxhubvnw2mVM",  # Click 'View API Keys' above to copy your API secret
    secure=True
)
