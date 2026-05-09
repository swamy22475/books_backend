"""
Application Factory and Main Entry Point
"""
from flask import Flask
from flask_cors import CORS
from routes import notification_bp
from database import db
from config import Config


def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Configuration
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register blueprints
    app.register_blueprint(notification_bp)

    # Create tables
    with app.app_context():
        db.create_all()

        # Seed initial data if tables are empty
        from models import NotificationSetting
        if NotificationSetting.query.count() == 0:
            seed_notification_settings()

    return app


def seed_notification_settings():
    """Seed initial notification settings"""
    from database import db
    from models import NotificationSetting

    events = [
        'Online Admission Fees Submission',
        'Behaviour Incident Assigned',
        'CBSE Exam Result',
        'CBSE Exam Marksheet PDF',
        'Online Course Guest User Sign Up',
        'Online Course Purchase for Guest User',
        'Email PDF Exam Marksheet',
        'Student Apply Leave',
        'Online Admission Fees Processing',
        'Fee Processing',
        'Staff Login Credential',
        'Student Login Credential',
        'Online Course Purchase',
        'Online Course Publish',
        'Student Admission',
        'Forgot Password',
        'Exam Result',
        'Fee Submission',
        'Student Absent Attendance',
        'Homework',
        'Fees Reminder',
        'Zoom Live Meetings Start',
        'Online Examination Publish Exam',
        'Online Examination Publish Result',
        'Zoom Live Classes',
        'Zoom Live Meetings',
        'Gmeet Live Meetings',
        'Gmeet Live Classes',
        'Gmeet Live Meeting Start',
        'Gmeet Live Classes Start',
        'Student Present Attendance',
        'Homework Evaluation',
        'Staff Present Attendance',
        'Staff Absent Attendance',
    ]

    samples = {
        'online admission fees submission': 'Dear {{student_name}}, your admission fee of {{amount}} has been submitted. Your admission number is {{admission_no}}.',
        'behaviour incident assigned': 'Hello {{student_name}}, a behavior incident has been reported by {{staff_name}} on {{date}}. Please contact your guardian.',
        'student admission': 'Congratulations {{student_name}}! You have been admitted to {{class}} {{section}}. Admission No: {{admission_no}}',
        'exam result': 'Dear {{student_name}}, your {{subject}} exam result is {{mark}}. For admission number {{admission_no}}, {{date}}.',
        'student absent attendance': '{{student_name}} was marked absent on {{date}} for {{subject}}. Please contact the school if this is incorrect.',
        'student present attendance': '{{student_name}} was marked present on {{date}} for {{subject}}.',
    }

    for i, event_name in enumerate(events):
        event_key = event_name.lower().replace(' ', '_')

        setting = NotificationSetting(
            event_key=event_key,
            event_name=event_name,
            enable_email=i % 2 == 0,
            enable_sms=i % 3 == 0,
            enable_app=i % 4 == 0,
            enable_whatsapp=i % 5 == 0,
            recipients=['student'] if i % 2 == 0 else ['student', 'guardian'],
            sms_template_id=f'TMPLT_SMS_{str(i).zfill(3)}' if i % 2 == 0 else None,
            whatsapp_template_id=f'TMPLT_WA_{str(i).zfill(3)}' if i % 3 == 0 else None,
            sample_message=samples.get(event_name.lower()),
        )
        db.session.add(setting)

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
