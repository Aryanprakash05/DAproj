import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]  # Replace with your database name
collection = db["mycollection2"]

# Load data from MongoDB
data = list(collection.find())
df = pd.DataFrame(data)

# Clean up the DataFrame
df.drop(columns=["_id"], inplace=True, errors="ignore")  # Remove MongoDB's ObjectId column if present

# Streamlit app configuration
st.set_page_config(page_title="Event Data Analytics", layout="wide")
st.title("📊 Event Data Analytics Dashboard")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dataset Overview", "Analytics Dashboard", "Conclusions"])

if page == "Dataset Overview":
    st.header("Dataset Overview")
    st.write("Explore the event dataset loaded from MongoDB.")

    # Display the dataset
    st.write(df)

    # Summary statistics
    st.subheader("Summary Statistics")
    st.write(df.describe())

    # Display unique values for selected columns
    st.subheader("Unique Values in Key Columns")
    st.write("**Event Names:**", df["EventName"].unique())
    st.write("**Drivers:**", df["Driver"].unique())
    st.write("**Teams:**", df["Team"].unique())
    st.write("**Compounds:**", df["Compound"].unique())

elif page == "Analytics Dashboard":
    st.header("Analytics Dashboard")
    st.write("Perform data analysis and visualize event performance metrics.")

    # Sidebar filters
    st.sidebar.header("Filters")
    selected_event = st.sidebar.selectbox("Select Event", df["EventName"].unique())
    selected_team = st.sidebar.multiselect("Select Teams", df["Team"].unique(), default=df["Team"].unique())
    selected_driver = st.sidebar.multiselect("Select Drivers", df["Driver"].unique(), default=df["Driver"].unique())

    # Filter the dataset
    filtered_df = df[
        (df["EventName"] == selected_event) &
        (df["Team"].isin(selected_team)) &
        (df["Driver"].isin(selected_driver))
    ]

    st.subheader(f"Filtered Dataset: {selected_event}")
    st.write(filtered_df)

    # Visualization: Grid Position vs. Race Position
    st.subheader("Grid Position vs. Race Position")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=filtered_df,
        x="GridPosition",
        y="Position",
        hue="Compound",
        size="TyreAge",
        sizes=(50, 300),
        ax=ax
    )
    ax.set_title("Grid Position vs. Race Position")
    st.pyplot(fig)

    # Visualization: Stint Length Distribution
    st.subheader("Stint Length Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(filtered_df["StintLen"], bins=10, kde=True, ax=ax, color="blue")
    ax.set_title("Stint Length Distribution")
    st.pyplot(fig)

    # Visualization: Tyre Compound Analysis
    st.subheader("Tyre Compound Analysis")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=filtered_df, x="Compound", y="Position", palette="Set3", ax=ax)
    ax.set_title("Tyre Compound vs. Race Position")
    st.pyplot(fig)

    # Visualization: Mean Track Temperature vs. Mean Air Temperature
    st.subheader("Mean Track Temperature vs. Mean Air Temperature")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=filtered_df,
        x="meanTrackTemp",
        y="meanAirTemp",
        hue="Rainfall",
        size="meanHumid",
        sizes=(50, 300),
        ax=ax
    )
    ax.set_title("Track vs. Air Temperature")
    st.pyplot(fig)

    # New Visualization: Fuel Efficiency Trends
    st.subheader("Fuel Efficiency Trends")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=filtered_df, x="lapNumberAtBeginingOfStint", y="fuel_slope", hue="Driver", ax=ax)
    ax.set_title("Fuel Efficiency Across Stints")
    st.pyplot(fig)

    # New Visualization: Temperature Impact on Stint Performance
    st.subheader("Temperature Impact on Stint Performance")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=filtered_df, x="meanTrackTemp", y="StintLen", hue="Compound", size="deg_slope", sizes=(50, 300), ax=ax)
    ax.set_title("Track Temperature vs. Stint Length (with Degradation Slope)")
    st.pyplot(fig)

    # New Visualization: Position vs. Designed Laps
    st.subheader("Position vs. Designed Laps")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=filtered_df, x="Position", y="designedLaps", hue="Team", ax=ax, palette="coolwarm")
    ax.set_title("Position vs. Designed Laps per Team")
    st.pyplot(fig)

elif page == "Conclusions":
    st.header("Conclusions and Insights")
    st.write("""
    Key insights and takeaways from the analytics:
    - **Grid Position vs. Race Position**: Drivers starting in lower grid positions tend to finish lower, but some compounds show better recovery potential.
    - **Stint Length Analysis**: Longer stints are more likely with harder compounds, as degradation rates (deg_slope) are lower.
    - **Tyre Compound Trends**: Harder compounds tend to result in higher average positions, while softer compounds lead to lower positions but are effective in shorter stints.
    - **Temperature Impact**: Higher track temperatures negatively impact stint length, especially for softer compounds.
    - **Fuel Efficiency**: Certain drivers show steeper fuel consumption slopes, indicating opportunities for optimizing strategies.
    - **Team Performance**: Specific teams demonstrate consistent lap designs that align with their positions.
    
    These insights can help teams and drivers refine strategies for compound selection, stint management, and overall race performance optimization.
    """)

    # Summary Visualization: Correlation Heatmap
    # Summary Visualization: Correlation Heatmap
    st.subheader("Feature Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(12, 8))

    # Select only numeric columns for the correlation matrix
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    corr_matrix = df[numeric_cols].corr()

    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Feature Correlation Matrix")
    st.pyplot(fig)


# Footer
st.markdown("---")
st.markdown("**📊 Powered by MongoDB, Pandas, Seaborn, and Streamlit**")
st.markdown("_Designed for Advanced Event Analytics Enthusiasts_")
