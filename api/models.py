from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db, login_manager
from uuid import uuid4
from flask_login import LoginManager, UserMixin


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)



class Patient(db.Model):
    uuid = db.Column(db.String(36), primary_key=True,
                     default=lambda: str(uuid4()))
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(9), nullable=False)
    birthday = db.Column(db.Date, nullable=False)

    # def __repr__(self):
    #     return "<Patient: name={}, phone={}, birthday=\"{}\">\n"\
    #         .format(self.name, self.phone, self.birthday)


class Doctor(db.Model):
    uuid = db.Column(db.String(36), primary_key=True,
                     default=lambda: str(uuid4()))
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(9), nullable=False)
    speciality = db.Column(db.String(50), nullable=False)
    qualification = db.Column(db.String(50), nullable=False)


class Service(db.Model):
    uuid = db.Column(db.String(36), primary_key=True,
                     default=lambda: str(uuid4()))
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)


class Record(db.Model):
    uuid = db.Column(db.String(36), primary_key=True,
                     default=lambda: str(uuid4()))
    patient_uuid = db.Column(db.String, db.ForeignKey('patient.uuid'),
                             nullable=False)
    doctor_uuid = db.Column(db.String, db.ForeignKey('doctor.uuid'),
                            nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    # used_services = db.relationship('Services', lazy='select',
    #                                 backref=db.backref('Record', lazy='joined'))
    used_services = db.Column(db.String, nullable=False)
    # used_services = db.Column(db.String, nullable=False)
    disease = db.Column(db.String(200), nullable=False)
    discharge = db.Column(db.String, nullable=False)
    payment_status = db.Column(db.Boolean, nullable=False, default=False)
    sum = db.Column(db.Integer, nullable=False, default=0)
