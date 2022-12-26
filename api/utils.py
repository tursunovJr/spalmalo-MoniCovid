from flask import jsonify, make_response as flask_make_response


# def make_response(status_code, **kwargs):
#     response = jsonify({
#         **kwargs
#     })
#     response.status_code = status_code
#     return response

def make_data_response(status_code, **kwargs):
    response = jsonify({
            **kwargs
        })
    response.status_code = status_code
    return response

def make_empty(status_code):
    response = flask_make_response()
    response.status_code = status_code
    del response.headers["Content-Type"]
    del response.headers["Content-Length"]
    return response
