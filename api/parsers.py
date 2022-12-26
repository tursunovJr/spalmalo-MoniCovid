from marshmallow import Schema, fields

class UserDataSchema(Schema):
    name = fields.String(attribute="name", required=True)
    last_name = fields.String(attribute="lastname", required=True)
    gender = fields.String(attribute="gender", required=True)
    birthdate = fields.Date(attribute="date", required=True)
    address = fields.String(attribute="address", required=True)
    health_status = fields.Boolean(attribute="address", required=True)
    percentage = fields.Decimal(attribute="percentage", required=True)
    password = fields.String(attribute="password", required=True)
