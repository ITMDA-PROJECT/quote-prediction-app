#(ml_client.py) 
#Quotation Service - ml_client.py -- sends ML Service ML Prediction Request and receives response from ML Service
import requests
from typing import Optional, Dict, Any
from .quote_schema import MLPredictionResponse  , MLPredictionRequest #request schema not used??

#ML service URL CONFIGURATION
ML_SERVICE_URL = "http://localhost:8001/predict"  #ML URL -- at port 8000

""" from dotenv import load_dotenv
load_dotenv()
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000/predict") """

#snake_case or camelCase option... (Changed ML pydantic then can keep top snake_case implementation)
        #Convert pydantic model to dict for JSON POST
        #payload_dict = r_payload.model_dump()  #-- removed -- can keep if ml pydantic adjusted for snake case and not just camel case
        #^^ OR BELOW #CAMEL CASE WAY   (top failiing thus keeping bottom adjustment and ML pydantic changed )

def send_prediction_request(r_payload: MLPredictionRequest) -> MLPredictionResponse: #reqest and response ==> pydantic
    """ Sends a validated Pydantic request model to the ML service and returns a structured response. """
    try:
        #CAMEL CASE WAY
        #Convert pydantic MLPredictionRequest model to dict, then rename keys for ML Service     
        # (If ML service pydantic model not updated - workaround)
        p = r_payload.model_dump()
        payload_dict = {
            "orderDate": p["order_date"],
            "materialCode": p["material_code"],
            "actualTime": p["calculated_total_time"],
            "quantity": p["quantity"]
        }

        #Send the request to ML SERVICE
        ml_response = requests.post(ML_SERVICE_URL, json=payload_dict, timeout=60)
        ml_response.raise_for_status()  #raises error for 400/500 responses

        #Parse ML response JSON  --  Handle field name differences across ML versions
        data = ml_response.json()
        predicted = (
            data.get("predictedTime")
            or data.get("predicted_time")
            or data.get("prediction")
        )

        #Return as MLPredictionResponse model
        return MLPredictionResponse(predicted_total_time=predicted, input=data) #added 20/10
    
    #Non-200 response (ERRORS)
    except requests.RequestException as e:
        raise Exception(f"Request to ML service failed: {e}") #Connection or timeout error
    except Exception as e:
        raise Exception(f"Error processing ML response: {e}") #Any other unexpected issue



#GOOD METHOD (REAL) WORKED BEFORE model_dump for pydantic used
""" #def send_prediction_request(payload: Dict[str, Any] ) -> MLPredictionResponse: #,timeout: int = 10 #changed to pydantic - but still send data as json when making request  (in main)
def send_prediction_request(r_payload: MLPredictionRequest) -> MLPredictionResponse:
    #change -- payload: Dict[str, Any]  -->  MLPredictionRequest???
    
    #Send a prediction request to the ML service.
    #payload should be a JSON-serializable dict. 
    #Returns PredictionResponse from ML service.
    
    try:
        #ml_response = requests.post(ML_SERVICE_URL, json=payload ) #, timeout=timeout
        #20/10 added due to pydantic MLPredictionRequest used #changed to pydantic - but still send data as json when making request  (in main)
        ml_response = requests.post(ML_SERVICE_URL, json=r_payload.model_dump()) #, timeout=60)

    except requests.RequestException as e:
        return MLPredictionResponse(predicted_time=None, raw={"error": str(e)})

    #200 success message - got response
    if ml_response.status_code == 200:
        try:
            data = ml_response.json() #data from ml_response
        except Exception:
            return MLPredictionResponse(predicted_time=None, raw={"error": "invalid json", "status": ml_response.text})
        
        #ML service returns JSON like {"predicted_time": 12.5}
        predicted = data.get("predictedTime") or data.get("predicted_time") or data.get("prediction") 
        return MLPredictionResponse(predicted_time=predicted, raw=data)
   
    #Response Error / (Response None)
    else:
        return MLPredictionResponse(predicted_time=None, raw={"status_code": ml_response.status_code, "text": ml_response.text}) """


#MOCK FOR TESTING (WHEN CANNOT RUN ML SERVICE -- before integration)
"""import random
from .quote_schema import MLPredictionResponse

# Mock ML service call
def send_prediction_request(payload: dict) -> MLPredictionResponse:
    #Mock ML prediction when ML service isn't available.
    # Create a fake prediction value (slightly randomized for realism)
    base_time = payload.get("calculated_total_time", 0)
    quantity = payload.get("quantity", 1)
    mock_prediction = base_time * random.uniform(0.9, 1.1) + (quantity * 0.1)

    return MLPredictionResponse(
        predicted_total_time=round(mock_prediction, 2),
        input=payload
    ) """
 
 #WORKS -- shows endpoint can be accessed - post request fulfilled with mock dummy data using random then the quote predicted time is updated in db



#SCRAP: 
#REPLACED W MS Pydantic schemas
""" from pydantic import BaseModel
class PredictRequest(BaseModel):
    #Request model for ML prediction endpoint
    orderDate: str                          # Format: YYYY-MM-DD
    materialCode: str
    actualTime: float   #calculated_total_time (mins)
    quantity: int       #delimitation -- working with 1 quotepart

class PredictResponse(BaseModel):
    prediction: float
    input : dict """


 #return MLPredictionResponse(predicted_time=predicted, raw=data) #OLD before pydantic raw instead of input