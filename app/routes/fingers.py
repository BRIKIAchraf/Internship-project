from typing import Any
from flask import Blueprint, jsonify, request
from zk.finger import Finger
from app.services.zk_devices import access_by_id
from marshmallow import Schema, fields
from marshmallow.exceptions import ValidationError
from app.routes.util import get_device_id

bp = Blueprint("fingers", __name__)

class FingerSchema(Schema):
    fid = fields.Str(required=True)
    template = fields.Str(required=True)
class FingersSchema(Schema):
    data = fields.List(fields.Nested(FingerSchema))

@bp.route("/user/<int:uid>/enroll-finger", methods=["POST"])
def enroll_finger(uid: int):
    """Enroll a user's finger on the ZK device."""
    device_id = get_device_id()
    with access_by_id(device_id) as (_, conn):
        fid = int(request.args.get('fid', 0))
        conn.enroll_user(uid, fid)
        return jsonify({"success": True})


@bp.route('/templates', methods=['GET'])
def get_templates():
    """Retrieve all templates."""
    device_id = get_device_id()
    with access_by_id(device_id) as (_, conn):
        fingers: list[Finger] = conn.get_templates()
        return jsonify(*map(lambda x: x.json_pack(), fingers))


@bp.route('/user/<int:uid>/template/<int:fid>', methods=['GET'])
def get_user_template(uid: int, fid: int):
    """Retrieve all templates."""
    device_id = get_device_id()
    with access_by_id(device_id) as (_, conn):
        finger = conn.get_user_template(uid, fid)
        if not finger:
            return jsonify(None)
        return jsonify(finger.json_pack())

@bp.route('/user/<int:uid>/template/<int:fid>', methods=['PUT'])
def set_user_template(uid: int):
    """Retrieve user specific template."""
    device_id = get_device_id()
    schema = FingersSchema()
    try:
        data: Any = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    with access_by_id(device_id) as (_, conn):
        finger = conn.save_user_template(uid, map(lambda x: Finger(0, x.fid, 0, x.template), data['data']))
        if not finger:
            return jsonify(None)
        return jsonify(finger.json_pack())
