import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import os
import logging
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================

REQUIRED_COLUMNS = ['calling_number', 'called_number', 'call_direction', 'start_time']

CDR_COLUMN_MAP = {
    "calling_number": ["calling_number", "caller", "source_number", "a_party"],
    "called_number": ["called_number", "callee", "dest_number", "b_party"],
    "call_direction": ["call_direction", "direction", "type", "call_type"],
    "start_time": ["start_time", "timestamp", "date_time", "call_time"]
}

DEFAULT_PREFIXES = "1800, 1860, 800, 198, 199"

# ==========================================
# 2. DATA NORMALIZATION & VALIDATION
# ==========================================

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
    
    # Ensure numbers are strings for prefix matching
    for col in ['calling_number', 'called_number']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
            
    return df

# ==========================================
# 3. ANALYSIS LOGIC (CORE ENGINE)
# ==========================================

def analyze_logic(df: pd.DataFrame, abuse_threshold: int, prefixes_str: str):
    """
    Detects abusive calling patterns to specific toll-free prefixes.
    """
    # 1. Parse Prefixes
    # Convert "1800, 1860" -> ('1800', '1860')
    prefixes = tuple(p.strip() for p in prefixes_str.split(',') if p.strip())
    
    # 2. Filter for Toll-Free Calls (Mobile Originating)
    # We look for calls STARTING with the prefixes
    tollfree_mask = (
        (df['call_direction'].astype(str).str.upper().isin(['MO', 'OUTGOING', '1', 'CALL OUT'])) &
        (df['called_number'].str.startswith(prefixes))
    )
    tollfree_calls = df[tollfree_mask].copy()

    if tollfree_calls.empty:
        return pd.DataFrame(), pd.DataFrame()

    # 3. Logic A: Daily Abuse Analysis
    tollfree_calls['call_date'] = tollfree_calls['start_time'].dt.date
    daily_counts = tollfree_calls.groupby(['calling_number', 'call_date']).size().reset_index(name='call_count')
    
    # Filter by threshold
    abusive_users = daily_counts[daily_counts['call_count'] > abuse_threshold].sort_values(
        by='call_count', ascending=False
    )

    # 4. Logic B: Top Targets (Most called toll-free numbers)
    top_targets = tollfree_calls['called_number'].value_counts().head(10).reset_index()
    top_targets.columns = ['called_number', 'total_calls']

    return abusive_users, top_targets

# ==========================================
# 4. REPORT GENERATION (PDF)
# ==========================================

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Forensic Analysis: Toll-Free Abuse Detection', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(file_name, abusive_users, top_targets, settings):
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
        f"This report identifies subscribers making excessive calls to toll-free services. "
        f"The analysis focused on numbers starting with [{settings['prefixes']}] "
        f"and flagged users making more than {settings['threshold']} calls per day to these services."
    )
    pdf.multi_cell(0, 5, summary_text)
    pdf.ln(10)

    # -- Part 1: Abusers --
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"2. High Frequency Callers (> {settings['threshold']}/day)", ln=True)
    
    if abusive_users.empty:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "No abusive calling patterns detected.", ln=True)
    else:
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(60, 10, "Calling Number", 1, 0, 'C', 1)
        pdf.cell(40, 10, "Date", 1, 0, 'C', 1)
        pdf.cell(40, 10, "Total Calls", 1, 1, 'C', 1)
        
        pdf.set_font("Arial", size=10)
        for _, row in abusive_users.iterrows():
            pdf.cell(60, 10, str(row['calling_number']), 1)
            pdf.cell(40, 10, str(row['call_date']), 1)
            pdf.cell(40, 10, str(row['call_count']), 1, 1, 'C')
            
    pdf.ln(10)

    # -- Part 2: Top Targets --
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. Most Targeted Toll-Free Numbers", ln=True)
    
    if top_targets.empty:
        pdf.cell(0, 10, "No data available.", ln=True)
    else:
        pdf.set_font("Arial", size=10)
        for _, row in top_targets.iterrows():
            pdf.cell(0, 8, f"- {row['called_number']}: {row['total_calls']} calls received", ln=True)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(tmp_file.name)
    return tmp_file.name

# ==========================================
# 5. MAIN CONTROLLER
# ==========================================

def run():
    st.markdown("## ☎️ Toll-Free Abuse Detection")
    st.markdown("---")

    # Initialize State
    if 'uploaded_file' not in st.session_state: st.session_state.uploaded_file = None
    if 'tf_abusers' not in st.session_state: st.session_state.tf_abusers = None
    if 'tf_targets' not in st.session_state: st.session_state.tf_targets = None
    if 'tf_pdf' not in st.session_state: st.session_state.tf_pdf = None

    # --- 1. SETTINGS & UPLOAD ---
    with st.expander("⚙️ Analysis Parameters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            threshold = st.number_input(
                "Daily Call Limit", 
                min_value=1, value=5, step=1,
                help="Flag users calling toll-free numbers more than this many times a day."
            )
        with col2:
            custom_prefixes = st.text_input(
                "Toll-Free Prefixes (comma separated)", 
                value=DEFAULT_PREFIXES,
                help="Enter prefixes to identify toll-free numbers (e.g., 1800, 198)."
            )

    uploaded_file = st.file_uploader("Upload CDR File", type=["csv", "xlsx"], key="tf_uploader")

    # --- 2. EXECUTION ENGINE ---
    if uploaded_file:
        try:
            # Load Data
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            df = parse_cdr(df)
            df = validate_input(df)

            # Run Analysis
            abusers, targets = analyze_logic(df, threshold, custom_prefixes)

            # Store State
            st.session_state.uploaded_file = uploaded_file
            st.session_state.tf_abusers = abusers
            st.session_state.tf_targets = targets
            st.session_state.tf_pdf = generate_pdf_report(
                uploaded_file.name, abusers, targets, 
                {"threshold": threshold, "prefixes": custom_prefixes}
            )

            st.success("Analysis Complete")

        except Exception as e:
            st.error(f"Error processing file: {e}")
            logging.error(f"Toll Free Analysis failed: {e}")

    # --- 3. DISPLAY RESULTS ---
    if st.session_state.tf_abusers is not None:
        
        # Section A: Abusers
        st.subheader("🚩 Frequent Toll-Free Callers")
        if st.session_state.tf_abusers.empty:
            st.info(f"No callers exceeded {threshold} calls/day to toll-free numbers.")
        else:
            st.dataframe(st.session_state.tf_abusers, use_container_width=True)

        st.divider()

        # Section B: Top Targets
        st.subheader("📊 Most Dialed Services")
        if not st.session_state.tf_targets.empty:
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                st.bar_chart(
                    st.session_state.tf_targets.set_index('called_number')['total_calls']
                )
            with col_table:
                st.dataframe(st.session_state.tf_targets, use_container_width=True)
        else:
            st.info("No toll-free calls found.")

        # PDF Download
        if st.session_state.tf_pdf and os.path.exists(st.session_state.tf_pdf):
            st.divider()
            with open(st.session_state.tf_pdf, "rb") as f:
                st.download_button(
                    label="📄 Download Forensic Report (PDF)",
                    data=f,
                    file_name="Toll_Free_Abuse_Report.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    run()
