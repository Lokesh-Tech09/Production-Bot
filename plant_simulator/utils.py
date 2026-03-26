def generate_time_steps(duration_hours: float, interval_minutes: int = 30) -> list[int]:
    '''Generates a list of time steps in minutes based on duration and interval.'''
    total_minutes = int(duration_hours * 60)
    return list(range(interval_minutes, total_minutes + interval_minutes, interval_minutes))
