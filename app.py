import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Customer Retention Dashboard",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("Customer Retention and Churn Analysis Dashboard")
st.caption("Business Intelligence Dashboard  : Customer Analytics & Retention Strategy")


df = pd.read_csv("SampleSuperstore.csv", encoding="latin1")

CHART_HEIGHT = 500
CHART_WIDTH = 900

def apply_chart_style(fig):
    fig.update_layout(
        height=CHART_HEIGHT,
        width=CHART_WIDTH,
        template="plotly_white",
        title_x=0.1,
        font=dict(size=14),
        margin=dict(l=40, r=40, t=70, b=40)
    )
    return fig

st.subheader("Executive Summary")

st.write("""
This analysis evaluates customer retention performance, churn analysis,
customer segmentation, and overall business profitability.

The findings indicate that repeat customers contribute significantly to total revenue,
while increasing inactivity among certain customer groups may impact long-term business growth
and customer lifetime value.

The dashboard also highlights seasonal revenue trends, profitability risks,
and opportunities for customer retention optimization.
""")

st.markdown("---")

with st.expander("Data Overview"):
    st.write("Dataset Shape:", df.shape)
    st.write("Sample Data:", df.head())

    null_val = df.isnull().sum().sum()

    st.write("Total Null Values:", null_val)

    if null_val == 0:
        st.success("Dataset contains no missing values.")
    else:
        st.error("Dataset contains missing values.")

    st.write("Sales Summary Statistics:", df["Sales"].describe())

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])

    st.write("Data Types:", df.dtypes)

    df["Profit Margin"] = (df["Profit"] / df["Sales"]) * 100

    df["Month Name"] = df["Order Date"].dt.month_name()

    month_order = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]

    df["Month Name"] = pd.Categorical(
        df["Month Name"],
        categories=month_order,
        ordered=True
    )

    df["Month"] = df["Order Date"].dt.month

st.markdown("---")

with st.expander("Customer-Level Metrics"):

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Customers", df["Customer ID"].nunique())

    with col2:
        st.metric("Total Orders", df["Order ID"].nunique())

    with col3:
        st.metric("Total Revenue", f"${df['Sales'].sum():,.2f}")

    col4, col5 = st.columns([1, 2])

    with col4:
        st.metric("Total Profit", f"${df['Profit'].sum():,.2f}")

    with col5:
        st.metric(
            "Analysis Period",
            f"{df['Order Date'].min().date()} to {df['Order Date'].max().date()}"
        )

st.markdown("---")

with st.expander("Customer Analytics"):

    st.subheader("A. Customer Segmentation Analysis")

    cust_summary = df.groupby(
        ["Customer ID", "Customer Name"]
    ).agg({
        "Sales": "sum",
        "Profit": "sum",
        "Order ID": "nunique",
        "Order Date": "max"
    }).reset_index()

    cust_summary.columns = [
        "Customer ID",
        "Customer Name",
        "Total Sale",
        "Total Profit",
        "Total Orders",
        "Last Purchase"
    ]

    cust_summary["Segment"] = cust_summary["Total Sale"].apply(
        lambda x:
        "High Value" if x > 10000
        else ("Medium Value" if x > 5000 else "Low Value")
    )

    st.write("Customer Distribution by Segment:",cust_summary["Segment"].value_counts())

    st.markdown("---")

    st.write( "Revenue Contribution by Customer Segment:",cust_summary.groupby("Segment")["Total Sale"].sum())

    st.markdown("---")

    segment_fig = px.pie(
        cust_summary,
        names="Segment",
        values="Total Sale",
        title="Revenue Contribution by Customer Segment"
    )

    segment_fig = apply_chart_style(segment_fig)

    st.plotly_chart(segment_fig, use_container_width=True)

    with st.expander("Insights"):

        st.info("""
Observation:
Low-value customers collectively contribute to total revenue,
while high-value customers generate disproportionately higher individual revenue contributions.

Business Impact:
The business remains highly dependent on customer retention and repeat purchasing behavior.

Recommendation:
The organization should strengthen customer loyalty initiatives,
personalized engagement strategies, and retention campaigns to improve customer lifetime value.
""")

    st.markdown("---")
    st.subheader("B. Repeat Customer Analysis")

    st.write( "Top Repeat Customers:",df["Customer Name"].value_counts().head(10))

    st.markdown("---")

    st.write(
        "Total Repeat Customers:",
        df["Customer Name"].value_counts().count()
    )

    st.markdown("---")

    st.write(
        "Revenue Generated by Repeat Customers:",
        df.groupby("Customer Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.markdown("---")

    st.subheader("C. Customer Churn Analysis")

    latest_date = df["Order Date"].max()

    last_purchase = df.groupby("Customer ID")["Order Date"].max()

    inactive_days = (latest_date - last_purchase)
    inactive_days = inactive_days.dt.days

    churn_customers = inactive_days[inactive_days > 90]

    total_churn = len(churn_customers)

    churn_rate = (
        total_churn / df["Customer ID"].nunique()
    ) * 100

    churn_data = df[
        df["Customer ID"].isin(churn_customers.index)
    ]

    col6, col7, col8 = st.columns(3)

    with col6:
        st.metric("Total Churn Customers", total_churn)

    with col7:
        st.metric("Churn Rate", f"{churn_rate:.2f}%")

    with col8:
        st.metric(
            "Revenue from Churn Customers",
            f"${churn_data['Sales'].sum():,.2f}"
        )

    st.markdown("---")

    region_churn = churn_data.groupby(
        "Customer ID"
    )["Region"].first()

    st.write(
        "Regional Distribution of Churn Customers:",
        region_churn.value_counts()
    )

    last_pur = df.groupby("Customer ID")["Order Date"].max().reset_index()

    last_date = df["Order Date"].max()

    last_pur["inactive days"] = (
        last_date - last_pur["Order Date"]
    )

    last_pur["inactive days"] = last_pur["inactive days"].dt.days

    def inactive_groups(days):

        if days <= 30:
            return "Active"

        elif days <= 90:
            return "Low Risk"

        elif days <= 150:
            return "Medium Risk"

        else:
            return "High Risk"

    last_pur["Customer Status"] = last_pur[
        "inactive days"
    ].apply(inactive_groups)

    st.write(
        "Customer Distribution by Engagement Status:",
        last_pur["Customer Status"].value_counts()
    )

    status_count = last_pur["Customer Status"].value_counts().reset_index()

    status_count.columns = ["Status", "Customers"]

    st.markdown("---")

    churn_fig = px.bar(
        status_count,
        x="Status",
        y="Customers",
        title="Customer Inactivity Risk Analysis"
    )

    churn_fig = apply_chart_style(churn_fig)

    st.plotly_chart(churn_fig, use_container_width=True)

    with st.expander("Insights"):

        st.info("""
Observation:
A significant proportion of customers fall within medium-
and high-risk inactivity categories.

Business Impact:
This indicates elevated churn exposure and weakening customer engagement levels,
which may negatively impact long-term revenue stability.

Recommendation:
The business should prioritize customer retention initiatives,
targeted re-engagement campaigns, and personalized marketing strategies
to improve customer lifetime value.
""")

st.markdown("---")

with st.expander("RFM Analysis"):

    cust_summary["Recency"] = (
        latest_date - cust_summary["Last Purchase"]
    ).dt.days

    cust_summary["Frequency"] = cust_summary["Total Orders"]

    cust_summary["Monetary"] = cust_summary["Total Sale"]

    cust_summary["R_Score"] = pd.qcut(
        cust_summary["Recency"],
        4,
        labels=[4, 3, 2, 1]
    )

    cust_summary["F_Score"] = pd.qcut(
        cust_summary["Frequency"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4]
    )

    cust_summary["M_Score"] = pd.qcut(
        cust_summary["Monetary"],
        4,
        labels=[1, 2, 3, 4]
    )

    cust_summary["RFM Score"] = (
        cust_summary["R_Score"].astype(str)
        + cust_summary["F_Score"].astype(str)
        + cust_summary["M_Score"].astype(str)
    )

    def segment_customer(row):

        if (
            row["Total Sale"] > 10000
            and row["Frequency"] > 10
            and row["Recency"] < 30
        ):
            return "VIP Customer"

        elif (
            row["Frequency"] > 5
            and row["Recency"] < 60
        ):
            return "Loyal Customer"

        elif row["Recency"] > 120:
            return "At Risk"

        else:
            return "Regular"

    cust_summary["Segment"] = cust_summary.apply(
        segment_customer,
        axis=1
    )

    st.write(
        "Customer Distribution by RFM Segment:",
        cust_summary["Segment"].value_counts()
    )

    st.markdown("---")

    st.write(
        "Revenue Contribution by RFM Segment:",
        cust_summary.groupby("Segment")["Total Sale"].sum()
    )

st.markdown("---")

with st.expander("Business Performance Analysis"):
    st.subheader("A. Monthly Revenue Trend")

    monthly_revenue = df.groupby("Month Name")["Sales"].sum()

    revenue_trend_fig = px.line(
        monthly_revenue,
        x=monthly_revenue.index,
        y=monthly_revenue.values,
        title="Monthly Revenue Trend"
    )

    revenue_trend_fig.update_traces(
        hovertemplate="<b>Month:</b> %{x}<br><b>Revenue:</b> %{y:,.0f}"
    )

    revenue_trend_fig = apply_chart_style(revenue_trend_fig)

    st.plotly_chart(revenue_trend_fig, use_container_width=True)

    with st.expander("Insights"):

        st.info("""
Observation:
Revenue increased significantly during September,
indicating strong seasonal purchasing behavior and elevated customer demand.

Business Impact:
Heavy dependence on seasonal demand may expose the business
to revenue fluctuations during low-performing periods.

Recommendation:
The organization should optimize inventory planning during peak periods
while strengthening promotional strategies during weaker months
to stabilize overall revenue performance.
""")

    st.markdown("---")

    customer_growth = df.groupby("Month Name")["Customer ID"].count()

    customer_growth_fig = px.line(
        customer_growth,
        x=customer_growth.index,
        y=customer_growth.values,
        title="Monthly Customer Growth Trend"
    )

    customer_growth_fig.update_traces(
        hovertemplate="<b>Month:</b> %{x}<br><b>Customers:</b> %{y}"
    )

    customer_growth_fig = apply_chart_style(customer_growth_fig)

    st.plotly_chart(customer_growth_fig, use_container_width=True)

    with st.expander("Insights"):

        st.info("""
Observation:
Customer activity increased significantly during September
but declined during October.

Business Impact:
Declining customer engagement may increase churn exposure
and weaken customer retention performance.

Recommendation:
The business should strengthen retention initiatives
and implement targeted engagement campaigns for high-risk customer segments.
""")

    st.markdown("---")
    st.subheader("B. Profitability Analysis")

    loss_products = df.groupby("Product Name")["Profit"].sum()

    loss_products = round(
        loss_products[loss_products < 0],
        2
    )

    st.write(
        "Top Loss-Making Products:",
        loss_products.sort_values(ascending=True).head(10)
    )

    st.markdown("---")

    low_margin = df.groupby("Product Name")["Profit Margin"].sum()

    low_margin = round(
        low_margin[low_margin < 0],
        2
    )

    st.write(
        "Products with Negative Profit Margins:",
        low_margin.sort_values(ascending=True).head(10)
    )

    st.markdown("---")

    discount_profit_fig = px.scatter(
        df,
        x="Discount",
        y="Profit",
        title="Discount vs Profitability Analysis"
    )

    discount_profit_fig = apply_chart_style(discount_profit_fig)

    st.plotly_chart(discount_profit_fig, use_container_width=True)

    st.markdown("---")

    st.write(
        "Correlation Analysis:",
        df[["Discount", "Profit"]].corr()
    )

    st.markdown("---")

    st.error("""
Higher discount levels negatively impact profitability,
particularly for low-margin products.
""")

st.markdown("---")


with st.expander("Advanced Analytical Insights"):

    st.subheader("A. Correlation Analysis")

    st.info("""
Higher discount levels are negatively associated with profitability,
particularly for low-margin products.

The business should optimize pricing and discount strategies
to improve overall profit margins and operational efficiency.
""")

    st.markdown("---")

    st.subheader("B. Trend Interpretation")

    st.info("""
Customer demand demonstrates recurring seasonal fluctuations,
indicating varying engagement levels throughout the year.

The organization should align inventory planning,
marketing campaigns, and promotional strategies
with seasonal purchasing behavior.
""")

    st.markdown("---")

    st.subheader("C. Customer Concentration Analysis")

    st.info("""
Low-value customers collectively contribute a substantial share of total revenue,
while high-value customers generate disproportionately higher profitability.

Strengthening retention and personalized engagement strategies
can improve long-term customer loyalty and lifetime value.
""")

    st.markdown("---")

    st.subheader("D. Customer Churn Insights")

    st.info("""
A considerable proportion of customers fall within medium-
and high-risk inactivity groups,
indicating elevated customer churn exposure.

Targeted retention campaigns and personalized promotional strategies
may help improve customer engagement and retention performance.
""")

    st.markdown("---")

    st.subheader("E. VIP Customer Insights")

    st.info("""
VIP customers contribute disproportionately to total revenue and profitability,
making customer retention highly important for long-term business sustainability.
""")

st.markdown("---")


st.subheader("Strategic Recommendations")

st.write("""
• Strengthen loyalty programs for VIP and high-value customers

• Optimize discount strategies to improve profitability

• Launch targeted re-engagement campaigns for inactive customers

• Improve seasonal inventory and demand forecasting

• Enhance customer retention through personalized marketing initiatives
""")