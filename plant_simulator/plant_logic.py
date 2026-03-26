import math
from typing import List

class Crutcher:
    def __init__(self, name: str, capacity: float, cycle_time: int, efficiency: float, work_hours: float, start_time: int = 0):
        self.name = name
        self.capacity = capacity
        self.cycle_time = cycle_time
        self.efficiency = efficiency
        self.work_hours = work_hours
        self.start_time = start_time
        self.batch_output = capacity * efficiency

    def get_production_at_time(self, time_min: int) -> float:
        # Check if crutcher is active (within working hours from its start_time)
        # We need to wrap this so it works across multiple days (24h = 1440m)
        time_of_day_min = time_min % 1440
        
        end_time_min = self.start_time + (self.work_hours * 60)
        
        # Check if the current time of day falls inside the working hours shift for the day
        if time_of_day_min < self.start_time or time_of_day_min > end_time_min:
            return 0.0

        # active_time tracks how long it has been running IN THIS SHIFT
        active_time = time_of_day_min - self.start_time
        
        # Production appears ONLY when cycle completes
        if active_time > 0 and active_time % self.cycle_time == 0:
            return self.batch_output
        return 0.0


class Dryer:
    def __init__(self, name: str, rate_per_hour: float, efficiency: float = 1.0, connected_silos: List[str] = None):
        self.name = name
        self.rate_per_hour = rate_per_hour
        self.efficiency = efficiency
        self.connected_silos = connected_silos if connected_silos else []

    def get_consumption_per_step(self, step_minutes: int) -> float:
        # Dryer runs continuously
        hours_per_step = step_minutes / 60.0
        return self.rate_per_hour * self.efficiency * hours_per_step


class StockTank:
    def __init__(self, count: int, capacity_per_tank: float, initial_level_ratio: float = 1.0):
        self.count = count
        self.total_capacity = count * capacity_per_tank
        self.current_level = self.total_capacity * initial_level_ratio
        
    def add(self, amount: float):
        self.current_level += amount
        if self.current_level > self.total_capacity:
            self.current_level = self.total_capacity
            
    def remove(self, amount: float) -> bool:
        # Returns True if successful, False if tank runs dry (dryer stops)
        if self.current_level - amount < 0:
            self.current_level = 0
            return False
        self.current_level -= amount
        return True

class NoodleSilo:
    def __init__(self, name: str, capacity: float, priority: int = 1, initial_level_ratio: float = 1.0):
        self.name = name
        self.capacity = capacity
        self.current_level = self.capacity * initial_level_ratio
        self.priority = priority


from typing import List

class SigmaMixer:
    def __init__(self, name: str, input_rate_mt_hr: float, efficiency: float, connected_silos: List[str]):
        self.name = name
        self.input_rate_mt_hr = input_rate_mt_hr
        self.efficiency = efficiency
        self.connected_silos = connected_silos
        
    def get_input_per_step(self, step_minutes: int) -> float:
        hours_per_step = step_minutes / 60.0
        return self.input_rate_mt_hr * hours_per_step


class Cascade:
    def __init__(self, name: str, efficiency: float, connected_mixer: str):
        self.name = name
        self.efficiency = efficiency
        self.connected_mixer = connected_mixer

