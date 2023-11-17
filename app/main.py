from flask import Flask
from flask_login import LoginManager

from app.config import config
from app.db import db_session
from app.db.models.user import User
from blueprints.my_blueprint import my_blueprint

app = Flask(__name__)
app.register_blueprint(my_blueprint)
app.config['SECRET_KEY'] = config.secret_key_flask.get_secret_value()
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
