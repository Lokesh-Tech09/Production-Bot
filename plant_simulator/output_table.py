import pandas as pd
import io
import streamlit as st
import datetime
import xlsxwriter

def format_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    # We want Excel style with time on the top row
    # i.e., transpose the dataframe
    
    # Set time as index
    df_t = df.set_index("TIME (MIN)").T
    
    # Optionally round all floats
    df_t = df_t.round(3)
    
    return df_t

def highlight_rows(row):
    # This highlights cells in the row based on the machine type
    row_name = str(row.name)
    styles = ['' for _ in row]
    
    if "(MT/HR)" in row_name:
        # Dryer stopped
        styles = ['background-color: #FFC7CE; color: #9C0006' if v == 0 else '' for v in row]
    elif "Output (MT)" in row_name and "Dryer" not in row_name:
        # Sigma Mixer working vs stopped
        styles = ['background-color: #C6EFCE; color: #006100' if v > 0 else 'background-color: #FFC7CE; color: #9C0006' for v in row]
        
    return styles

def render_table(df_display: pd.DataFrame):
     # Apply styling before rendering
     styled_df = df_display.style.apply(highlight_rows, axis=1)
     # We use format to keep precision but also apply the styling
     st.dataframe(styled_df, use_container_width=True)
     
def export_to_excel(df_display: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    
    # Use xlsxwriter to apply conditional formatting
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_display.to_excel(writer, sheet_name='Plant Simulation')
        workbook = writer.book
        worksheet = writer.sheets['Plant Simulation']
        
        # Define the highlight formats
        red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
        green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
        
        # Scan the index names and apply formatting
        for row_num, index_name in enumerate(df_display.index):
            row_name = str(index_name)
            
            num_cols = len(df_display.columns)
            start_cell = xlsxwriter.utility.xl_rowcol_to_cell(row_num + 1, 1)
            end_cell = xlsxwriter.utility.xl_rowcol_to_cell(row_num + 1, num_cols)
            cell_range = f"{start_cell}:{end_cell}"

            if "(MT/HR)" in row_name:
                # Dryer stopped
                worksheet.conditional_format(cell_range, {
                    'type': 'cell', 'criteria': '==', 'value': 0, 'format': red_format
                })
            elif "Output (MT)" in row_name and "Dryer" not in row_name:
                # Sigma Mixer working
                worksheet.conditional_format(cell_range, {
                    'type': 'cell', 'criteria': '>', 'value': 0, 'format': green_format
                })
                # Sigma Mixer stopped
                worksheet.conditional_format(cell_range, {
                    'type': 'cell', 'criteria': '==', 'value': 0, 'format': red_format
                })

    return output.getvalue()
