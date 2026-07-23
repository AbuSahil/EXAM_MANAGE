from flask import Flask, flash , render_template , redirect , request,url_for
from flask_login import LoginManager , login_required , current_user, logout_user , login_user
import pandas as pd
from werkzeug.security import generate_password_hash ,check_password_hash

from sqlalchemy import or_
from sqlalchemy import cast, Integer
# from app import  --> circular import error
from flask import current_app as app

from .model import *
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#  ========================= App Management ====================
@app.errorhandler(Exception) # golble exception handler
def handle_exception(e):
    db.session.rollback()
    app.logger.exception(e)
    return render_template("500.html"), 500
@app.route("/", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]   # Plain password

            this_user = User.query.filter_by(email=email).first()

            if not this_user:
                flash("Your Email is not registered" , 'danger')
                return redirect(url_for('login'))

            if check_password_hash(this_user.password, password):

                login_user(this_user, remember=True)

                if this_user.role == "admin":
                    return redirect("/admin")

                elif this_user.role == "staff":
                    return redirect("/staff")

                elif this_user.role == "student":
                    return redirect("/student")
            flash("INCORRECT PASSWORD" , 'danger')
            return redirect(url_for('login'))

        return render_template("home.html")
    except Exception as e:
        db.session.rollback()
        print("ERROR:", e)
        app.logger.exception(e)
        flash("Something went wrong.", "danger")
        return render_template("login.html")

@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        flash("Only Admin can access this page.", "danger")
        return redirect(url_for("login"))


    total_students = Student.query.count()
    total_staff = Staff.query.count()
    total_classes = SchoolClass.query.count()
    total_subjects = Subject.query.count()
    total_exams = Exam.query.count()

    return render_template(
        "admin/admin_dashboard.html",
        total_students=total_students,
        total_staff=total_staff,
        total_classes=total_classes,
        total_subjects=total_subjects,
        total_exams=total_exams
    )
@app.route("/staff")
@login_required
def staff():
    if current_user.role != "staff":
        flash("Only Staff can access this page.", "danger")
        return redirect(url_for("login"))
    if not current_user.staff:
            flash("Staff profile not found.", "danger")
            return redirect(url_for("login"))

    return render_template("staff/staff_dashboard.html" , staff=current_user)
@app.route("/student")
@login_required
def student():
    if current_user.role != "student":
        flash("Only Student can access this page.", "danger")
        return redirect(url_for("login"))
    if not current_user.student:
        flash("Student profile not found.", "danger")
        return redirect(url_for("login"))
    return render_template("student/result_soon.html")
#     return render_template(
#     "student/student_dashboard.html",
#     student=current_user,
#     student_id=current_user.student.id
# )
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
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))
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
        user = User( role="staff", name=name, email=email, password=generate_password_hash(password))

            # Create Staff Profile
        staff = Staff( employee_id=employee_id, designation=designation, subject_id=subject_id , phone=phone )

            # Link Staff with User
        staff.user = user

        
        try:
            db.session.add(staff)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)        
        
        flash("Staff added successfully.", "success")
        return redirect(url_for("staff_list"))

        
    
    return render_template("admin/add_staff.html", subjects=subjects)
@app.route("/staff_list")
@login_required
def staff_list():
    if current_user.role != "admin":
        flash("Only Admin can access this page.", "danger")
        return redirect(url_for("login"))
    staffs=Staff.query.all()

    return render_template("admin/staff_list.html" , staffs=staffs)
@app.route("/activate_staff/<int:staff_id>", methods=["POST"])
def activate_staff(staff_id):
    if current_user.role != "admin":
        flash("Only Admin can access this page.", "danger")
        return redirect(url_for("login"))
    

    staff = Staff.query.get(staff_id)
    if staff:
        staff.user.is_active = True
        
        try:
            db.session.commit()
            flash("Staff activated successfully.", "success")

        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")
    return redirect(url_for("staff_list"))
@app.route("/deactivate_staff/<int:staff_id>", methods=["POST"])
def deactivate_staff(staff_id):
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))
    

    staff = Staff.query.get(staff_id)
    if staff:
        staff.user.is_active = False
        try:
            db.session.commit()
            flash("Staff deactivated successfully.", "warning")
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")            

    return redirect(url_for("staff_list"))

@app.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))
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
        existing_student = Student.query.filter_by(roll_no=roll_no , class_id=class_id).first()

        if existing_student:
            flash("Roll No already exists.", "danger")
            return redirect(url_for("add_student"))

        # Create User
        user = User( role="student", name=name, email=email, password=generate_password_hash(password))

            # Create Student Profile
        student = Student( roll_no=roll_no, class_id=class_id, phone=phone )

            # Link Staff with User
        student.user = user

        try:
            db.session.add(student)
            db.session.commit()
            flash("Student added successfully.", "success")
            return redirect(url_for("student_list"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")        

        

    return render_template("admin/add_student.html", classes=classes)
@app.route("/add_student_bystaff", methods=["GET", "POST"])
@login_required
def add_student_bystaff():
    if current_user.role != "staff":
        flash("Only staff can access this page.", "danger")
        return redirect(url_for("login"))

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
            return redirect(url_for("add_student_bystaff"))

        # Check employee id
        existing_student = Student.query.filter_by(roll_no=roll_no , class_id=class_id).first()

        if existing_student:
            flash("Roll No already exists.", "danger")
            return redirect(url_for("add_student_bystaff"))

        # Create User
        user = User( role="student", name=name, email=email, password=password)

            # Create Student Profile
        student = Student( roll_no=roll_no, class_id=class_id, phone=phone )

            # Link Staff with User
        student.user = user

        try:
            db.session.add(student)
            db.session.commit()

            flash("Student added successfully.", "success")
            return redirect(url_for("add_student_bystaff"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")        

        

    return render_template("staff/add_student.html", classes=classes ,staff=current_user)

@app.route("/student_list")
@login_required
def student_list():
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))
    students=Student.query.all()

    return render_template("admin/student_list.html" , students=students)
@app.route("/activate_student/<int:student_id>", methods=["POST"])
def activate_student(student_id):
    
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))
    student = Student.query.get(student_id)
    if student:
        student.user.is_active = True
        try:
            db.session.commit()
            flash("Student activated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")
    return redirect(url_for("student_list"))
@app.route("/deactivate_student/<int:student_id>", methods=["POST"])
def deactivate_student(student_id):
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))

    student = Student.query.get(student_id)
    if student:
        student.user.is_active = False
        try:
            db.session.commit()
            flash("student deactivated successfully.", "warning")
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")            

    return redirect(url_for("student_list"))

@app.route("/create_exam", methods=["GET", "POST"])
@login_required
def create_exam():
    if current_user.role != "admin":
        flash("Only admin can access this page.", "danger")
        return redirect(url_for("login"))

    exams=Exam.query.order_by(Exam.subject_id).all()

    subjects = Subject.query.order_by(Subject.name).all()
    staffs = Staff.query.order_by(Staff.id).all()

    if request.method == "POST":
        existing_exam = Exam.query.filter_by(subject_id=request.form.get("subject_id"),  name=request.form.get("name")).first()
        if existing_exam:
                    flash("Exam already created.", "danger")
                    return redirect(url_for("create_exam"))

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

        try:
            db.session.add(exam)
            db.session.commit()

            flash("Exam created successfully.", "success")

            return redirect(url_for("create_exam"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")        

    return render_template(
        "admin/create_exam.html",
        subjects=subjects,
        staffs=staffs,
        exams = exams
    )

@app.route("/add_subject", methods=["GET", "POST"])
def add_subject():
    if current_user.role != "admin":
        flash("Only staff can access this page.", "danger")
        return redirect(url_for("login"))

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

        try:
            db.session.add(subject)
            db.session.commit()

            flash("Subject added successfully.", "success")

            return redirect(url_for("add_subject"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")        

    return render_template("admin/add_subject.html" , subjects=subjects ,classes= classes)
@app.route("/delete_subject/<int:subject_id>", methods=["POST"])
@login_required
def delete_subject(subject_id):
    if current_user.role != "staff":
        flash("Only admin can access this page.", "danger")
        return redirect(url_for("login"))


    subject = Subject.query.get_or_404(subject_id)

    try:
        db.session.delete(subject)
        db.session.commit()

        flash("Subject deleted successfully.", "success")

        return redirect(url_for("add_subject"))
    except Exception as e:
        db.session.rollback()
        app.logger.error(e)
        flash("Unable to save staff details. Please check the entered data.", "danger")    

@app.route("/manage_exams")
@login_required
def manage_exams():
    staff_id = current_user.staff.id
    exams = Exam.query.filter_by(staff_id=staff_id).all()
    return render_template("staff/manage_exams.html", exams=exams , staff=current_user)

@app.route("/add_marks/<int:exam_id>", methods=["GET", "POST"])
@login_required
def add_marks(exam_id):
    exam = Exam.query.get_or_404(exam_id)

    if current_user.role != "staff":
        flash("Only staff can access this page.", "danger")
        return redirect(url_for("login"))

    if current_user.staff is None or current_user.staff.id != exam.staff_id:
        flash("You are not the examiner for this subject.", "danger")
        return redirect(url_for("staff"))

    

    

    students = (
    Student.query
    .filter_by(class_id=exam.class_id)
    .order_by(cast(Student.roll_no, Integer))
    .all()
)

    if request.method == "POST":

        student_ids = request.form.getlist("student_id")
        marks = request.form.getlist("marks")
        remarks = request.form.getlist("remarks")

        try:

            for i in range(len(student_ids)):

                student_id = int(student_ids[i])

                mark_value = float(marks[i]) if marks[i] else 0

                existing = Mark.query.filter_by(
                    student_id=student_id,
                    exam_id=exam.id
                ).first()

                if existing:
                    existing.marks_obtained = mark_value
                    existing.remarks = remarks[i]

                else:
                    mark = Mark(
                        student_id=student_id,
                        exam_id=exam.id,
                        marks_obtained=mark_value,
                        remarks=remarks[i]
                    )

                    db.session.add(mark)

            db.session.commit()

            flash("Marks saved successfully.", "success")
            return redirect(url_for("manage_exams"))

        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save marks. Please check the entered data.", "danger")

    marks = Mark.query.filter_by(exam_id=exam.id).all()

    return render_template(
        "staff/add_marks.html",
        exam=exam,
        students=students,
        staff=current_user,
        marks=marks
    )
@app.route("/student_result/<int:student_id>" , methods=['POST','GET'])
@login_required
def student_result(student_id):

    student = Student.query.get_or_404(student_id)

    marks = (
        Mark.query
        .filter_by(student_id=student.id)
        .join(Exam)
        .order_by(Exam.exam_date)
        .all()
    )

    return render_template(
        "admin/student_result.html",
        student=student,
        marks=marks
    )


 # FEES MANAGEMENT++++++++++++++++++++++
 # FEES MANAGEMENT++++++++++++++++++++++
@app.route("/create_class", methods=["GET", "POST"])
@login_required
def create_class():
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"].strip()
        section = request.form["section"].strip()

        existing = SchoolClass.query.filter_by(
            name=name,
            section=section
        ).first()

        if existing:
            flash(f"{name} - {section} already exists.", "warning")
            return redirect(url_for("create_class"))

        school_class = SchoolClass(
            name=name,
            section=section
        )

        try:
            db.session.add(school_class)
            db.session.commit()
            flash("Class created successfully.", "success")
            return redirect(url_for("create_class"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")        

    return render_template("admin/create_class.html")

@app.route("/create_fee", methods=["GET", "POST"])
@login_required
def create_fee():
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))
    classes = SchoolClass.query.order_by(SchoolClass.name,SchoolClass.section).all()
    if request.method == "POST":
        class_id=request.form["class_id"]
        fee_name=request.form["fee_name"]
        amount=request.form["amount"]
        existing= FeeType.query.filter_by(class_id=class_id, fee_name=fee_name).first()
        if existing:
                    flash(f"{fee_name} - {amount} already exists.", "warning")
                    return redirect(url_for("create_fee"))
        fee = FeeType(
            class_id=class_id,
            fee_name=fee_name,
            amount=amount,
            is_monthly="is_monthly" in request.form
        )

        try:
            db.session.add(fee)
            db.session.commit()

            flash("Fee created successfully.", "success")

            return redirect(url_for("create_fee"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")        

    return render_template("admin/fees/create_fee.html",classes=classes)    

@app.route("/subject_list")
@login_required
def subject_list():
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))

    subjects = Subject.query.order_by(Subject.name).all()

    return render_template(
        "admin/subject_list.html",
        subjects=subjects
    )

@app.route("/collect_fee", methods=["GET", "POST"])
@login_required
def collect_fee():
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))

    students = []

    if request.method == "POST":

        search = request.form.get("search", "").strip()
        class_id = request.form.get("class_id")

        query = Student.query.join(User)

        if search:
            query = query.filter(
                db.or_(
                    Student.id.ilike(f"%{search}%"),   # Admission No
                    Student.roll_no.ilike(f"%{search}%"),
                    User.name.ilike(f"%{search}%")
                )
            )

        if class_id:
            query = query.filter(Student.class_id == class_id)

        students = query.order_by(Student.roll_no).all()

    classes = SchoolClass.query.order_by(SchoolClass.name).all()

    return render_template(
        "admin/fees/collect_fee.html",
        students=students,
        classes=classes
    )
    # return render_template("admin/fees/fee_dashboard")

@app.route("/add_fee/<int:student_id>", methods=["GET", "POST"])
@login_required
def add_fee(student_id):
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))
    student = Student.query.get_or_404(student_id)
    fee_types = FeeType.query.filter_by(
        class_id=student.class_id
    ).all()
    
    
    exams = (
    Exam.query
    .join(Subject)
    .filter(Subject.class_id == student.class_id)
    .all()
)

    fee_history = (
        FeeCollection.query
        .filter_by(student_id=student.id)
        .order_by(FeeCollection.payment_date.desc())
        .all()
    )

    if request.method == "POST":
        # Save fee
        fee_type = FeeType.query.get_or_404(request.form["fee_type_id"])
        fee = FeeCollection(
            student_id=student.id,
            fee_type_id=fee_type.id,
            exam_id=request.form.get("exam_id") or None,
            year=request.form.get("year") or None,
            month=request.form.get("month") or None,
            amount=fee_type.amount,
            discount=float(request.form.get("discount") or 0),
            fine=float(request.form.get("fine") or 0),
            payment_mode=request.form["payment_mode"],
            # receipt_no=request.form["receipt_no"],
            remarks=request.form.get("remarks")
        )

        try:
            db.session.add(fee)
            db.session.flush()
            fee.receipt_no = f"RCPT2026{fee.id:06d}"
            db.session.commit()

            flash("Fee collected successfully.", "success")
            return redirect(url_for('collect_fee'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")
    return render_template(
        "admin/add_fee.html",
        student=student,
        fee_types=fee_types,
        exams=exams,
        fee_history=fee_history
    )

from sqlalchemy import and_
from datetime import datetime

@app.route("/fee_report")
@login_required
def fee_report():
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))

    page = request.args.get("page", 1, type=int)

    class_id = request.args.get("class_id", type=int)
    student_id = request.args.get("student_id")
    student_name = request.args.get("student_name")

    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    fee_type = request.args.get("fee_type", type=int)

    payment_mode = request.args.get("payment_mode")

    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    query = FeeCollection.query.join(Student).join(User)

    if class_id:
        query = query.filter(Student.class_id == class_id)

    if student_id:
        query = query.filter(Student.id.ilike(f"%{student_id}%"))

    if student_name:
        query = query.filter(User.name.ilike(f"%{student_name}%"))

    if year:
        query = query.filter(FeeCollection.year == year)

    if month:
        query = query.filter(FeeCollection.month == month)

    if fee_type:
        query = query.filter(FeeCollection.fee_type_id == fee_type)

    if payment_mode:
        query = query.filter(FeeCollection.payment_mode == payment_mode)

    if from_date and to_date:

        start = datetime.strptime(from_date,"%Y-%m-%d")
        end = datetime.strptime(to_date,"%Y-%m-%d")

        query = query.filter(
            FeeCollection.payment_date.between(start,end)
        )

    pagination = query.order_by(
        FeeCollection.payment_date.desc()
    ).paginate(page=page,per_page=20)

    fees = pagination.items

    total_amount = sum(f.amount for f in fees)
    total_discount = sum(f.discount for f in fees)
    total_fine = sum(f.fine for f in fees)

    return render_template(
        "admin/fees/fee_report.html",
        fees=fees,
        pagination=pagination,
        total_amount=total_amount,
        total_discount=total_discount,
        total_fine=total_fine,
        classes=SchoolClass.query.all(),
        fee_types=FeeType.query.all()
    )


from werkzeug.utils import secure_filename
import os

@app.route("/add_school", methods=["GET", "POST"])
@login_required
def add_school():
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))

    # Allow only one school record
    school = School.query.first()

    if school:
        flash("School details already exist. Please edit them.", "warning")
        return redirect(url_for("edit_school", id=school.id))

    if request.method == "POST":

        logo = request.files.get("logo")
        filename = None

        if logo and logo.filename != "":
            filename = secure_filename(logo.filename)

            upload_folder = os.path.join(
                app.root_path,
                "static",
                "uploads",
                "school_logo"
            )

            os.makedirs(upload_folder, exist_ok=True)

            logo.save(os.path.join(upload_folder, filename))

            filename = "uploads/school_logo/" + filename

        school = School(

            name=request.form.get("name"),
            code=request.form.get("code"),
            affiliation_no=request.form.get("affiliation_no"),
            udise_code=request.form.get("udise_code"),
            address=request.form.get("address"),
            city=request.form.get("city"),
            district=request.form.get("district"),
            state=request.form.get("state"),
            pin_code=request.form.get("pin_code"),
            phone=request.form.get("phone"),
            alternate_phone=request.form.get("alternate_phone"),
            email=request.form.get("email"),
            website=request.form.get("website"),
            principal=request.form.get("principal"),
            established_year=request.form.get(
                "established_year",
                type=int
            ),
            board=request.form.get("board"),
            medium=request.form.get("medium"),
            currency=request.form.get("currency"),
            logo=filename

        )

        try:
            db.session.add(school)
            db.session.commit()

            flash("School added successfully.", "success")

            return redirect(url_for("school_details"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")        

    return render_template("admin/add_school.html")

@app.route("/school_details")
@login_required
def school_details():
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))

    school = School.query.first()

    return render_template(
        "admin/school_details.html",
        school=school
    )


@app.route("/edit_school/<int:id>", methods=["GET", "POST"])
@login_required
def edit_school(id):
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))

    school = School.query.get_or_404(id)

    if request.method == "POST":

        school.name = request.form.get("name")
        school.code = request.form.get("code")
        school.affiliation_no = request.form.get("affiliation_no")
        school.udise_code = request.form.get("udise_code")
        school.address = request.form.get("address")
        school.city = request.form.get("city")
        school.district = request.form.get("district")
        school.state = request.form.get("state")
        school.pin_code = request.form.get("pin_code")
        school.phone = request.form.get("phone")
        school.alternate_phone = request.form.get("alternate_phone")
        school.email = request.form.get("email")
        school.website = request.form.get("website")
        school.principal = request.form.get("principal")
        school.established_year = request.form.get(
            "established_year",
            type=int
        )
        school.board = request.form.get("board")
        school.medium = request.form.get("medium")
        school.currency = request.form.get("currency")

        # Upload New Logo
        logo = request.files.get("logo")

        if logo and logo.filename:

            filename = secure_filename(logo.filename)

            upload_folder = os.path.join(
                app.root_path,
                "static",
                "uploads",
                "school_logo"
            )

            os.makedirs(upload_folder, exist_ok=True)

            # Delete old logo
            if school.logo:
                old_logo = os.path.join(
                    app.root_path,
                    "static",
                    school.logo
                )

                if os.path.exists(old_logo):
                    os.remove(old_logo)

            logo.save(
                os.path.join(upload_folder, filename)
            )

            school.logo = "uploads/school_logo/" + filename

        try:
            db.session.commit()

            flash("School updated successfully.", "success")

            return redirect(url_for("school_details"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to save staff details. Please check the entered data.", "danger")        

    return render_template(
        "admin/edit_school.html",
        school=school
    )

@app.route("/student_result_show/<int:student_id>" , methods=['POST','GET'])
@login_required
def student_result_show(student_id):
    if current_user.role != "student":
            flash("Only Student can access this page.", "danger")
            return redirect(url_for("login"))

    student = Student.query.get_or_404(student_id)

    marks = (
        Mark.query
        .filter_by(student_id=student.id)
        .join(Exam)
        .order_by(Exam.exam_date)
        .all()
    )

    return render_template(
        "student/student_result.html",
        student=student,
        marks=marks,
        
    )

#  bulk result 
from datetime import datetime

@app.route("/bulk_marksheet/<int:class_id>/<int:exam_id>")
@login_required
def bulk_marksheet(class_id, exam_id):
    if current_user.role != "admin":
            flash("Only Admin can access this page.", "danger")
            return redirect(url_for("login"))

    school = School.query.first()
    school_class = SchoolClass.query.get_or_404(class_id)
    selected_exam = Exam.query.get_or_404(exam_id)

    # All subjects of this examination
    exams = (
        Exam.query
        .join(Subject)
        .filter(
            Exam.name == selected_exam.name,
            Subject.class_id == class_id
        )
        .order_by(Subject.name)
        .all()
    )

    students = (
        Student.query
        .filter_by(class_id=class_id)
        .order_by(Student.roll_no)
        .all()
    )

    report_cards = []

    for student in students:

        student_marks = []
        total = 0
        obtained = 0

        for subject_exam in exams:

            mark = Mark.query.filter_by(
                student_id=student.id,
                exam_id=subject_exam.id
            ).first()

            total += subject_exam.total_marks

            marks_obtained = 0

            if mark:
                marks_obtained = mark.marks_obtained
                obtained += mark.marks_obtained

            student_marks.append({
                "exam": subject_exam,
                "mark": mark,
                "marks": marks_obtained
            })

        percentage = round((obtained / total) * 100, 2) if total else 0

        report_cards.append({
            "student": student,
            "marks": student_marks,
            "total": total,
            "obtained": obtained,
            "percentage": percentage
        })

    # -------------------------
    # Calculate Rank
    # -------------------------

    report_cards.sort(
        key=lambda x: x["obtained"],
        reverse=True
    )

    rank = 1

    for i, card in enumerate(report_cards):

        if i > 0 and card["obtained"] < report_cards[i-1]["obtained"]:
            rank = i + 1

        card["rank"] = rank

    # Optional: sort back by roll number for printing
    report_cards.sort(
        key=lambda x: x["student"].roll_no
    )

    return render_template(
        "admin/bulk_result.html",
        school=school,
        school_class=school_class,
        exam_name=selected_exam.name,
        report_cards=report_cards,
        exam=selected_exam,
        current_year=datetime.now().year
    )




@app.route("/import_students", methods=["GET", "POST"])
@login_required
def import_students():

    if current_user.role != "admin":
        flash("Only Admin can access this page.", "danger")
        return redirect(url_for("login"))

    classes = SchoolClass.query.all()

    if request.method == "POST":

        class_id = int(request.form.get("class_id"))
        file = request.files["excel"]

        if not file:
            flash("Please select an Excel file.", "danger")
            return redirect(url_for("import_students"))

        df = pd.read_excel(file)

        try:

            for _, row in df.iterrows():

                # Skip duplicate emails
                if User.query.filter_by(email=str(row["Email"])).first():
                    continue

                user = User(
                    role="student",
                    name=str(row["Name"]),
                    email=str(row["Email"]),
                    password=generate_password_hash(str(row["Password"]))
                )

                db.session.add(user)
                db.session.flush()   # Generates user.id

                student = Student(
                    user_id=user.id,
                    class_id=class_id,
                    roll_no=str(row["Roll No"]),
                    phone=str(row["Phone"])
                )

                db.session.add(student)

            db.session.commit()

            flash("Students imported successfully.", "success")
            return redirect(url_for("student_list"))

        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            flash("Unable to import students. Please check the Excel file.", "danger")

    return render_template(
        "admin/bulk_add_student.html",
        classes=classes
    )