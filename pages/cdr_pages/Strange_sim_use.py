import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import os
import logging
from datetime import datetime

# 1. CONFIGURATION & CONSTANTS
# Columns required for this specific analysis
REQUIRED_COLUMNS = ['calling_number', 'called_number', 'call_direction', 'start_time']

CDR_COLUMN_MAP = {
    "calling_number": ["calling_number", "caller", "source_number", "a_party"],
    "called_number": ["called_number", "callee", "dest_number", "b_party"],
    "start_time": ["start_time", "timestamp", "date_time", "call_time"],
    "call_direction": ["call_direction", "direction", "type", "call_type"],
    "duration": ["duration", "duration_seconds", "billable_duration"]
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
    """Clean and prepare CDR data."""
    df = normalize_columns(df, CDR_COLUMN_MAP)
    
    if 'start_time' in df.columns:
        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
        
    # Ensure phone numbers are strings and clean them (remove .0 from floats)
    for col in ['calling_number', 'called_number']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
            
    return df

# 3. ANALYSIS LOGIC (CORE ENGINE)
def analyze_logic(df: pd.DataFrame, threshold: int):
    """
    Detects numbers making excessive international calls.
    Logic: Call Direction = Outgoing AND Called Number does NOT start with '91'.
    """
    # 1. Filter for Outgoing (Mobile Originating) calls
    # valid_mo = ['MO', 'OUTGOING', '1', 'CALL OUT']
    # We use a case-insensitive string match
    outgoing_mask = df['call_direction'].astype(str).str.upper().isin(['MO', 'OUTGOING', '1', 'CALL OUT'])
    outgoing_df = df[outgoing_mask].copy()

    if outgoing_df.empty:
        return pd.DataFrame()

    # 2. Filter for International Calls
    # Logic: Numbers NOT starting with '91' (India Country Code)
    # Improvement: Also ensure it's not a short code (length > 5) to avoid false positives on service numbers
    intl_mask = (
        (~outgoing_df['called_number'].str.startswith('91')) & 
        (outgoing_df['called_number'].str.len() > 6) 
    )
    intl_calls = outgoing_df[intl_mask]

    # 3. Aggregate Counts
    call_counts = intl_calls.groupby('calling_number').size().reset_index(name='international_call_count')
    
    # 4. Filter by Threshold
    suspicious_numbers = call_counts[call_counts['international_call_count'] > threshold].sort_values(
        by='international_call_count', ascending=False
    )
    
    return suspicious_numbers

# 4. REPORT GENERATION (PDF)
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Forensic Analysis: Strange SIM Usage', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(file_name, suspicious_df, settings):
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
        f"This report highlights numbers flagged for 'Strange SIM Usage', specifically "
        f"defined as excessive international outgoing calls. \n"
        f"The analysis excluded domestic calls (prefix '91') and flagged any number "
        f"making more than {settings['threshold']} international calls."
    )
    pdf.multi_cell(0, 5, summary_text)
    pdf.ln(10)

    # -- Findings Table --
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"2. Suspicious Numbers ({len(suspicious_df)} found)", ln=True)

    if suspicious_df.empty:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "No suspicious numbers detected with current settings.", ln=True)
    else:
        # Table Header
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(95, 10, "Calling Number (IMSI/MSISDN)", 1, 0, 'C', 1)
        pdf.cell(95, 10, "International Call Count", 1, 1, 'C', 1)

        # Table Rows
        pdf.set_font("Arial", size=10)
        for _, row in suspicious_df.iterrows():
            pdf.cell(95, 10, str(row['calling_number']), 1)
            pdf.cell(95, 10, str(row['international_call_count']), 1, 1, 'C')

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(tmp_file.name)
    return tmp_file.name
    
# 5. MAIN CONTROLLER
def run():
    st.markdown("## Strange SIM Use (International Abuse)")
    st.markdown("---")

    # Initialize Session State
    if 'uploaded_file' not in st.session_state: st.session_state.uploaded_file = None
    if 'strange_results' not in st.session_state: st.session_state.strange_results = None
    if 'strange_pdf' not in st.session_state: st.session_state.strange_pdf = None

    # --- 1. SETTINGS & UPLOAD ---
    with st.expander("Analysis Parameters", expanded=True):
        threshold = st.number_input(
            "Max International Calls Allowed", 
            min_value=1, value=5, step=1,
            help="Flag numbers that make more than this many international calls."
        )

    uploaded_file = st.file_uploader("Upload CDR File", type=["csv", "xlsx"], key="strange_uploader")

    # --- 2. EXECUTION ENGINE ---
    if uploaded_file:
        try:
            # Load Data
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            df = parse_cdr(df)
            df = validate_input(df)

            # Run Analysis
            results = analyze_logic(df, threshold)

            # Store State
            st.session_state.uploaded_file = uploaded_file
            st.session_state.strange_results = results
            st.session_state.strange_pdf = generate_pdf_report(
                uploaded_file.name, results, {"threshold": threshold}
            )

            st.success("Analysis Complete")

        except Exception as e:
            st.error(f"Error processing file: {e}")
            logging.error(f"Strange SIM Analysis failed: {e}")

    # --- 3. DISPLAY RESULTS ---
    if st.session_state.strange_results is not None:
        st.subheader("Suspicious International Activity")
        
        if st.session_state.strange_results.empty:
            st.info("No numbers exceeded the international call threshold.")
        else:
            # Dataframe
            st.dataframe(
                st.session_state.strange_results, 
                use_container_width=True
            )
            
            # Visualization
            st.bar_chart(
                st.session_state.strange_results.set_index('calling_number')['international_call_count']
            )

        # PDF Download
        if st.session_state.strange_pdf and os.path.exists(st.session_state.strange_pdf):
            st.divider()
            with open(st.session_state.strange_pdf, "rb") as f:
                st.download_button(
                    label="Download Forensic Report (PDF)",
                    data=f,
                    file_name="Strange_SIM_Report.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    run()
