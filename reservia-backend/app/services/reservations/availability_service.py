from datetime import date, datetime, time, timedelta


def add_minutes(t: time, minutes: int) -> time:
    combined = datetime.combine(date.today(), t) + timedelta(minutes=minutes)
    return combined.time()


def generate_slots(
    window_start: time, window_end: time, slot_minutes: int
) -> list[tuple[time, time]]:
    slots: list[tuple[time, time]] = []
    current_start = window_start

    while True:
        current_end = add_minutes(current_start, slot_minutes)
        if current_end > window_end:
            break
        slots.append((current_start, current_end))
        current_start = current_end

    return slots


def _ranges_overlap(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    return start_a < end_b and start_b < end_a


def mark_availability(
    slots: list[tuple[time, time]], booked_ranges: list[tuple[time, time]]
) -> list[dict]:
    result = []
    for slot_start, slot_end in slots:
        disponible = True
        for booked_start, booked_end in booked_ranges:
            if _ranges_overlap(slot_start, slot_end, booked_start, booked_end):
                disponible = False
                break
        result.append(
            {"hora_inicio": slot_start, "hora_fin": slot_end, "disponible": disponible}
        )
    return result


def is_aligned(hora_inicio: time, window_start: time, slot_minutes: int) -> bool:
    start_dt = datetime.combine(date.today(), window_start)
    target_dt = datetime.combine(date.today(), hora_inicio)
    delta_minutes = (target_dt - start_dt).total_seconds() / 60

    if delta_minutes < 0:
        return False

    return delta_minutes % slot_minutes == 0