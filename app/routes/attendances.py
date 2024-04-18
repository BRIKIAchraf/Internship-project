from datetime import datetime
from typing import Any, Callable
from flask import Blueprint, jsonify, request
from zk.attendance import Attendance
from app.services.zk_devices import access_by_id
from app.routes.util import get_device_id

bp = Blueprint("attendances", __name__)

@bp.route("/attendances", methods=["GET"])
def get_all_attendances():
    """Get all attendance records from the ZK device."""
    device_id = get_device_id()
    def datefrom(query_name: str) -> datetime | None:
        date = request.args.get(query_name)
        if date:
            return datetime.fromisoformat(date)
    start_date = datefrom('start_date')
    end_date = datefrom('end_date')
    uid = request.args.get('uid')
    def is_ok (att: Attendance) -> bool:
        nonlocal start_date, end_date, uid
        ts: datetime = att.timestamp
        if uid and att.uid != int(uid):
            return False
        if start_date and start_date > ts:
            return False
        if end_date and end_date < ts:
            return False
        return True
    with access_by_id(device_id) as (_, conn):
        attendances: list[Attendance] = conn.get_attendance()
        return jsonify([att.__dict__ for att in attendances if is_ok(att)])

@bp.route("/attendances", methods=["DELETE"])
def delete_all_attendances():
    """Delete all attendance records from the ZK device."""
    device_id = get_device_id()
    with access_by_id(device_id) as (_, conn):
        conn.clear_attendance()
        return jsonify({"success": True})
