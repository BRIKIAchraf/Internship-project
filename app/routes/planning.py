from flask import Blueprint, jsonify, request
from app import db
from app.models.planning import Planning, DayTimeBlock
from app.models.user import User

bp = Blueprint("planning", __name__, url_prefix="/planning")

@bp.route('/', methods=['POST'])
def create_planning():
    data = request.get_json()
    planning = Planning(
        title=data.get('title'),
        description=data.get('description'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        user_id=data.get('user_id')
    )

    time_blocks_data = data.get('time_blocks', [])
    for block in time_blocks_data:
        day_time_block = DayTimeBlock(
            day_of_week=block.get('day_of_week'),
            start_time=block.get('start_time'),
            end_time=block.get('end_time')
        )
        planning.time_blocks.append(day_time_block)

    db.session.add(planning)
    db.session.commit()
    return jsonify(planning.serialize()), 201

@bp.route('/', methods=['GET'])
def get_plannings():
    plannings = Planning.query.all()
    return jsonify([planning.serialize() for planning in plannings])

@bp.route('/<int:planning_id>', methods=['PATCH'])
def update_planning(planning_id):
    planning = Planning.query.get_or_404(planning_id)
    data = request.get_json()
    
    # Update the basic details of the planning
    for key in ['title', 'description', 'start_date', 'end_date', 'user_id']:
        if key in data:
            setattr(planning, key, data[key])
    
    # Update time blocks
    if 'time_blocks' in data:
        # Clear existing time blocks first
        planning.time_blocks = []
        for block in data['time_blocks']:
            new_block = DayTimeBlock(
                day_of_week=block['day_of_week'],
                start_time=block['start_time'],
                end_time=block['end_time']
            )
            planning.time_blocks.append(new_block)

    db.session.commit()
    return jsonify(planning.serialize())

@bp.route('/<int:planning_id>', methods=['DELETE'])
def delete_planning(planning_id):
    planning = Planning.query.get_or_404(planning_id)
    db.session.delete(planning)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/<int:planning_id>/assign_user/<string:user_id>', methods=['POST'])
def assign_user_to_planning(planning_id, user_id):
    planning = Planning.query.get_or_404(planning_id)
    user = User.query.filter_by(user_id=user_id).first_or_404()
    planning.user_id = user.uid
    db.session.commit()
    return jsonify(planning.serialize())
