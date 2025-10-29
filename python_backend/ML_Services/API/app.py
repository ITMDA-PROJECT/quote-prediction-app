from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, ConfigDict  #LK added Field and Conf - 20/10
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

#from python_backend.ML_Model.FinalML import train_model, predict, dataprep #OLD NEEDED FIX PATH
#from python_backend.ML_Services.ML_Model.FinalML import train_model, predict, dataprep #TESTING -- no module backend ...
#from ML_Services.ML_Model.FinalML import train_model, predict, dataprep #TESTING
from ..ML_Model.FinalML import train_model, predict, dataprep #TESTING
import pickle
import os
from datetime import datetime
from typing import Optional 

app = FastAPI(title = "Quote Application", version = "1.0")

# Define paths relative to the python_backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "label_encoder.pkl")
DEFAULT_DATA_PATH = os.path.join(BASE_DIR, "Data", "Quotes_For_ML.xlsx")

model = None
label_encoder = None

class TrainRequest(BaseModel):
    file_path: Optional[str] = None         # Path to Excel file containing training data. If not provided, uses default data

#-----------------------------------------------------------
#D + T (OLD VERSION)
""" class PredictRequest(BaseModel):
    #Request model for prediction endpoint
    orderDate: str                          # Format: YYYY-MM-DD
    materialCode: str
    actualTime: float
    quantity: int """

#LK NEW VERSION  -- added 20/10   -- allow for camelCase and snake_case 
class PredictRequest(BaseModel):
    orderDate: Optional[str] = None
    materialCode: Optional[str] = None
    actualTime: Optional[float] = None
    quantity: Optional[int] = None

    #Extra alias names for integration
    order_date: Optional[str] = Field(None, alias="order_date")
    material_code: Optional[str] = Field(None, alias="material_code")
    calculated_total_time: Optional[float] = Field(None, alias="calculated_total_time")

    model_config = ConfigDict(populate_by_name=True)
#-----------------------------------------------------------

class PredictResponse(BaseModel):
    prediction: float
    input : dict

class StatusResponse(BaseModel):
    status: str                             #sends back "ready or not_ready"
    model_loaded : bool
    encoder_loaded: bool
    message: str

def load_model():
    global model, label_encoder
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)

        if os.path.exists(ENCODER_PATH):
            with open (ENCODER_PATH, 'rb') as f:
                label_encoder = pickle.load(f)
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False
    
def save_model(trained_model):
    global model
    model = trained_model
    try:
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        return True
    except Exception as e:
        print(f"Error saving model: {e}")
        return False

@app.on_event("startup")
async def startUp_event():
    load_model()                            #loads model on startup

@app.post("/train")
async def train(request: TrainRequest):
    #Train a new model using the provided Excel file or default data
    try:
        # Use default data path if none provided
        file_path = request.file_path if request.file_path else DEFAULT_DATA_PATH
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=400, 
                detail=f"Data file not found at {file_path}. Please ensure the file exists."
            )
            
        # Train the model using FinalML.py's train_model function
        trained_model = train_model(file_path)
        
        # Save the trained model
        if save_model(trained_model):
            return {"status": "success", "message": "Model trained and saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save trained model")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quote Prediction</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            input {
                width: 100%;
                padding: 8px;
                margin-bottom: 10px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
            #result {
                margin-top: 20px;
                padding: 10px;
                border: 1px solid #ddd;
                display: none;
            }
        </style>
    </head>
    <body>
        <h1>Quote Prediction System</h1>
        <form id="predictionForm">
            <div class="form-group">
                <label for="orderDate">Order Date:</label>
                <input type="date" id="orderDate" name="orderDate" required>
            </div>
            <div class="form-group">
                <label for="materialCode">Material Code:</label>
                <input type="text" id="materialCode" name="materialCode" placeholder="e.g., TYPE-CODE" required>
            </div>
            <div class="form-group">
                <label for="actualTime">Actual Time (minutes):</label>
                <input type="number" id="actualTime" name="actualTime" step="0.1" required>
            </div>
            <div class="form-group">
                <label for="quantity">Quantity:</label>
                <input type="number" id="quantity" name="quantity" required>
            </div>
            <button type="submit">Get Prediction</button>
        </form>
        <div id="result">
            <h3>Prediction Result:</h3>
            <p id="predictionValue"></p>
        </div>

        <script>
            document.getElementById('predictionForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = {
                    orderDate: document.getElementById('orderDate').value,
                    materialCode: document.getElementById('materialCode').value,
                    actualTime: parseFloat(document.getElementById('actualTime').value),
                    quantity: parseInt(document.getElementById('quantity').value)
                };

                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });

                    const data = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('result').style.display = 'block';
                        document.getElementById('predictionValue').textContent = 
                            `Predicted turnaround time: ${data.prediction} days`;
                    } else {
                        alert('Error: ' + data.detail);
                    }
                } catch (error) {
                    alert('Error making prediction: ' + error.message);
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get('/status', response_model = StatusResponse)
async def status():
    """Check if model has been correctly loaded"""
    is_ready = model is not None and label_encoder is not None
    return StatusResponse(
        status = "ready" if is_ready else "not_ready",
        model_loaded = model is not None,
        encoder_loaded = label_encoder is not None,
        message = "Model is ready for predictions" if is_ready else "Please train model first."
    )

@app.post("/predict", response_model = PredictResponse)
async def predict_endpoint(request: PredictRequest):
    global model

    if model is None:
        raise HTTPException(
            status_code=400, detail="Model not trained. Please train the model first."
        )
    
    try:
        # Create a DataFrame with the input features
        input_data = pd.DataFrame([{
            'actualTime (min)': request.actualTime,
            'materialType': request.materialCode.split('-')[0],  # Extract material type
            'quantity': request.quantity,
            'Quarter': pd.to_datetime(request.orderDate).quarter
        }])
        
        # Convert categorical columns to category type
        input_data['materialType'] = input_data['materialType'].astype('category')
        input_data['Quarter'] = input_data['Quarter'].astype('category')
        
        # Make prediction using FinalML.py's predict function
        prediction = predict(model, input_data)

        return PredictResponse(
            prediction= float(prediction[0]),
            input= {
                'orderDate' : request.orderDate,
                'materialCode': request.materialCode,
                'actualTime' : request.actualTime,
                'quantity' : request.quantity
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code= 500, detail= str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = 'localhost', port = 8000)
