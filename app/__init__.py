from flask import Flask, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from datetime import datetime, date
from flask_cors import CORS
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    class UpdatedJSONProvider(json.provider.DefaultJSONProvider):
        def default(self, o):
            if isinstance(o, date) or isinstance(o, datetime):
                return o.isoformat()
            return super().default(o)

    app.json = UpdatedJSONProvider(app)

    from app.routes import util, devices, users, fingers, attendances # Import routes
    db.init_app(app)

    with app.app_context():
        print('creating tables...')
        db.create_all()  # Create SQLite database tables

    # Custom error handler
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error=str(e)), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify(error=str(e)), 500


    app.register_blueprint(util.bp)
    app.register_blueprint(devices.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(fingers.bp)
    app.register_blueprint(attendances.bp)
    for bp in app.blueprints.values():
        for err, handler in bp.error_handler_spec.items():
            for code, view in handler.items():
                app.error_handler_spec[err][code] = view

    return app
