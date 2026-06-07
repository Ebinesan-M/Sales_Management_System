import streamlit as st
import pandas as pd
import psycopg2 
import time
import plotly.express as px

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Access Denied. Please log in first.")
    time.sleep(1)
    st.session_state.logged_in = False
    st.stop()

user_role = st.session_state.get("role", "Admin")
user_branch = st.session_state.get("branch", "All")
user_real_name = st.session_state.get("admin_name", "User")

if "welcomed" not in st.session_state:
    st.session_state.welcomed = False

DB_HOST = "localhost"
DB_NAME = "sales intelligence hub"
DB_USER = "postgres"
DB_PASS = "ppasd"
DB_PORT = "5432"

@st.cache_data(ttl=60)
def load_postgres_data():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    query = "SELECT * FROM customer_sales;"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if not st.session_state.welcomed:
    left_co, cent_co, right_co = st.columns([2, 2, 2])
    with cent_co:
        st.subheader("Welcome", text_alignment="center")
        st.title(user_real_name.upper(), text_alignment="center")
        st.subheader(f"{user_role} for ({user_branch})", text_alignment="center") 
        
        countdown_placeholder = st.empty()
        for seconds_left in range(5, 0, -1):
            countdown_placeholder.info(f"Loading database in {seconds_left} seconds...")
            time.sleep(1)
        countdown_placeholder.empty()
    
    st.session_state.welcomed = True
    st.rerun()

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

st.title("Customer Sales Dashboard")

try:
    df_raw = load_postgres_data()
    
    date_col = 'date' if 'date' in df_raw.columns else (df_raw.select_dtypes(include=['datetime64', 'object']).columns[0] if len(df_raw.columns) > 0 else None)
    if date_col and df_raw[date_col].dtype == 'object':
        df_raw[date_col] = pd.to_datetime(df_raw[date_col], errors='coerce')

    branch_id_mapping = {
        "Chennai": 1, "Bangalore": 2, "Hyderabad": 3, "Delhi": 4,
        "Mumbai": 5, "Pune": 6, "Kolkata": 7, "Ahmedabad": 8
    }

    st.write("### Database")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if user_role.lower() == "super admin":
            all_branches_options = ["All Branches", "Chennai", "Bangalore", "Hyderabad", "Delhi", "Kolkata", "Mumbai", "Pune", "Ahmedabad"]
            filter_branch = st.selectbox("Branch", all_branches_options)
        else:
            filter_branch = st.selectbox("Branch", [user_branch], disabled=True)

    with col2:
        if 'product_name' in df_raw.columns:
            available_products = ["All Products"] + sorted(df_raw['product_name'].dropna().unique().tolist())
        else:
            available_products = ["All Products"]
        filter_product = st.selectbox("Product Name", available_products)

    with col3:
        min_date = df_raw[date_col].min().date() if (date_col and not df_raw[date_col].isna().all()) else None
        filter_start_date = st.date_input("Starting Day", value=min_date)

    with col4:
        max_date = df_raw[date_col].max().date() if (date_col and not df_raw[date_col].isna().all()) else None
        filter_end_date = st.date_input("Ending Day", value=max_date)

    df_filtered = df_raw.copy()

    if filter_branch != "All Branches" and filter_branch != "All":
        target_id = branch_id_mapping.get(filter_branch)
        if target_id is not None and 'branch_id' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['branch_id'] == target_id]
        elif 'branch' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['branch'].str.lower() == filter_branch.lower()]
        elif 'city' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['city'].str.lower() == filter_branch.lower()]

    if filter_product != "All Products" and 'product_name' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['product_name'] == filter_product]

    if date_col and filter_start_date and filter_end_date:
        df_filtered = df_filtered[
            (df_filtered[date_col].dt.date >= filter_start_date) & 
            (df_filtered[date_col].dt.date <= filter_end_date)
        ]

    st.write("### Live Database Table")
    if not df_filtered.empty:
        st.dataframe(df_filtered, use_container_width=True)
        st.markdown("---")
        
        left_pad, master_center_container, right_pad = st.columns([1, 4, 1])
        
        with master_center_container:
            left_summary_col, right_chart_col = st.columns([2, 3])
            
            sales_col = 'gross_sales'
            received_col = 'received_amount'
            pending_col = 'pending_amount'

            total_sales_val = df_filtered[sales_col].sum() if sales_col in df_filtered.columns else 0.0
            total_received_val = df_filtered[received_col].sum() if received_col in df_filtered.columns else 0.0
            
            if pending_col in df_filtered.columns:
                total_pending_val = df_filtered[pending_col].sum()
            elif sales_col and received_col:
                total_pending_val = total_sales_val - total_received_val
            else:
                total_pending_val = 0.0

            with left_summary_col:
                st.write("### Summary Metrics")
                if sales_col in df_filtered.columns:
                    st.metric(label="Total Sales", value=f"₹{total_sales_val:,.2f}")
                else:
                    st.error("Column 'gross_sales' not found")
                    
                if received_col in df_filtered.columns:
                    st.metric(label="Total Received", value=f"₹{total_received_val:,.2f}")
                else:
                    st.error("Column 'received_amount' not found")
                    
                st.metric(label="Total Pending", value=f"₹{total_pending_val:,.2f}")

            with right_chart_col:
                if total_received_val == 0 and total_pending_val <= 0:
                    st.info("No financial data available to generate chart breakdowns.")
                else:
                    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>Summary Breakdown</h3>", unsafe_allow_html=True)
                    
                    chart_data = pd.DataFrame({
                        "Financial Status": ["Total Received", "Total Pending"],
                        "Amount": [total_received_val, max(0.0, total_pending_val)] 
                    })

                    fig = px.pie(
                        chart_data, 
                        values="Amount", 
                        names="Financial Status", 
                        hole=0.4,
                        color="Financial Status",
                        color_discrete_map={
                            "Total Received": "#2ecc71",
                            "Total Pending": "#e74c3c"
                        }
                    )

                    fig.update_traces(
                        textposition='inside', 
                        textinfo='percent+value',
                        hovertemplate="<b>%{label}</b><br>Value: ₹%{value:,.2f}<br>Percentage: %{percent}<extra></extra>"
                    )
                    
                    fig.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
                        height=320
                    )

                    st.plotly_chart(fig, use_container_width=True)
            
    else:
        st.warning("No records found matching current criteria filters.")
        
except Exception as e:
    st.error(f"Database Error. Details: {e}")