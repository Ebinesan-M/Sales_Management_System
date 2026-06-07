import streamlit as st
import pandas as pd
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

if "chosen_category" not in st.session_state:
    st.session_state.chosen_category = "select the categories"
if "chosen_question" not in st.session_state:
    st.session_state.chosen_question = "select the question"

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

left_space, layout_container, right_space = st.columns([1, 4, 1])

with layout_container:
    st.markdown("<h1 style='text-align: center;'>SQL QUESTIONS</h1>", unsafe_allow_html=True)
    st.write("Select a thematic calculation standard category to inspect structural pipeline code behaviors.")
    
    base_categories = ["Basic Queries", "Aggregation Queries", "Join-Based Queries", "Financial Tracking Queries"]
    if st.session_state.chosen_category == "select the categories":
        category_options = ["select the categories"] + base_categories
    else:
        category_options = base_categories
        
    category_selection = st.selectbox(
        "Queries Categories", 
        category_options, 
        index=category_options.index(st.session_state.chosen_category)
    )
    
    if category_selection != st.session_state.chosen_category:
        st.session_state.chosen_category = category_selection
        st.session_state.chosen_question = "select the question"
        st.rerun()
        
    query_to_run = ""
    
    if st.session_state.chosen_category != "select the categories":
        if st.session_state.chosen_category == "Basic Queries":
            base_questions = [
                "Retrieve all records from the customer_sales table.",
                "Retrieve all records from the branches table.",
                "Retrieve all records from the payment_splits table.",
                "Display all sales with status = 'Open'.",
                "Retrieve all sales belonging to the Chennai branch."
            ]
        elif st.session_state.chosen_category == "Aggregation Queries":
            base_questions = [
                "Calculate the total gross sales across all branches.",
                "Calculate the total received amount across all sales.",
                "Calculate the total pending amount across all sales.",
                "Count the total number of sales per branch.",
                "Find the average gross sales amount."
            ]
        elif st.session_state.chosen_category == "Join-Based Queries":
            base_questions = [
                "Retrieve sales details along with the branch name.",
                "Retrieve sales details along with total payment received (using payment_splits).",
                "Show branch-wise total gross sales (using JOIN & GROUP BY).",
                "Display sales along with payment method used.",
                "Retrieve sales along with branch admin name."
            ]
        elif st.session_state.chosen_category == "Financial Tracking Queries":
            base_questions = [
                "Find sales where the pending amount is greater than 5000.",
                "Retrieve top 3 highest gross sales.",
                "Find the branch with highest total gross sales.",
                "Retrieve monthly sales summary (group by month & year).",
                "Calculate payment method-wise total collection (Cash / UPI / Card)."
            ]
            
        if st.session_state.chosen_question == "select the question":
            question_options = ["select the question"] + base_questions
        else:
            question_options = base_questions
            
        question_selection = st.selectbox(
            "Select Question Details", 
            question_options, 
            index=question_options.index(st.session_state.chosen_question)
        )
        
        if question_selection != st.session_state.chosen_question:
            st.session_state.chosen_question = question_selection
            st.rerun()
            
        if st.session_state.chosen_question != "select the question":
            if st.session_state.chosen_question == "Retrieve all records from the customer_sales table.":
                query_to_run = "SELECT * FROM customer_sales;"
            elif st.session_state.chosen_question == "Retrieve all records from the branches table.":
                query_to_run = "SELECT * FROM branches;"
            elif st.session_state.chosen_question == "Retrieve all records from the payment_splits table.":
                query_to_run = "SELECT * FROM payment_splits;"
            elif st.session_state.chosen_question == "Display all sales with status = 'Open'.":
                query_to_run = "SELECT * FROM customer_sales WHERE status = 'Open';"
            elif st.session_state.chosen_question == "Retrieve all sales belonging to the Chennai branch.":
                query_to_run = "SELECT * FROM customer_sales WHERE branch_id = 1;"
            elif st.session_state.chosen_question == "Calculate the total gross sales across all branches.":
                query_to_run = "SELECT SUM(gross_sales) AS total_gross_sales FROM customer_sales;"
            elif st.session_state.chosen_question == "Calculate the total received amount across all sales.":
                query_to_run = "SELECT SUM(received_amount) AS total_received_amount FROM customer_sales;"
            elif st.session_state.chosen_question == "Calculate the total pending amount across all sales.":
                query_to_run = "SELECT SUM(pending_amount) AS total_pending_amount FROM customer_sales;"
            elif st.session_state.chosen_question == "Count the total number of sales per branch.":
                query_to_run = "SELECT branch_id, COUNT(*) AS sales_count FROM customer_sales GROUP BY branch_id ORDER BY branch_id;"
            elif st.session_state.chosen_question == "Find the average gross sales amount.":
                query_to_run = "SELECT AVG(gross_sales) AS average_gross_sales FROM customer_sales;"
            elif st.session_state.chosen_question == "Retrieve sales details along with the branch name.":
                query_to_run = "SELECT cs.*, b.branch_name FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id;"
            elif st.session_state.chosen_question == "Retrieve sales details along with total payment received (using payment_splits).":
                query_to_run = "SELECT cs.sale_id, cs.name, SUM(ps.amount_paid) AS structural_received_total FROM customer_sales cs LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id GROUP BY cs.sale_id, cs.name;"
            elif st.session_state.chosen_question == "Show branch-wise total gross sales (using JOIN & GROUP BY).":
                query_to_run = "SELECT b.branch_name, SUM(cs.gross_sales) AS total_sales_volume FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id GROUP BY b.branch_name;"
            elif st.session_state.chosen_question == "Display sales along with payment method used.":
                query_to_run = "SELECT cs.sale_id, cs.name, ps.payment_method FROM customer_sales cs JOIN payment_splits ps ON cs.sale_id = ps.sale_id;"
            elif st.session_state.chosen_question == "Retrieve sales along with branch admin name.":
                query_to_run = "SELECT cs.*, b.admin_name FROM customer_sales cs JOIN branches b ON cs.branch_id = b.branch_id;"
            elif st.session_state.chosen_question == "Find sales where the pending amount is greater than 5000.":
                query_to_run = "SELECT * FROM customer_sales WHERE pending_amount > 5000;"
            elif st.session_state.chosen_question == "Retrieve top 3 highest gross sales.":
                query_to_run = "SELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3;"
            elif st.session_state.chosen_question == "Find the branch with highest total gross sales.":
                query_to_run = "SELECT branch_id, SUM(gross_sales) AS branch_total FROM customer_sales GROUP BY branch_id ORDER BY branch_total DESC LIMIT 1;"
            elif st.session_state.chosen_question == "Retrieve monthly sales summary (group by month & year).":
                query_to_run = "SELECT EXTRACT(YEAR FROM date) AS year_label, EXTRACT(MONTH FROM date) AS month_label, SUM(gross_sales) AS monthly_turnover FROM customer_sales GROUP BY year_label, month_label ORDER BY year_label DESC, month_label DESC;"
            elif st.session_state.chosen_question == "Calculate payment method-wise total collection (Cash / UPI / Card).":
                query_to_run = "SELECT payment_method, SUM(amount_paid) AS total_collected FROM payment_splits GROUP BY payment_method;"

        if query_to_run != "":
            st.markdown("### Generated Query Code View")
            st.code(query_to_run, language="sql")
            
            st.markdown("---")
            if st.button("Execute Query", use_container_width=True):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute(query_to_run)
                    columns = [desc[0] for desc in cursor.description]
                    data = cursor.fetchall()
                    
                    df_result = pd.DataFrame(data, columns=columns)
                    
                    cursor.close()
                    conn.close()
                    
                    st.markdown("<h3 style='text-align: center;'>Query Output Records</h3>", unsafe_allow_html=True)
                    if not df_result.empty:
                        st.dataframe(df_result, use_container_width=True)
                        st.caption(f"Returned {len(df_result)} valid rows match mapping records.")
                    else:
                        st.info("Query compiled successfully, but returned 0 active data objects.")
                        
                except Exception as query_err:
                    st.error(f"PostgreSQL Execution Failure. Details: {query_err}")