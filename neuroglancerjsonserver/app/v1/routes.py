from flask import Blueprint, request
from middle_auth_client import auth_required
from middle_auth_client import auth_requires_admin
from neuroglancerjsonserver.app import common
import time
import datetime


bp = Blueprint('neuroglancerjsonserver_v1', __name__, url_prefix="/nglstate/api/v1")

# -------------------------------
# ------ Access control and index
# -------------------------------


@bp.route('/', methods=["GET"])
@bp.route("/index", methods=["GET"])
@auth_required
def index():
    return common.index()


@bp.route
def home():
    return common.home()


# -------------------------------
# ------ Measurements and Logging
# -------------------------------

@bp.before_request
@auth_required
def before_request():
    return common.before_request()


@bp.after_request
@auth_required
def after_request(response):
    return common.after_request(response)


@bp.errorhandler(Exception)
def internal_server_error(e):
    return common.internal_server_error(e)


@bp.errorhandler(Exception)
def unhandled_exception(e):
    return common.unhandled_exception(e)

# -------------------
# ------ Applications
# -------------------

@bp.route('/<json_id>', methods=['GET'])
@auth_required
def get_json(json_id):
    return common.get_json(json_id)


@bp.route('/raw/<json_id>', methods=['GET'])
@auth_required
def get_raw_json(json_id):
    return common.get_raw_json(json_id)


@bp.route('/post', methods=['POST', 'GET'])
@auth_required
def add_json():
    return common.add_json()

@bp.route('/post/<json_id>', methods=['POST', 'GET'])
@auth_requires_admin
def add_json_with_id(json_id):
    timestamp = float(request.args.get("timestamp", time.time()))
    timestamp = datetime.datetime.fromtimestamp(timestamp)
    return common.add_json(int(json_id), timestamp=timestamp)

@bp.route('/table_info', methods=['GET'])
@auth_required
def table_info():
    return common.table_info()


