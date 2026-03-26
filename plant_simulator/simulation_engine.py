import pandas as pd
from typing import List
from plant_logic import Crutcher, Dryer, StockTank, NoodleSilo, SigmaMixer, Cascade

def run_simulation(
    crutchers: List[Crutcher], 
    dryers: List[Dryer], 
    stock_tank: StockTank, 
    silos: List[NoodleSilo],
    mixers: List[SigmaMixer],
    cascades: List[Cascade],
    duration_hours: float, 
    step_minutes: int = 30,
    dryer_restart_threshold_ratio: float = 0.9
) -> tuple[pd.DataFrame, dict]:
    '''
    Runs the plant simulation and returns a DataFrame of the results and a dictionary of summary metrics.
    '''
    time_steps = []
    
    # Initialize data structures for results
    results = {
        "TIME (MIN)": []
    }
    
    for c in crutchers:
        results[f"{c.name} Production (MT)"] = []
        
    results["Tank Level (MT)"] = []
    
    for d in dryers:
        results[f"{d.name} (MT/HR)"] = []
        results[f"{d.name} Output (MT)"] = []
        
    results["Total Dryer Output (MT)"] = []
    
    # Sort silos by priority (lower number = higher priority)
    silos_sorted = sorted(silos, key=lambda s: s.priority)
    for s in silos:
        results[f"{s.name} (MT)"] = []
        
    for m in mixers:
        results[f"{m.name} Output (MT)"] = []
        
    for c in cascades:
        results[f"{c.name} Cumulative (MT)"] = []
        
    # Metrics
    total_production = 0.0
    total_consumption = 0.0
    min_tank_level = stock_tank.total_capacity
    dryer_stop_events = []
    dryer_start_events = []
    
    total_steps = int((duration_hours * 60) / step_minutes)
    
    current_time = 0
    dryers_active = True
    
    for step in range(1, total_steps + 1):
        current_time += step_minutes
        results["TIME (MIN)"].append(current_time)
        
        # 1. Calculate Crutcher Production
        step_production = 0.0
        for c in crutchers:
            prod = c.get_production_at_time(current_time)
            results[f"{c.name} Production (MT)"].append(prod)
            step_production += prod
            total_production += prod
            
        # 2. Add to Tank
        stock_tank.add(step_production)
        
        # 3. Handle Dryer State
        # Check if we should restart dryers
        if not dryers_active and stock_tank.current_level >= (stock_tank.total_capacity * dryer_restart_threshold_ratio):
            dryers_active = True
            dryer_start_events.append(current_time)

        # 4. Calculate Consumption & Remove from Tank
        step_consumption = 0.0
        
        # We need to know what the target consumption WOULD be if fully active
        target_consumption = 0.0
        for d in dryers:
            target_consumption += d.get_consumption_per_step(step_minutes)

        if dryers_active:
            # Check if tank has enough for full requested consumption
            if stock_tank.current_level >= target_consumption:
                stock_tank.current_level -= target_consumption
                total_consumption += target_consumption
                for d in dryers:
                    results[f"{d.name} (MT/HR)"].append(d.rate_per_hour)
            else:
                # Tank ran dry THIS step.
                # Consume whatever was left in the tank.
                actual_consumption = stock_tank.current_level
                total_consumption += actual_consumption
                stock_tank.current_level = 0
                
                # Dryers ran partially. We record the equivalent rate they ran at for this step.
                ratio = actual_consumption / target_consumption if target_consumption > 0 else 0
                for d in dryers:
                    results[f"{d.name} (MT/HR)"].append(d.rate_per_hour * ratio)
                
                # Stop dryers for future steps
                dryers_active = False
                dryer_stop_events.append(current_time)
        else:
            # Dryers are currently stopped. They consume 0.
            for d in dryers:
                results[f"{d.name} (MT/HR)"].append(0.0)
                    
        # 5. Record Tank Level
        results["Tank Level (MT)"].append(stock_tank.current_level)
        
        if stock_tank.current_level < min_tank_level:
            min_tank_level = stock_tank.current_level

        # 6. Dryer Output & Silo Distribution (Fill Silos BEFORE Mixers have pulled)
        step_dryer_output = 0.0
        for d in dryers:
            # We already calculated the rate it ran at for this step in step 4.
            # Convert rate (MT/HR) back to step consumption and multiply by efficiency
            # To get actual consumption, we use the registered rate in the results dict
            actual_rate = results[f"{d.name} (MT/HR)"][-1]
            actual_consumption = actual_rate * (step_minutes / 60.0)
            d_output = actual_consumption * d.efficiency
            results[f"{d.name} Output (MT)"].append(d_output)
            step_dryer_output += d_output
            
            # Distribute THIS dryer's output to its connected silos (in priority order)
            connected_silos = [s for s in silos_sorted if s.name in d.connected_silos]
            remaining_d_material = d_output
            
            for s in connected_silos:
                available_space = s.capacity - s.current_level
                if available_space > 0 and remaining_d_material > 0:
                    fill = min(remaining_d_material, available_space)
                    s.current_level += fill
                    remaining_d_material -= fill

        results["Total Dryer Output (MT)"].append(step_dryer_output)

        # 7. Run Sigma Mixers (Pull from current silo levels limit: must be full input)
        mixer_outputs = {} # store outputs to feed cascades
        for m in mixers:
            # Find the connected silo objects
            connected_silos = [s for s in silos_sorted if s.name in m.connected_silos]
            
            mixer_input_req = m.get_input_per_step(step_minutes)
            actual_pulled = 0.0
            
            # Mixers stops if total available in connected silos < requirement
            total_available = sum(s.current_level for s in connected_silos)
            
            if total_available >= mixer_input_req:
                actual_pulled = mixer_input_req
                remaining_to_pull = mixer_input_req
                for s in connected_silos:
                    if remaining_to_pull <= 0:
                        break
                    pull_from_this = min(s.current_level, remaining_to_pull)
                    s.current_level -= pull_from_this
                    remaining_to_pull -= pull_from_this
            else:
                actual_pulled = 0.0
            
            mixer_output = actual_pulled * m.efficiency
            mixer_outputs[m.name] = mixer_output
            results[f"{m.name} Output (MT)"].append(mixer_output)

        for s in silos:
            results[f"{s.name} (MT)"].append(s.current_level)

        # 8. Run Cascades
        for c in cascades:
            connected_mixer_output = mixer_outputs.get(c.connected_mixer, 0.0)
            cascade_output = connected_mixer_output * c.efficiency
            
            # The previous step's cumulative value or 0 if first step
            prev_cumulative = results[f"{c.name} Cumulative (MT)"][-1] if len(results[f"{c.name} Cumulative (MT)"]) > 0 else 0.0
            results[f"{c.name} Cumulative (MT)"].append(prev_cumulative + cascade_output)


    df = pd.DataFrame(results)
    
    metrics = {
        "Total Production (MT)": round(total_production, 2),
        "Total Dryer Consumption (MT)": round(total_consumption, 2),
        "Minimum Tank Level (MT)": round(min_tank_level, 2),
        "Dryer Stop Events": dryer_stop_events,
        "Dryer Start Events": dryer_start_events
    }

    return df, metrics
