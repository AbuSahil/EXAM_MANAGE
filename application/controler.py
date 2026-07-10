from flask import Flask, flash , render_template , redirect , request,url_for
from flask_login import LoginManager , login_required , current_user, logout_user , login_user

from sqlalchemy import or_
# from app import  --> circular import error
from flask import current_app as app

from .model import *
login_manager = LoginManager()
login_manager.init_app(app)
app.app_context().push()

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

app.app_context().push()
#  ========================= App Management ====================
# @app.route("/")
# def home():

#     return render_template("home.html")
@app.route("/" , methods=['POST','GET'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        this_user = User.query.filter_by(email=email).first()
        if this_user:
            if this_user.role== 'admin':
                if this_user.password==password:
                    login_user(this_user)
                    return render_template("admin/admin_dashboard.html")
                return "<h1>Incorect Password</h1>"
            elif this_user.role == 'staff':
                if this_user.password ==password:
                    login_user(this_user)
                    return render_template("staff/staff_dashboard.html")
                return "<h1>Incorect Password</h1>"
            elif this_user.role =='student':
                if this_user.password == password:
                    login_user(this_user)
                    return render_template("student/student_dashboard.html")
                return "<h1>Incorect Password</h1>"

        return "<h1> No User Registerd with this Email</h1>"
    return render_template("home.html")
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/retrieve_password" , methods = ['POST','GET'])
def retrieve_password():
    if request.method == 'POST':
      email = request.form['email']
      password = User.query.filter_by(email=email).first()
      if password:
          return render_template("retrieve.html" , password=password.password)
      return render_template("retrieve.html" , password=" No Password found ")
    return render_template("forgot.html")
       





