from pydantic import BaseModel, Field, conint
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class DayStatus(str, Enum):
    P = "P"
    A = "A"
    HD = "HD"
    L = "L"

class PeriodStatus(str, Enum):
    P = "P"
    A = "A"
    L = "L"

class SessionName(str, Enum):
    Morning = "Morning"
    Afternoon = "Afternoon"

class AttendancePeriodCreate(BaseModel):
    student_id: int
    date: date
    period_no: int
    status: PeriodStatus

class AttendanceDayCreate(BaseModel):
    student_id: int
    date: date
    day_status: DayStatus
    total_periods: Optional[int] = 0
    present_periods: Optional[int] = 0
    late_minutes: Optional[int] = 0

class SessionAttendanceCreate(BaseModel):
    student_id: int
    date: date
    session: SessionName
    status: PeriodStatus

class AttendanceSettingsSchema(BaseModel):
    day_wise: bool = True
    period_wise: bool = False
    session_wise: bool = False
    biometric: bool = False
    school_start_time: str = "09:00"
    periods_per_day: conint(ge=1, le=12) = 6

class BulkPeriodPayload(BaseModel):
    date: date
    class_id: Optional[int]
    entries: List[AttendancePeriodCreate]

class BulkDayPayload(BaseModel):
    date: date
    class_id: Optional[int]
    entries: List[AttendanceDayCreate]

class ReportFilter(BaseModel):
    start_date: date
    end_date: date
    class_id: Optional[int]
    student_id: Optional[int]
