import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import os
import logging
from datetime import datetime

# 1. CONFIGURATION & CONSTANTS
REQUIRED_COLUMNS = ['imsi', 'imei', 'calling_number', 'called_number', 'start_time']

CDR_COLUMN_MAP = {
    "imsi": ["imsi", "subscriber_id", "sim_id"],
    "imei": ["imei", "device_id", "serial_number"],
    "calling_number": ["calling_number", "caller", "source_number", "a_party"],
    "called_number": ["called_number", "callee", "dest_number", "b_party"],
    "start_time": ["start_time", "timestamp", "date_time", "call_time"]
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
    
    # Ensure ID columns are treated as strings
    for col in ['imsi', 'imei', 'called_number']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
            
    return df.dropna(subset=REQUIRED_COLUMNS)
 
# 3. ANALYSIS LOGIC (CORE ENGINE)
def calculate_jaccard_similarity(set_a, set_b):
    """Calculates intersection over union for two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union

def analyze_logic(df: pd.DataFrame, time_window='30min', similarity_threshold=0.6):
    """
    Detects SIM Swapping using two methods:
    1. IMEI Re-use: Different IMSIs using the exact same IMEI.
    2. Pattern Matching: Different IMSIs calling the same set of people (Jaccard Sim).
    """
    
    # --- Logic A: IMEI Reuse Analysis ---
    # Find IMEIs associated with > 1 unique IMSI
    imei_counts = df.groupby('imei')['imsi'].nunique().reset_index(name='unique_imsis')
    imei_swaps = imei_counts[imei_counts['unique_imsis'] > 1].copy()
    
    # --- Logic B: Behavioral Pattern Analysis ---
    # Group calls by IMSI and Time Window
    df['time_bucket'] = df['start_time'].dt.floor(time_window)
    
    # Create a "Signature" for each IMSI per time bucket (Set of numbers called)
    signatures = df.groupby(['imsi', 'time_bucket'])['called_number'].apply(set).reset_index(name='called_set')
    
    suspicious_patterns = []
    
    # We only care about buckets where multiple IMSIs were active
    # This optimization prevents checking IMSI A (Monday) vs IMSI B (Friday)
    for bucket, group in signatures.groupby('time_bucket'):
        if len(group) < 2: 
            continue
            
        # Pairwise comparison within the same time bucket
        imsis = group['imsi'].values
        sets = group['called_set'].values
        
        for i in range(len(imsis)):
            for j in range(i + 1, len(imsis)):
                sim_score = calculate_jaccard_similarity(sets[i], sets[j])
                
                if sim_score >= similarity_threshold:
                    suspicious_patterns.append({
                        'time_window': bucket,
                        'imsi_1': imsis[i],
                        'imsi_2': imsis[j],
                        'similarity_score': round(sim_score, 2),
                        'common_contacts': list(sets[i] & sets[j])
                    })
                    
    pattern_df = pd.DataFrame(suspicious_patterns)
    
    return imei_swaps, pattern_df

# 4. REPORT GENERATION (PDF)
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Forensic Analysis: SIM Swapping Detection', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(file_name, imei_swaps, pattern_df, settings):
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
        f"This report identifies potential SIM Swapping incidents using two forensic indicators: "
        f"1) Multiple SIM cards (IMSIs) being used in the exact same device (IMEI). "
        f"2) Different SIM cards exhibiting highly similar calling patterns (Jaccard Similarity > {settings['threshold']})."
    )
    pdf.multi_cell(0, 5, summary_text)
    pdf.ln(10)

    # -- Part 1: IMEI Swaps --
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"2. Device Re-use (IMEI Swapping) - {len(imei_swaps)} Devices", ln=True)
    
    if imei_swaps.empty:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "No suspicious IMEI sharing detected.", ln=True)
    else:
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(95, 10, "Device IMEI", 1, 0, 'C', 1)
        pdf.cell(95, 10, "Unique SIMs (IMSIs) Used", 1, 1, 'C', 1)
        
        pdf.set_font("Arial", size=10)
        for _, row in imei_swaps.iterrows():
            pdf.cell(95, 10, str(row['imei']), 1)
            pdf.cell(95, 10, str(row['unique_imsis']), 1, 1, 'C')
    
    pdf.ln(10)

    # -- Part 2: Behavioral Similarity --
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"3. Behavioral Pattern Matching - {len(pattern_df)} Pairs", ln=True)
    
    if pattern_df.empty:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "No SIMs with similar calling patterns detected.", ln=True)
    else:
        pdf.set_font("Arial", size=9)
        for _, row in pattern_df.iterrows():
            txt = (
                f"Time Window: {row['time_window']} | Similarity: {row['similarity_score']*100}%\n"
                f"IMSI A: {row['imsi_1']} <--> IMSI B: {row['imsi_2']}\n"
                f"Shared Contacts: {', '.join(list(row['common_contacts'])[:5])}..." 
            )
            pdf.multi_cell(0, 6, txt, border=1)
            pdf.ln(2)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(tmp_file.name)
    return tmp_file.name
 
# 5. MAIN CONTROLLER
def run():
    st.markdown("## SIM Swapping & Cloning Detection")
    st.markdown("---")

    # Initialize State
    if 'uploaded_file' not in st.session_state: st.session_state.uploaded_file = None
    if 'imei_swaps' not in st.session_state: st.session_state.imei_swaps = None
    if 'pattern_swaps' not in st.session_state: st.session_state.pattern_swaps = None
    if 'sim_pdf' not in st.session_state: st.session_state.sim_pdf = None

    # --- 1. SETTINGS & UPLOAD ---
    with st.expander("Analysis Parameters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            sim_threshold = st.slider(
                "Pattern Similarity Threshold", 
                min_value=0.1, max_value=1.0, value=0.6, step=0.1,
                help="Higher value means patterns must be nearly identical (1.0 = 100% same calls)."
            )
        with col2:
            time_window = st.selectbox(
                "Pattern Grouping Window",
                options=['15min', '30min', '1h', '2h'],
                index=1,
                help="Time window to group calls for pattern comparison."
            )

    uploaded_file = st.file_uploader("Upload CDR File", type=["csv", "xlsx"], key="sim_uploader")

    # --- 2. EXECUTION ENGINE ---
    if uploaded_file:
        try:
            # Load Data
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            df = parse_cdr(df)
            df = validate_input(df)

            # Run Analysis
            imei_swaps, pattern_df = analyze_logic(df, time_window, sim_threshold)

            # Store State
            st.session_state.uploaded_file = uploaded_file
            st.session_state.imei_swaps = imei_swaps
            st.session_state.pattern_swaps = pattern_df
            st.session_state.sim_pdf = generate_pdf_report(
                uploaded_file.name, imei_swaps, pattern_df, 
                {"threshold": sim_threshold}
            )

            st.success("Analysis Complete")

        except Exception as e:
            st.error(f"Error processing file: {e}")
            logging.error(f"SIM Swap Analysis failed: {e}")

    # --- 3. DISPLAY RESULTS ---
    if st.session_state.imei_swaps is not None:
        
        # Section A: IMEI Swaps
        st.subheader("Device Re-use (IMEI Swapping)")
        if st.session_state.imei_swaps.empty:
            st.info("No suspicious IMEI reuse found.")
        else:
            st.dataframe(st.session_state.imei_swaps, use_container_width=True)
            st.caption("These IMEIs were used with multiple different SIM cards (IMSIs).")

        st.divider()

        # Section B: Pattern Matching
        st.subheader("Behavioral Similarity (SIM Cloning/Burners)")
        if st.session_state.pattern_swaps is not None and not st.session_state.pattern_swaps.empty:
            st.dataframe(
                st.session_state.pattern_swaps[['time_window', 'imsi_1', 'imsi_2', 'similarity_score']], 
                use_container_width=True
            )
            st.caption(f"Pairs of SIMs that called the exact same people within the same {time_window} window.")
        else:
            st.info("No similar calling patterns detected.")

        # PDF Download
        if st.session_state.sim_pdf and os.path.exists(st.session_state.sim_pdf):
            st.divider()
            with open(st.session_state.sim_pdf, "rb") as f:
                st.download_button(
                    label="Download Forensic Report (PDF)",
                    data=f,
                    file_name="SIM_Swap_Analysis_Report.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    run()
