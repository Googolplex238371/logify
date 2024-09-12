from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LOGIN_MESSAGE, LoginManager
from werkzeug.security import generate_password_hash
db = SQLAlchemy()
DB_NAME = "database.db"
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    db.init_app(app)
    create_database(app)
    @app.errorhandler(404)
    def page_not_found(error):
        return redirect(url_for("views.nopage"))
    
    from .views import views
    from .auth import auth
    from .models import User
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app


def create_database(app):
    with app.app_context():
        from .models import User
        if not path.exists('website/' + DB_NAME):
            db.create_all(app=app)
            print('Created Database!')
            teacher = User(email="teacher@gmail.com",password=generate_password_hash("Bobo@123",method="sha256"),name="Teacher",admin=False,teacher=True,verified=True)
            admin = User(email="googolplex238371@gmail.com", password=generate_password_hash(
                "Bobo@123", method='sha256'),name="Divyansh Ghosh",admin=True,verified=True)
            db.session.add(admin)
            db.session.add(teacher)
            db.session.commit()
