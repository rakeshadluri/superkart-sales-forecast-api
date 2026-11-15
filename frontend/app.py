import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend ('backend' is the name of the backend container on the Docker network)
BACKEND_URL = "http://backend:7860"

# Title and description of the Streamlit app
st.title("SuperKart Sales Forecast")
st.write("Predict the total sales revenue of a product in a SuperKart store from the product and store details.")

# Section for online prediction
st.subheader("Online Prediction")

# Collect the product details
Product_Weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.1)
Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
Product_Allocated_Area = st.number_input(
    "Product Allocated Area (ratio of the store's display area)",
    min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f"
)
Product_MRP = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=117.08, step=1.0)
Product_Id_char = st.selectbox(
    "Product Group (first two letters of the Product Id)",
    ["FD", "NC", "DR"],
    format_func=lambda x: {"FD": "FD - Food", "NC": "NC - Non-Consumable", "DR": "DR - Drinks"}[x]
)
Product_Type_Category = st.selectbox("Product Type Category", ["Non Perishables", "Perishables"])

# Collect the store details
Store_Size = st.selectbox("Store Size", ["Medium", "High", "Small"])
Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 2", "Tier 1", "Tier 3"])
Store_Type = st.selectbox(
    "Store Type",
    ["Supermarket Type2", "Supermarket Type1", "Departmental Store", "Food Mart"]
)
Store_Age_Years = st.number_input("Store Age (in years)", min_value=0, max_value=100, value=16, step=1)

# Put the user input into the format expected by the backend API
input_data = {
    'Product_Weight': Product_Weight,
    'Product_Sugar_Content': Product_Sugar_Content,
    'Product_Allocated_Area': Product_Allocated_Area,
    'Product_MRP': Product_MRP,
    'Store_Size': Store_Size,
    'Store_Location_City_Type': Store_Location_City_Type,
    'Store_Type': Store_Type,
    'Product_Id_char': Product_Id_char,
    'Store_Age_Years': Store_Age_Years,
    'Product_Type_Category': Product_Type_Category
}

# Make a prediction when the "Predict" button is clicked
if st.button("Predict", type="primary"):
    try:
        # Send the data to the Flask API
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=input_data)
        if response.status_code == 200:
            prediction = response.json()['Predicted_Product_Store_Sales_Total']
            st.success(f"Predicted Product Store Sales Total: {prediction:,.2f}")
        else:
            st.error(f"Error in API request (status code {response.status_code}).")
    except requests.exceptions.RequestException:
        st.error("Unable to connect to the prediction API.")

# Section for batch prediction
st.subheader("Batch Prediction")

# Allow the user to upload a CSV file for batch prediction
uploaded_file = st.file_uploader("Upload a CSV file for batch prediction", type=["csv"])

# Make batch predictions when the "Predict Batch" button is clicked
if uploaded_file is not None:
    if st.button("Predict Batch", type="primary"):
        try:
            # Send the file to the Flask API
            response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files={"file": uploaded_file})
            if response.status_code == 200:
                predictions = response.json()
                st.success("Batch predictions completed!")
                # Show the predictions as a table (row index -> predicted sales)
                result_df = pd.DataFrame(
                    {"Row": list(predictions.keys()), "Predicted Sales": list(predictions.values())}
                )
                st.dataframe(result_df)
            else:
                st.error(f"Error in API request (status code {response.status_code}).")
        except requests.exceptions.RequestException:
            st.error("Unable to connect to the prediction API.")
