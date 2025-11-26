import streamlit as st
import base64
from streamlit_extras.stylable_container import stylable_container

# Import the analysis modules
# NOTE: These modules (CDR_analysis, etc.) must exist in your project directory
from CDR_analysis import show_cdr_analysis
from IPDR_analysis import show_ipdr_analysis
from FIREWALL_analysis import show_firewall_analysis
from CO_Relation_analysis import show_correlation_analysis

# --- Helper Functions (Page Views) ---

def show_evidence_library():
    """Placeholder screen for Evidence Library."""
    st.title("Evidence Library")
    st.markdown("---")
    # Added back button for navigation flow
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"
        st.rerun()

    # NOTE: These lines were previously unindented, causing the error.
    st.text_input("Search Evidence Library", placeholder="Enter keywords, hash values, or file names...")
    st.markdown('<div style="margin-top: 50px; padding: 30px; border: 1px dashed #555; border-radius: 10px; color: #aaa; text-align: center;">\
    <h3>No Evidence Uploaded Yet</h3>\
    <p>Start a new case to upload and categorize digital evidence.</p>\
    </div>', unsafe_allow_html=True)

def show_search_cases():
    """Placeholder screen for Search Cases."""
    st.title("Search Historical Cases")
    st.markdown("---")
    # Added back button for navigation flow
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"
        st.rerun()

    # NOTE: These lines were previously unindented, causing the error.
    st.text_input("Search Cases", placeholder="Enter case number, investigator name, or keywords...")
    st.markdown('<div style="margin-top: 50px; padding: 30px; border: 1px dashed #555; border-radius: 10px; color: #aaa; text-align: center;">\
    <h3>No Cases Archived</h3>\
    <p>Completed case analyses will appear here for future reference and searching.</p>\
    </div>', unsafe_allow_html=True)

def show_legal_reference():
    """Placeholder screen for Legal Reference."""
    st.title("Legal Reference and Standards")
    st.markdown("---")
    # Added back button for navigation flow
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"
        st.rerun()

    # NOTE: This line was previously unindented, causing the error.
    st.markdown('<div style="padding: 30px; border: 1px dashed #555; border-radius: 10px; color: #aaa;">\
    <p>This section is reserved for relevant legal statutes, compliance documentation, and digital forensics standards.</p>\
    <p>Content to be integrated...</p>\
    </div>', unsafe_allow_html=True)

def show_new_case_selector():
    """Selector for the specific type of case data to be uploaded."""
    # NOTE: All content inside this function was previously unindented, causing the error.
    st.markdown(f"### Select Data Type for New Case:")

    col1, col2, col3, col4 = st.columns(4)

    # Back button for navigation flow
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"
        st.rerun()

    # Updated button style for selector screen: #1c4868 background, #61a3cd border/outline
    selector_button_style = """
    button {
    background-color: #1c4868 !important;
    color: #fff !important;
    border: 2px solid #61a3cd !important;
    border-radius: 12px;
    height: 60px;
    font-size: 1.1rem;
    width: 100%;
    margin-bottom: 12px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    transition: background-color 0.2s, border-color 0.2s;
    }
    button:hover {
    background-color: #367588 !important;
    border: 2px solid #fff !important;
    }
    """

    with col1:
        with stylable_container("cdr_button", css_styles=selector_button_style):
            if st.button("CDR Analysis", key="select_cdr"):
                st.session_state.page = "cdr"
                st.session_state.form_submitted = False
                st.rerun()

    with col2:
        with stylable_container("ipdr_button", css_styles=selector_button_style):
            if st.button("IPDR Analysis", key="select_ipdr"):
                st.session_state.page = "ipdr"
                st.session_state.form_submitted = False
                st.rerun()

    with col3:
        with stylable_container("firewall_button", css_styles=selector_button_style):
            if st.button("Firewall Logs", key="select_firewall"):
                st.session_state.page = "firewall"
                st.session_state.form_submitted = False
                st.rerun()

    with col4:
        with stylable_container("correlation_button", css_styles=selector_button_style):
            if st.button("Correlation", key="select_correlation"):
                st.session_state.page = "correlation"
                st.session_state.form_submitted = False
                st.rerun()

# --- CSS and Core Function ---

def dashboard_css():
    st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
<style>
/* 1. Global Background and Padding */
.main .block-container {
/* Pushing the content down past the two fixed bars (Header 60px + Nav 60px + margin) */
padding-top: 140px !important;
padding-left: 40px;
padding-right: 40px;
padding-bottom: 40px;
max-width: 100% !important;
}
body, [data-testid="stAppViewContainer"] {
background: #001928 !important; /* New Dark Background */
}

/* --- FIXED HEADER CONTAINER --- */
/* Target the custom div ID applied in Python for fixed position */
#fixed-header-container {
position: fixed;
left: 0;
top: 0;
width: 100%;
z-index: 10;
padding: 0 40px; /* Padding handles the side margins */
background: #15425b; /* New Title Bar Color */
box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.fixed-header-content {
height: 60px; /* Reduced Height for the header content */
display: flex;
align-items: center;
}
.dashboard-title {
font-size: 2rem;
font-weight: 700;
color: #fff;
margin-right: 32px;
}
.user-actions {
display: flex;
align-items: center;
gap: 16px;
margin-left: auto;
}
.user-box {
font-size: 1.2rem;
font-weight: 600;
color: #fff;
display: flex;
align-items: center;
gap: 8px;
}
.user-avatar {
width: 36px;
height: 36px;
background: #367588;
border-radius: 50%;
display: flex;
align-items: center;
justify-content: center;
font-size: 1.2rem;
color: #fff;
}

/* --- FIXED NAVIGATION BAR CONTAINER --- */
#fixed-nav-container {
position: fixed;
top: 60px; /* Right below the 60px header */
left: 0;
width: 100%;
z-index: 9;
background-color: #001928; /* Matches background */
padding: 10px 40px;
box-shadow: 0 2px 5px rgba(0,0,0,0.3);
}

/* Global style for main navigation buttons (New Case, Evidence Library, etc.) */
.main-nav-button button {
background-color: #1c4868 !important;
color: white;
border: 2px solid #61a3cd !important; /* Light blue border */
border-radius: 8px;
font-size: 1.05rem;
font-weight: 600;
width: 100%;
height: 40px;
margin: 0;
transition: all 0.2s;
}
.main-nav-button button:hover {
background-color: #367588 !important;
border-color: #fff !important;
}

/* 5. Main Content Area */
.dashboard-main {
padding-top: 20px;
}
.section-header {
font-size: 1.8rem;
font-weight: 700;
color: #3a7ba4 !important; /* Bookmarked/Recent Cases Header Color */
margin-top: 30px;
margin-bottom: 15px;
border-bottom: 2px solid #367588;
padding-bottom: 5px;
}
.placeholder-box {
background: #15425b; /* Dark Blue Placeholder Box */
color: #99aab5; /* Light grey text */
padding: 20px;
border-radius: 12px;
margin-bottom: 20px;
box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.placeholder-box h4 {
margin-top: 0;
color: #fff;
}

/* Remove Sidebar */
[data-testid="stSidebar"] {
display: none !important;
}
[data-testid="stSidebarContent"] {
display: none !important;
}
/* Style for the Logout Button */
[data-testid="stButton"][key="header_logout"] button {
background-color: #367588;
color: white;
border-radius: 8px;
font-size: 1.0rem;
font-weight: 600;
width: auto;
padding: 8px 15px;
height: 40px;
margin: 0;
transition: background-color 0.2s;
border: none;
}
[data-testid="stButton"][key="header_logout"] button:hover {
background-color: #e57373; /* Light red hover for danger/logout */
}
</style>
""", unsafe_allow_html=True)

def dashboard(username):
    st.set_page_config(page_title="Anomalyze Dashboard", layout="wide")
    dashboard_css()

    # --- Session State Initialization ---
    if "page" not in st.session_state:
        st.session_state.page = "main"
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False

    # --- Fixed Header (Title, User ID, Logout) ---
    # Wrap in a DIV with the fixed-header-container ID
    st.markdown('<div id="fixed-header-container">', unsafe_allow_html=True)
    st.markdown('<div class="fixed-header-content">', unsafe_allow_html=True)

    # Header Content Layout using Streamlit columns
    title_col, spacer_col, user_col, logout_col = st.columns([2, 5, 2, 1.5])

    with title_col:
        st.markdown('<div class="dashboard-title">Dashboard</div>', unsafe_allow_html=True)

    with user_col:
        st.markdown(f'''
<div class="user-box">
{username.upper()}
<div class="user-avatar">👤</div>
</div>
''', unsafe_allow_html=True)

    with logout_col:
        if st.button("Logout", key="header_logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.page = "main"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True) # Close fixed-header-content
    st.markdown('</div>', unsafe_allow_html=True) # Close fixed-header-container

    # --- Fixed Navigation Bar (Main Buttons) ---
    # Wrap in a DIV with the fixed-nav-container ID
    st.markdown('<div id="fixed-nav-container">', unsafe_allow_html=True)

    # Columns for navigation, ensuring equal width
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    # Function to create a nav button with common styling
    def nav_button(label, key, target_page, col):
        with col:
            with stylable_container(f"nav_button_{key}", css_styles=".main-nav-button"):
                if st.button(label, key=key, help=f"Go to {label}"):
                    st.session_state.page = target_page
                    st.rerun()

    # Navigation Buttons
    nav_button("New Case", "nav_new_case", "new_case_selector", nav_col1)
    nav_button("Evidence Library", "nav_evidence", "evidence_library", nav_col2)
    nav_button("Search Cases", "nav_search", "search_cases", nav_col3)
    nav_button("Legal Reference", "nav_legal", "legal_reference", nav_col4)

    st.markdown('</div>', unsafe_allow_html=True) # Close fixed-nav-container


    # --- Main Content Router ---
    st.markdown('<div class="dashboard-main">', unsafe_allow_html=True)

    if st.session_state.page == "main":
        st.markdown('<h2 class="section-header">Bookmarked Cases</h2>', unsafe_allow_html=True)
        st.markdown('<div class="placeholder-box"><h4>No bookmarked cases available.</h4><p>Use the bookmark feature on case analysis pages to quickly access important investigations.</p></div>', unsafe_allow_html=True)

        st.markdown('<h2 class="section-header">Recent Activity</h2>', unsafe_allow_html=True)
        st.markdown('<div class="placeholder-box"><h4>No recent cases analyzed.</h4><p>Start a new case using the "New Case" button above to begin your analysis.</p></div>', unsafe_allow_html=True)

    # New Case Selector (Replaces the old CDR/IPDR buttons)
    elif st.session_state.page == "new_case_selector":
        show_new_case_selector()

    # Placeholder Pages
    elif st.session_state.page == "evidence_library":
        show_evidence_library()
    elif st.session_state.page == "search_cases":
        show_search_cases()
    elif st.session_state.page == "legal_reference":
        show_legal_reference()

    # FORM PAGES (The original CDR/IPDR upload forms)
    elif st.session_state.page in ["cdr", "ipdr", "firewall", "correlation"]:
        st.markdown(f"### Uploading **{st.session_state.page.upper()}** Case")

        # Back button to return to the New Case Selector
        if st.button("⬅ Back to New Case Selection"):
            st.session_state.page = "new_case_selector"
            st.session_state.form_submitted = False
            st.rerun()

        with st.form(f"{st.session_state.page}_form"):
            case_number = st.text_input("Case Number")
            investigator_name = st.text_input("Investigator Name")
            case_name = st.text_input("Case Name")
            remarks = st.text_area("Remarks")
            submit = st.form_submit_button("Submit")
            if submit:
                st.success(
                    f"{st.session_state.page.upper()} Case '{case_name}' (Case No: {case_number}) uploaded by {investigator_name}."
                )
                st.session_state.form_submitted = True
                st.session_state.case_number = case_number
                st.session_state.investigator_name = investigator_name
                st.session_state.case_name = case_name
                st.session_state.remarks = remarks

        # Show the "Start Analysis" button only after successful submit
        if st.session_state.form_submitted:
            analysis_labels = {
                "cdr": "Start CDR Analysis",
                "ipdr": "Start IPDR Analysis",
                "firewall": "Start FIREWALL Analysis",
                "correlation": "Start CO-RELATION Analysis"
            }
            label = analysis_labels.get(st.session_state.page, "Start Analysis")
            if st.button(label):
                st.session_state.page = f"{st.session_state.page}_analysis"
                st.session_state.form_submitted = False
                st.rerun()

    # ANALYSIS PAGES (imported from separate files)
    elif st.session_state.page == "cdr_analysis":
        show_cdr_analysis(
            st.session_state.case_number,
            st.session_state.investigator_name,
            st.session_state.case_name,
            st.session_state.remarks
        )
    elif st.session_state.page == "ipdr_analysis":
        show_ipdr_analysis(
            st.session_state.case_number,
            st.session_state.investigator_name,
            st.session_state.case_name,
            st.session_state.remarks
        )
    elif st.session_state.page == "firewall_analysis":
        show_firewall_analysis(
            st.session_state.case_number,
            st.session_state.investigator_name,
            st.session_state.case_name,
            st.session_state.remarks
        )
    elif st.session_state.page == "correlation_analysis":
        show_correlation_analysis(
            st.session_state.case_number,
            st.session_state.investigator_name,
            st.session_state.case_name,
            st.session_state.remarks
        )

    st.markdown('</div>', unsafe_allow_html=True)
