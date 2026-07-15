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
        existing_student = Student.query.filter_by(roll_no=roll_no , class_id=class_id).first()

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
@app.route("/add_student_bystaff", methods=["GET", "POST"])
@login_required
def add_student_bystaff():
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

        db.session.add(student)
        db.session.commit()

        flash("Student added successfully.", "success")
        return redirect(url_for("student_list"))

        

    return render_template("staff/add_student.html", classes=classes ,staff=current_user)

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
    exams=Exam.query.order_by(Exam.subject_id).all()

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
        staffs=staffs,
        exams = exams
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
    staff_id = current_user.staff.id
    exams = Exam.query.filter_by(staff_id=staff_id).all()
    return render_template("staff/manage_exams.html", exams=exams , staff=current_user)

@app.route("/add_marks/<int:exam_id>" , methods=['POST','GET'])
@login_required
def add_marks(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    


    students = Student.query.filter_by(class_id=exam.subject.class_id).order_by(Student.roll_no).all()
    if request.method == "POST":

        student_ids = request.form.getlist("student_id")
        marks = request.form.getlist("marks")
        grades = request.form.getlist("grade")
        remarks = request.form.getlist("remarks")

        for i in range(len(student_ids)):

            student_id = int(student_ids[i])

            # Prevent duplicate entries
            existing = Mark.query.filter_by(
                student_id=student_id,
                exam_id=exam.id
            ).first()

            if existing:
                existing.marks_obtained = float(marks[i])
                existing.grade = grades[i]
                existing.remarks = remarks[i]

            else:
                mark = Mark(
                    student_id=student_id,
                    exam_id=exam.id,
                    marks_obtained=float(marks[i]),
                    grade=grades[i],
                    remarks=remarks[i]
                )

                db.session.add(mark)

        db.session.commit()

        flash("Marks saved successfully.", "success")

        return redirect(url_for("manage_exams"))
    
    marks = Mark.query.filter_by(exam_id=exam.id).all()
    print(marks)

    
    return render_template(
    "staff/add_marks.html",
    exam=exam,
    students=students,
    staff=current_user, marks = marks)
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

@app.route("/marksheet")
@login_required
def marksheet():
    students=Student.query.all()
    return render_template("admin/marksheet.html" , students=students)

 # FEES MANAGEMENT++++++++++++++++++++++
 # FEES MANAGEMENT++++++++++++++++++++++
@app.route("/create_class", methods=["GET", "POST"])
@login_required
def create_class():

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

        db.session.add(school_class)
        db.session.commit()

        flash("Class created successfully.", "success")
        return redirect(url_for("create_class"))

    return render_template("admin/create_class.html")

@app.route("/create_fee", methods=["GET", "POST"])
@login_required
def create_fee():
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

        db.session.add(fee)
        db.session.commit()

        flash("Fee created successfully.", "success")

        return redirect(url_for("create_fee"))

    return render_template("admin/fees/create_fee.html",classes=classes)    

@app.route("/subject_list")
@login_required
def subject_list():

    subjects = Subject.query.order_by(Subject.name).all()

    return render_template(
        "admin/subject_list.html",
        subjects=subjects
    )

@app.route("/collect_fee", methods=["GET", "POST"])
@login_required
def collect_fee():

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
        "admin/collect_fee.html",
        students=students,
        classes=classes
    )

@app.route("/add_fee/<int:student_id>", methods=["GET", "POST"])
@login_required
def add_fee(student_id):
    student = Student.query.get_or_404(student_id)
    fee_types = FeeType.query.filter_by(
        class_id=student.class_id
    ).all()
    print(request.form)
    
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

        db.session.add(fee)
        db.session.flush()
        fee.receipt_no = f"RCPT2026{fee.id:06d}"
        db.session.commit()

        flash("Fee collected successfully.", "success")
        return redirect(url_for('collect_fee'))

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
        query = query.filter(Student.student_id.ilike(f"%{student_id}%"))

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
        "admin/fee_report.html",
        fees=fees,
        pagination=pagination,
        total_amount=total_amount,
        total_discount=total_discount,
        total_fine=total_fine,
        classes=SchoolClass.query.all(),
        fee_types=FeeType.query.all()
    )