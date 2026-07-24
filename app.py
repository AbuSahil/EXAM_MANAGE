from flask import Flask , redirect , render_template , request , flash
from flask_login import LoginManager , login_required , login_user , logout_user
from application.database import db
# from application.master_database import init_master_db
# from application.school_model import School
from sqlalchemy import text
from datetime import timedelta

import psycopg2
# app=Flask(__name__) 
app = None

def create_app():
    app = Flask(__name__)
    app.debug =False
    
    app.config['SECRET_KEY'] = 'qwertyuioplkjhgfdsazxcvbnm'
    

    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://schooladmin:BJV2026@localhost:5432/school_management"
    # app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Alpana2030%40%23@localhost:5432/BJV"
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3" 
    
    db.init_app(app)
    # init_master_db(app)
    
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
            admin = User(name = 'Abu Sahil' , email = 'superuser@gmail.com' ,password =generate_password_hash("Alpana2030@#") , role='admin')
            db.session.add(admin)
            db.session.commit()
    app.run(host="0.0.0.0", port=5000)

