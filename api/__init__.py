from flask import Blueprint, json
from flask_restful import Api
from werkzeug.exceptions import HTTPException

from api.controllers import Patients, PatientAction, Doctors, DoctorAction, Services, ServiceAction, Records, \
    RecordAction, UserSignUp, UserLogIn, Main, UserLogOut

api_bp = Blueprint("api", __name__, template_folder='templates', static_folder='static')
api_urls = Api(api_bp)


# Add resources
api_urls.add_resource(UserLogOut, "/logout")
api_urls.add_resource(Main, "")
api_urls.add_resource(UserSignUp, "/signup")
api_urls.add_resource(UserLogIn, "/login")
api_urls.add_resource(Patients, "/patients")
api_urls.add_resource(PatientAction, "/patients/<uuid:patient_uuid>",
                      endpoint="patient_info")
api_urls.add_resource(Doctors, "/doctors")
api_urls.add_resource(DoctorAction, "/doctors/<uuid:doctor_uuid>",
                      endpoint="doctor_info")
api_urls.add_resource(Services, "/services")
api_urls.add_resource(ServiceAction, "/services/<uuid:service_uuid>")
api_urls.add_resource(Records, "/records")
api_urls.add_resource(RecordAction, "/records/<uuid:record_uuid>",
                      endpoint="record_info")

# JSON format for error
@api_bp.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response
