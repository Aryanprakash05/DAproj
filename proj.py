from pymongo import MongoClient
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Streamlit app configuration
st.set_page_config(page_title="F1 Drivers Data Analytics", layout="wide")
st.title("🏎️ F1 Drivers Data Analytics Dashboard")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  
db = client["mydatabase"]  # Replace 'mydatabase' with your database name
collection = db["mycollection"]  # Replace 'mycollection' with your collection name

# Fetch data from MongoDB
data = list(collection.find())
df = pd.DataFrame(data)
df.drop(columns=["_id"], inplace=True, errors="ignore")

# Sidebar - Filters
st.sidebar.header("Filters")
nationality_filter = st.sidebar.multiselect(
    "Filter by Nationality", options=df["Nationality"].unique(), default=df["Nationality"].unique()
)
season_filter = st.sidebar.slider(
    "Select Season Range", 
    min_value=min(min(season) for season in df["Seasons"]), 
    max_value=max(max(season) for season in df["Seasons"]),
    value=(min(min(season) for season in df["Seasons"]), max(max(season) for season in df["Seasons"]))
)
championship_filter = st.sidebar.checkbox("Show Only Championship Winners", value=False)
points_filter = st.sidebar.slider(
    "Minimum Points Per Entry", 
    min_value=float(df["Points_Per_Entry"].min()), 
    max_value=float(df["Points_Per_Entry"].max()), 
    value=float(df["Points_Per_Entry"].min())
)

# Apply filters
filtered_df = df[df["Nationality"].isin(nationality_filter)]
filtered_df = filtered_df[filtered_df["Seasons"].apply(lambda seasons: any(season_filter[0] <= year <= season_filter[1] for year in seasons))]
filtered_df = filtered_df[filtered_df["Points_Per_Entry"] >= points_filter]
if championship_filter:
    filtered_df = filtered_df[filtered_df["Championships"] > 0]

# Display filtered dataset
st.header("📊 Filtered Dataset")
st.write(filtered_df)

# Key Statistics
st.header("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Drivers", len(filtered_df))
with col2:
    st.metric("Average Championships", f"{filtered_df['Championships'].mean():.2f}")
with col3:
    st.metric("Average Years Active", f"{filtered_df['Years_Active'].mean():.2f}")
with col4:
    st.metric("Average Points/Entry", f"{filtered_df['Points_Per_Entry'].mean():.2f}")

# Visualization 1: Championships by Nationality
st.subheader("🏆 Championships by Nationality")
fig, ax = plt.subplots(figsize=(12, 6))
championships_by_nationality = filtered_df.groupby("Nationality")["Championships"].sum().sort_values(ascending=False)
championships_by_nationality.plot(kind="bar", ax=ax, color="goldenrod")
ax.set_title("Total Championships by Nationality", fontsize=16)
ax.set_ylabel("Championships", fontsize=12)
ax.set_xlabel("Nationality", fontsize=12)
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
st.pyplot(fig)

# Visualization 2: Points Distribution
st.subheader("🎯 Points Distribution")
fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(filtered_df["Points_Per_Entry"], kde=True, ax=ax, color="blue", bins=20)
ax.set_title("Distribution of Points Per Entry", fontsize=16)
ax.set_xlabel("Points Per Entry", fontsize=12)
st.pyplot(fig)

# Visualization 3: Championships vs. Years Active
st.subheader("📌 Championships vs. Years Active")
fig, ax = plt.subplots(figsize=(12, 6))
sns.scatterplot(
    data=filtered_df, 
    x="Years_Active", 
    y="Championships", 
    hue="Nationality", 
    size="Points_Per_Entry", 
    sizes=(50, 500), 
    ax=ax, 
    palette="viridis"
)
ax.set_title("Championships vs. Years Active", fontsize=16)
ax.set_xlabel("Years Active", fontsize=12)
ax.set_ylabel("Championships", fontsize=12)
st.pyplot(fig)

# Visualization 4: Championships Over Time
st.subheader("📅 Championships Over Time")
df["Seasons_Years"] = df["Seasons"].apply(lambda x: [int(year) for year in x])
df_exploded = df.explode("Seasons_Years")
championships_by_year = df_exploded.groupby("Seasons_Years")["Championships"].sum()

fig, ax = plt.subplots(figsize=(12, 6))
championships_by_year.plot(ax=ax, marker="o", color="crimson")
ax.set_title("Championships Over the Years", fontsize=16)
ax.set_ylabel("Championships", fontsize=12)
ax.set_xlabel("Year", fontsize=12)
st.pyplot(fig)

# Advanced Insights
st.header("📚 Advanced Insights")
col5, col6 = st.columns(2)
with col5:
    top_n = st.slider("Select Top N Drivers by Championships", min_value=1, max_value=20, value=10)
    top_drivers = filtered_df.sort_values(by="Championships", ascending=False).head(top_n)
    st.write(top_drivers[["Driver", "Nationality", "Championships", "Years_Active", "Points_Per_Entry"]])
with col6:
    st.write("### Nationality Analysis")
    nationality_counts = filtered_df["Nationality"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    nationality_counts.plot.pie(ax=ax, autopct="%.2f%%", colors=sns.color_palette("pastel"))
    ax.set_ylabel("")
    ax.set_title("Drivers by Nationality", fontsize=16)
    st.pyplot(fig)

# Interactive Analysis
st.header("🔍 Interactive Driver Analysis")
driver_filter = st.selectbox("Select a Driver", options=filtered_df["Driver"].unique())
driver_data = filtered_df[filtered_df["Driver"] == driver_filter]
st.write(driver_data)

# Footer
st.markdown("---")
st.markdown("**📊 Powered by MongoDB, Pandas, and Streamlit**")
st.markdown("_Designed with 💡 for F1 Enthusiasts_")
