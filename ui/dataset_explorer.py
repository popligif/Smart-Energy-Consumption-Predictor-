"""
UI component for raw telemetry exploration, data dictionaries, and dataset audits (FR-1).
"""
import streamlit as st
import pandas as pd
from services.data_service import DataService

def render_dataset_explorer() -> None:
    """Renders the Dataset Explorer page in Streamlit."""
    st.header("🔍 Campus Telemetry Explorer")
    st.write("Browse, search, and audit raw data points collected from MIET smart meters.")
    
    data_service = DataService()
    df = data_service.load_dataset()
    
    # 1. Dataset stats summary
    st.subheader("Dataset Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records Ingested", len(df))
    col2.metric("Telemetry Columns", len(df.columns))
    col3.metric("Campus Buildings Tracked", df["Building"].nunique())
    col4.metric("Temporal Span", "24 Hours (Hourly)")
    
    st.markdown("---")
    
    # 2. Filters
    st.subheader("Search & Export Telemetry")
    
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        search_building = st.selectbox("Search by Building (Explorer)", options=["All"] + sorted(df["Building"].unique().tolist()))
    with col_e2:
        search_weather = st.selectbox("Search by Weather Condition", options=["All"] + sorted(df["Weather Condition"].unique().tolist()))
    with col_e3:
        search_hour = st.slider("Hour Filter", min_value=0, max_value=23, value=(0, 23))
        
    df_filtered = df.copy()
    if search_building != "All":
        df_filtered = df_filtered[df_filtered["Building"] == search_building]
    if search_weather != "All":
        df_filtered = df_filtered[df_filtered["Weather Condition"] == search_weather]
        
    df_filtered = df_filtered[
        (df_filtered["Hour"] >= search_hour[0]) & 
        (df_filtered["Hour"] <= search_hour[1])
    ]
    
    st.dataframe(df_filtered, use_container_width=True)
    
    # Download filtered CSV
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Filtered Dataset to CSV",
        data=csv_data,
        file_name="miet_energy_filtered_telemetry.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # 3. Data Dictionary
    st.subheader("MIET Campus Telemetry Dictionary")
    st.write("Description of primary database fields extracted from sensors and campus schedules:")
    
    dictionary_data = [
        {"Field Name": "Timestamp", "Data Type": "Datetime", "Description": "Date and hour of telemetry log."},
        {"Field Name": "Building", "Data Type": "String (Categorical)", "Description": "Building location (Academic Block A-D, CoE, Workshop)."},
        {"Field Name": "Occupancy / Students / Faculty", "Data Type": "Integer", "Description": "Count of individuals present on the building floors."},
        {"Field Name": "Running Computers / ACs", "Data Type": "Integer", "Description": "Active device counts contributing to appliance base load."},
        {"Field Name": "Power Factor", "Data Type": "Float [0.0 - 1.0]", "Description": "Electrical efficiency ratio. Values < 0.90 trigger alerts."},
        {"Field Name": "Current Power (kW)", "Data Type": "Float", "Description": "Instantaneous power demand in kilowatts (Identical to Energy Consumption)."},
        {"Field Name": "Voltage / Current", "Data Type": "Float", "Description": "Core line telemetry (Volts, Amperes)."},
        {"Field Name": "Dynamic Cost (INR)", "Data Type": "Float (Engineered)", "Description": "Hourly cost calculated based on calibrated tariffs."},
        {"Field Name": "Dynamic Carbon (kg CO2)", "Data Type": "Float (Engineered)", "Description": "Hourly carbon output calculated based on grid emission coefficients."}
    ]
    
    dict_df = pd.DataFrame(dictionary_data)
    st.table(dict_df)
