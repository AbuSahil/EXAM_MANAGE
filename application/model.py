from .database import db
from datetime import datetime ,date
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    role= db.Column(db.String(), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    staff = db.relationship("Staff", back_populates="user", uselist=False)

    student = db.relationship("Student",back_populates="user", uselist=False )
class Staff(db.Model):
    __tablename__ = 'staffs' 
    id =  db.Column(db.Integer , primary_key = True)
    user_id = db.Column(db.Integer , db.ForeignKey("users.id") , unique =  True)
    employee_id = db.Column(db.String(30), unique = True)
    designation = db.Column(db.String())
    subject = db.Column(db.String())
    # relationShip with other Table
    schedules = db.relationship("ExamSchedule", back_populates="staff")
    user = db.relationship("User",back_populates="staff")
    

class Student(db.Model):
    __tablename__ = 'students'
    id =  db.Column(db.Integer , primary_key = True)
    user_id = db.Column(db.Integer , db.ForeignKey("users.id") , unique =  True)
    roll_no = db.Column(db.String(),unique = True)
    class_name = db.Column(db.String())
    section = db.Column(db.String())
    # RelationShip with other table
    user = db.relationship("User",back_populates="student")
    marks = db.relationship("Mark", back_populates="student")

class AcademicYear(db.Model):
    __tablename__ = 'academic_year'
    id =  db.Column(db.Integer , primary_key = True)
    year = db.Column(db.String())
    is_active = db.Column(db.Boolean , default = False)

class Exam(db.Model):
    __tablename__ = 'exams'
    id =  db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String())
    academic_year_id = db.Column(db.Integer , db.ForeignKey("academic_year.id"))
    schedules = db.relationship("ExamSchedule",back_populates="exam")

class ExamSchedule(db.Model):
    __tablename__ = 'exam_schedule'
    id =  db.Column(db.Integer , primary_key = True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    subject  = db.Column(db.String())
    exam_date = db.Column(db.Date )
    total_marks = db.Column(db.Integer)
    pass_marks = db.Column(db.Integer)
    staff_id = db.Column(db.Integer , db.ForeignKey("staffs.id"))
    # relationShip
    exam = db.relationship("Exam", back_populates='schedules')
    staff = db.relationship("Staff", back_populates='schedules')
    marks = db.relationship("Mark",  back_populates="schedule")

class Mark(db.Model):
    __tablename__ = 'marks'
    id =  db.Column(db.Integer , primary_key = True)
    student_id = db.Column(db.Integer , db.ForeignKey("students.id"))
    exam_schedule_id = db.Column(db.Integer , db.ForeignKey("exam_schedule.id"))
    marks_obtained = db.Column(db.Float)
    grade = db.Column(db.String(5))
    remarks = db.Column(db.String(100))
    # relationShip

    student = db.relationship("Student", back_populates = 'marks')
    schedule = db.relationship("ExamSchedule" , back_populates = 'marks')













    

       



