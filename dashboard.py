import streamlit as st

# Dummy functions to satisfy the import requirements from the login page
def show_evidence_library(): pass
def show_search_cases(): pass
def show_legal_reference(): pass
def show_new_case_selector(): pass
def show_cdr_analysis(a, b, c, d): pass
def show_ipdr_analysis(a, b, c, d): pass
def show_firewall_analysis(a, b, c, d): pass
def show_correlation_analysis(a, b, c, d): pass

# --- CSS and Core Function ---

def dashboard_css():
    st.markdown("""
    <style>
    /* Global Background and Padding */
    .main .block-container {
        padding-top: 80px !important; 
        padding-left: 40px;
        padding-right: 40px;
        padding-bottom: 40px;
        max-width: 100% !important;
    }
    body, [data-testid="stAppViewContainer"] {
        background: #001928 !important; /* Dark Background */
    }

    /* Fixed Header Container (Uses CSS Grid for stable alignment) */
    #fixed-header-container {
        position: fixed;
        left: 0;
        top: 0;
        width: 100%;
        height: 60px;
        z-index: 10;
        background: #15425b; /* Requested Title Bar Color */
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        padding: 0 20px;
        
        /* GRID Layout: Left actions, Center space for title, Right spacer */
        /* Columns: auto (left actions) | 1fr (flexible center title) | auto (right spacer/empty) */
        display: grid;
        grid-template-columns: auto 1fr auto; 
        align-items: center;
        gap: 20px;
    }
    
    /* Dashboard Title Styling (Centered using the 1fr middle grid cell) */
    .dashboard-title-text {
        grid-column: 2 / 3; /* Position in the flexible center cell */
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        text-align: center;
        white-space: nowrap;
        margin: 0; 
    }

    /* Left Side Actions Styling */
    .header-actions-left {
        grid-column: 1 / 2; /* Position in the leftmost cell */
        display: flex;
        justify-content: flex-start;
        align-items: center;
        gap: 15px;
    }
    .user-box {
        display: flex;
        align-items: center;
        color: #fff;
        font-size: 1rem;
        font-weight: 500;
        gap: 6px;
        white-space: nowrap;
    }
    .user-avatar {
        width: 30px;
        height: 30px;
        background: #367588; 
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        color: #fff;
    }
    
    /* Style for the Logout Button in the header (Content-fit width) */
    [data-testid="stButton"][key="header_logout"] button {
        background-color: #367588; 
        color: white;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        width: fit-content; /* Force width to fit content */
        min-width: unset; 
        padding: 5px 10px;
        height: 30px;
        transition: background-color 0.2s;
        border: none;
        margin-left: 0; /* Remove any default Streamlit margin that pushes it */
    }
    [data-testid="stButton"][key="header_logout"] button:hover {
        background-color: #e57373; /* Light red hover for danger/logout */
    }
    
    /* Remove Sidebar */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] { display: none !important; }

    /* Remove extra margin/padding from inner markdown elements */
    #fixed-header-container p {
        margin: 0;
        padding: 0;
    }
    </style>
    """, unsafe_allow_html=True)

def dashboard(username):
    st.set_page_config(page_title="Anomalyze Dashboard", layout="wide")
    dashboard_css()

    # --- Session State Initialization (Required for login page logic) ---
    if "page" not in st.session_state:
        st.session_state.page = "main"
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False

    # --- Fixed Header (Title Bar with User/Logout) ---
    st.markdown('<div id="fixed-header-container">', unsafe_allow_html=True)
    
    # 1. Left Content (User Icon, ID, and Logout Button)
    st.markdown('<div class="header-actions-left">', unsafe_allow_html=True)
    
    # User Icon and ID
    st.markdown(f'''
        <div class="user-box">
            <div class="user-avatar">👤</div>
            {username.upper()}
        </div>
    ''', unsafe_allow_html=True)
    
    # Logout Button
    if st.button("Logout", key="header_logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.page = "main"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True) # Close header-actions-left
    
    # 2. Center Content (Dashboard Title)
    st.markdown('<div class="dashboard-title-text">Dashboard</div>', unsafe_allow_html=True)
    
    # 3. Right Spacer (Implicitly created by the grid structure)
    
    st.markdown('</div>', unsafe_allow_html=True) # Close fixed-header-container

    # Main content area (intentionally blank)
    st.markdown('<div style="height: 500px;"></div>', unsafe_allow_html=True)
