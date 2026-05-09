from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class DayStatusEnum(str, enum.Enum):
    P = "P"
    A = "A"
    HD = "HD"
    L = "L"

class PeriodStatusEnum(str, enum.Enum):
    P = "P"
    A = "A"
    L = "L"

class SessionEnum(str, enum.Enum):
    Morning = "Morning"
    Afternoon = "Afternoon"

class AttendanceDays(Base):
    __tablename__ = "attendance_days"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    date = Column(Date, index=True)
    day_status = Column(Enum(DayStatusEnum), nullable=False)
    total_periods = Column(Integer, default=0)
    present_periods = Column(Integer, default=0)
    late_minutes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AttendancePeriods(Base):
    __tablename__ = "attendance_periods"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    date = Column(Date, index=True)
    period_no = Column(Integer)
    status = Column(Enum(PeriodStatusEnum), nullable=False)

class SessionAttendance(Base):
    __tablename__ = "session_attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    date = Column(Date, index=True)
    session = Column(Enum(SessionEnum), nullable=False)
    status = Column(Enum(PeriodStatusEnum), nullable=False)

# Simple settings table for admin toggles
class AttendanceSettings(Base):
    __tablename__ = "attendance_settings"
    id = Column(Integer, primary_key=True, index=True)
    day_wise = Column(Integer, default=1)  # 0/1
    period_wise = Column(Integer, default=0)
    session_wise = Column(Integer, default=0)
    biometric = Column(Integer, default=0)
    school_start_time = Column(String(5), default="09:00")
    periods_per_day = Column(Integer, default=6)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
