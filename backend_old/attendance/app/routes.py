from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from . import models, schemas, services
from datetime import date

router = APIRouter(prefix="/api/attendance", tags=["attendance"]) 

@router.get("/settings", response_model=schemas.AttendanceSettingsSchema)
def get_settings(db: Session = Depends(get_db)):
    s = db.query(models.AttendanceSettings).first()
    if not s:
        # return defaults
        return schemas.AttendanceSettingsSchema()
    return schemas.AttendanceSettingsSchema(
        day_wise=bool(s.day_wise),
        period_wise=bool(s.period_wise),
        session_wise=bool(s.session_wise),
        biometric=bool(s.biometric),
        school_start_time=s.school_start_time,
        periods_per_day=s.periods_per_day
    )

@router.post("/settings", response_model=schemas.AttendanceSettingsSchema)
def save_settings(payload: schemas.AttendanceSettingsSchema, db: Session = Depends(get_db)):
    s = db.query(models.AttendanceSettings).first()
    if not s:
        s = models.AttendanceSettings()
        db.add(s)
    s.day_wise = 1 if payload.day_wise else 0
    s.period_wise = 1 if payload.period_wise else 0
    s.session_wise = 1 if payload.session_wise else 0
    s.biometric = 1 if payload.biometric else 0
    s.school_start_time = payload.school_start_time
    s.periods_per_day = payload.periods_per_day
    db.commit()
    return payload

@router.post("/mark/periods")
def mark_periods(payload: schemas.BulkPeriodPayload, db: Session = Depends(get_db)):
    # Simplified: insert or update period records and aggregate
    for entry in payload.entries:
        obj = models.AttendancePeriods(
            student_id=entry.student_id,
            date=entry.date,
            period_no=entry.period_no,
            status=entry.status
        )
        db.add(obj)
    db.commit()
    # aggregation would be triggered in a real system
    return {"status":"ok"}

@router.post("/mark/days")
def mark_days(payload: schemas.BulkDayPayload, db: Session = Depends(get_db)):
    for entry in payload.entries:
        obj = models.AttendanceDays(
            student_id=entry.student_id,
            date=entry.date,
            day_status=entry.day_status,
            total_periods=entry.total_periods,
            present_periods=entry.present_periods,
            late_minutes=entry.late_minutes
        )
        db.add(obj)
    db.commit()
    return {"status":"ok"}

@router.post("/mark/session")
def mark_session(payload: schemas.SessionAttendanceCreate, db: Session = Depends(get_db)):
    obj = models.SessionAttendance(
        student_id=payload.student_id,
        date=payload.date,
        session=payload.session,
        status=payload.status
    )
    db.add(obj)
    db.commit()
    return {"status":"ok"}

@router.get("/report/daily")
def daily_report(report: schemas.ReportFilter = Depends(), db: Session = Depends(get_db)):
    # basic daily report: join attendance_days
    rows = db.query(models.AttendanceDays).filter(models.AttendanceDays.date >= report.start_date, models.AttendanceDays.date <= report.end_date).all()
    return rows

@router.get("/report/monthly")
def monthly_report(start_date: date, end_date: date, db: Session = Depends(get_db)):
    rows = db.query(models.AttendanceDays).filter(models.AttendanceDays.date >= start_date, models.AttendanceDays.date <= end_date).all()
    return rows

@router.get("/report/late")
def late_report(start_date: date, end_date: date, db: Session = Depends(get_db)):
    rows = db.query(models.AttendanceDays).filter(models.AttendanceDays.late_minutes > 0, models.AttendanceDays.date >= start_date, models.AttendanceDays.date <= end_date).all()
    return rows

@router.get("/report/halfday")
def halfday_report(start_date: date, end_date: date, db: Session = Depends(get_db)):
    rows = db.query(models.AttendanceDays).filter(models.AttendanceDays.day_status == 'HD', models.AttendanceDays.date >= start_date, models.AttendanceDays.date <= end_date).all()
    return rows
