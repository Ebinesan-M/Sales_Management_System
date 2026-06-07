import streamlit as st
import time

st.set_page_config(
    page_title="Nexus Institute of Technology",
    layout="wide"  
)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = "Guest"

ADMIN_USER = "superadmin"
ADMIN_PASSWORD = "super123"

def login_view():
    
    left_co, cent_co, right_co = st.columns([2, 2, 2])
    with cent_co:
        st.header("Welcome to",text_alignment="center")
        st.title("NEXUS INSTITUTE",text_alignment="center")
        st.subheader("Deep Learning for High-Level Success",text_alignment="center")
        
        with st.form("login_form"):
            st.write("System Login")
            username = st.text_input("Username", placeholder="username")
            password = st.text_input("Password", type="password", placeholder="password")
            submit_button = st.form_submit_button("Login")

            if submit_button:
                if username == ADMIN_USER and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.role = "SUPER ADMIN"
                    st.session_state.branch = "All BRANCHES" 
                    st.session_state.admin_name = "Victor"
                    st.success("Login Successful!")
                    time.sleep(0.5)
                    st.rerun() 
                    
                elif username in ["admin_chennai", "admin_bangalore", "admin_hyderabad", "admin_delhi", 
                                  "admin_kolkata", "admin_mumbai", "admin_pune", "admin_ahmedabad"] and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.role = "ADMIN"       
                    
                    extracted_branch = username.split("_")[1].title().capitalize()
                    st.session_state.branch = extracted_branch
                    
                    branch_admins = {
                        "Chennai": "Arun Kumar",
                        "Bangalore": "Ravi Shankar",
                        "Hyderabad": "Suresh Reddy",
                        "Delhi": "Neha Sharma",
                        "Mumbai": "Rahul Mehta",
                        "Pune": "Amit Patil",
                        "Kolkata": "Subham Ghosh",
                        "Ahmedabad": "Raj Patel"
                    }

                    st.session_state.admin_name = branch_admins.get(extracted_branch, f"{extracted_branch} Admin")
                 
                    
                    st.success(f"Login Successful! Branch: {extracted_branch}")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid Username or Password.")

if not st.session_state.logged_in:
    login_page = st.Page(login_view, title="Login",)
    pg = st.navigation([login_page], position="hidden")
else:
    dashboard_page = st.Page("pages/page_2.py", title="Sales Dashboard")
    add_customer_page = st.Page("pages/add_customer.py", title="Add Customer")
    make_payment_page = st.Page("pages/make_payment.py", title="Make Payment")
    test_query_page = st.Page("pages/test_query.py", title="Test Query")
    
    pg = st.navigation([dashboard_page, add_customer_page, make_payment_page, test_query_page], position="hidden")

pg.run()