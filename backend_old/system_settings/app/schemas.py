"""
Schemas for API Request/Response Validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class NotificationSettingUpdate(BaseModel):
    """Schema for updating notification settings"""
    event_key: str
    enable_email: Optional[bool] = None
    enable_sms: Optional[bool] = None
    enable_app: Optional[bool] = None
    enable_whatsapp: Optional[bool] = None
    recipients: Optional[List[str]] = None
    sms_template_id: Optional[str] = None
    whatsapp_template_id: Optional[str] = None
    sample_message: Optional[str] = None


class NotificationSettingResponse(BaseModel):
    """Schema for notification settings response"""
    id: int
    event_key: str
    event_name: str
    enable_email: bool
    enable_sms: bool
    enable_app: bool
    enable_whatsapp: bool
    recipients: List[str]
    sms_template_id: Optional[str] = None
    whatsapp_template_id: Optional[str] = None
    sample_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class NotificationSettingBulkUpdate(BaseModel):
    """Schema for bulk update of notification settings"""
    settings: List[NotificationSettingUpdate]


class NotificationSettingsListResponse(BaseModel):
    """Schema for list response"""
    data: List[NotificationSettingResponse]
    total: int
    page: int = 1
    per_page: int = 100
