from typing import Any
from flask import Blueprint, jsonify, request
from zk.user import User
from zk import const
from app.services.zk_devices import access_by_id
from app.routes.util import get_device_id
from marshmallow import Schema, fields, validate
from marshmallow.exceptions import ValidationError

bp = Blueprint("users", __name__)

@bp.route("/users", methods=["GET"])
def get_users():
    device_id = get_device_id()
    """Get all users from the ZK device."""
    with access_by_id(device_id) as (_, conn):
        users = conn.get_users()
        return jsonify([user.__dict__ for user in users])

@bp.route("/user/<int:uid>/verif", methods=["GET"])
def get_user_verif_mode(uid: int):
    device_id = get_device_id()
    with access_by_id(device_id) as (_, conn):
        return jsonify({"mode": conn.get_user_verif_mode(uid)})

@bp.route("/user/<int:uid>/verif", methods=["PUT"])
def set_user_verif_mode(uid: int):
    device_id = get_device_id()
    data = request.get_json()
    mode = data.get("mode")
    with access_by_id(device_id) as (_, conn):
        conn.set_user_verif_mode(uid, mode)
        return jsonify({"mode": conn.get_user_verif_mode(uid)})

class UserSchema(Schema):
    name = fields.Str()
    privilege = fields.Int()
    password = fields.Str()
    group_id = fields.Str()
    card = fields.Int()
    uid = fields.Int()
    verif = fields.Str(validate=validate.OneOf([None, *const.VERIF_MODES]), allow_none=True)

USER_KEYS = list(UserSchema().dump_fields.keys())
USER_KEYS.remove('uid')
USER_KEYS.remove('verif')

@bp.route("/users", methods=["POST"])
def add_user():
    device_id = get_device_id()
    schema = UserSchema()
    try:
        data: Any = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    with access_by_id(device_id) as (_, conn):
        if not 'uid' in data:
            conn.get_users()
            data['uid'] = conn.next_uid
        conn.set_user(**{k: v for k, v in data.items() if k != 'verif'})
        if "verif" in data:
            conn.set_user_verif_mode(data['uid'], data.get("verif"))
        return jsonify(data)

@bp.route("/user/<int:uid>", methods=["PATCH"])
def set_user(uid: int):
    device_id = get_device_id()
    schema = UserSchema()
    try:
        data: Any = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    if data.get("uid", uid) != uid:
        return jsonify({"error": "Uid mismatch"}), 400
    data["uid"] = uid
    with access_by_id(device_id) as (_, conn):
        if any(not k in data for k in USER_KEYS):
            users: list[User] = conn.get_users()
            user: User | None = None
            for u in users:
                if u.uid == uid:
                    user = u
            if not user:
                return jsonify({"error": "User not found"}), 404
            for k in USER_KEYS:
                if not k in data:
                    data[k] = user.__dict__[k]
        conn.set_user(**{k: v for k, v in data.items() if k != 'verif'})
        if "verif" in data:
            conn.set_user_verif_mode(uid, data.get("verif"))
        return jsonify(data)

@bp.route("/user/<int:uid>", methods=["DELETE"])
def delete_user(uid: int):
    device_id = get_device_id()
    """Delete a user from the ZK device."""
    with access_by_id(device_id) as (_, conn):
        conn.delete_user(uid)
        return jsonify({"success": True})
