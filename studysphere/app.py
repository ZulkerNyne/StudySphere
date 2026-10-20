from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        from studysphere.config import Config
        app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    from studysphere.routes.health import health_bp
    from studysphere.routes.auth import auth_bp
    from studysphere.routes.courses import courses_bp
    from studysphere.routes.enrollment import enrollment_bp
    from studysphere.routes.schedule import schedule_bp
    from studysphere.routes.advisor import advisor_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(enrollment_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(advisor_bp)

    with app.app_context():
        db.create_all()

    return app
