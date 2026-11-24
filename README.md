# Production-Bot: Dynamic Plant Simulation Dashboard

An interactive **Streamlit** dashboard that simulates material flow through a soap/detergent-style production line, minute by minute. You configure the equipment in the sidebar; the app runs the simulation and shows levels, throughput and bottlenecks as charts and a table you can export to Excel.

## What it models

| Unit | Role |
|---|---|
| **Crutcher** | Batch mixer: produces material per cycle, by capacity, cycle time, efficiency and work hours |
| **Stock tanks** | Buffer storage between the crutcher and the dryers |
| **Dryers** | Consume from the tanks at an hourly rate and feed the connected noodle silos |
| **Noodle silos** | Intermediate storage with priority and starting level |
| **Sigma mixers** | Pull from the connected silos at a set input rate |
| **Cascades** | Downstream finishing lines fed by a mixer |

## Quick start

```bash
cd plant_simulator
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## Project structure

```
plant_simulator/
├── app.py                # Streamlit UI and charts
├── plant_logic.py        # Equipment classes (Crutcher, Dryer, StockTank, ...)
├── simulation_engine.py  # Time-step simulation loop
├── ui_inputs.py          # Sidebar input widgets
├── output_table.py       # Result table + Excel export
└── utils.py
```

## Tech stack

Python · Streamlit · pandas · NumPy · Plotly · openpyxl / XlsxWriter

## Ideas for next steps

- Add downtime/maintenance events and random breakdowns
- Find the bottleneck automatically and suggest capacity changes
- Save and load plant configurations as JSON
- Deploy a public demo on Streamlit Community Cloud

## License

[MIT](LICENSE)
