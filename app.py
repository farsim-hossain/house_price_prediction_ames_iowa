from flask import Flask, request, jsonify
import pandas as pd
import pickle
import numpy as np

app = Flask(__name__)

# Load the model and other necessary components
with open('gradient_boosting_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
with open('selected_features.pkl', 'rb') as f:
    selected_features = pickle.load(f)
with open('skewed_features.pkl', 'rb') as f:
    skewed_features = pickle.load(f)

def preprocess_input(input_data):
    # Select features
    input_selected = input_data[selected_features]
    
    # Log transform skewed features
    for feat in skewed_features:
        input_selected[feat] = np.log1p(input_selected[feat])
    
    # Handle infinite values
    input_selected = input_selected.replace([np.inf, -np.inf], np.nan)
    input_selected = input_selected.fillna(input_selected.mean())
    
    # Scale features
    input_scaled = pd.DataFrame(scaler.transform(input_selected), 
                                columns=input_selected.columns, 
                                index=input_selected.index)
    
    return input_scaled

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_df = pd.DataFrame(data, index=[0])
    processed_input = preprocess_input(input_df)
    prediction = model.predict(processed_input)[0]
    return jsonify({'prediction': prediction})

if __name__ == '__main__':
    app.run(debug=True)
