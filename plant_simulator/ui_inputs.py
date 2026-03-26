import streamlit as st

def get_crutcher_inputs():
    st.sidebar.header("Crutcher Settings")
    num_crutchers = st.sidebar.number_input("Number of Crutchers", min_value=1, max_value=10, value=3, step=1)
    crutchers_data = []
    
    for i in range(num_crutchers):
        with st.sidebar.expander(f"C{i+1} Settings", expanded=(i==0)):
            name = st.text_input(f"C{i+1} Name", value=f"C{i+1}")
            capacity = st.number_input(f"C{i+1} Capacity (MT)", min_value=0.1, value=4.0, step=0.5)
            cycle_time = st.number_input(f"C{i+1} Cycle Time (minutes)", min_value=10, value=90, step=10)
            efficiency = st.slider(f"C{i+1} Efficiency", min_value=0.1, max_value=1.0, value=0.95, step=0.01)
            work_hours = st.number_input(f"C{i+1} Working Hours/Day", min_value=1.0, max_value=24.0, value=12.0)
            start_time = st.number_input(f"C{i+1} Start Time (minutes)", min_value=0, value=0, step=30)
            
            crutchers_data.append({
                "name": name,
                "capacity": capacity,
                "cycle_time": cycle_time,
                "efficiency": efficiency,
                "work_hours": work_hours,
                "start_time": start_time
            })
    return crutchers_data

def get_dryer_inputs(silo_names):
    st.sidebar.header("Dryer Settings")
    num_dryers = st.sidebar.number_input("Number of Dryers", min_value=1, max_value=10, value=2, step=1)
    dryers_data = []

    default_names = ["Dryer 1", "Dryer 3", "Dryer 4", "Dryer 5"]
    default_rates = [5.8, 5.8, 5.8, 5.8]
    default_effs = [0.85, 0.85, 0.85, 0.85]

    for i in range(num_dryers):
         with st.sidebar.expander(f"Dryer {i+1} Settings", expanded=(i==0)):
            default_name = default_names[i] if i < len(default_names) else f"Dryer {i+1}"
            default_rate = default_rates[i] if i < len(default_rates) else 3.825
            default_eff = default_effs[i] if i < len(default_effs) else 1.0

            name = st.text_input(f"Dryer {i+1} Name", value=default_name, key=f"dryer_name_{i}")
            rate = st.number_input(f"{name} Input Rate (MT/HR)", min_value=0.1, value=default_rate, step=0.1, key=f"dryer_rate_{i}")
            efficiency = st.slider(f"{name} Efficiency", min_value=0.1, max_value=1.0, value=default_eff, step=0.05, key=f"dryer_eff_{i}")
            
            # Default to all silos
            connected_silos = st.multiselect(f"{name} Connected Silos", options=silo_names, default=silo_names, key=f"dryer_silos_{i}")
            
            dryers_data.append({
                "name": name,
                "rate": rate,
                "efficiency": efficiency,
                "connected_silos": connected_silos
            })
    return dryers_data
    
def get_tank_inputs():
    st.sidebar.header("Tank Settings")
    num_tanks = st.sidebar.number_input("Number of Tanks", min_value=1, value=2, step=1)
    capacity = st.sidebar.number_input("Capacity per Tank (MT)", min_value=1.0, value=20.0, step=5.0)
    initial_level = st.sidebar.slider("Initial Tank Level (%)", min_value=0, max_value=100, value=100, step=5)
    
    return {
        "num_tanks": num_tanks,
        "capacity_per_tank": capacity,
        "initial_level_ratio": initial_level / 100.0
    }

def get_simulation_inputs():
    st.sidebar.header("Simulation Settings")
    duration_hours = st.sidebar.number_input("Simulation Duration (Hours)", min_value=1.0, max_value=720.0, value=72.0, step=12.0)
    step_minutes = st.sidebar.selectbox("Time Step (Minutes)", options=[10, 15, 30, 60], index=2)
    dryer_restart_threshold = st.sidebar.slider("Dryer Restart Threshold (%)", min_value=10, max_value=100, value=90, step=5)
    return {
        "duration_hours": duration_hours,
        "step_minutes": step_minutes,
        "dryer_restart_threshold": dryer_restart_threshold / 100.0
    }

def get_silo_inputs():
    st.sidebar.header("Noodle Silo Settings")
    num_silos = st.sidebar.number_input("Number of Silos", min_value=1, max_value=10, value=4, step=1)
    initial_level = st.sidebar.slider("Initial Silo Level (%)", min_value=0, max_value=100, value=100, step=5)
    silos_data = []
    
    # Default as per requirement
    default_configs = [
        {"name": "Main Silo", "capacity": 40.0, "priority": 1},
        {"name": "Silo 1", "capacity": 3.0, "priority": 2},
        {"name": "Silo 2", "capacity": 17.0, "priority": 3},
        {"name": "Silo 3", "capacity": 17.0, "priority": 4}
    ]

    for i in range(num_silos):
         with st.sidebar.expander(f"Silo {i+1} Settings", expanded=(i==0)):
            default_name = default_configs[i]["name"] if i < len(default_configs) else f"Silo {i+1}"
            default_cap = default_configs[i]["capacity"] if i < len(default_configs) else 10.0
            default_pri = default_configs[i]["priority"] if i < len(default_configs) else i+1

            name = st.text_input(f"Silo {i+1} Name", value=default_name, key=f"silo_name_{i}")
            capacity = st.number_input(f"{name} Capacity (MT)", min_value=1.0, value=default_cap, step=1.0, key=f"silo_cap_{i}")
            priority = st.number_input(f"{name} Priority (Lower = Higher Priority)", min_value=1, value=default_pri, step=1, key=f"silo_pri_{i}")
            
            silos_data.append({
                "name": name,
                "capacity": capacity,
                "priority": priority,
                "initial_level_ratio": initial_level / 100.0
            })
    return silos_data


def get_mixer_inputs(silo_names):
    st.sidebar.header("Sigma Mixer Settings")
    num_mixers = st.sidebar.number_input("Number of Mixers", min_value=1, max_value=10, value=3, step=1)
    mixers_data = []

    default_mixers = [
        {"rate": 1.908, "eff": 0.8},
        {"rate": 3.84, "eff": 0.8},
        {"rate": 3.84, "eff": 0.8}
    ]

    for i in range(num_mixers):
         with st.sidebar.expander(f"Mixer {i+1} Settings", expanded=(i==0)):
            default_rate = default_mixers[i]["rate"] if i < len(default_mixers) else 5.0
            default_eff = default_mixers[i]["eff"] if i < len(default_mixers) else 1.0

            name = st.text_input(f"Mixer {i+1} Name", value=f"SM{i+1}", key=f"mixer_name_{i}")
            rate = st.number_input(f"{name} Input Rate (MT/HR)", min_value=0.1, value=default_rate, step=0.1, key=f"mixer_rate_{i}")
            efficiency = st.slider(f"{name} Efficiency", min_value=0.1, max_value=1.0, value=default_eff, step=0.05, key=f"mixer_eff_{i}")
            
            # Set proper defaults: Mixer 1 -> [Main Silo], Mixer 2 -> [Silo 1], Mixer 3 -> [Silo 2]
            default_silos = []
            if i == 0 and "Main Silo" in silo_names:
                default_silos = ["Main Silo"]
            elif i == 1 and "Silo 1" in silo_names:
                default_silos = ["Silo 1"]
            elif i == 2 and "Silo 2" in silo_names:
                default_silos = ["Silo 2"]
            else:
                default_silos = []
                
            connected_silos = st.multiselect(f"{name} Connected Silos", options=silo_names, default=default_silos, key=f"mixer_silos_{i}")
            
            mixers_data.append({
                "name": name,
                "input_rate_mt_hr": rate,
                "efficiency": efficiency,
                "connected_silos": connected_silos
            })
    return mixers_data


def get_cascade_inputs(mixer_names):
    st.sidebar.header("Cascade Settings")
    num_cascades = st.sidebar.number_input("Number of Cascades", min_value=1, max_value=10, value=3, step=1)
    cascades_data = []

    default_cascades = [
        {"eff": 0.8},
        {"eff": 0.8},
        {"eff": 0.8}
    ]

    for i in range(num_cascades):
         with st.sidebar.expander(f"Cascade {i+1} Settings", expanded=(i==0)):
            default_eff = default_cascades[i]["eff"] if i < len(default_cascades) else 1.0

            name = st.text_input(f"Cascade {i+1} Name", value=f"Cascade {i+1}", key=f"casc_name_{i}")
            efficiency = st.slider(f"{name} Efficiency", min_value=0.1, max_value=1.0, value=default_eff, step=0.05, key=f"casc_eff_{i}")
            
            default_mixer_idx = min(i, len(mixer_names)-1) if mixer_names else 0
            connected_mixer = st.selectbox(f"{name} Connected Mixer", options=mixer_names if mixer_names else ["None"], index=default_mixer_idx, key=f"casc_mixer_{i}")
            
            cascades_data.append({
                "name": name,
                "efficiency": efficiency,
                "connected_mixer": connected_mixer
            })
    return cascades_data

