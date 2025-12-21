import streamlit as st
import pandas as pd
import math
import numpy as np
from datetime import datetime
from fpdf import FPDF
import tempfile
import os
import logging

# 1. CONFIGURATION & CONSTANTS

REQUIRED_COLUMNS = ['imsi', 'start_time', 'latitude', 'longitude', 'cell_id']

CDR_COLUMN_MAP = {
    "imsi": ["imsi", "subscriber_id"],
    "start_time": ["start_time", "timestamp", "date_time", "call_time"],
    "cell_id": ["cell_id", "cellid", "cid"],
    "tower_id": ["tower_id", "towerid", "lac", "location_area_code"],
    "latitude": ["latitude", "lat"],
    "longitude": ["longitude", "lon", "lng"]
}

# 2. DATA NORMALIZATION & VALIDATION

def normalize_columns(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    """Standardizes column names based on a mapping dictionary."""
    col_rename = {}
    df_cols = {col.lower().replace(" ", "").replace("_", ""): col for col in df.columns}
    for std_col, variants in column_map.items():
        for variant in variants:
            key = variant.lower().replace(" ", "").replace("_", "")
            if key in df_cols:
                col_rename[df_cols[key]] = std_col
                break
    return df.rename(columns=col_rename)

def validate_input(df: pd.DataFrame) -> pd.DataFrame:
    """Checks if the dataframe contains necessary columns."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        st.error(f"❌ Missing required columns: {missing}")
        st.stop()
    return df

def parse_cdr(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare CDR data for analysis."""
    df = normalize_columns(df, CDR_COLUMN_MAP)
    # Ensure distinct types
    if 'start_time' in df.columns:
        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    for col in ['latitude', 'longitude']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df.dropna(subset=REQUIRED_COLUMNS)

# 3. ANALYSIS LOGIC (VECTORIZED)


def haversine_vectorized(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Vectorization.
    """
    R = 6371  # Earth radius in km
    
    # Convert decimal degrees to radians
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    d_phi = np.radians(lat2 - lat1)
    d_lambda = np.radians(lon2 - lon1)
    
    # Haversine formula
    a = np.sin(d_phi/2)**2 + np.cos(phi1)*np.cos(phi2) * np.sin(d_lambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return R * c

def analyze_logic(df: pd.DataFrame, max_dist_km: float, max_time_min: float):
    """
    Detects impossible travel (Tower Jumping) using vectorized operations.
    Returns a DataFrame of anomalous events.
    """
    # 1. Sort by User and Time
    df = df.sort_values(by=['imsi', 'start_time']).reset_index(drop=True)
    
    # 2. Shift columns to compare Row N with Row N-1
    df['prev_start_time'] = df.groupby('imsi')['start_time'].shift(1)
    df['prev_lat'] = df.groupby('imsi')['latitude'].shift(1)
    df['prev_lon'] = df.groupby('imsi')['longitude'].shift(1)
    df['prev_cell'] = df.groupby('imsi')['cell_id'].shift(1)
    
    # 3. Calculate Differences
    df['time_diff_min'] = (df['start_time'] - df['prev_start_time']).dt.total_seconds() / 60.0

    df['dist_km'] = haversine_vectorized(
        df['prev_lat'], df['prev_lon'], 
        df['latitude'], df['longitude']
    )
    
    # 4. Filter Anomalies
    mask = (df['dist_km'] >= max_dist_km) & (df['time_diff_min'] <= max_time_min) & (df['time_diff_min'] >= 0)
    
    anomalies = df[mask].copy()
    
    # Select and rename for report
    result = anomalies[[
        'imsi', 'start_time', 'prev_cell', 'cell_id', 
        'dist_km', 'time_diff_min'
    ]].rename(columns={
        'prev_cell': 'from_cell_id',
        'cell_id': 'to_cell_id',
        'dist_km': 'jump_distance_km',
        'time_diff_min': 'time_gap_minutes'
    })
    
    return result

# 4. REPORT GENERATION (PDF)

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Forensic Analysis: Tower Jumping Detection', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(file_name, anomalies, settings):
    pdf = PDFReport()
    pdf.add_page()
    
    # -- Meta Data --
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 10, f"Source File: {file_name}", ln=True)
    pdf.ln(5)
    
    # -- Executive Summary --
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Executive Summary", ln=True)
    pdf.set_font("Arial", size=10)
    
    summary_text = (
        f"This analysis identifies 'Tower Jumping' events, where a subscriber ID (IMSI) "
        f"appears at two geographically distant locations within a physically impossible timeframe. "
        f"\n\nConfiguration Used:\n"
        f"- Minimum Jump Distance: {settings['dist']} km\n"
        f"- Maximum Time Window: {settings['time']} minutes"
    )
    pdf.multi_cell(0, 5, summary_text)
    pdf.ln(10)
    
    # -- Findings Table --
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"2. Detected Anomalies ({len(anomalies)} events)", ln=True)
    
    if anomalies.empty:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "No tower jumping events detected with current settings.", ln=True)
    else:
        # Table Header
        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(220, 220, 220)
        
        # Define column widths
        w_imsi = 40
        w_time = 40
        w_dist = 25
        w_gap = 25
        w_loc = 60 # Combined from/to
        
        pdf.cell(w_imsi, 10, "IMSI", 1, 0, 'C', 1)
        pdf.cell(w_time, 10, "Timestamp", 1, 0, 'C', 1)
        pdf.cell(w_loc, 10, "Movement (Cell ID)", 1, 0, 'C', 1)
        pdf.cell(w_dist, 10, "Dist (km)", 1, 0, 'C', 1)
        pdf.cell(w_gap, 10, "Gap (min)", 1, 1, 'C', 1)
        
        # Table Rows
        pdf.set_font("Arial", size=8)
        for _, row in anomalies.iterrows():
            # Create a string like "123 -> 456" for location
            loc_str = f"{row['from_cell_id']} -> {row['to_cell_id']}"
            
            pdf.cell(w_imsi, 8, str(row['imsi']), 1)
            pdf.cell(w_time, 8, str(row['start_time']), 1)
            pdf.cell(w_loc, 8, loc_str, 1)
            pdf.cell(w_dist, 8, f"{row['jump_distance_km']:.2f}", 1, 0, 'C')
            pdf.cell(w_gap, 8, f"{row['time_gap_minutes']:.2f}", 1, 1, 'C')

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(tmp_file.name)
    return tmp_file.name

# 5. MAIN CONTROLLER

def run():
    st.markdown("## Tower Jumping Analysis")
    st.markdown("---")
    
    # Initialize State
    if 'uploaded_file' not in st.session_state: st.session_state.uploaded_file = None
    if 'tj_anomalies' not in st.session_state: st.session_state.tj_anomalies = None
    if 'tj_pdf' not in st.session_state: st.session_state.tj_pdf = None

    # --- 1. SETTINGS & UPLOAD ---
    with st.expander("Analysis Parameters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            dist_thresh = st.number_input(
                "Min. Jump Distance (km)", 
                min_value=1, value=10, step=1,
                help="Minimum distance between towers to qualify as a jump."
            )
        with col2:
            time_thresh = st.number_input(
                "Max. Time Window (minutes)", 
                min_value=1, value=5, step=1,
                help="Maximum time allowed to travel that distance."
            )

    uploaded_file = st.file_uploader("Upload CDR File", type=["csv", "xlsx"], key="tj_uploader")

    # --- 2. EXECUTION ENGINE ---
    if uploaded_file:
        try:
            # Load Data
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            df = parse_cdr(df)
            df = validate_input(df)
            
            # Run Logic
            anomalies = analyze_logic(df, dist_thresh, time_thresh)
            
            # Store State
            st.session_state.uploaded_file = uploaded_file
            st.session_state.tj_anomalies = anomalies
            st.session_state.tj_pdf = generate_pdf_report(
                uploaded_file.name, anomalies, 
                {"dist": dist_thresh, "time": time_thresh}
            )
            
            st.success("Analysis Complete")
            
        except Exception as e:
            st.error(f"Error during analysis: {e}")
            logging.error(f"Tower Jumping Error: {e}")

    # --- 3. RESULTS DISPLAY ---
    if st.session_state.tj_anomalies is not None:
        st.subheader("Detected Tower Jumps")
        
        if st.session_state.tj_anomalies.empty:
            st.info(f"No events found where distance > {dist_thresh}km and time < {time_thresh}min.")
        else:
            # Display interactive table
            st.dataframe(
                st.session_state.tj_anomalies.style.format({
                    "jump_distance_km": "{:.2f}", 
                    "time_gap_minutes": "{:.2f}"
                }), 
                use_container_width=True
            )
            
            # Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Events", len(st.session_state.tj_anomalies))
            m2.metric("Avg Jump Distance", f"{st.session_state.tj_anomalies['jump_distance_km'].mean():.1f} km")
            m3.metric("Avg Time Gap", f"{st.session_state.tj_anomalies['time_gap_minutes'].mean():.1f} min")

        # Report Download
        if st.session_state.tj_pdf and os.path.exists(st.session_state.tj_pdf):
            st.divider()
            with open(st.session_state.tj_pdf, "rb") as f:
                st.download_button(
                    label="📄 Download Forensic Report (PDF)",
                    data=f,
                    file_name="Tower_Jumping_Report.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    run()
