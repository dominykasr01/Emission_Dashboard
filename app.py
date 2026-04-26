import streamlit as st
import pandas as pd

st.title("Global Emissions Dashboard")
st.divider()

# Load dataset
df = pd.read_csv("emissions.csv")

# Identify year columns
year_columns = [col for col in df.columns if col.isdigit()]

# Identify the country column
possible_country_columns = [
    "Reference area",
    "Country",
    "Country Name",
    "REF_AREA",
    "Geographic area",
    "Location"
]

country_column = None

for col in possible_country_columns:
    if col in df.columns:
        country_column = col
        break

if country_column is None:
    st.error("Country column not found. Please check the dataset column names.")
    st.write(df.columns.tolist())
    st.stop()

# Keep only country and year columns
df_clean = df[[country_column] + year_columns].copy()
df_clean.rename(columns={country_column: "Country"}, inplace=True)

# Convert wide data into long data
df_long = df_clean.melt(
    id_vars="Country",
    var_name="Year",
    value_name="Emissions"
)

# Convert data types
df_long["Year"] = pd.to_numeric(df_long["Year"], errors="coerce")
df_long["Emissions"] = pd.to_numeric(df_long["Emissions"], errors="coerce")

# Remove empty rows
df_long = df_long.dropna()

# Remove global total from country comparisons
df_countries = df_long[df_long["Country"] != "WLD"]

# Dashboard intro
st.write(
    "This dashboard explores global greenhouse gas emissions over time. "
    "Users can analyse global trends, explore emissions by country, and "
    "identify the highest emitting countries using interactive visualisations."
)

# Dataset preview
st.header("Dataset Preview")
st.caption("A random sample of the cleaned dataset is shown below.")
st.dataframe(df_countries.sample(10, random_state=1))

# Dataset information
st.header("Dataset Information")
st.write("Number of rows:", df_countries.shape[0])
st.write("Number of columns:", df_countries.shape[1])

# Year filter
st.header("Filter Data by Year")

min_year = int(df_countries["Year"].min())
max_year = int(df_countries["Year"].max())

year_range = st.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

filtered_df = df_countries[
    (df_countries["Year"] >= year_range[0]) &
    (df_countries["Year"] <= year_range[1])
]

# Global emissions over time
st.header("Global Emissions Over Time")

emissions_year = (
    filtered_df.groupby("Year")["Emissions"]
    .sum()
    .sort_index()
)

st.line_chart(emissions_year, height=400)

# Country exploration
st.header("Explore Emissions by Country")

countries = sorted(filtered_df["Country"].unique())

selected_country = st.selectbox(
    "Select a Country",
    countries
)

country_data = filtered_df[filtered_df["Country"] == selected_country]
country_data = country_data.sort_values("Year")

st.line_chart(
    country_data.set_index("Year")["Emissions"],
    height=400
)

# Top emitters
st.header("Top 10 Emitting Countries")

top_countries = (
    filtered_df.groupby("Country")["Emissions"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_countries.sort_values(ascending=True), height=400)

st.divider()

# Key insights
st.header("Key Insights")

highest_country = top_countries.index[0]
highest_value = top_countries.iloc[0]

st.write(
    f"The highest emitting country in the selected time period is **{highest_country}**, "
    f"with total emissions of approximately **{highest_value:,.0f}**."
)

st.write(
    "The visualisations indicate a general increase in emissions over time, "
    "reflecting the effects of industrial growth, increased energy consumption, "
    "and expanding economic activity."
)
