from flask import request, make_response, jsonify, g
from flask import current_app
import json
import time

from neuroglancerjsonserver.app import app_utils
from neuroglancerjsonserver import __version__


__api_versions__ = [0]

# -------------------------------
# ------ Access control and index
# -------------------------------

def index():
    return f"NeuroglancerJsonServer - v{__version__}"


def home():
    resp = make_response()
    resp.headers['Access-Control-Allow-Origin'] = '*'
    acah = "Origin, X-Requested-With, Content-Type, Accept"
    resp.headers["Access-Control-Allow-Headers"] = acah
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    resp.headers["Connection"] = "keep-alive"
    return resp


# -------------------------------
# ------ Measurements and Logging
# -------------------------------

def before_request():
    g.request_start_time = time.time()


def after_request(response):
    dt = (time.time() - g.request_start_time) * 1000

    url_split = request.url.split("/")
    current_app.logger.info("%s - %s - %s - %s - %f.3" %
                            (request.path.split("/")[-1], "1",
                             "".join([url_split[-2], "/", url_split[-1]]),
                             str(request.data), dt))

    print("Response time: %.3fms" % (dt))
    return response


def internal_server_error(error):
    dt = (time.time() - g.request_start_time) * 1000

    url_split = request.url.split("/")
    current_app.logger.error("%s - %s - %s - %s - %f.3" %
                             (request.path.split("/")[-1],
                              "Server Error: " + error,
                              "".join([url_split[-2], "/", url_split[-1]]),
                              str(request.data), dt))
    return 500


def unhandled_exception(e):
    dt = (time.time() - g.request_start_time) * 1000

    url_split = request.url.split("/")
    current_app.logger.error("%s - %s - %s - %s - %f.3" %
                             (request.path.split("/")[-1],
                              "Exception: " + str(e),
                              "".join([url_split[-2], "/", url_split[-1]]),
                              str(request.data), dt))
    return 500

# -------------------
# ------ Applications
# -------------------

def get_json(json_id):
    db = app_utils.get_json_db()

    json_data = db.get_json(int(json_id), decompress=True)

    return jsonify(json.loads(json_data))


def get_raw_json(json_id):
    db = app_utils.get_json_db()

    json_data = db.get_json(int(json_id), decompress=False)

    return json_data


def add_json():
    user_id = str(g.auth_user["id"])
    print("ADD - {user_id} - 1")

    db = app_utils.get_json_db()

    print("ADD - {user_id} - 2")

    # Verify that data is json
    try:
        _ = json.loads(request.data)
    except ValueError:
        raise ValueError

    print("ADD - {user_id} - 3")

    json_id = db.add_json(request.data, user_id=user_id)
    url_base = request.url.strip("/").rsplit("/", 1)[0]

    print("ADD - {user_id} - 4")

    return jsonify("{}/{}".format(url_base, json_id))


def table_info():
    user_id = str(g.auth_user["id"])
    db = app_utils.get_json_db()

    return f"User: {user_id} - project {db.project_id} - table {db.namespace}"
