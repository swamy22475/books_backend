"""
API Routes for Notification Settings
"""
from flask import Blueprint, request, jsonify, send_file
from schemas import (
    NotificationSettingResponse,
    NotificationSettingUpdate,
    NotificationSettingBulkUpdate,
)
from services import NotificationSettingsService
from functools import wraps
import io

# Create blueprint
notification_bp = Blueprint('notification_settings', __name__, url_prefix='/api/system-settings')


def require_auth(f):
    """Decorator for authentication (placeholder)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Add your authentication logic here
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """Decorator for admin authorization (placeholder)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Add your admin check logic here
        return f(*args, **kwargs)
    return decorated


@notification_bp.route('/notification-settings', methods=['GET'])
@require_auth
def get_notification_settings():
    """
    GET /api/system-settings/notification-settings
    Fetch all notification settings
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)

        result = NotificationSettingsService.get_all_settings(page, per_page)

        return jsonify({
            'success': True,
            'data': result['data'],
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages'],
            },
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@notification_bp.route('/notification-settings/<event_key>', methods=['GET'])
@require_auth
def get_notification_setting(event_key):
    """
    GET /api/system-settings/notification-settings/{event_key}
    Fetch a single notification setting
    """
    try:
        setting = NotificationSettingsService.get_setting_by_event_key(event_key)

        if not setting:
            return jsonify({'success': False, 'error': 'Setting not found'}), 404

        return jsonify({'success': True, 'data': setting}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@notification_bp.route('/notification-settings', methods=['POST'])
@require_admin
def create_or_bulk_update_notification_settings():
    """
    POST /api/system-settings/notification-settings
    Create or bulk update notification settings
    """
    try:
        data = request.get_json()

        # Check if bulk update (array of settings)
        if isinstance(data, dict) and 'settings' in data:
            # Bulk update
            results = NotificationSettingsService.bulk_update_settings(
                data['settings'],
                updated_by=request.headers.get('X-User-ID', 'API')
            )
            return jsonify({'success': True, 'data': results}), 200

        # Single create/update
        event_key = data.get('event_key')
        if not event_key:
            return jsonify({'success': False, 'error': 'event_key is required'}), 400

        # Check if setting exists
        existing = NotificationSettingsService.get_setting_by_event_key(event_key)

        if existing:
            # Update
            result = NotificationSettingsService.update_setting(
                event_key,
                data,
                updated_by=request.headers.get('X-User-ID', 'API')
            )
        else:
            # Create
            result = NotificationSettingsService.create_setting(
                event_key,
                data.get('event_name', event_key),
                data,
            )

        return jsonify({'success': True, 'data': result}), 201

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@notification_bp.route('/notification-settings', methods=['PUT'])
@require_admin
def update_notification_setting():
    """
    PUT /api/system-settings/notification-settings
    Update a notification setting
    """
    try:
        data = request.get_json()
        event_key = data.get('event_key')

        if not event_key:
            return jsonify({'success': False, 'error': 'event_key is required'}), 400

        # Validate setting
        is_valid, errors = NotificationSettingsService.validate_setting(data)
        if not is_valid:
            return jsonify({'success': False, 'errors': errors}), 400

        result = NotificationSettingsService.update_setting(
            event_key,
            data,
            updated_by=request.headers.get('X-User-ID', 'API')
        )

        return jsonify({'success': True, 'data': result}), 200

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@notification_bp.route('/notification-settings/<event_key>', methods=['DELETE'])
@require_admin
def delete_notification_setting(event_key):
    """
    DELETE /api/system-settings/notification-settings/{event_key}
    Delete a notification setting
    """
    try:
        result = NotificationSettingsService.delete_setting(event_key)
        return jsonify({'success': True, 'message': result['message']}), 200

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@notification_bp.route('/notification-settings/export', methods=['GET'])
@require_auth
def export_notification_settings():
    """
    GET /api/system-settings/notification-settings/export?format=csv|excel|json
    Export notification settings
    """
    try:
        format = request.args.get('format', 'json')

        if format not in ['csv', 'excel', 'json']:
            return jsonify({'success': False, 'error': 'Invalid format'}), 400

        data = NotificationSettingsService.export_settings(format)

        if format == 'csv':
            return send_file(
                io.BytesIO(data.encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name='notification-settings.csv'
            )
        elif format == 'excel':
            return send_file(
                data,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='notification-settings.xlsx'
            )
        else:  # JSON
            return jsonify({'success': True, 'data': data}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@notification_bp.route('/notification-templates', methods=['GET'])
@require_auth
def get_notification_templates():
    """
    GET /api/system-settings/notification-templates?channel=sms|whatsapp|email
    Get available template IDs for a channel
    """
    try:
        channel = request.args.get('channel', 'sms')

        # Mock template data - replace with actual template service
        templates = {
            'sms': [
                {'id': 'TMPLT_SMS_001', 'name': 'Student Admission'},
                {'id': 'TMPLT_SMS_002', 'name': 'Fee Submission'},
                {'id': 'TMPLT_SMS_003', 'name': 'Exam Result'},
                {'id': 'TMPLT_SMS_004', 'name': 'Attendance'},
                {'id': 'TMPLT_SMS_005', 'name': 'Homework'},
            ],
            'whatsapp': [
                {'id': 'TMPLT_WA_001', 'name': 'Student Admission'},
                {'id': 'TMPLT_WA_002', 'name': 'Fee Submission'},
                {'id': 'TMPLT_WA_003', 'name': 'Exam Result'},
                {'id': 'TMPLT_WA_004', 'name': 'Attendance'},
                {'id': 'TMPLT_WA_005', 'name': 'Homework'},
            ],
            'email': [
                {'id': 'TMPLT_EMAIL_001', 'name': 'Student Admission'},
                {'id': 'TMPLT_EMAIL_002', 'name': 'Fee Submission'},
                {'id': 'TMPLT_EMAIL_003', 'name': 'Exam Result'},
                {'id': 'TMPLT_EMAIL_004', 'name': 'Attendance'},
                {'id': 'TMPLT_EMAIL_005', 'name': 'Homework'},
            ],
        }

        return jsonify({
            'success': True,
            'channel': channel,
            'templates': templates.get(channel, []),
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@notification_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'notification-settings'}), 200
