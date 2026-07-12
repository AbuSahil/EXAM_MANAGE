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
                    return redirect("/admin")
                return "<h1>Incorect Password</h1>"
            elif this_user.role == 'staff':
                if this_user.password ==password:
                    login_user(this_user)
                    return redirect("/staff")
                return "<h1>Incorect Password</h1>"
            elif this_user.role =='student':
                if this_user.password == password:
                    login_user(this_user)
                    return redirect("/student")
                return "<h1>Incorect Password</h1>"

        return "<h1> No User Registerd with this Email</h1>"
    return render_template("home.html")
@app.route("/admin")
@login_required
def admin():
    return render_template("admin/admin_dashboard.html")
@app.route("/staff")
@login_required
def staff():

    return render_template("staff/staff_dashboard.html" , staff=current_user)
@app.route("/student")
@login_required
def student():
    return render_template("student/student_dashboard.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/retrieve_password" , methods = ['POST','GET'])
def retrieve_password():
    if request.method == 'POST':
      email = request.form['email']
      password = User.query.filter_by(email=email).first()
      if password:
          return render_template("retrieve.html" , password=password.password)
      return render_template("retrieve.html" , password=" No Password found ")
    return render_template("forgot.html")


@app.route("/add_staff", methods=["GET", "POST"])
@login_required
def add_staff():
    subjects = Subject.query.all()

    if request.method == "POST":

        name = request.form.get("name")
        employee_id = request.form.get("employee_id")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        designation = request.form.get("designation")
        subject_id = request.form.get("subject")

        # Check email
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already exists.", "danger")
            return redirect(url_for("add_staff"))

        # Check employee id
        existing_staff = Staff.query.filter_by(employee_id=employee_id).first()

        if existing_staff:
            flash("Employee ID already exists.", "danger")
            return redirect(url_for("add_staff"))

        # Create User
        user = User( role="staff", name=name, email=email, password=password)

            # Create Staff Profile
        staff = Staff( employee_id=employee_id, designation=designation, subject_id=subject_id , phone=phone )

            # Link Staff with User
        staff.user = user

        db.session.add(staff)
        db.session.commit()

        flash("Staff added successfully.", "success")
        return redirect(url_for("staff_list"))

        
    
    return render_template("admin/add_staff.html", subjects=subjects)
@app.route("/staff_list")
@login_required
def staff_list():
    staffs=Staff.query.all()

    return render_template("admin/staff_list.html" , staffs=staffs)
@app.route("/activate_staff/<int:staff_id>", methods=["POST"])
def activate_staff(staff_id):
    

    staff = Staff.query.get(staff_id)
    if staff:
        staff.user.is_active = True
        db.session.commit()
        flash("Staff activated successfully.", "success")

    return redirect(url_for("staff_list"))
@app.route("/deactivate_staff/<int:staff_id>", methods=["POST"])
def deactivate_staff(staff_id):
    

    staff = Staff.query.get(staff_id)
    if staff:
        staff.user.is_active = False
        db.session.commit()
        flash("Staff deactivated successfully.", "warning")

    return redirect(url_for("staff_list"))

@app.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():
    classes=SchoolClass.query.all()

    if request.method == "POST":

        name = request.form.get("name")
        roll_no = request.form.get("roll_no")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        class_id = request.form.get("class_name")
        

        # Check email
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already exists.", "danger")
            return redirect(url_for("add_student"))

        # Check employee id
        existing_student = Student.query.filter_by(roll_no=roll_no).first()

        if existing_student:
            flash("Roll No already exists.", "danger")
            return redirect(url_for("add_student"))

        # Create User
        user = User( role="student", name=name, email=email, password=password)

            # Create Student Profile
        student = Student( roll_no=roll_no, class_id=class_id, phone=phone )

            # Link Staff with User
        student.user = user

        db.session.add(student)
        db.session.commit()

        flash("Student added successfully.", "success")
        return redirect(url_for("student_list"))

        

    return render_template("admin/add_student.html", classes=classes)

@app.route("/student_list")
@login_required
def student_list():
    students=Student.query.all()

    return render_template("admin/student_list.html" , students=students)
@app.route("/activate_student/<int:student_id>", methods=["POST"])
def activate_student(student_id):
    

    student = Student.query.get(student_id)
    if student:
        student.user.is_active = True
        db.session.commit()
        flash("Student activated successfully.", "success")

    return redirect(url_for("student_list"))
@app.route("/deactivate_student/<int:student_id>", methods=["POST"])
def deactivate_student(student_id):
    

    student = Student.query.get(student_id)
    if student:
        student.user.is_active = False
        db.session.commit()
        flash("student deactivated successfully.", "warning")

    return redirect(url_for("student_list"))

@app.route("/create_exam", methods=["GET", "POST"])
@login_required
def create_exam():

    subjects = Subject.query.order_by(Subject.name).all()
    staffs = Staff.query.order_by(Staff.id).all()

    if request.method == "POST":

        exam = Exam(
            name=request.form.get("name"),
            subject_id=request.form.get("subject_id"),
            exam_date=datetime.strptime(
                request.form.get("exam_date"),
                "%Y-%m-%d"
            ).date(),
            total_marks=request.form.get("total_marks"),
            pass_marks=request.form.get("pass_marks"),
            staff_id=request.form.get("staff_id")
        )

        db.session.add(exam)
        db.session.commit()

        flash("Exam created successfully.", "success")

        return redirect(url_for("create_exam"))

    return render_template(
        "admin/create_exam.html",
        subjects=subjects,
        staffs=staffs
    )

@app.route("/add_subject", methods=["GET", "POST"])
def add_subject():
    classes = SchoolClass.query.all()
    subjects = Subject.query.order_by(Subject.class_id).all()


    if request.method == "POST":

        name = request.form.get("name").strip()
        class_id = request.form.get("class_name")

        subject = Subject.query.filter_by(
            name=name,
            class_id=class_id
        ).first()

        if subject:
            flash("Subject already exists.", "warning")
            return redirect(url_for("add_subject"))

        subject = Subject(
            name=name,
            class_id=class_id
        )

        db.session.add(subject)
        db.session.commit()

        flash("Subject added successfully.", "success")

        return redirect(url_for("add_subject"))

    return render_template("admin/add_subject.html" , subjects=subjects ,classes= classes)
@app.route("/delete_subject/<int:subject_id>", methods=["POST"])
@login_required
def delete_subject(subject_id):

    subject = Subject.query.get_or_404(subject_id)

    db.session.delete(subject)
    db.session.commit()

    flash("Subject deleted successfully.", "success")

    return redirect(url_for("add_subject"))

@app.route("/manage_exams")
@login_required
def manage_exams():
    exams = Exam.query.all()
    return render_template("staff/manage_exams.html", exams=exams , staff=current_user)

@app.route("/add_marks/<int:exam_id>")
@login_required
def add_marks(exam_id):
    exam = Exam.query.get_or_404(exam_id)

    students = Student.query.filter_by(
    class_id=exam.subject.class_id
).order_by(Student.roll_no).all()

    return render_template("staff/add_marks.html" , exam = exam, students=students , staff=current_user)