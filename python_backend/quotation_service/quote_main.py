#RUN QUOTATION SERVICE with below: 
# uvicorn python_backend.quotation_service.quote_main:app --reload --port 8002 
#--------- quote_main.py imports --------------------------------------
from fastapi import FastAPI, Depends, HTTPException, Header #FastAPI & Depends (Dependency) , Header for auth token
from sqlalchemy.orm import Session, joinedload #Sqlachemy - Session used in DB Dependency
""" #from database_schema.Database_schema import Session #as DBSession  
#removed as Session is handled in below get_db  """

import requests
import jwt  #jwt token - User Service for admin jwt tokens  #pip install jwt
import os  #load SECRET_KEY and ML_SERVICE_URL from environment.
from dotenv import load_dotenv #added 21/10 - for loading same super key for token


""" from python_backend.quotation_service.quote_schema import (
    QuoteCreate, QuoteRead, QuoteStatusUpdate,
    PartCreate, PartRead, QuotePartAdd, QuotePartRead, QuotePartUpdate,
    MLPredictionResponse, MLPredictionRequest
)

from python_backend.quotation_service import quote_crud
from python_backend.quotation_service.quote_crud import get_db
from python_backend.quotation_service.ml_client import send_prediction_request
 """
#*NOTE: 23/10 added full paths for imports (added python_backend.)
#added quotation_service.for fix
from python_backend.quotation_service.quote_schema import QuoteCreate, QuoteRead, QuoteStatusUpdate  #QUOTE - Create, Read, (U) QPAdd, Update
from python_backend.quotation_service.quote_schema import PartCreate, PartRead #PART - Create, Read
from python_backend.quotation_service.quote_schema import QuotePartAdd, QuotePartRead, QuotePartUpdate #QUOTEPART - create/add, read, update

from python_backend.quotation_service import quote_crud 
from python_backend.quotation_service.quote_crud import get_db #DB   
#prevent circular dpendency
#from quotation_service.quote_crud import get_all_materials, get_material  #MATERIALS
#from quotation_service.quote_crud import create_part, get_all_parts, get_part, update_part, delete_part #PARTS 
#, create_quote_with_parts, get_quote, list_quotes 

#from quotation_service import ml_client  #prevent circular dpendency
from python_backend.quotation_service.ml_client import send_prediction_request
from python_backend.quotation_service.quote_schema import MLPredictionResponse, MLPredictionRequest #added 20/10

#------------------------------------------------------------------------

#------------------------------------------------------------------------
#---------------------CONFIGURATIONS------------------------------------
#------------------------------------------------------------------------
app = FastAPI(title="Quotation Service API")

#connecting userservice and .env  (.env in both services -- SECRET KEY , *not for now.. DB URL)

#Configuration ( SECRET KEY & ML SERVICE URL (ENDPOINT in QS for Prediction))
load_dotenv() #share secret key
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretjwtkey") #Loads secret key (match UserService key)
ENC_ALGORITHM = "HS256" #Algorithm used for jwt token
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000/predict") #ML Service URL 8003 preferred -- 8000 chosen
#------------------------------------------------------------------------


#=================================================
#------------ JWT AUTHENTICATION HELPER----------- 
#=================================================
#verify authenticated user/admin  (then get the admin / admin id)
def verify_jwt_token(authorization: str = Header(None))->int:  #Auth Header None by default - if missing 
    """
    Verifies JWT token sent from the User Service.
    Returns the admin_id (as int) if valid --if fail raises HTTPException (401).
    """
    #Verify Admin JWT token coming from Frontend (created by UserService) 
    #-- Admin JWT Token Verification required for all protected endpoint access

    #if no token or no authorization header "Bearer <token>" in token 
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token header") 
        #401 unauthorizaed error 
    
    #Get token: splits authorization string -- "Bearer <token>" to get the <token>
    token = authorization.split(" ")[1]  
    try:
        #Decode JWT using the SECRET_KEY and HS256 algo -- to get token payload
        t_payload = jwt.decode(token, SECRET_KEY, algorithms=[ENC_ALGORITHM])

        #Check correct token type --> login (logged in admin)
        if t_payload.get("type") != "login":
            raise HTTPException(status_code=401, detail="Invalid token type") #token type error
        
        #get admin_id from token payload  (if none raise exception)  - 21/10
        admin_id_from_token = t_payload.get("admin_id")
        if not admin_id_from_token:
            raise HTTPException(status_code=401, detail="admin_id missing from token")
        
        return admin_id_from_token #admin_id returned when verified successfully
    
    #TOKEN ERRORS -- Expired or Invalid (raises jwt errors) 
    #EXPIRED TOKEN 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired") 
    #INVALID TOKEN - error if cannot decode
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")



#INSTEAD verifyin Quotation Service --- allows for decoupling from UserService - not constant calls
#Below doesnt scale well if called on UserService for each protected endpoint request. 
#LK THOUGHT:  can make use of USERSERVICE to get admin  then admin id from this 

#=================================================

#======================================================================
#========================= ENDPOINTS ==================================
#======================================================================
#run in terminal from python_backend directory -- uvicorn quotation_service.quote_main:app --reload

#TEST ENDPOINT - health running check :)
@app.get("/")
def health_check():
    return {"message": "Quotation Service is running"}

# ==========================================================
#TEST SECURE ENDPOINT - with jwt logic  (can be deleted later)
@app.get("/verify-token-test")
def verify_test(admin_id: int = Depends(verify_jwt_token)):
    return {"message": f"Token valid. Hello Admin #{admin_id}"}

#=====================================================
#================MATERIAL ENDPOINTS========= :) works
#=====================================================
#READ ALL MATERIALS 
@app.get("/materials")
def read_all_materials(db: Session = Depends(quote_crud.get_db), 
                       admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    return quote_crud.get_all_materials(db) #pass db -session -- to quote_crud 

#READ/GET (ONE) MATERIAL  *not sure if needed - but tested and works
@app.get("/materials/{material_code}") 
def read_material(material_code: str, db: Session = Depends(quote_crud.get_db), 
                  admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    #Depends(get_db) or Depends(quote_crud.get_db) 
    # = Depends(quote_crud.get_db) ==> Inject the result of quote_crud.get_db()

    material = quote_crud.get_material(db, material_code) #get material by material_code from db (quote_crud.py)
    
    #No material found (with material_code)
    if not material: 
        return {"error": "Material not found - Does not match material code given"}
    return material  #if material found - returned


#=====================================================
#================PART ENDPOINTS======================= works :)
#=====================================================
#==(C) CREATE/SAVE NEW PART (POST)    
# **possibly needed in final - as 2 step allows for part to be created then quotepart created/linked in qoute
@app.post("/parts", response_model=PartRead) #19/10 added -validate outputs
def add_part(new_part: PartCreate, db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    #PartCreate pydantic , db dependency injection
    try:
        #create part in db (using quote_crud.py method)
        return quote_crud.create_part(db, new_part.part_description, new_part.material_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))  #valueError - description or material code X

#==(R) READ PART (GET)
#-- GET (ONE) PART (by part_id provided)
@app.get("/parts/{part_id}") 
def read_part(part_id: int, db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected
    part = quote_crud.get_part(db, part_id) #or quote_crud.get_part
    #if part not found (by part id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part #found - return part

#==(R) READ ALL PARTS (GET)     
@app.get("/parts")
def read_all_parts(db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected 
    return quote_crud.get_all_parts(db)

#(U) UPDATE PART DETAILS??  -- part_description or material_code?  -- if so then need to add endpoint
""" #assuming not changing part description or material_code for now...
#NOTE: if required - endpoint(s) can be created...  """

#==(D) DELETE PART  (FROM CATALOG)  ** not needed - only in rare cases 
""" @app.delete("/parts/{part_id}")
def remove_part(part_id: int, db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    #delete part and get delete part result -- if no result then 404 error part not found
    result = delete_part(db, part_id)
    if not result:
        raise HTTPException(status_code=404, detail="Part not found")
    return {"message": "Part deleted successfully"} """

#================================================
#==============QUOTE ENDPOINTS===================
#================================================

# (C) CREATE/SAVE NEW QUOTE (POST)
@app.post("/quotes", response_model=QuoteRead)  #19/10 response model *validates responses/outputs
def create_quote( quote: QuoteCreate, admin_id: int = Depends(verify_jwt_token), db: Session = Depends(get_db) ): #with JWT* dependency injection - 21/10
    """Create new empty quote for authenticated admin"""
    try:
        #JWT logic - admin id provided from dependency (by helper method) - 21/10
        quote.admin_id = admin_id  #admin id specific to quote (admin_id fk in quote)

        #create new quote (empty initialized) and return new_quote
        new_quote = quote_crud.create_empty_quote(db, quote)
        return new_quote
    
    except ValueError as e: #VALUE ERROR - wrong/missing values
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e: #SERVER ERROR - error creating quote
        raise HTTPException(status_code=500, detail=f"Error creating quote: {e}")
    

#==(R) READ ALL QUOTES (GET)
@app.get("/quotes")
def read_all_quotes(db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    return quote_crud.get_all_quotes(db) #call on quote_crud's  get_all_quotes method

#==(R) READ ALL (IN PROGRESS) QUOTES (GET) NOTE:can uncomment endpoint if needed**
""" @app.get("/quotes/in-progress")
def get_in_progress_quotes(db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    try:
        #get all quotes that are in progress (all columns) 
        in_progress_quotes = quote_crud.get_all_in_progress_quotes(db)
        return in_progress_quotes
    #if details not found or valueError occurs then http exception raised (404)
    except ValueError as e: 
        raise HTTPException(status_code=404, detail=str(e)) """

#==(R) READ ALL (COMPLETED) QUOTES (GET)  -- NOTE:can uncomment endpoint code if needed**
""" @app.get("/quotes/completed")
def get_completed_quotes(db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    try:
        #get all quotes that are completed (all columns) 
        in_progress_quotes = quote_crud.get_all_in_progress_quotes(db)
        return in_progress_quotes
    #if details not found or valueError occurs then http exception raised (404)
    except ValueError as e: 
        raise HTTPException(status_code=404, detail=str(e)) """

#==(R) READ ALL (IN PROGRESS)*FILTERED QUOTES (GET)  -- chose this based on wireframe
@app.get("/quotes/in-progress-filtered")
def get_filtered_in_progress_quotes(db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    try:
        #get all quotes that are in progress (filtered with --quote_number and predicted_total_time) 
        filtered_in_progress_quotes = quote_crud.get_all_in_progress_quotes_filtered(db)
        return filtered_in_progress_quotes
    #if details not found or valueError occurs then http exception raised (404)
    except ValueError as e: 
        raise HTTPException(status_code=404, detail=str(e))

#==(R) READ ALL (COMPLETE D)*FILTERED QUOTES (GET) -- chose this based on wireframe
@app.get("/quotes/completed-filtered")
def get_filtered_completed_quotes(db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    try:
        #get all quotes that are completed (filtered with --quote_number and predicted_total_time) 
        filtered_completed_quotes = quote_crud.get_all_completed_quotes_filtered(db)
        return filtered_completed_quotes
    #if details not found or valueError occurs then http exception raised (404)
    except ValueError as e: 
        raise HTTPException(status_code=404, detail=str(e))

#==(R) READ QUOTE (GET) - by id  ---> BASIC QUOTE DETAILS    
@app.get("/quotes/{quote_id}")
def read_quote(quote_id: int, db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run    
    #get quote by id in db -- if quote not found - raise 404 error message
    quote = quote_crud.get_quote(db, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote

#XXX
#NOTE:  XXX ^^^^^ **POSSIBLY NEED to modify crud (only quotes related to admin id?)  XXX
#XXX

#----------------------------------------------------------
#------QUOTE DETAILS (JOINED TABLES - Q, QP, P , M )---------
#==(R) READ QUOTE (GET) - by id  ---> ALL DETAILS RELATED TO QUOTE (Q, QP, P , M )
@app.get("/quotes/{quote_id}/details")
def get_quote_details(quote_id: int, db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run    
    try:
        #get quote details with joined details
        quote = quote_crud.get_quote_with_details(db, quote_id)
        return quote
    #if details not found or valueError occurs then 404 http exception raised
    except ValueError as e: 
        raise HTTPException(status_code=404, detail=str(e))
#----------------------------------------------------------

#(U) UPDATE QUOTE DETAILS -- endpoint(s)
@app.put("/quotes/{quote_id}/status")
def update_quote_status_endpoint(quote_id: int, status_update: QuoteStatusUpdate,  #QuoteStatusUpdate pydantic
                                 db: Session = Depends(get_db), 
                                 admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification 

    try:  
        #Update quote status to new_quote_status then return updated quote
        updated_quote = quote_crud.update_quote_status(db, quote_id, status_update.new_quote_status) #status_update's new_quote_status (key) in json       
        return updated_quote

    # ValueError raises Exception for 404 (Quote not found)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
"""***QuoteStatus update """
""" EG: PUT /quotes/5/status
{ "new_quote_status": true }
or { "new_quote_status": false }  """

"""*** XX  Time update #1 XX --- calc not needed (done auto for qp added, update, deletes) """
#if manual calc update needed - can add endpoint 
"""*** XX Time update  #2 XX --- prediction update needed when prediction endpoint called. """
# (so in prediction endpoint at end) -- when prediction called manually -- then it is also updated in db 
# (thus see below (below QP endpoints) for prediction api endpoint)


#==(D) DELETE QUOTE 
# -- causes cascade delete - Quote Deleted and QuotePart children deleted
@app.delete("/quotes/{quote_id}")
def delete_quote(quote_id: int, db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run    
    #delete quote in db using quote_crud's method delete_quote
    deleted = quote_crud.delete_quote(db, quote_id) 
    
    #if quote not found to be deleted then 404 error raised 
    if not deleted:
        raise HTTPException(status_code=404, detail="Quote not found")
    return {"message": "Quote and associated QuoteParts deleted"} #success msg

#XXX
#NOTE:  XXX ^^^^^ **POSSIBLY NEED to modify crud (only quotes related to admin id?)  XXX
#XXX



#==================================================
#==============QUOTEPART ENDPOINTS================  
#==================================================
""" #TWO STEPS PROCESS FOR ADDING PART TO QUOTE: 
    # 1. Create Part (for custom parts) or Get existing part 2. Then add part to quote
    # QuotePart link created when part added to quote  """

# (C) CREATE QUOTEPART/ADD NEW PART TO QUOTE (POST)
@app.post("/quotes/{quote_id}/add-part", response_model=QuotePartRead) #added response model 19/10
def add_quote_part(quote_id: int, quote_part: QuotePartAdd, db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    #QuotePartAdd from quote_schema pydantic schema
    try:
        #Add quotepart (add part to quote) and return it
        quote_part_added = quote_crud.add_quote_part(db, quote_id, quote_part)
        return quote_part_added
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) #request syntax is incorrect
    
#(R) read qp not needed XX -- as read quote details allows for quote with qp, p + m 
#==XX (R) READ QUOTEPART (GET) - by id  & (R) READ ALL QUOTEPARTS (GET) XX
#NOTE: can code read quotepart endpoint if needed but do not see why. 

#==(U) UPDATE QUOTEPARTS DETAILS -- needed yes for update
@app.put("/quote-parts/{quote_part_id}", response_model=QuotePartRead) #Added response model 19/10
def update_quote_part(quote_part_id: int, update_data: QuotePartUpdate, db: Session = Depends(get_db) , admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run  
    try:
        updated_quote_part = quote_crud.update_quote_part(db, quote_part_id, update_data.model_dump(exclude_unset=True))
        #“Convert the Pydantic model into a dictionary, only including fields that admin actually sent in request.”
        #prevents overwriting values to None values when only 1 field to update is sent 19/10
        return updated_quote_part
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
#==(D) DELETE QUOTEPART 
@app.delete("/quote-parts/{quote_part_id}")
def delete_quote_part(quote_part_id: int, db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    try:
        #Delete quotepart in db
        quote_crud.delete_quote_part(db, quote_part_id) #delete method -- True bool returned if successful
        return {"message": "QuotePart deleted and total recalculated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) #404 not found error - exception raised


#==================================================
#======== ML PREDICTION ENDPOINT ==================
#==================================================
#FULL PYDANTIC DONE FOR POST PREDICTION
@app.post("/quotes/{quote_id}/predict", response_model=MLPredictionResponse) #added response model 20/10
def predict_quote_time(quote_id: int, db: Session = Depends(get_db), admin_id: int = Depends(verify_jwt_token) ): #21/10 endpoint protected *token verification run
    #Manual trigger for ML prediction (when mobile frontend user clicks button).

    try:

        #NOTE: COULD ADD ADDITIONAL METHOD TO RECALC QUOTE TOTAL BEFORE REQUESTING THE QUOTE 
        updated_calc_quote = quote_crud.recalc_quote_total_time(db, quote_id)
        #updated_calc_quote not used -- need more details thus below 

        #get quote with full details (joins from Q to QP, P, M tables)
        quote_with_details = quote_crud.get_quote_with_details(db, quote_id)
        if not quote_with_details: #if no quote details  (no quote with details)
            raise HTTPException(status_code=404, detail="Quote not found")

        if not quote_with_details.quote_parts: #if no quoteparts -- in quote details
            raise HTTPException(status_code=400, detail="Quote has no parts to predict")

        """ #put the ml_prediction_request_payload together
        ml_prediction_request_payload = MLPredictionRequest( order_date = str(quote_with_details.order_date), #order_date from order
                                                            material_code = quote_with_details.quote_parts[0].part.material_code, #material_code from part
                                                            calculated_total_time = quote_with_details.calculated_total_time or 0, #calculated_total_time from order or 0 prevents NoneType crash if DB has none for calc time
                                                            quantity= sum(qp.quantity for qp in quote_with_details.quote_parts)
                                                            #sum all the quoteparts' quantities within the quotedetails to get total quantity for ml service prediction req
    ) """
        
        #CHANGING TO PREDICT PER PART THEN SUM PREDICTIONS TOGETHER FOR TOTAL QUOTE PREDICTION TIME 
        #put the ml_prediction_request_payload together  (REQUIRES CHANGE BELOW)
        ml_prediction_request_payload = MLPredictionRequest( order_date = str(quote_with_details.order_date), #order_date from order
                                                            material_code = quote_with_details.quote_parts[0].part.material_code, #material_code from part (1)
                                                            calculated_total_time =  quote_with_details.quote_parts[0].calculated_part_time , #or 0, #calculated_part_time from quotepart or 0 prevents NoneType crash if DB has none for calc time
                                                            quantity= quote_with_details.quote_parts[0].quantity )
        #SEND ML PREDICTION REQUEST PAYLOAD TO ML SERVICE 
    
        #Send ML Prediction Request and receive prediction
        prediction_response = send_prediction_request(ml_prediction_request_payload)

        #Update predicted total time in db (for quote)
        predicted_time = prediction_response.predicted_total_time or 0  #get predicted value from prediction_response
        #or 0 prevents NoneType crash if DB has none for calc time 
        updated = quote_crud.update_quote_prediction(db, quote_id, predicted_time)

        #return quote_id, predicted_time, and a message -- successful prediction response and db update
        return {
            "quote_id": updated.id,
            "predicted_total_time": updated.predicted_total_time,
            "message": "Prediction saved successfully" #, 
        }
    except Exception as e:
        #Internal server error - Failed ML Prediction 
        raise HTTPException(status_code=500, detail=f"ML prediction failed: {e}")

#==================================================
""" if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = 'localhost', port = 8002) """



#================================================================================
#=============================SCRAPS=============================================
""" #should i add DBSessionLocal = DBSession then change below to DBSessionLocal???
#already have get_db() in quote_crud.py, and you’re importing it:
#DB dependency
def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close() """

"""#================= Material Types and Time Calculations ============
#Actual Time Calculations
def calculate_actual_time(cutting_time, drilling_time, num_pierces, setup_time):
    actual_time = cutting_time + (drilling_time * num_pierces) + setup_time
    return actual_time """

#==============================BEFORE REFACTOR======================================
""" #quote_main.py imports 
from fastapi import FastAPI, Depends, HTTPException, Header #FastAPI
from sqlalchemy.orm import Session, joinedload #Sqlachemy

import requests
#import jwt  #jwt token
import os  #load SECRET_KEY and ML_SERVICE_URL from environment.

from database_schema.Database_schema import Session as DBSession #SQLALCH MODEL SCHEMA 

from .quote_schema import QuoteCreate, QuoteRead

#from quotation_service import  quote_crud
#from quotation_service.quote_crud import get_all_materials, get_material, get_db #absolute
from .quote_crud import get_db, get_all_materials, get_material
#, create_quote_with_parts, get_quote, list_quotes  """

#REMOVED FROM POST PART -- caused error -- thus used PartCreate pydantic
#XX REPLACE --USING DICT NOT PYDANTIC 
""" @app.post("/parts")
def add_part(part_description: str, material_code: str, db: Session = Depends(get_db)):
    try:
        return quote_crud.create_part(db, part_description, material_code)
        #return quote_crud.create_part(db, part_description, material_code) #quote_crud.create_part or import and use create_part
    except ValueError as e: 
        raise HTTPException(status_code=400, detail=str(e)) #valueError - description or material code X
 """


#SCREP --NOT FULL PYDANTIC DONE FOR POST PREDICTION
""" @app.post("/quotes/{quote_id}/predict", response_model=MLPredictionResponse) #added response model 20/10
def predict_quote_time(quote_id: int, db: Session = Depends(get_db)):
    #Manual trigger for ML prediction (when mobile frontend user clicks button).

    #NOTE: COULD ADD ADDITIONAL METHOD TO RECALC QUOTE TOTAL BEFORE REQUESTING THE QUOTE 
    updated_calc_quote = quote_crud.recalc_quote_total_time(db, quote_id)
    #updated_calc_quote not used -- need more details thus below 

    #get quote with full details (joins from Q to QP, P, M tables)
    quote_with_details = quote_crud.get_quote_with_details(db, quote_id)
    if not quote_with_details: #if no quote details  (no quote with details)
        raise HTTPException(status_code=404, detail="Quote not found")

    if not quote_with_details.quote_parts: #if no quoteparts -- in quote details
        raise HTTPException(status_code=400, detail="Quote has no parts to predict")

    #put the ml_prediction_request_payload together
    ml_prediction_request_payload = {
        "order_date": str(quote_with_details.order_date), #order_date from order
        "material_code": quote_with_details.quote_parts[0].part.material_code,  #material_code from part
        "calculated_total_time": quote_with_details.calculated_total_time or 0,  #calculated_total_time from order or 0 prevents NoneType crash if DB has none for calc time
        "quantity": sum(quote_part.quantity for quote_part in quote_with_details.quote_parts) #, 
        #sum all the quoteparts' quantities within the quotedetails to get total quantity for ml service prediction req
    }

    #SEND ML PREDICTION REQUEST PAYLOAD TO ML SERVICE 
    try:
        #Send ML Prediction Request and receive prediction
        prediction_response = send_prediction_request(ml_prediction_request_payload)

        #Update predicted total time in db (for quote)
        predicted_time = prediction_response.predicted_total_time or 0  #get predicted value from prediction_response
        #or 0 prevents NoneType crash if DB has none for calc time 
        updated = quote_crud.update_quote_prediction(db, quote_id, predicted_time)

        #return quote_id, predicted_time, and a message -- successful prediction response and db update
        return {
            "quote_id": updated.id,
            "predicted_total_time": updated.predicted_total_time,
            "message": "Prediction saved successfully" #, 
        }
    except Exception as e:
        #Internal server error - Failed ML Prediction 
        raise HTTPException(status_code=500, detail=f"ML prediction failed: {e}") """