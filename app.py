from flask import Flask , redirect , render_template , request , flash
from flask_login import LoginManager , login_required , login_user , logout_user
from application.database import db
from sqlalchemy import text

import psycopg2
# app=Flask(__name__) 
app = None

def create_app():
    app = Flask(__name__)
    app.debug =True
    
    app.config['SECRET_KEY'] = 'qwertyuioplkjhgfdsazxcvbnm'
    app.config["SQLALCHEMY_DATABASE_URI"] = \
    "postgresql://postgres:StrongPassword123@localhost:5432/school_management"

    db.init_app(app)
    
    app.app_context().push()
    return app
app = create_app()

from application.controler import * # controler file resides in the application folder
from application.model import * 




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role ='admin').first()
        if admin is None :
            admin = User(name = 'Admin' , email = 'admin@gmail.com' ,password =generate_password_hash("123") , role='admin')
            db.session.add(admin)
            db.session.commit()
    app.run(host="0.0.0.0", port=5000)

