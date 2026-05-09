"""
Database Models for System Settings
"""
from database import db
from datetime import datetime


class NotificationSetting(db.Model):
    """Notification Settings Model"""
    __tablename__ = 'notification_settings'

    id = db.Column(db.Integer, primary_key=True)
    event_key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    event_name = db.Column(db.String(255), nullable=False, index=True)
    
    enable_email = db.Column(db.Boolean, default=False)
    enable_sms = db.Column(db.Boolean, default=False)
    enable_app = db.Column(db.Boolean, default=False)
    enable_whatsapp = db.Column(db.Boolean, default=False)
    
    recipients = db.Column(db.JSON, default=lambda: [])
    
    sms_template_id = db.Column(db.String(255), nullable=True)
    whatsapp_template_id = db.Column(db.String(255), nullable=True)
    sample_message = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'event_key': self.event_key,
            'event_name': self.event_name,
            'enable_email': self.enable_email,
            'enable_sms': self.enable_sms,
            'enable_app': self.enable_app,
            'enable_whatsapp': self.enable_whatsapp,
            'recipients': self.recipients or [],
            'sms_template_id': self.sms_template_id,
            'whatsapp_template_id': self.whatsapp_template_id,
            'sample_message': self.sample_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
        }
