import streamlit as st
import json
import folium
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium

st.set_page_config(page_title="Parking Finder Valencia", layout="wide")

st.title("Parking Finder Valencia")
st.write(
    """
    This application allows users to explore public parking facilities in Valencia.
    Users can visualize their locations, compare capacities and identify the largest
    parking areas available in the city.
    """
)

with open("data/parking.geojson", "r", encoding="utf-8") as file:
    data = json.load(file)

features = data["features"]

rows = []

for feature in features:
    lon, lat = feature["geometry"]["coordinates"]
    props = feature["properties"]

    rows.append({
        "name": props.get("nombre", "Unknown"),
        "address": props.get("direccion", "Unknown"),
        "spaces": props.get("plazastota", 0),
        "latitude": lat,
        "longitude": lon
    })

df = pd.DataFrame(rows)

st.sidebar.header("Filters")

selected_parking = st.sidebar.selectbox(
    "Select a parking",
    df["name"].sort_values()
)

selected_row = df[df["name"] == selected_parking].iloc[0]

st.sidebar.subheader("Selected parking")
st.sidebar.write(f"**Name:** {selected_row['name']}")
st.sidebar.write(f"**Address:** {selected_row['address']}")
st.sidebar.write(f"**Total spaces:** {selected_row['spaces']}")

col1, col2, col3 = st.columns(3)

col1.metric("Number of parkings", len(df))
col2.metric("Total parking spaces", int(df["spaces"].sum()))
col3.metric("Average spaces per parking", round(df["spaces"].mean(), 1))

largest = df.loc[df["spaces"].idxmax()]
smallest = df.loc[df["spaces"].idxmin()]

st.info(
    f"The largest parking is '{largest['name']}' with {largest['spaces']} spaces. "
    f"The smallest parking is '{smallest['name']}' with {smallest['spaces']} spaces."
)

st.subheader("Parking map")
st.write(
    "The red marker indicates the parking selected in the sidebar. "
    "Click on any blue marker to see its name, address and total capacity."
)


m = folium.Map(location=[39.4699, -0.3763], zoom_start=13)

for _, row in df.iterrows():
    popup_text = f"""
    <b>{row['name']}</b><br>
    Address: {row['address']}<br>
    Total spaces: {row['spaces']}
    """

    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=popup_text,
        icon=folium.Icon(icon="car", prefix="fa")
    ).add_to(m)

folium.Marker(
    location=[selected_row["latitude"], selected_row["longitude"]],
    popup=f"Selected parking: {selected_row['name']}",
    icon=folium.Icon(color="red", icon="star")
).add_to(m)

st_folium(m, width=1000, height=600)

st.subheader("Top 10 parkings by number of spaces")

top_10 = df.sort_values("spaces", ascending=False).head(10)

st.dataframe(top_10[["name", "address", "spaces"]])

fig = px.bar(
    top_10.sort_values("spaces", ascending=True),
    x="spaces",
    y="name",
    orientation="h",
    title="Top 10 parkings by number of spaces",
    labels={
        "spaces": "Number of spaces",
        "name": "Parking"
    }
)

st.plotly_chart(fig, use_container_width=True)