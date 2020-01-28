from flask import Blueprint
from middle_auth_client import auth_requires_admin, auth_requires_permission
from neuroglancerjsonserver.app import common


bp = Blueprint('neuroglancerjsonserver_v0', __name__, url_prefix="/nglstate")

# -------------------------------
# ------ Access control and index
# -------------------------------


@bp.route('/', methods=["GET"])
@bp.route("/index", methods=["GET"])
def index():
    return common.index()


@bp.route
def home():
    return common.home()


# -------------------------------
# ------ Measurements and Logging
# -------------------------------

@bp.before_request
def before_request():
    return common.before_request()


@bp.after_request
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
@auth_requires_permission("view")
def get_json(json_id):
    return common.get_json(json_id)


@bp.route('/raw/<json_id>', methods=['GET'])
@auth_requires_permission("view")
def get_raw_json(json_id):
    return common.get_raw_json(json_id)


@bp.route('/post', methods=['POST', 'GET'])
@auth_requires_permission("view")
def add_json():
    return common.add_json()
