# app/blueprints/department.py
from flask import Blueprint, jsonify, request
from app import db
from app.models.department import Department, user_departments
from app.models.user import User

bp = Blueprint("department", __name__, url_prefix="/department")

@bp.route('/', methods=['POST'])
def create_department():
    data = request.get_json()
    department = Department(name=data.get('name'), description=data.get('description'))
    db.session.add(department)
    db.session.commit()
    return jsonify(department.serialize()), 201

@bp.route('/', methods=['GET'])
def get_departments():
    departments = Department.query.all()
    return jsonify([department.serialize() for department in departments])

@bp.route('/<int:department_id>', methods=['PATCH'])
def update_department(department_id):
    department = Department.query.get_or_404(department_id)
    data = request.get_json()
    department.name = data.get('name', department.name)
    department.description = data.get('description', department.description)
    db.session.commit()
    return jsonify(department.serialize())

@bp.route('/<int:department_id>', methods=['DELETE'])
def delete_department(department_id):
    department = Department.query.get_or_404(department_id)
    db.session.delete(department)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/<int:department_id>/assign_user/<string:user_id>', methods=['POST'])
def assign_user_to_department(department_id, user_id):
    department = Department.query.get_or_404(department_id)
    user = User.query.filter_by(user_id=user_id).first_or_404()
    if user not in department.users:
        department.users.append(user)
        db.session.commit()
    return jsonify(department.serialize())

@bp.route('/<int:department_id>/remove_user/<string:user_id>', methods=['POST'])
def remove_user_from_department(department_id, user_id):
    department = Department.query.get_or_404(department_id)
    user = User.query.filter_by(user_id=user_id).first_or_404()
    if user in department.users:
        department.users.remove(user)
        db.session.commit()
    return jsonify(department.serialize())
