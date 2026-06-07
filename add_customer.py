import streamlit as st
import datetime
import psycopg2
import time
import re

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Access Denied. Please log in first.")
    time.sleep(1)
    st.session_state.logged_in = False
    st.stop()

user_role = st.session_state.get("role", "Admin")
user_branch = st.session_state.get("branch", "All")
user_real_name = st.session_state.get("admin_name", "User")

DB_HOST = "localhost"
DB_NAME = "sales intelligence hub"
DB_USER = "postgres"
DB_PASS = "ppasd"
DB_PORT = "5432"

branch_id_mapping = {
    "Chennai": 1,
    "Bangalore": 2,
    "Hyderabad": 3,
    "Delhi": 4,
    "Mumbai": 5,
    "Pune": 6,
    "Kolkata": 7,
    "Ahmedabad": 8
}

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
    )

@st.cache_data(ttl=30)
def fetch_distinct_products():
    """Dynamically pull existing distinct products from your database column."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT product_name FROM customer_sales WHERE product_name IS NOT NULL ORDER BY product_name;")
        products = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return products if products else ["Default Deep Learning Course"]
    except Exception:
        return ["Deep Learning Basics", "Advanced Neural Networks", "Computer Vision Masterclass"]

st.sidebar.title("NEXUS INSTITUTE")
st.sidebar.markdown("### Navigation")
if st.sidebar.button("Customer Sales Dashboard", use_container_width=True):
    st.switch_page("pages/page_2.py")
if st.sidebar.button("Add Customer", use_container_width=True):
    st.switch_page("pages/add_customer.py")
if st.sidebar.button("Make Payment", use_container_width=True):
    st.switch_page("pages/make_payment.py")
if st.sidebar.button("Test Query", use_container_width=True):
    st.switch_page("pages/test_query.py")

st.sidebar.markdown("---")
st.sidebar.markdown("### Profile Info")
st.sidebar.write(f"**Name:** {user_real_name.upper()}")
st.sidebar.write(f"**Role:** {user_branch.upper()} - {user_role}")  

st.sidebar.markdown("---")
if st.sidebar.button("Log Out", use_container_width=True):
    st.session_state.clear()
    st.rerun()  

left_space, layout_container, right_space = st.columns([2, 2, 2])

with layout_container:
   
    st.title("Add Customer", text_alignment="center")
    st.write("New Customer Entry Form.")

    # Form boundary configuration
    with st.form("add_customer_form", clear_on_submit=False):
        st.markdown("### Record Parameters")
        
        # Branch Input Handling
        if user_role.lower() == "super admin":
            branch_options = list(branch_id_mapping.keys())
            selected_branch_name = st.selectbox("Branch Location", branch_options)
        else:
            display_branch = user_branch if user_branch in branch_id_mapping else "Chennai"
            st.selectbox("Assigned Branch", [display_branch], disabled=True)
            selected_branch_name = display_branch

        sale_date = st.date_input("Registration Date", value=datetime.date.today())
        customer_name = st.text_input("Customer Name", value="", placeholder="Enter name")
        mobile_input = st.text_input("Mobile Number", value="", placeholder="e.g., 9876543210")
        
        db_products = fetch_distinct_products()
        product_name = st.selectbox("Product Enrolled", db_products)
        gross_sales = st.number_input("Gross Sales Amount (₹)", min_value=0.0, step=500.0, format="%.2f")

        st.markdown("---")
        submit_record = st.form_submit_button("Submit", use_container_width=True)


    if submit_record:
        if not customer_name.strip():
            st.error("Submission Denied: Please fill out the **Customer Name** field.")
        elif not mobile_input.strip():
            st.error("Submission Denied: Please provide a valid **Mobile Number**.")
        elif gross_sales <= 0:
            st.error("Submission Denied: **Gross Sales Amount** must be greater than zero.")
        else:
            numeric_mobile = re.sub(r"\D", "", mobile_input)
            
            if len(numeric_mobile) < 10:
                st.error("Formatting Error: Mobile number must contain at least 10 digits.")
            else:
                final_mobile = numeric_mobile[-10:]
                target_branch_id = branch_id_mapping.get(selected_branch_name, 1)

                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    insert_query = """
                        INSERT INTO customer_sales (branch_id, date, name, mobile_number, product_name, gross_sales, received_amount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """

                    initial_received = 0.00
                    
                    record_data = (
                        int(target_branch_id),
                        sale_date,
                        customer_name.strip(),
                        final_mobile,
                        product_name,
                        float(gross_sales),
                        initial_received,
                    )
                    
                    cursor.execute(insert_query, record_data)
                    conn.commit()
                    
                    cursor.close()
                    conn.close()
                    
                    st.cache_data.clear()
                    st.success(f"Success! Record added.")
                    time.sleep(1)
                except Exception as db_err:
                    st.error(f"SQL Storage Exception Encountered. Details: {db_err}")