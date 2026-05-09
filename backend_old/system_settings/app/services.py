"""
Service Layer for Notification Settings
"""
from models import NotificationSetting
from database import db
from datetime import datetime


class NotificationSettingsService:
    """Service for managing notification settings"""

    @staticmethod
    def get_all_settings(page: int = 1, per_page: int = 100):
        """Fetch all notification settings with pagination"""
        pagination = NotificationSetting.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        return {
            'data': [s.to_dict() for s in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
        }

    @staticmethod
    def get_setting_by_event_key(event_key: str):
        """Fetch a single notification setting by event key"""
        setting = NotificationSetting.query.filter_by(event_key=event_key).first()
        if not setting:
            return None
        return setting.to_dict()

    @staticmethod
    def create_setting(event_key: str, event_name: str, data: dict):
        """Create a new notification setting"""
        existing = NotificationSetting.query.filter_by(event_key=event_key).first()
        if existing:
            raise ValueError(f"Setting for event '{event_key}' already exists")

        setting = NotificationSetting(
            event_key=event_key,
            event_name=event_name,
            enable_email=data.get('enable_email', False),
            enable_sms=data.get('enable_sms', False),
            enable_app=data.get('enable_app', False),
            enable_whatsapp=data.get('enable_whatsapp', False),
            recipients=data.get('recipients', []),
            sms_template_id=data.get('sms_template_id'),
            whatsapp_template_id=data.get('whatsapp_template_id'),
            sample_message=data.get('sample_message'),
            updated_by=data.get('updated_by'),
        )

        db.session.add(setting)
        db.session.commit()
        return setting.to_dict()

    @staticmethod
    def update_setting(event_key: str, data: dict, updated_by: str = None):
        """Update a notification setting"""
        setting = NotificationSetting.query.filter_by(event_key=event_key).first()
        if not setting:
            raise ValueError(f"Setting for event '{event_key}' not found")

        # Update fields
        for key, value in data.items():
            if key != 'event_key' and hasattr(setting, key):
                setattr(setting, key, value)

        setting.updated_at = datetime.utcnow()
        if updated_by:
            setting.updated_by = updated_by

        db.session.commit()
        return setting.to_dict()

    @staticmethod
    def bulk_update_settings(settings_data: list, updated_by: str = None):
        """Update multiple notification settings"""
        results = []
        errors = []

        for setting_data in settings_data:
            try:
                event_key = setting_data.get('event_key')
                if not event_key:
                    errors.append({'error': 'event_key is required'})
                    continue

                updated_setting = NotificationSettingsService.update_setting(
                    event_key, setting_data, updated_by
                )
                results.append(updated_setting)
            except Exception as e:
                errors.append({'event_key': setting_data.get('event_key'), 'error': str(e)})

        return {
            'updated': results,
            'errors': errors,
            'total_updated': len(results),
            'total_errors': len(errors),
        }

    @staticmethod
    def delete_setting(event_key: str):
        """Delete a notification setting"""
        setting = NotificationSetting.query.filter_by(event_key=event_key).first()
        if not setting:
            raise ValueError(f"Setting for event '{event_key}' not found")

        db.session.delete(setting)
        db.session.commit()
        return {'message': f"Setting for event '{event_key}' deleted successfully"}

    @staticmethod
    def validate_setting(setting_data: dict) -> tuple[bool, list]:
        """Validate notification setting data"""
        errors = []

        # Check if SMS enabled without template ID
        if setting_data.get('enable_sms') and not setting_data.get('sms_template_id'):
            errors.append('SMS Template ID is required when SMS is enabled')

        # Check if WhatsApp enabled without template ID
        if setting_data.get('enable_whatsapp') and not setting_data.get('whatsapp_template_id'):
            errors.append('WhatsApp Template ID is required when WhatsApp is enabled')

        # Check if at least one channel is enabled
        if not any([
            setting_data.get('enable_email'),
            setting_data.get('enable_sms'),
            setting_data.get('enable_app'),
            setting_data.get('enable_whatsapp'),
        ]):
            errors.append('At least one notification channel must be enabled')

        return len(errors) == 0, errors

    @staticmethod
    def export_settings(format: str = 'json'):
        """Export notification settings in different formats"""
        settings = NotificationSetting.query.all()
        data = [s.to_dict() for s in settings]

        if format == 'csv':
            # CSV export logic
            return NotificationSettingsService._to_csv(data)
        elif format == 'excel':
            # Excel export logic
            return NotificationSettingsService._to_excel(data)
        else:  # Default to JSON
            return data

    @staticmethod
    def _to_csv(data):
        """Convert settings to CSV format"""
        import csv
        from io import StringIO

        output = StringIO()
        if not data:
            return output.getvalue()

        fieldnames = data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

        return output.getvalue()

    @staticmethod
    def _to_excel(data):
        """Convert settings to Excel format"""
        try:
            import openpyxl
            from openpyxl.utils.dataframe import dataframe_to_rows
            import pandas as pd

            df = pd.DataFrame(data)
            return df.to_excel(index=False)
        except ImportError:
            # Fallback to CSV if openpyxl not installed
            return NotificationSettingsService._to_csv(data)
