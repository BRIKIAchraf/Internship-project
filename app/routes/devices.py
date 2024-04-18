from flask import Blueprint, jsonify, request
from app.models.device import Device
from app import db
from app.services.zk_devices import scan_by_inet, scan_by_port

# Blueprint for device-related routes
bp = Blueprint("devices", __name__, url_prefix="/")


@bp.route("/devices/scan", methods=["POST"])
def scan_device():
    # Retrieve port and inet parameters from the request
    port = request.args.get('port')
    inet = request.args.get('inet')

    # If port is provided
    if port:
        # Check for invalid combinations or non-numeric port values
        if inet or not port.isdigit():
            return jsonify({"error": "Invalid parameters"}), 400
        # Scan by port and return the result
        return jsonify(scan_by_port(int(port)))

    # If inet is provided
    elif inet:
        device = scan_by_inet(inet)
        # If no device is found for the given inet
        if not device:
            return jsonify({"error": "No device found"}), 404
        return jsonify(device)

    # If neither port nor inet is provided
    else:
        return jsonify({"error": "Invalid parameters"}), 400

@bp.route("/device/<string:device_id>/ping", methods=["POST"])
def scan_by_device_id(device_id):
    # Retrieve the device with the given device_id from the database
    device: Device | None = Device.query.filter_by(id=device_id).first()

    # If the device is not found
    if not device: 
        return jsonify({"error": "Device not found"}), 404

    # Scan by inet using the device's inet value and return the result
    return jsonify(scan_by_inet(device.inet, device))


@bp.route("/devices", methods=["GET"])
def list_devices():
    # Retrieve all devices from the database
    devices = Device.query.all()

    # Serialize and return the list of devices
    return jsonify([device.serialize() for device in devices])


@bp.route("/device/<string:device_id>", methods=["DELETE"])
def remove_device(device_id):
    # Retrieve the device with the given device_id from the database
    device = Device.query.get(device_id)

    # If the device is found
    if device:
        # Delete the device from the database and commit the changes
        db.session.delete(device)
        db.session.commit()
        return jsonify({"success": True})

    # If the device is not found
    return jsonify({"success": False, "message": "Device not found"}), 404


@bp.route('/device/<string:device_id>', methods=['PATCH'])
def update_device(device_id):
    # Retrieve the device from the database
    device = Device.query.get(device_id)
    
    # If the device doesn't exist, return a 404 error
    if not device:
        return jsonify({"error": "Device not found"}), 404

    # Get the new name from the request body
    data = request.get_json()
    new_name = data.get('name')

    # Update the device's name
    device.name = new_name

    # Commit the changes to the database
    db.session.commit()

    # Return the updated device
    return jsonify(device.serialize())
