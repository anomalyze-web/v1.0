import streamlit as st
import sqlite3
import bcrypt
# NOTE: Ensure 'dashboard.py' exists and contains a 'dashboard' function
# from dashboard import dashboard 

# Placeholder for dashboard function if actual file is missing
def dashboard(username):
    st.title(f"Welcome to the Dashboard, {username}!")
    st.info("Your dashboard content goes here.")
    if st.button("Logout", key="logout_dashboard"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
init_db()

# --- DATABASE HELPER FUNCTIONS ---
def get_db_connection():
    return sqlite3.connect('users.db')

def add_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    # Hash password using bcrypt
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed.decode()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Username already exists
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    # Check hashed password
    if row and bcrypt.checkpw(password.encode(), row[0].encode()):
        return True
    return False

st.set_page_config(page_title="Anomalyze Login", layout="wide")

# --- CUSTOM CSS FOR LOGIN/SIGNUP PAGE (V5 Layout and Color Palette) ---
st.markdown("""
<style>
/* Main Background Color: #15425b */
body, [data-testid="stAppViewContainer"], .main {
    background: #15425b !important; 
}

/* Left Panel (Welcome) - Dark Turquoise Background and Dynamic Height */
.left-panel-custom {
    background-color: #367588; /* Dark Turquoise/Teal */
    border-radius: 24px;
    /* This padding and min-height combination targets visual alignment with the form */
    padding: 70px 30px; 
    width: 100%; 
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    justify-content: center; /* Center content vertically */
    min-height: 480px; /* Adjusted height to match form visually */
    animation: fadeIn 1.2s ease;
    opacity: 0.95;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-30px);}
    to { opacity: 0.95; transform: translateY(0);}
}

/* Left Panel Title - Text Color changed to #15425b (Dark Blue) for visibility on Turquoise background */
.left-panel-title {
    color: #15425b; /* Changed back to dark blue as requested */
    font-size: 5rem; /* Adjusted font size to better fit the box */
    font-weight: bold;
    text-align: center;
    line-height: 1.1;
    letter-spacing: 1px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin: 0;
    width: 100%;
}

.login-title-custom {
    color: #ffff;
    font-size: 2.5rem;
    font-weight: bold;
    text-align: left;
    margin-bottom: 0.5rem;
    margin-top: 0;
    letter-spacing: 1px;
}

/* Input Fields - Grey Background */
input[type="text"], input[type="password"] {
    color: #111 !important;
    background-color: #f0f0f0 !important; /* Light Grey background */
    border: 1.5px solid #bbb !important;
    border-radius: 8px !important;
    transition: border 0.2s, background 0.2s;
}
input[type="text"]::placeholder, input[type="password"]::placeholder {
    color: #888 !important;
    opacity: 0.8 !important;
}
input[type="text"]:hover, input[type="password"]:hover, 
input[type="text"]:focus, input[type="password"]:focus {
    border: 1.5px solid #82c3d6 !important; /* Light turquoise border on focus */
    background-color: #f5f5f5 !important; 
}
.stTextInput label, .stPassword label {
    color: #ffff !important;
}

/* Primary Button (Login/Signup) - Turquoise #82c3d6 */
.stButton>button {
    width: 100%;
    padding: 1.1rem;
    font-size: 1.2rem;
    font-weight: bold;
    border-radius: 10px;
    background:#82c3d6; /* Updated Turquoise */
    color: #15425b; /* Dark text for contrast */
    box-shadow: 0 4px 16px rgba(43,65,98,0.10);
    margin-top: 1.3rem;
    transition: all 0.2s;
    border: none;
    opacity: 0.95;
}
.stButton>button:hover {
    background: #a3d8e6 !important; /* Lighter shade of 82c3d6 for hover */
    color: #15425b !important;
    transform: scale(1.02);
}

/* Link Buttons (Switch Login/Signup) - Link color #40e0d0, Hover color #82c3d6 */
[data-testid="stButton"][key="goto_signup"] button,
[data-testid="stButton"][key="goto_login"] button {
    all: unset; /* Reset Streamlit button styling */
    background: none !important;
    color: #40e0d0 !important; /* Light turquoise link color */
    border: none;
    padding: 0 !important;
    font-size: 1.08rem;
    text-decoration: underline;
    cursor: pointer;
    opacity: 0.9;
    margin-top: 1.7rem;
    display: block;
    text-align: center;
}
/* Link Buttons Hover - Updated to Turquoise #82c3d6 */
[data-testid="stButton"][key="goto_signup"] button:hover,
[data-testid="stButton"][key="goto_login"] button:hover {
    opacity: 1;
    color: #82c3d6 !important; /* Updated hover color */
}

/* ---- Reduce top spacing ---- */
.main .block-container {
    padding-top: 2rem !important;
}
section > div:first-child {
    margin-top: 0rem !important;
    padding-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

def login_signup_ui():
    
    # Logo centered above the main login structure
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.image("logo.png", width=400)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # New Column Ratio: 5% margin, 45% welcome, 5% spacer, 40% login, 5% margin (Total 100%)
    m1, c_welcome, c_spacer, c_login, m2 = st.columns([5, 45, 5, 40, 5])
    
    with c_welcome:
        # Left Panel (Welcome)
        st.markdown('<div class="left-panel-custom">', unsafe_allow_html=True)
        # Title is now correctly inside the custom div in the column, and its CSS color is set to #15425b
        st.markdown('<div class="left-panel-title">Welcome to<br>Anomalyze!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_login:
        # Right Panel (Login/Signup Form)
        st.markdown('<div class="login-box-custom">', unsafe_allow_html=True)
        if not st.session_state.show_signup:
            # Login Form
            st.markdown('<div class="login-title-custom">Login</div>', unsafe_allow_html=True)
            st.markdown('<div style="color:#ffff; margin-bottom:20px;">Welcome back! Please login to your account.</div>', unsafe_allow_html=True)
            
            username = st.text_input("User Name", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            
            login = st.button("LOGIN")
            
            if login:
                if username and password:
                    if check_user(username, password):
                        st.success(f"Welcome, {username}!")
                        st.session_state.logged_in = True
                        st.session_state.current_user = username
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.error("Please enter both username and password.")
            
            # Switch to Sign Up link (Styled via global CSS keys)
            if st.button("Create a new account? Sign Up", key="goto_signup", help="Switch to Sign Up", type="secondary"):
                st.session_state.show_signup = True
                st.rerun()

        else:
            # Sign Up Form
            st.markdown('<div class="login-title-custom">Sign Up</div>', unsafe_allow_html=True)
            st.markdown('<div style="color:#ffff; margin-bottom:20px;">Create a new account to get started.</div>', unsafe_allow_html=True)
            
            new_user = st.text_input("Choose a User Name", key="signup_user")
            new_password = st.text_input("Choose a Password", type="password", key="signup_pass")
            
            signup = st.button("SIGN UP")
            
            if signup:
                if new_user and new_password:
                    if add_user(new_user, new_password):
                        st.success("Account created! You can now log in.")
                        st.session_state.show_signup = False
                        st.rerun()
                    else:
                        st.error("Username already exists! Please choose another.")
                else:
                    st.error("Please enter both a username and password.")
            
            # Switch to Login link (Styled via global CSS keys)
            if st.button("Already have an account? Login", key="goto_login", help="Back to Login", type="secondary"):
                st.session_state.show_signup = False
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    if st.session_state.logged_in:
        dashboard(st.session_state.current_user) 
    else:
        login_signup_ui()

main()
