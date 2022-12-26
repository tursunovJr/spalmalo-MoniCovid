from marshmallow import fields, Schema


class PatientInfoSchema(Schema):
    uuid = fields.String(attribute="uuid")
    name = fields.String(attribute="name", required=True)
    phone = fields.String(attribute="phone", required=True)
    birthday = fields.Date(attribute="birthday", format="iso8601",
                           required=True)


class DoctorInfoSchema(Schema):
    uuid = fields.String(attribute="uuid")
    name = fields.String(attribute="name", required=True)
    phone = fields.String(attribute="phone", required=True)
    speciality = fields.String(attribute="speciality", required=True)
    qualification = fields.String(attribute="qualification", required=True)


class ServiceInfoSchema(Schema):
    uuid = fields.String(attribute="uuid")
    name = fields.String(attribute="name", required=True)
    price = fields.Integer(attribute="price", required=True)


class RecordInfoSchema(Schema):
    uuid = fields.String(attribute="uuid")
    patient_uuid = fields.String(attribute="patient_uuid", required=True)
    doctor_uuid = fields.String(attribute="doctor_uuid", required=True)
    date = fields.DateTime(attribute="date", required=True)
    used_services = fields.String(attribute="used_services", required=True)
    disease = fields.String(attribute="disease", required=True)
    discharge = fields.String(attribute="discharge", required=True)
    payment_status = fields.Boolean(attribute="payment_status", required=True)
    sum = fields.Integer(attribute="sum", required=True)


patients_info_schema = PatientInfoSchema(many=True)
patient_info_schema = PatientInfoSchema()
doctors_info_schema = DoctorInfoSchema(many=True)
doctor_info_schema = DoctorInfoSchema()
services_info_schema = ServiceInfoSchema(many=True)
records_info_schema = RecordInfoSchema(many=True)
record_info_schema = RecordInfoSchema()