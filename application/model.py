from .database import db
from flask_login import UserMixin
from datetime import datetime

# =========================================== School Model=========================

class School(db.Model):
    __tablename__ = "schools"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(30), unique=True)
    affiliation_no = db.Column(db.String(50))
    udise_code = db.Column(db.String(50))
    address = db.Column(db.String(300))
    city = db.Column(db.String(100))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pin_code = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    alternate_phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(120))
    principal = db.Column(db.String(150))
    established_year = db.Column(db.Integer)
    logo = db.Column(db.String(255))      # uploads/logo.png
    board = db.Column(db.String(50))      # SEBA / CBSE / ICSE
    medium = db.Column(db.String(50))     # English / Assamese
    currency = db.Column(db.String(10), default="₹")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )
# ==========================
# User
# ==========================
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)       # Admin / Staff / Student
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    staff = db.relationship("Staff",back_populates="user",uselist=False,cascade="all, delete-orphan")

    student = db.relationship("Student",back_populates="user",uselist=False,cascade="all, delete-orphan")

# ==========================
# Staff
# ==========================
class Staff(db.Model):
    __tablename__ = "staffs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),unique=True,nullable=False)
    employee_id = db.Column(db.String(30),unique=True, nullable=False )
    subject_id = db.Column(db.Integer,db.ForeignKey("subjects.id"))
    designation = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15))
    # Relationships
    user = db.relationship("User", back_populates="staff")
    subject = db.relationship("Subject" , back_populates="staff" , uselist=False)
    exams = db.relationship("Exam",back_populates="staff", cascade="all, delete-orphan")


# ==========================
# Student
# ==========================
class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"), unique=True, nullable=False )
    roll_no = db.Column(db.String(20), nullable=False)
    class_id = db.Column(db.Integer,db.ForeignKey("classes.id"),nullable=False)
    phone = db.Column(db.String(15))
      
    # Relationships
    user = db.relationship("User", back_populates="student")
    marks = db.relationship("Mark",back_populates="student",cascade="all, delete-orphan")
    school_class = db.relationship("SchoolClass",back_populates="students")
    fee_collections = db.relationship("FeeCollection",back_populates="student",cascade="all, delete-orphan")
    __table_args__ = (
        db.UniqueConstraint(
            "roll_no",
            "class_id",
            name="unique_roll_per_section"
        ),
    )

class SchoolClass(db.Model):
    __tablename__ = "classes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    # Relationships
    students = db.relationship("Student",back_populates="school_class",cascade="all, delete-orphan")
    subjects = db.relationship("Subject",back_populates="school_class",cascade="all, delete-orphan" )
    fee_types = db.relationship("FeeType",back_populates="school_class",cascade="all, delete-orphan")
    __table_args__ = (
        db.UniqueConstraint(
            "name",
            "section",
            name="unique_class_section"
        ),
    )

    def __repr__(self):
        return f"{self.name} - {self.section}"
# ==========================
# Subject
# ==========================
class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    class_id = db.Column(db.Integer,db.ForeignKey("classes.id"),nullable=False)
    # Relationships
    school_class = db.relationship("SchoolClass",back_populates="subjects")
    exams = db.relationship("Exam", back_populates="subject",cascade="all, delete-orphan" )
    staff = db.relationship("Staff",back_populates="subject" , uselist = False )
# ==========================
# Exam
# ==========================
class Exam(db.Model):
    __tablename__ = "exams"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer,  db.ForeignKey("subjects.id"),nullable=False )
    exam_date = db.Column(db.Date, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    pass_marks = db.Column(db.Integer, nullable=False)
    staff_id = db.Column(db.Integer,db.ForeignKey("staffs.id"),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    subject = db.relationship("Subject", back_populates="exams")
    staff = db.relationship("Staff", back_populates="exams")
    marks = db.relationship("Mark",back_populates="exam",cascade="all, delete-orphan")
    fee_collections = db.relationship("FeeCollection", back_populates="exam",cascade="all, delete-orphan")


# ==========================
# Marks
# ==========================
class Mark(db.Model):
    __tablename__ = "marks"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey("students.id"),nullable=False )
    exam_id = db.Column(db.Integer,db.ForeignKey("exams.id"), nullable=False )
    marks_obtained = db.Column(db.Float, nullable=False,default=0)
    grade = db.Column(db.String(5))
    remarks = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    student = db.relationship("Student", back_populates="marks")
    exam = db.relationship("Exam", back_populates="marks")
    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "exam_id",
            name="unique_student_exam"
        ),
    )

# ==========================
# Fee Type
# ==========================
class FeeType(db.Model):
    __tablename__ = "fee_types"
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer,db.ForeignKey("classes.id"),nullable=False)
    fee_name = db.Column(db.String(50), nullable=False) # Admission Fee, Monthly Fee, Exam Fee
    amount = db.Column(db.Float, nullable=False)
    is_monthly = db.Column(db.Boolean, default=False)
    school_class = db.relationship("SchoolClass",back_populates="fee_types")
    collections = db.relationship("FeeCollection", back_populates="fee_type", cascade="all, delete-orphan")
    __table_args__ = (
        db.UniqueConstraint(
            "class_id",
            "fee_name",
            name="unique_fee_per_class"
        ),
    )

# ==========================
# Fee Collection
# ==========================
class FeeCollection(db.Model):
    __tablename__ = "fee_collections"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey("students.id"), nullable=False )
    fee_type_id = db.Column(db.Integer,db.ForeignKey("fee_types.id"), nullable=False )
    exam_id = db.Column(db.Integer,db.ForeignKey("exams.id"),nullable=True )   # Only used for Exam Fee
    year = db.Column(db.Integer, nullable=True)
    month = db.Column(db.Integer, nullable=True)
    amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    fine = db.Column(db.Float, default=0)
    payment_mode = db.Column(db.String(20))
    receipt_no = db.Column(db.String(30), unique=True)
    payment_date = db.Column(db.DateTime,default=datetime.utcnow)
    remarks = db.Column(db.String(200))
    student = db.relationship("Student",back_populates="fee_collections")
    fee_type = db.relationship("FeeType", back_populates="collections")
    exam = db.relationship("Exam",back_populates="fee_collections" )