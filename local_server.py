from flask import Flask
from flask.ext.mail import Mail

app = Flask(__name__)
app.config.from_object('config')

# Initialize email
mail = Mail()
mail.init_app(app)