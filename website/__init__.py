from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LOGIN_MESSAGE, LoginManager
from werkzeug.security import generate_password_hash
db = SQLAlchemy()
DB_NAME = "database.db"
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs' #Secret key to encode data
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    db.init_app(app)
    create_database(app)
    @app.errorhandler(404)
    '''This handles the error of a page not being found, or Error 404'''
    def page_not_found(error):
        return redirect(url_for("views.nopage"))
    
    from .views import views
    from .auth import auth
    from .models import User
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    login_manager = LoginManager() #This helps users login and logout
    login_manager.login_view = 'auth.login' #Gives the location of the function for the login page
    login_manager.init_app(app)
    @login_manager.user_loader #This will load users to log them in
    def load_user(id):
        return User.query.get(int(id))
    return app


def create_database(app):
    with app.app_context():
        from .models import User
        if not path.exists('website/' + DB_NAME): #Checks if a database exists yet
            db.create_all(app=app)
            print('Created Database!')
            teacher = User(email="teacher@gmail.com",password=generate_password_hash("Bobo@123",method="sha256"),name="Teacher",admin=False,teacher=True,verified=True)
            admin = User(email="googolplex238371@gmail.com", password=generate_password_hash(
                "Bobo@123", method='sha256'),name="Divyansh Ghosh",admin=True,verified=True) #These are test users as there is no signup page
            db.session.add(admin)
            db.session.add(teacher)
            db.session.commit()
