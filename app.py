import json

import geopandas as gpd
import streamlit as st


def bbox(coord_list):
    """Calculate the bounding box for a list of coordinates."""
    box = []
    for i in (0, 1):
        res = sorted(coord_list, key=lambda x: x[i])
        box.append((res[0][i], res[-1][i]))
    correction = 0.000001  # correction to account for floating-point precision
    ret = [
        box[0][0] + correction,
        box[1][0] + correction,
        box[0][1] - correction,
        box[1][1] - correction,
    ]
    return ret


def calculate_bbox(geojson):
    for feature in geojson["features"]:
        geometry = feature["geometry"]
        coordinates = (
            geometry["coordinates"][0]
            if geometry["type"] == "Polygon"
            else [coord for polygon in geometry["coordinates"] for coord in polygon[0]]
        )
        feature["properties"]["bbox"] = bbox(coordinates)
    return geojson


def main():
    st.set_page_config(page_title="GeoJSON BBox Calculator", layout="wide")
    st.title("GeoJSON BBox Calculator")

    uploaded_file = st.file_uploader("Upload a GeoJSON file", type=["geojson"])
    geojson_text = st.text_area("or paste GeoJSON here")

    geojson = None

    if uploaded_file is not None:
        geojson = json.load(uploaded_file)
    elif geojson_text:
        try:
            geojson = json.loads(geojson_text)
        except json.JSONDecodeError:
            st.error("Invalid GeoJSON")

    if geojson:
        updated_geojson = calculate_bbox(geojson)
        gdf = gpd.GeoDataFrame.from_features(updated_geojson["features"])

        st.subheader("Updated GeoJSON Data")
        df = gdf.drop(["geometry"], axis=1)
        st.write(df)

        geojson_str = json.dumps(updated_geojson)
        st.download_button(
            label="Download Updated GeoJSON",
            data=geojson_str,
            file_name="updated_geojson.geojson",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
