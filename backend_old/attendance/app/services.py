from datetime import datetime, time
from typing import List, Tuple
from .models import DayStatusEnum, PeriodStatusEnum, SessionEnum


def parse_time_str(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def calculate_day_status_from_periods(total_periods: int, present_periods: int) -> DayStatusEnum:
    if total_periods <= 0:
        return DayStatusEnum.A
    if present_periods == total_periods:
        return DayStatusEnum.P
    if present_periods == 0:
        return DayStatusEnum.A
    if present_periods >= (total_periods / 2):
        return DayStatusEnum.HD
    return DayStatusEnum.A


def calculate_session_day_status(morning_status: PeriodStatusEnum, afternoon_status: PeriodStatusEnum) -> DayStatusEnum:
    if morning_status == PeriodStatusEnum.P and afternoon_status == PeriodStatusEnum.P:
        return DayStatusEnum.P
    if (morning_status == PeriodStatusEnum.P and afternoon_status == PeriodStatusEnum.A) or (morning_status == PeriodStatusEnum.A and afternoon_status == PeriodStatusEnum.P):
        return DayStatusEnum.HD
    if morning_status == PeriodStatusEnum.A and afternoon_status == PeriodStatusEnum.A:
        return DayStatusEnum.A
    return DayStatusEnum.L if (morning_status == PeriodStatusEnum.L or afternoon_status == PeriodStatusEnum.L) else DayStatusEnum.A


def calculate_biometric_day_status(punch_time_str: str, morning_cutoff: str = "11:00", afternoon_cutoff: str = "12:00") -> Tuple[DayStatusEnum, int]:
    # returns (day_status, late_minutes)
    if not punch_time_str:
        return (DayStatusEnum.A, 0)
    punch = datetime.fromisoformat(punch_time_str)
    punch_t = punch.time()
    mcut = parse_time_str(morning_cutoff)
    acut = parse_time_str(afternoon_cutoff)
    school_start = parse_time_str("09:00")
    if punch_t <= mcut:
        # Full Day
        late = 0
        if punch_t > school_start:
            late = int((datetime.combine(punch.date(), punch_t) - datetime.combine(punch.date(), school_start)).total_seconds() / 60)
        return (DayStatusEnum.P, late)
    if punch_t >= acut:
        late = int((datetime.combine(punch.date(), punch_t) - datetime.combine(punch.date(), school_start)).total_seconds() / 60)
        return (DayStatusEnum.HD, late)
    return (DayStatusEnum.A, 0)

# Additional helpers for aggregating periods

def aggregate_periods_to_day(periods: List[PeriodStatusEnum]) -> DayStatusEnum:
    total = len(periods)
    present = sum(1 for p in periods if p == PeriodStatusEnum.P)
    return calculate_day_status_from_periods(total, present)
