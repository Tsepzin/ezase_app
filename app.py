import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import timedelta


# Load the data
df = pd.read_excel("data/statement.xlsx")

# Convert dates
df['Actual Date'] = pd.to_datetime(df['Actual Date'])
df['Month End'] = pd.to_datetime(df['Month End'])
df['Month'] = df['Month End'].dt.to_period("M").astype(str)

# Filter by Isipheko contributions
isipheko_df = df[df["Type"] == "Isipheko"]

# Allocate Isipheko to Mhlengi
df['Name'] = np.where(df['Type'] == 'Isipheko', 'Mhlengi', df['Name'])

#st.title("💼 Ezase......Qedela Wena - Contribution Dashboard")
st.markdown("<h1 style='text-align: center; color: #da9922ff;'>Ezase......Qedela Wena</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Monthly Contribution Insights</h3>", unsafe_allow_html=True)


# Sidebar filters
st.sidebar.header("Filters")
name_filter = st.sidebar.multiselect("Select Name", df['Name'].unique(), default=df['Name'].unique())

filtered_df = df[df['Name'].isin(name_filter)]

# Define the cutoff deadline (5 days after Month End)
filtered_df['Cutoff Date'] = filtered_df['Month End'] + pd.Timedelta(days=5)

# Calculate days late beyond cutoff
filtered_df['Days Late'] = (filtered_df['Actual Date'] - filtered_df['Cutoff Date']).dt.days
filtered_df['Days Late'] = filtered_df['Days Late'].apply(lambda x: x if x > 0 else 0)

# KPIs
total_amount = filtered_df['Amount'].sum()
unique_contributors = filtered_df['Name'].nunique()
contribution_count = filtered_df.shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("Total Collected", f"R{total_amount:,.0f}")
col2.metric("Unique Contributors", unique_contributors)
col3.metric("Total Contributions", contribution_count)

# Contribution Trends
st.markdown("### 📈 Monthly Contribution Trend")
monthly_summary = (
    filtered_df.groupby('Month')['Amount'].sum().reset_index().sort_values('Month')
)
line_chart = alt.Chart(monthly_summary).mark_line(point=True).encode(
    x='Month',
    y='Amount'
).properties(height=350)
st.altair_chart(line_chart, use_container_width=True)

# Individual Breakdown
st.markdown("### 👥 Contributions by Person")
bar_chart = alt.Chart(filtered_df).mark_bar().encode(
    x='Name:N',
    y='sum(Amount):Q',
    color='Name:N'
).properties(height=350)
st.altair_chart(bar_chart, use_container_width=True)


st.markdown("### 🧱 Monthly Contributions by Person")
monthly_by_person = (
    filtered_df.groupby(['Month', 'Name'])['Amount'].sum().reset_index()
)
stacked_bar = alt.Chart(monthly_by_person).mark_bar().encode(
    x='Month:N',
    y='Amount:Q',
    color='Name:N',
    tooltip=['Name:N', 'Amount:Q']
).properties(height=350)
st.altair_chart(stacked_bar, use_container_width=True)

st.markdown("### 🥇 Top Contributors")
contributor_totals = (
    filtered_df.groupby('Name')['Amount'].sum().reset_index()
)
pie = alt.Chart(contributor_totals).mark_arc(innerRadius=50).encode(
    theta="Amount:Q",
    color="Name:N",
    tooltip=["Name:N", "Amount:Q"]
).properties(height=350)
st.altair_chart(pie, use_container_width=True)

# Create heatmap data
late_pivot = filtered_df.groupby(['Name', 'Month'])['Days Late'].mean().reset_index()

st.markdown("### ⏰ Heatmap of Contributions Past 5-Day Grace Period")
heatmap = alt.Chart(late_pivot).mark_rect().encode(
    x='Month:N',
    y='Name:N',
    color=alt.Color('Days Late:Q', scale=alt.Scale(scheme='orangered')),
    tooltip=['Name', 'Month', 'Days Late']
).properties(height=350)

st.altair_chart(heatmap, use_container_width=True)

# Isipheko Contributions
st.markdown("### 🎁 Isipheko Sika Gatsheni Contributions")
st.dataframe(isipheko_df[['Name', 'Amount', 'Actual Date']], use_container_width=False, hide_index=True)

# Raw Data
st.markdown("### 📄 Raw Data")
st.dataframe(filtered_df, hide_index=True)

# CSV Download
csv = filtered_df.to_csv(index=False).encode()
st.download_button("📥 Download Filtered Data", data=csv, file_name='filtered_contributions.csv', mime='text/csv')