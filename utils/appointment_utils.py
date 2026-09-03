from datetime import datetime, timedelta, date, time

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def parse_time_str(time_str: str) -> time:
    """Parses 'HH:MM', 'HH:MM:SS', or '09:00 AM' into a datetime.time object."""
    time_str = time_str.strip()
    if 'AM' in time_str.upper() or 'PM' in time_str.upper():
        try:
            return datetime.strptime(time_str, "%I:%M %p").time()
        except ValueError:
            return datetime.strptime(time_str, "%h:%M %p").time()
    parts = time_str.split(":")
    return time(int(parts[0]), int(parts[1]))

def format_time_12hr(time_str: str) -> str:
    """Converts 24-hr string or 12-hr string to standardized 12-hr string (e.g., '09:00 AM')."""
    try:
        t = parse_time_str(time_str)
        return t.strftime("%I:%M %p")
    except Exception:
        return time_str

def generate_slots(start_time_str: str, end_time_str: str, duration_mins: int = 30) -> list[str]:
    """Generates a list of time slot strings in 12-hour AM/PM format (e.g. 09:00 AM) between start_time and end_time."""
    start_t = parse_time_str(start_time_str)
    end_t = parse_time_str(end_time_str)
    
    current_dt = datetime.combine(date.today(), start_t)
    end_dt = datetime.combine(date.today(), end_t)
    
    slots = []
    while current_dt + timedelta(minutes=duration_mins) <= end_dt:
        slots.append(current_dt.strftime("%I:%M %p"))
        current_dt += timedelta(minutes=duration_mins)
        
    return slots

def is_doctor_available_on_date(available_days_str: str, target_date: date | str) -> bool:
    """Checks if target_date falls on one of the doctor's available days."""
    if not available_days_str:
        return True
        
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    
    day_name = target_date.strftime("%A").lower()
    avail_list = [d.strip().lower() for d in available_days_str.split(",")]
    
    if "all" in avail_list or "everyday" in avail_list or "daily" in avail_list:
        return True
        
    return day_name in avail_list

def get_available_slots_for_doctor(doctor_info: dict, target_date: date | str, booked_times: list[str]) -> tuple[list[str], str]:
    """
    Returns (available_slots, error_message).
    booked_times is a list of booked time strings for that doctor on target_date.
    """
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        
    if target_date < date.today():
        return [], "Cannot book appointments for past dates."
        
    available_days = doctor_info.get("available_days", "")
    if not is_doctor_available_on_date(available_days, target_date):
        day_name = target_date.strftime("%A")
        return [], f"Doctor is not available on {day_name}s. Working days: {available_days}."
        
    start_t = doctor_info.get("start_time", "09:00")
    end_t = doctor_info.get("end_time", "21:00")
    duration = doctor_info.get("slot_duration", 30)
    
    all_slots = generate_slots(start_t, end_t, duration)
    
    # Standardize booked times to 12hr format for accurate matching
    booked_12hr = [format_time_12hr(bt) for bt in booked_times]
    
    # If target_date is today, filter out times that have already passed
    now = datetime.now()
    if target_date == date.today():
        valid_slots = []
        for slot in all_slots:
            slot_t = parse_time_str(slot)
            if slot_t > now.time():
                valid_slots.append(slot)
        all_slots = valid_slots
        
    # Remove booked slots
    available = [slot for slot in all_slots if slot not in booked_12hr]
    
    if not available:
        return [], "No available slots left for this date."
        
    return available, ""
