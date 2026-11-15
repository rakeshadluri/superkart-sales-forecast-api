# Import necessary libraries
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Predictor")

# Load the trained model pipeline (preprocessing + model)
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in the order used during training
FEATURES = [
    'Product_Weight',
    'Product_Sugar_Content',
    'Product_Allocated_Area',
    'Product_MRP',
    'Store_Size',
    'Store_Location_City_Type',
    'Store_Type',
    'Product_Id_char',
    'Store_Age_Years',
    'Product_Type_Category'
]


# Define a route for the home page (GET request)
@superkart_api.get('/')
def home():
    """
    Handles GET requests to the root URL ('/') of the API
    and returns a simple welcome message.
    """
    return "Welcome to the SuperKart Sales Prediction API!"


# Define an endpoint for single product-store prediction (POST request)
@superkart_api.post('/v1/predict')
def predict_sales():
    """
    Handles POST requests to the '/v1/predict' endpoint.
    Expects a JSON payload with the product and store details and
    returns the predicted sales total as a JSON response.
    """
    # Get the JSON data from the request body
    input_json = request.get_json()

    # Extract the relevant features from the JSON data
    sample = {feature: input_json[feature] for feature in FEATURES}

    # Convert the extracted data into a DataFrame
    input_data = pd.DataFrame([sample])

    # Make the prediction and convert it to a Python float so that it can be sent as JSON
    predicted_sales = round(float(model.predict(input_data)[0]), 2)

    # Return the prediction as a JSON response
    return jsonify({'Predicted_Product_Store_Sales_Total': predicted_sales})


# Define an endpoint for batch prediction (POST request)
@superkart_api.post('/v1/predictbatch')
def predict_sales_batch():
    """
    Handles POST requests to the '/v1/predictbatch' endpoint.
    Expects a CSV file with the details of multiple product-store pairs and
    returns the predicted sales totals as a dictionary in the JSON response.
    """
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the CSV file into a DataFrame
    input_data = pd.read_csv(file)

    # Make predictions for all rows using only the features expected by the model
    predictions = [round(float(pred), 2) for pred in model.predict(input_data[FEATURES])]

    # Create a dictionary of predictions with the row index as the key
    output_dict = {str(index): pred for index, pred in zip(input_data.index, predictions)}

    # Return the predictions dictionary as a JSON response
    return jsonify(output_dict)


# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    superkart_api.run(debug=True)
