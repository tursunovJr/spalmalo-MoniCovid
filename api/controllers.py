from flask import request, render_template, make_response, flash, redirect
from flask_restful import Resource, abort, url_for
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash

from api.fields import patients_info_schema, doctors_info_schema, services_info_schema, records_info_schema, \
    record_info_schema, patient_info_schema, doctor_info_schema
from api.forms import LoginForm
from api.models import Patient, Record, Doctor, Service, User
from api.parsers import PatientSchema, RecordSchema, DoctorSchema, ServiceSchema, UserSchema
from api.utils import make_empty, make_data_response
from extensions import db
from sqlalchemy import exc
from flask_login import login_user, login_required, logout_user

class Main(Resource):
    @staticmethod
    @login_required
    def get():
        return make_response(render_template('api/main.html'), 200)


class UserLogOut(Resource):
    @staticmethod
    @login_required
    def get():
        logout_user()
        flash("You have been log out")
        return redirect('/api/v1')


class UserSignUp(Resource):
    @staticmethod
    def post():
        "Создать нового пользователя"
        try:
            args = UserSchema().load(request.json)
        except ValidationError as error:
            return make_data_response(400, message="Bad JSON format")
        args['password'] = generate_password_hash(str(args['password']))
        user = User(**args)
        try:
            db.session.add(user)
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database add error")

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        return make_empty(201)


class UserLogIn(Resource):
    @staticmethod
    def get():
        "Вход пользователя в систему"
        form = LoginForm()
        return make_response(render_template('api/index.html', form=form), 200)

    @staticmethod
    @login_required
    def post():
        "Вход пользователя в систему"
        form = LoginForm()
        if form.validate_on_submit():
            user = db.session.query(User).filter(User.username.like(form.username.data)).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect('/api/v1')
            flash("Invalid username/password", "error")
            return make_response(render_template('api/index.html', form=form))
        return make_response(render_template('api/index.html', form=form), 401)

class Patients(Resource):
    @staticmethod
    # разкомментируй внизу чтобы заработало проверка доступа
    # @login_required
    def post():
        """Создать нового пациента"""
        try:
            args = PatientSchema().load(request.json)
        except ValidationError as error:
            return make_data_response(400, message="Bad JSON format")
        patient = Patient(**args)
        try:
            db.session.add(patient)
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database add error")

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")
        location_url = url_for("api.patient_info", patient_uuid=patient.uuid)
        resp = make_data_response(201, location=location_url)
        resp.headers["Location"] = location_url
        return resp

    @staticmethod
    # @login_required
    def get():
        """Получить список всех пациентов"""
        patients = db.session.query(Patient).all()
        return make_data_response(200, patients=patients_info_schema.dump(patients))



class PatientAction(Resource):
    @staticmethod
    def get(patient_uuid):
        """Получить информамацию об одном пациенте"""
        patient_info = db.session.query(Patient).filter(Patient.uuid.like(str(patient_uuid)))\
                .one_or_none()
        if patient_info is None or patient_info.uuid is None:
            abort(404, message="Patient with uuid={} not found"
                  .format(patient_uuid))
        return make_data_response(200, **patient_info_schema.dump(patient_info))


    @staticmethod
    # @login_required
    def delete(patient_uuid):
        """Удалить пациента по uuid"""
        if db.session.query(Patient).filter(Patient.uuid.like(str(patient_uuid)))\
                .one_or_none() is None:
            abort(404, message="Patient with uuid={} not found"
                  .format(patient_uuid))

        patient = db.session.query(Patient).filter(Patient.uuid.like(str(patient_uuid))).one()
        try:
            db.session.delete(patient)
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database delete error")

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        return make_empty(200)

    @staticmethod
    # @login_required
    def patch(patient_uuid):
        """Обновить информацию о пациенте по uuid"""
        if db.session.query(Patient).filter(Patient.uuid.like(str(patient_uuid))) \
                .one_or_none() is None:
            abort(404, message="Patient with uuid={} not found"
                  .format(patient_uuid))
        try:
            args = request.json
        except ValidationError as error:
            return make_data_response(400, message="Bad JSON format")

        patient = db.session.query(Patient).filter(Patient.uuid.like(str(patient_uuid))).one()
        for key in args:
            if args[key] is not None:
                setattr(patient, key, args[key])
        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        return make_empty(200)

    @staticmethod
    # @login_required
    def post(patient_uuid):
        "Создать запись для пациента"
        if db.session.query(Patient).filter(Patient.uuid.like(str(patient_uuid))) \
                .one_or_none() is None:
            abort(404, message="Patient with uuid={} not found"
                  .format(patient_uuid))
        try:
            args = RecordSchema().load(request.json)
            args['patient_uuid'] = str(patient_uuid)
            # print(args['used_services'])
        except ValidationError as error:
            return make_data_response(400, message="Bad JSON format")
        record = Record(**args)
        try:
            db.session.add(record)
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database add error")

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        location_url = url_for("api.record_info", record_uuid=record.uuid)
        resp = make_data_response(201, location=location_url)
        resp.headers["Location"] = location_url
        return resp


class Doctors(Resource):
    @staticmethod
    # @login_required
    def post():
        """Создать нового врача"""
        try:
            args = DoctorSchema().load(request.json)
        except ValidationError as error:
            return make_data_response(400, message="Bad JSON format")
        doctor = Doctor(**args)
        try:
            db.session.add(doctor)
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database add error")

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        location_url = url_for("api.doctor_info", doctor_uuid=doctor.uuid)
        resp = make_data_response(201, location=location_url)
        resp.headers["Location"] = location_url
        return resp

    @staticmethod
    # @login_required
    def get():
        """Получить список всех врачей"""
        doctors = db.session.query(Doctor).all()
        return make_data_response(200, doctor=doctors_info_schema.dump(doctors))


class DoctorAction(Resource):
    @staticmethod
    def get(doctor_uuid):
        """Получить информамацию об одном враче"""
        doctor_info = db.session.query(Doctor).filter(Doctor.uuid.like(str(doctor_uuid))) \
            .one_or_none()
        if doctor_info is None or doctor_info.uuid is None:
            abort(404, message="Patient with uuid={} not found"
                  .format(doctor_uuid))
        return make_data_response(200, **doctor_info_schema.dump(doctor_info))

    @staticmethod
    # @login_required
    def delete(doctor_uuid):
        """Удалить врача по uuid"""
        if db.session.query(Doctor).filter(Doctor.uuid.like(str(doctor_uuid)))\
                .one_or_none() is None:
            abort(404, message="Doctor with uuid={} not found"
                  .format(doctor_uuid))

        doctor = db.session.query(Doctor).filter(Doctor.uuid.like(str(doctor_uuid))).one()
        try:
            db.session.delete(doctor)
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database delete error")

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        return make_empty(200)

    @staticmethod
    # @login_required
    def patch(doctor_uuid):
        """Обновить информацию о враче по uuid"""
        if db.session.query(Doctor).filter(Doctor.uuid.like(str(doctor_uuid))) \
                .one_or_none() is None:
            abort(404, message="Doctor with uuid={} not found"
                  .format(doctor_uuid))
        try:
            args = request.json
        except ValidationError as error:
            return make_data_response(400, message="Bad JSON format")

        doctor = db.session.query(Doctor).filter(Doctor.uuid.like(str(doctor_uuid))).one()
        for key in args:
            if args[key] is not None:
                setattr(doctor, key, args[key])
        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        return make_empty(200)


class Services(Resource):
    @staticmethod
    # @login_required
    def post():
        """Создать новую услугу"""
        try:
            args = ServiceSchema().load(request.json)
        except ValidationError as error:
            return make_data_response(400, message="Bad JSON format")
        service = Service(**args)
        try:
            db.session.add(service)
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database add error")

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        return make_empty(201)

    @staticmethod
    # @login_required
    def get():
        """Получить список всех услуг"""
        services = db.session.query(Service).all()
        return make_data_response(200, service=services_info_schema.dump(services))


class ServiceAction(Resource):
    @staticmethod
    # @login_required
    def delete(service_uuid):
        """Удалить услугу по id"""
        if db.session.query(Service).filter(Service.uuid.like(str(service_uuid)))\
                .one_or_none() is None:
            abort(404, message="Service with uuid={} not found"
                  .format(service_uuid))

        service = db.session.query(Service).filter(Service.uuid.like(str(service_uuid))).one()
        try:
            db.session.delete(service)
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database delete error")

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        return make_empty(200)

    @staticmethod
    # @login_required
    def patch(service_uuid):
        """Обновить информацию о услуге по id"""
        if db.session.query(Service).filter(Service.uuid.like(str(service_uuid))) \
                .one_or_none() is None:
            abort(404, message="Service with uuid={} not found"
                  .format(service_uuid))
        try:
            args = request.json
        except ValidationError as error:
            return make_data_response(400, message="Bad JSON format")

        service = db.session.query(Service).filter(Service.uuid.like(str(service_uuid))).one()
        for key in args:
            if args[key] is not None:
                setattr(service, key, args[key])
        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        return make_empty(200)


class Records(Resource):
    @staticmethod
    # @login_required
    def get():
        """Получить список всех записей пациентов у врача"""
        records = db.session.query(Record).all()
        return make_data_response(200, records=records_info_schema.dump(records))


class RecordAction(Resource):
    @staticmethod
    # @login_required
    def get(record_uuid):
        """Получить информамацию об одной записей"""
        record_info = db.session.query(Record).filter(Record.uuid.like(str(record_uuid))) \
            .one_or_none()
        if record_info is None or record_info.uuid is None:
            abort(404, message="Record with uuid={} not found"
                  .format(record_info))
        return make_data_response(200, **record_info_schema.dump(record_info))

    @staticmethod
    # @login_required
    def delete(record_uuid):
        """Удалить запись по uuid"""
        if db.session.query(Record).filter(Record.uuid.like(str(record_uuid))) \
                .one_or_none() is None:
            abort(404, message="Service with uuid={} not found"
                  .format(record_uuid))

        record = db.session.query(Record).filter(Record.uuid.like(str(record_uuid))).one()
        try:
            db.session.delete(record)
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database delete error")

        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        return make_empty(200)

    @staticmethod
    # @login_required
    def patch(record_uuid):
        """Обновить информацию о записи по uuid"""
        if db.session.query(Record).filter(Record.uuid.like(str(record_uuid))) \
                .one_or_none() is None:
            abort(404, message="Record with uuid={} not found"
                  .format(record_uuid))
        try:
            args = request.json
        except ValidationError as error:
            return make_data_response(400, message="Bad JSON format")

        record = db.session.query(Record).filter(Record.uuid.like(str(record_uuid))).one()
        for key in args:
            if args[key] is not None:
                setattr(record, key, args[key])
        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            return make_data_response(500, message="Database commit error")

        return make_empty(200)