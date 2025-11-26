import streamlit as st
import base64
from streamlit_extras.stylable_container import stylable_container

from CDR_analysis import show_cdr_analysis
from IPDR_analysis import show_ipdr_analysis
from FIREWALL_analysis import show_firewall_analysis
from CO_Relation_analysis import show_correlation_analysis

def show_cdr_analysis(case_number, investigator_name, case_name, remarks):
    st.header("CDR Analysis Page")
    st.write(f"Case: {case_name}, Investigator: {investigator_name}")
def show_ipdr_analysis(case_number, investigator_name, case_name, remarks):
    st.header("IPDR Analysis Page")
    st.write(f"Case: {case_name}, Investigator: {investigator_name}")
def show_firewall_analysis(case_number, investigator_name, case_name, remarks):
    st.header("FIREWALL Analysis Page")
    st.write(f"Case: {case_name}, Investigator: {investigator_name}")
def show_correlation_analysis(case_number, investigator_name, case_name, remarks):
    st.header("CO-RELATION Analysis Page")
    st.write(f"Case: {case_name}, Investigator: {investigator_name}")

def show_evidence_library():
    st.title("Evidence Library")
    st.markdown("---")
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"
        st.rerun()

    st.text_input("Search Evidence Library", placeholder="Enter keywords, hash values, or file names...")
    st.markdown('<div style="margin-top: 50px; padding: 30px; border: 1px dashed #555; border-radius: 10px; color: #aaa; text-align: center;">\
    <h3>No Evidence Uploaded Yet</h3>\
    <p>Start a new case to upload and categorize digital evidence.</p>\
    </div>', unsafe_allow_html=True)

def show_search_cases():
    st.title("Search Historical Cases")
    st.markdown("---")
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"
        st.rerun()

    st.text_input("Search Cases", placeholder="Enter case number, investigator name, or keywords...")
    st.markdown('<div style="margin-top: 50px; padding: 30px; border: 1px dashed #555; border-radius: 10px; color: #aaa; text-align: center;">\
    <h3>No Cases Archived</h3>\
    <p>Completed case analyses will appear here for future reference and searching.</p>\
    </div>', unsafe_allow_html=True)

def show_legal_reference():
    st.title("Legal Reference and Standards")
    st.markdown("---")
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown('<div style="padding: 30px; border: 1px dashed #555; border-radius: 10px; color: #aaa;">\
    <p>This section is reserved for relevant legal statutes, compliance documentation, and digital forensics standards.</p>\
    <p>Content to be integrated...</p>\
    </div>', unsafe_allow_html=True)

def show_new_case_selector():
    st.markdown(f"### Select Data Type for New Case:")

    if st.button("⬅ Back to Dashboard", key="back_to_dash_new_case_sel"):
        st.session_state.page = "main"
        st.rerun()

    col1, col2, col3, col4 = st.columns(4)

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

def inject_css():
    # The external link is kept separate for safety.
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">', unsafe_allow_html=True)
    
    # CSS compressed for injection reliability, with height adjustments for the header and navigation.
    css_code_compressed = """
<style>
[data-testid="stAppViewContainer"]{margin-top:0!important;padding-top:0!important;}
body,[data-testid="stAppViewContainer"]{background:#001928!important;}
[data-testid="stSidebar"],[data-testid="stSidebarContent"]{display:none!important;}

/* HEADER HEIGHT 120px to hold two rows (Title/Logout + Nav Buttons) */
#fixed-header-container{
    position:fixed;
    left:0;
    top:0;
    width:100%;
    z-index:10;
    padding:0 40px;
    background:#15425b;
    box-shadow:0 4px 12px rgba(0,0,0,0.3);
    height:120px;
    display:flex;
    flex-direction:column;
    justify-content:flex-start; 
}
/* Top row for User/Title/Logout */
.fixed-header-content{
    width:100%;
    display:flex;
    align-items:center;
    height: 60px; 
    /* NEW FIX: Pin row to the absolute top of the container and add padding to move content down */
    position: absolute;
    top: 0;
    padding-top: 10px; /* Use this to adjust vertical centering relative to top edge */
}
/* Bottom row for Navigation Buttons */
.fixed-nav-row{
    width:100%;
    display:flex;
    align-items:center;
    height: 60px;
    padding-bottom: 5px;
    /* NEW FIX: Pin this row exactly 60px from the top */
    position: absolute;
    top: 60px;
}

/* Adjusted title font size and margin to fit the header */
.dashboard-title{font-size:1.8rem;font-weight:700;color:#fff;text-align:center;margin:0;line-height:1.2;}
.user-box{font-size:1.0rem;font-weight:600;color:#fff;display:flex;align-items:center;gap:8px;}
.user-avatar{width:30px;height:30px;background:#367588;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.0rem;color:#fff;}

/* Main Navigation Buttons (used by stylable_container) */
.main-nav-button button{
    background-color:#1c4868!important;
    color:white;
    border:2px solid #61a3cd!important;
    border-radius:8px;
    font-size:1.05rem;
    font-weight:600;
    width:100%;
    height:40px;
    margin:0;
    transition:all 0.2s;
}
.main-nav-button button:hover{background-color:#367588!important;border-color:#fff!important;}

/* Adjusted Logout button size to fit the header */
[data-testid="stButton"][key="header_logout"] button{background-color:#367588;color:white;border-radius:8px;font-size:0.9rem;font-weight:600;width:80px;padding:5px 10px;height:30px;margin:0;transition:background-color 0.2s;border:none;}
[data-testid="stButton"][key="header_logout"] button:hover{background-color:#e57373;}

/* Main Content Area Padding - Adjusted to clear 120px header + 10px buffer */
.main .block-container{padding-top:130px!important;padding-left:40px;padding-right:40px;padding-bottom:40px;max-width:100%!important;}
.section-header{font-size:1.8rem;font-weight:700;color:#3a7ba4!important;margin-top:30px;margin-bottom:15px;border-bottom:2px solid #367588;padding-bottom:5px;}
.placeholder-box{background:#15425b;color:#99aab5;padding:20px;border-radius:12px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,0.15);}
.placeholder-box h4{margin-top:0;color:#fff;}
</style>
"""
    st.markdown(css_code_compressed, unsafe_allow_html=True)


def dashboard(username):
    st.set_page_config(page_title="Anomalyze Dashboard", layout="wide")
    
    # 1. CSS INJECTION BLOCK (Must be called first)
    inject_css()
    
    # 2. Session State Initialization
    if "page" not in st.session_state:
        st.session_state.page = "main"
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True
    if "current_user" not in st.session_state:
        st.session_state.current_user = username

    # 3. FIXED HEADER HTML STRUCTURE (Now 120px tall, holds all header elements)
    st.markdown('<div id="fixed-header-container">', unsafe_allow_html=True)

    # --- TOP ROW: User, Title, Logout ---
    st.markdown('<div class="fixed-header-content">', unsafe_allow_html=True)
    user_col, title_col, logout_col = st.columns([2, 6, 2])

    with user_col:
        st.markdown(f'''
<div class="user-box" style="justify-content: flex-start;">
<div class="user-avatar">👤</div>
{username.upper()}
</div>
''', unsafe_allow_html=True)

    with title_col:
        st.markdown('<div class="dashboard-title">Anomalyze Dashboard</div>', unsafe_allow_html=True)


    with logout_col:
        st.markdown('<div style="width: 100%; display: flex; justify-content: flex-end; align-items: center;">', unsafe_allow_html=True)
        if st.button("Logout", key="header_logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.page = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Closes fixed-header-content (Top Row)
    
    # --- BOTTOM ROW: Navigation Buttons ---
    st.markdown('<div class="fixed-nav-row">', unsafe_allow_html=True)
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

    def nav_button(label, key, target_page, col):
        with col:
            with stylable_container(f"nav_button_{key}", css_styles=".main-nav-button"):
                if st.button(label, key=key, help=f"Go to {label}"):
                    st.session_state.page = target_page
                    st.rerun()

    nav_button("New Case", "nav_new_case", "new_case_selector", nav_col1)
    nav_button("Evidence Library", "nav_evidence", "evidence_library", nav_col2)
    nav_button("Search Cases", "nav_search", "search_cases", nav_col3)
    nav_button("Legal Reference", "nav_legal", "legal_reference", nav_col4)

    st.markdown('</div>', unsafe_allow_html=True) # Closes fixed-nav-row (Bottom Row)
    
    st.markdown('</div>', unsafe_allow_html=True) # Closes fixed-header-container

    # 5. MAIN CONTENT AREA
    st.markdown('<div class="dashboard-main">', unsafe_allow_html=True)

    if st.session_state.page == "main":
        
        st.markdown('<h2 class="section-header">Bookmarked Cases</h2>', unsafe_allow_html=True)
        st.markdown('<div class="placeholder-box"><h4>No bookmarked cases available.</h4><p>Use the bookmark feature on case analysis pages to quickly access important investigations.</p></div>', unsafe_allow_html=True)

        st.markdown('<h2 class="section-header">Recent Activity</h2>', unsafe_allow_html=True)
        st.markdown('<div class="placeholder-box"><h4>No recent cases analyzed.</h4><p>Start a new case using the "New Case" button above to begin your analysis.</p></div>', unsafe_allow_html=True)

    elif st.session_state.page == "new_case_selector":
        show_new_case_selector()

    elif st.session_state.page == "evidence_library":
        show_evidence_library()
    elif st.session_state.page == "search_cases":
        show_search_cases()
    elif st.session_state.page == "legal_reference":
        show_legal_reference()

    elif st.session_state.page in ["cdr", "ipdr", "firewall", "correlation"]:
        st.markdown(f"### Uploading **{st.session_state.page.upper()}** Case")

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

        if st.session_state.form_submitted:
            analysis_labels = {
                "cdr": "Start CDR Analysis",
                "ipdr": "Start IPDR Analysis",
                "firewall": "Start FIREWALL Analysis",
                "correlation": "Start CO-RELATION Analysis"
            }
            label = analysis_labels.get(st.session_state.page, "Start Analysis")
            if st.button(label, key=f"start_{st.session_state.page}_analysis"):
                st.session_state.page = f"{st.session_state.page}_analysis"
                st.session_state.form_submitted = False
                st.rerun()

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
