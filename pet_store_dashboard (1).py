import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Pet Store Sales Dashboard", page_icon="🐾", layout="wide")

st.title("🐾 Pet Store Sales Dashboard")
st.caption("Explore sales, product categories, pet types, countries, and repeat purchases.")

# Upload the dataset
uploaded_file = st.sidebar.file_uploader("Upload pet store CSV dataset", type=["csv"])

if uploaded_file is None:
    st.info("Upload your pet_store_records_2020 (1).csv file in the sidebar to begin.")
    st.stop()

df = pd.read_csv(uploaded_file)

required_columns = [
    "product_category", "sales", "price",
    "pet_size", "pet_type", "rating", "re_buy"
]
missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error("These required columns are missing: " + ", ".join(missing))
    st.stop()

# Clean basic data types
for col in ["sales", "price", "rating", "re_buy"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["sales", "price", "rating", "re_buy"])

# Keep only cats and dogs
df["pet_type"] = df["pet_type"].astype(str).str.strip().str.title()
df = df[df["pet_type"].isin(["Cat", "Dog"])].copy()

# Sidebar filters
st.sidebar.header("Dashboard Filters")
filtered = df.copy()

for col, label in [
    ("product_category", "Product Category"),
    ("pet_type", "Pet Type"),
    ("pet_size", "Pet Size"),
]:
    options = sorted(filtered[col].dropna().astype(str).unique().tolist())
    selected = st.sidebar.multiselect(
        label, options, default=options, key=f"filter_{col}"
    )
    filtered = filtered[filtered[col].astype(str).isin(selected)]

if filtered.empty:
    st.warning("No records match the selected filters. Change the filters in the sidebar.")
    st.stop()

# KPI cards
total_sales = filtered["sales"].sum()
average_price = filtered["price"].mean()
average_rating = filtered["rating"].mean()
repeat_rate = (filtered["re_buy"].eq(1).mean()) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"{total_sales:,.0f}")
c2.metric("Average Price", f"{average_price:,.2f}")
c3.metric("Average Rating", f"{average_rating:.2f}")
c4.metric("Repeat Purchase Rate", f"{repeat_rate:.1f}%")

st.caption(f"Showing {len(filtered):,} records out of {len(df):,} valid records. Sales and price units follow the source dataset.")

sns.set_theme(style="whitegrid")

# Charts row 1
left, right = st.columns(2)

with left:
    st.subheader("Sales by Product Category")
    category_sales = (
        filtered.groupby("product_category", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=category_sales, x="sales", y="product_category", ax=ax)
    ax.set_xlabel("Total Sales")
    ax.set_ylabel("Product Category")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Records by Pet Type")
    pet_counts = filtered["pet_type"].value_counts().rename_axis("pet_type").reset_index(name="records")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=pet_counts, x="records", y="pet_type", ax=ax)
    ax.set_xlabel("Number of Records")
    ax.set_ylabel("Pet Type")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# Charts row 2
left, right = st.columns(2)

with left:
    st.subheader("Sales by Pet Type")
    pet_sales = (
        filtered.groupby("pet_type", as_index=False)["sales"]
        .sum()
        .sort_values("sales", ascending=False)
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=pet_sales, x="sales", y="pet_type", ax=ax)
    ax.set_xlabel("Total Sales")
    ax.set_ylabel("Pet Type")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Repeat Purchase Breakdown")
    repeat_counts = filtered["re_buy"].map({1: "Repeat purchase", 0: "No repeat purchase"}).fillna("Other").value_counts()
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.pie(
        repeat_counts.values,
        labels=repeat_counts.index,
        autopct="%1.1f%%",
        startangle=90
    )
    ax.axis("equal")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

# Data table and download
st.subheader("Filtered Dataset")
st.dataframe(filtered, use_container_width=True)

csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered data as CSV",
    data=csv_data,
    file_name="filtered_pet_store_records.csv",
    mime="text/csv"
)
