import streamlit as st
import datetime
import psycopg2
import time

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

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
    )

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
    st.title("Make Payment", text_alignment="center")
    st.write("Safe Payment method.")

    st.markdown("### Step 1: Verify Sale ID")

    if "active_sale" not in st.session_state:
        st.session_state.active_sale = None

    input_sale_id = st.number_input("Enter Sale ID Number", min_value=1, step=1, value=1)
    
    if st.button("Verify", use_container_width=True):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            

            fetch_query = """
                SELECT date, name, product_name, gross_sales, COALESCE(received_amount, 0.00) 
                FROM customer_sales 
                WHERE sale_id = %s;
            """
            cursor.execute(fetch_query, (int(input_sale_id),))
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if row:
                st.session_state.active_sale = {
                    "sale_id": int(input_sale_id),
                    "date": row[0],
                    "name": row[1],
                    "product_name": row[2],
                    "gross_sales": float(row[3]),
                    "current_received": float(row[4])
                }
                st.success(f"Sale ID Found!")
            else:
                st.session_state.active_sale = None
                st.error("Please enter a valid sale ID")
        except Exception as e:
            st.error(f"Lookup Error: {e}")

    if st.session_state.active_sale is not None:
        sale = st.session_state.active_sale

        st.markdown("---")
        st.markdown("### Customer Details")
        st.info(f"""
        * **Customer Name:** {sale['name']}
        * **Enrollment Date:** {sale['date']}
        * **Product Enrolled:** {sale['product_name']}
        * **Product Value:** ₹{sale['gross_sales']:,.2f}
        * **Total Paid:** ₹{sale['current_received']:,.2f}
        """)

        st.markdown("### Step 2: Payment Details")
        with st.form("payment_processing_form", clear_on_submit=True):
            
            payment_date = st.date_input("Payment Processing Date", value=datetime.date.today())
            amount_to_pay = st.number_input("Amount Paid (₹)", min_value=100.0, max_value=(sale['gross_sales'] - sale['current_received']), step=500.0, format="%.2f")
            
            method_options = ["Cash", "UPI / GooglePay / PhonePe", "Net Banking", "Credit Card", "Debit Card"]
            payment_method = st.selectbox("Payment Mode / Method", method_options)
            
            st.markdown("---")
            submit_payment = st.form_submit_button("Submit", use_container_width=True)
            
            if submit_payment:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    insert_split_query = """
                        INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method)
                        VALUES (%s, %s, %s, %s);
                    """
                    
                    cursor.execute(insert_split_query, (
                        sale['sale_id'],
                        payment_date,
                        float(amount_to_pay),
                        payment_method
                    ))

                    new_accumulated_total = sale['current_received'] + float(amount_to_pay)
                    
                    update_customer_query = """
                        UPDATE customer_sales 
                        SET received_amount = %s 
                        WHERE sale_id = %s;
                    """
                    
                    cursor.execute(update_customer_query, (new_accumulated_total, sale['sale_id']))

                    conn.commit()
                    cursor.close()
                    conn.close()

                    st.cache_data.clear()
                    st.session_state.active_sale = None
                    
                    st.success(f"Successfully! Payment of ₹{amount_to_pay:,.2f} processed.")
                    time.sleep(1.5)
                    st.rerun()
                    
                except Exception as db_err:
                    st.error(f"SQL Storage Error Encountered: {db_err}")