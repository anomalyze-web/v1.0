import streamlit as st
import base64
from streamlit_extras.stylable_container import stylable_container

# Import the analysis modules
from CDR_analysis import show_cdr_analysis
from IPDR_analysis import show_ipdr_analysis
from FIREWALL_analysis import show_firewall_analysis
from CO_Relation_analysis import show_correlation_analysis

# --- Helper Functions (Page Views) ---

def show_evidence_library():
    """Placeholder screen for Evidence Library."""
    st.title("Evidence Library")
    st.markdown("---")
    st.text_input("Search Evidence Library", placeholder="Enter keywords, hash values, or file names...")
    st.markdown('<div style="margin-top: 50px; padding: 30px; border: 1px dashed #555; border-radius: 10px; color: #aaa; text-align: center;">\
        <h3>No Evidence Uploaded Yet</h3>\
        <p>Start a new case to upload and categorize digital evidence.</p>\
    </div>', unsafe_allow_html=True)

def show_search_cases():
    """Placeholder screen for Search Cases."""
    st.title("Search Historical Cases")
    st.markdown("---")
    st.text_input("Search Cases", placeholder="Enter case number, investigator name, or keywords...")
    st.markdown('<div style="margin-top: 50px; padding: 30px; border: 1px dashed #555; border-radius: 10px; color: #aaa; text-align: center;">\
        <h3>No Cases Archived</h3>\
        <p>Completed case analyses will appear here for future reference and searching.</p>\
    </div>', unsafe_allow_html=True)

def show_legal_reference():
    """Placeholder screen for Legal Reference."""
    st.title("Legal Reference and Standards")
    st.markdown("---")
    st.markdown('<div style="padding: 30px; border: 1px dashed #555; border-radius: 10px; color: #aaa;">\
        <p>This section is reserved for relevant legal statutes, compliance documentation, and digital forensics standards.</p>\
        <p>Content to be integrated...</p>\
    </div>', unsafe_allow_html=True)

def show_new_case_selector():
    """Selector for the specific type of case data to be uploaded."""
    st.markdown(f"### Select Data Type for New Case:")
    
    col1, col2, col3, col4 = st.columns(4)

    # Use a single, dark blue button color scheme for consistency
    button_style = """
        button {
            background-color: #15425b !important;
            color: #fff !important;
            border-radius: 12px;
            height: 60px;
            font-size: 1.1rem;
            width: 100%;
            margin-bottom: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #367588 !important; /* Darker hover */
        }
    """
    
    with col1:
        with stylable_container("cdr_button", css_styles=button_style):
            if st.button("CDR Analysis", key="select_cdr"):
                st.session_state.page = "cdr"
                st.session_state.form_submitted = False
                st.rerun()

    with col2:
        with stylable_container("ipdr_button", css_styles=button_style):
            if st.button("IPDR Analysis", key="select_ipdr"):
                st.session_state.page = "ipdr"
                st.session_state.form_submitted = False
                st.rerun()

    with col3:
        with stylable_container("firewall_button", css_styles=button_style):
            if st.button("Firewall Logs", key="select_firewall"):
                st.session_state.page = "firewall"
                st.session_state.form_submitted = False
                st.rerun()

    with col4:
        with stylable_container("correlation_button", css_styles=button_style):
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
        /* This prevents Streamlit's default padding from creating unnecessary space */
        padding-top: 150px !important; /* Adjusted top padding for new header height */
        padding-left: 40px;
        padding-right: 40px;
        padding-bottom: 40px;
        max-width: 100% !important;
    }
    body, [data-testid="stAppViewContainer"] {
        background: #001928 !important; /* New Dark Background */
    }

    /* 2. Header Style */
    .dashboard-header {
        position: fixed;
        left: 0;
        top: 0;
        width: 100vw;
        height: 100px; /* Reduced Height */
        z-index: 10;
        background: #15425b; /* New Title Bar Color */
        padding: 16px 40px; /* Adjusted padding */
        display: flex;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        box-sizing: border-box;
    }
    .dashboard-title {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        margin-right: 32px;
    }

    /* 3. User Actions (Logout/Avatar) */
    .dashboard-header-spacer {
        flex: 1;
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
        background: #367588; /* Darker avatar */
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        color: #fff;
    }
    
    /* 4. Top Navigation Buttons */
    .top-nav-button {
        background-color: #367588; /* Dark Teal */
        color: white;
        border: none;
        padding: 12px 20px;
        margin-right: 15px;
        border-radius: 8px;
        font-size: 1.05rem;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .top-nav-button:hover {
        background-color: #4c8a99;
    }
    .top-nav-button.active {
        background-color: #15425b; /* Active state is header color */
    }

    /* 5. Main Content Area */
    .dashboard-main {
        padding-top: 20px;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #fff; /* White header text */
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
    </style>
    """, unsafe_allow_html=True)

def dashboard(username):
    # Set page config here to ensure the wide layout sticks
    st.set_page_config(page_title="Anomalyze Dashboard", layout="wide")
    dashboard_css()

    # --- Session State Initialization ---
    if "page" not in st.session_state:
        st.session_state.page = "main"
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False

    # --- Header and Navigation ---
    
    # 1. Header (Fixed position)
    st.markdown(f'''
        <div class="dashboard-header">
            <div class="dashboard-title">Anomalyze</div>
            <div class="dashboard-header-spacer"></div>
            <div class="user-actions">
                <div class="user-box">
                    {username.upper()}
                    <div class="user-avatar">👤</div>
                </div>
                
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # 2. Top Navigation Bar (Just below the header)
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col_logout = st.columns([1, 1, 1, 1, 0.5])

    # Function to create a nav button
    def nav_button(label, key, target_page, col):
        is_active = st.session_state.page == target_page
        with col:
            # We use a markdown-styled button to control its appearance inside the columns
            if st.button(label, key=key, help=f"Go to {label}"):
                st.session_state.page = target_page
                st.rerun()

    with st.container():
        st.markdown('<div style="height: 70px;"></div>', unsafe_allow_html=True) # Spacer
        nav_col1, nav_col2, nav_col3, nav_col4, _ = st.columns([1, 1, 1, 1, 3])
        
        # New Case button logic (goes to selector page)
        with nav_col1:
            if st.button("New Case", key="nav_new_case"):
                st.session_state.page = "new_case_selector"
                st.rerun()

        nav_button("Evidence Library", "nav_evidence", "evidence_library", nav_col2)
        nav_button("Search Cases", "nav_search", "search_cases", nav_col3)
        nav_button("Legal Reference", "nav_legal", "legal_reference", nav_col4)

    # Logout button (separate style)
    with nav_col_logout:
        # Use a simple st.button outside the main column block for cleaner styling
        if st.button("Logout", key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.page = "main"
            st.rerun()


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
