
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Pharmacy Dashboard",
    page_icon="💊",
    layout="wide"
)


# Professional Dashboard Styling
st.markdown(
    '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #F4F7FB;
    }

    h1 {
        color: #16324F;
        font-weight: 800;
    }

    h2, h3 {
        color: #1F456E;
        font-weight: 700;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #E6ECF2;
        box-shadow: 0 3px 10px rgba(22, 50, 79, 0.06);
    }

    [data-testid="stMetricLabel"] {
        color: #62758A;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #16324F;
        font-weight: 800;
    }

    [data-testid="stSidebar"] {
        background-color: #EAF0F6;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Fix text contrast */
    .stApp, .stApp p, .stApp label,
    .stApp span, .stApp div,
    [data-testid="stMarkdownContainer"] {
        color: #26384A;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #16324F !important;
    }

    [data-testid="stSidebar"] * {
        color: #26384A;
    }

    [data-testid="stSelectbox"] *,
    [data-testid="stTextInput"] * {
        color: #26384A;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
        color: #16324F !important;
    }

    </style>
    ''',
    unsafe_allow_html=True
)


df = pd.read_csv(
    "/content/Pharmacy_Sales_Analysis.csv",
    encoding="utf-8-sig"
)

# Interactive Filters
st.sidebar.title("Dashboard Filters")

companies = ["All Companies"] + sorted(
    df["الشركة"].dropna().astype(str).unique().tolist()
)

selected_company = st.sidebar.selectbox(
    "Select Company",
    companies
)

product_search = st.sidebar.text_input(
    "Search Product",
    placeholder="Enter product name..."
)

if selected_company != "All Companies":
    df = df[df["الشركة"].astype(str) == selected_company]

if product_search:
    df = df[
        df["اسم الصنف"].astype(str).str.contains(
            product_search, case=False, na=False
        )
    ]

# Calculations
total_sales = df["إجمالى البيع"].sum()
total_cost = df["إجمالى التكلفة"].sum()
total_profit = df["Product_Profit"].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales else 0

total_products = len(df)
zero_stock = (df["الرصيد"] == 0).sum()
negative_profit = (df["Product_Profit"] < 0).sum()

# Header
st.title("💊 Pharmacy Sales & Inventory Dashboard")
st.caption("Sales and Inventory Analysis | 30 Apr – 30 Oct 2026")

st.divider()

# KPI Cards
st.subheader("Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Sales", f"{total_sales:,.2f} EGP")
c2.metric("Total Cost", f"{total_cost:,.2f} EGP")
c3.metric("Gross Profit", f"{total_profit:,.2f} EGP")
c4.metric("Gross Profit Margin", f"{profit_margin:.2f}%")

c5, c6, c7 = st.columns(3)

c5.metric("Total Products", f"{total_products:,}")
c6.metric("Zero Stock Products", f"{zero_stock:,}")
c7.metric("Negative Profit Products", f"{negative_profit:,}")

st.divider()

# Sales Charts
st.subheader("Sales Analysis")

left, right = st.columns(2)

top_sales = (
    df.nlargest(10, "إجمالى البيع")
    .sort_values("إجمالى البيع", ascending=True)
)

fig1 = px.bar(
    top_sales,
    x="إجمالى البيع",
    y="اسم الصنف",
    orientation="h",
    title="Top 10 Products by Sales",
    labels={
        "إجمالى البيع": "Sales (EGP)",
        "اسم الصنف": "Product"
    }
)

left.plotly_chart(fig1, use_container_width=True)

company_sales = (
    df.groupby("الشركة", as_index=False)["إجمالى البيع"]
    .sum()
    .nlargest(10, "إجمالى البيع")
)

fig2 = px.pie(
    company_sales,
    names="الشركة",
    values="إجمالى البيع",
    title="Top 10 Companies by Sales"
)

right.plotly_chart(fig2, use_container_width=True)

st.divider()

# Profit Analysis
st.subheader("Profit Analysis")

top_profit = (
    df.nlargest(10, "Product_Profit")
    .sort_values("Product_Profit", ascending=True)
)

fig3 = px.bar(
    top_profit,
    x="Product_Profit",
    y="اسم الصنف",
    orientation="h",
    title="Top 10 Products by Gross Profit",
    labels={
        "Product_Profit": "Gross Profit (EGP)",
        "اسم الصنف": "Product"
    }
)

st.plotly_chart(fig3, use_container_width=True)

# Negative profit products
st.subheader("Products with Negative Profit")

negative_df = df[df["Product_Profit"] < 0]

st.dataframe(
    negative_df[[
        "اسم الصنف",
        "الشركة",
        "كمية البيع",
        "إجمالى البيع",
        "إجمالى التكلفة",
        "Product_Profit"
    ]],
    use_container_width=True
)

st.divider()

st.subheader("Inventory Analysis")

# Zero stock products
zero_df = df[df["الرصيد"] == 0].copy()

st.markdown("### 🔴 Products with Zero Stock")

st.metric("Zero Stock Products", len(zero_df))

zero_top = zero_df.nlargest(15, "كمية البيع")

st.dataframe(
    zero_top[[
        "اسم الصنف",
        "الشركة",
        "كمية البيع",
        "إجمالى البيع",
        "الرصيد"
    ]],
    use_container_width=True
)

# High stock and low sales
st.markdown("### 🟠 High Stock / Low Sales Candidates")

slow_stock = df[
    (df["الرصيد"] >= 10) &
    (df["كمية البيع"] <= 2)
].copy()

st.caption(
    "Screening candidates based on current stock and cumulative sales "
    "during the analysis period. These are not confirmed dead-stock items."
)

st.metric("Products to Review", len(slow_stock))

st.dataframe(
    slow_stock[[
        "اسم الصنف",
        "الشركة",
        "كمية البيع",
        "الرصيد",
        "إجمالى البيع"
    ]].sort_values("الرصيد", ascending=False),
    use_container_width=True
)

# Stock vs sales
st.markdown("### 📊 Current Stock vs Sales Quantity")

fig4 = px.scatter(
    df,
    x="كمية البيع",
    y="الرصيد",
    hover_name="اسم الصنف",
    title="Current Stock vs Sales Quantity",
    labels={
        "كمية البيع": "Sales Quantity (6 Months)",
        "الرصيد": "Current Stock"
    }
)

st.plotly_chart(fig4, use_container_width=True)
