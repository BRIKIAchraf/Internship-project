from flask import Blueprint, jsonify, request

bp = Blueprint("util", __name__, url_prefix="/")

class NoDeviceID(Exception):
    pass

def get_device_id():
    device_id = request.headers.get('Device-ID')
    if not device_id:
        raise NoDeviceID()
    return device_id

@bp.errorhandler(NoDeviceID)
def handle_no_device_error(e):
  return jsonify({"error": "Device-ID header is required"}), 400
