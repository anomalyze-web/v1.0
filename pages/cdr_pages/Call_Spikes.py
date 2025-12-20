import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import os
import logging

# --- Config & Setup ---
REQUIRED_COLUMNS = ['calling_number', 'called_number', 'start_time', 'call_direction']

CDR_COLUMN_MAP = {
    "calling_number": ["calling_number", "caller", "source_number"],
    "called_number": ["called_number", "callee", "dest_number"],
    "start_time": ["start_time", "timestamp", "date_time", "call_time"],
    "call_direction": ["call_direction", "direction", "type"]
}

# --- Helper Functions ---

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
    """Clean and prepare CDR data."""
    df = normalize_columns(df, CDR_COLUMN_MAP)
    if 'start_time' in df.columns:
        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    return df

def analyze_logic(df: pd.DataFrame, intl_threshold: int, spike_threshold: int):
    """
    Core Logic: Now accepts dynamic thresholds from the user.
    """
    # Filter for outgoing calls (Mobile Originating)
    # Note: Adjust 'MO' if your data uses different codes like 'Outgoing' or '1'
    outgoing_df = df[df['call_direction'].astype(str).str.upper().isin(['MO', 'OUTGOING', 'CALL OUT'])].copy()
    
    if outgoing_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Logic 1: International Calls (Not starting with 91)
    # Assumes '91' is the home country code. 
    # TODO: In the future, you could make the "Home Country Code" a user input too!
    intl_calls = outgoing_df[~outgoing_df['called_number'].astype(str).str.startswith('91')]
    intl_counts = intl_calls.groupby('calling_number').size().reset_index(name='international_call_count')
    intl_suspects = intl_counts[intl_counts['international_call_count'] > intl_threshold]

    # Logic 2: Call Spikes (Hourly)
    outgoing_df['hour_window'] = outgoing_df['start_time'].dt.floor('h')
    call_spikes = outgoing_df.groupby(['calling_number', 'hour_window']).size().reset_index(name='calls_in_hour')
    spike_suspects = call_spikes[call_spikes['calls_in_hour'] > spike_threshold]
    
    return intl_suspects, spike_suspects

def generate_pdf_report(file_name, intl_suspects, spike_suspects, thresholds):
    """Generates a PDF summary including the settings used."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="CDR Call Spike Analysis Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(200, 10, txt=f"File: {file_name}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Parameters Used: Intl Threshold > {thresholds['intl']}, Spike Threshold > {thresholds['spike']}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(200, 10, txt="Part 1: Excessive International Outgoing Calls", ln=True)
    pdf.set_font("Arial", size=11)
    
    if intl_suspects.empty:
        pdf.cell(200, 10, txt="No excessive international callers found.", ln=True)
    else:
        for _, row in intl_suspects.iterrows():
            pdf.cell(200, 10, txt=f"{row['calling_number']}: {row['international_call_count']} calls", ln=True)
            
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(200, 10, txt="Part 2: Sudden Spike in Outgoing Calls", ln=True)
    pdf.set_font("Arial", size=11)
    
    if spike_suspects.empty:
        pdf.cell(200, 10, txt="No sudden spikes detected.", ln=True)
    else:
        for _, row in spike_suspects.iterrows():
            pdf.cell(200, 10, txt=f"{row['calling_number']} at {row['hour_window']}: {row['calls_in_hour']} calls", ln=True)
            
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(tmp_file.name)
    return tmp_file.name

# --- Main Entry Point (Run Function) ---

def run():
    st.markdown("## 📈 Call Spikes & International Anomalies")
    st.markdown("---")

    # --- 1. USER SETTINGS (The "Investigator Options") ---
    with st.expander("⚙️ Analysis Parameters (Adjust Thresholds)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            thresh_intl = st.number_input(
                "Min. International Calls", 
                min_value=1, value=5, step=1,
                help="Flag numbers that make more than this many international calls."
            )
        with col2:
            thresh_spike = st.number_input(
                "Hourly Call Spike Limit", 
                min_value=5, value=15, step=5,
                help="Flag numbers making more than this many calls in a single hour."
            )

    # --- 2. FILE UPLOADER ---
    if 'uploaded_file' not in st.session_state: st.session_state.uploaded_file = None
    
    uploaded_file = st.file_uploader("Upload CDR File", type=["csv", "xlsx"], key='spike_uploader')

    if uploaded_file:
        try:
            # Load & Preprocess
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            df = parse_cdr(df)
            df = validate_input(df)
            
            # Analyze using User Inputs
            intl_suspects, spike_suspects = analyze_logic(df, thresh_intl, thresh_spike)
            
            # --- 3. DISPLAY RESULTS ---
            
            # Section A: International Calls
            st.subheader("🌍 International Call Anomalies")
            if not intl_suspects.empty:
                st.dataframe(intl_suspects, use_container_width=True)
                # Visualization: Simple Bar Chart
                st.bar_chart(intl_suspects.set_index('calling_number')['international_call_count'])
            else:
                st.success(f"No callers exceeded {thresh_intl} international calls.")

            st.divider()

            # Section B: Call Spikes
            st.subheader("🔥 High Volume Call Spikes (Hourly)")
            if not spike_suspects.empty:
                # Format the date for better readability
                spike_display = spike_suspects.copy()
                spike_display['hour_window'] = spike_display['hour_window'].dt.strftime('%Y-%m-%d %H:00')
                
                st.dataframe(spike_display, use_container_width=True)
                
                # Metric Cards for quick insight
                col_m1, col_m2 = st.columns(2)
                col_m1.metric("Total Spikes Detected", len(spike_suspects))
                col_m1.metric("Highest Volume in 1 Hour", spike_suspects['calls_in_hour'].max())
            else:
                st.success(f"No hourly spikes exceeded {thresh_spike} calls.")

            # --- 4. REPORT GENERATION ---
            if st.button("📄 Generate PDF Report"):
                pdf_path = generate_pdf_report(
                    uploaded_file.name, 
                    intl_suspects, 
                    spike_suspects, 
                    {"intl": thresh_intl, "spike": thresh_spike}
                )
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Analysis PDF",
                        data=f,
                        file_name="CDR_Call_Spikes_Report.pdf",
                        mime="application/pdf"
                    )

        except Exception as e:
            st.error(f"Error during analysis: {e}")
            logging.error(f"Analysis failed: {e}")

# This allows testing the file independently
if __name__ == "__main__":
    run()
