#Defines Pydantic schemas — how data is validated and serialized 

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import date, datetime


#------------------------------------------------------------------------------------------------------------------------


# #PYDANTIC PRACTICE EXAMPLES:
# class User(BaseModel):
#     name: str
#     email: str
#     account_id: int

# user = User(name="John Doe", email="john.doe@example.com", account_id=123)
# print(user.email)  # Output: john.doe@example.com

# #Custome validation
# @validator("account_id")
# def validate_account_id(cls, value):
#     if value <= 0:
#         raise ValueError(f"account_id must be positive: {value}")
#     return value

# #JSON serialisation
# #1. Convert pydantic to JSON
# user_json_str = user.json()
# print(user_json_str)  # Output: {"name": "John Doe", "email": "john.doe@example.com", "account_id": 123}
# #2. Instead of JSON string, can also convert to dict
# user_dict_object = user.dict()
# #3. JSON string to pydantic model
# json_str = '{"name": "Jane Doe", "email": "jane.doe@example.com", "account_id": 456}'
# user_from_json = User.parse_raw(json_str)


#--------------------------------------------------------------------------------------------------------------------------


#----------------Material schema---------------- works
class MaterialBase(BaseModel):
    material_code: str = Field(..., max_length=20, example="MS-8")
    #The following fields aren't entered by admin, but found in material table in DB, based on materialCode
    cutting_speed: float = Field(..., gt=0, example=100.0) #in mm/min
    drilling_time: float = Field(..., gt=0, example=10.0) #in seconds per pierce
    setup_time: float = Field(..., gt=0, example=5.0) #in minutes

#If ever need to add to material directly (not used currently)
class MaterialCreate(MaterialBase):
    pass

class MaterialRead(MaterialBase):
#No additional fields for read operations
    model_config = ConfigDict(from_attributes=True) #Tells Pydantic to read data even if it is not a dict, but an ORM model (like SQLAlchemy model)



#----------------Part schema---------------- works
class PartBase(BaseModel):
    part_description: str = Field(..., max_length=100, example="Bracket")
    material_code: str   #Used to look up Material in DB (FK)  

class PartCreate(PartBase):
    pass

class PartRead(PartBase):
    id: int     #AutoIncremented PK ID
    material: Optional[MaterialRead] = None   #Nested Material object (optional as it may not be loaded)
    #Returns material object inside part object, access via material.material_code etc

    model_config = ConfigDict(from_attributes=True)




#----------------QuotePart schema (bridging entity)----------------
class QuotePartBase(BaseModel):
    quantity: int = Field(..., gt=0, example=10)
    cutting_length: float = Field(..., gt=0, example=150.5)
    num_pierces: int = Field(..., gt=0, example=5)
    calculated_part_time: Optional[float] = None #Calculated total time for this specific part (quantity * (cutting_time + drilling_time + setup_time))
    quote_id: int   #FK to Quote table
    part_id: int    #FK to Part table

class QuotePartCreate(QuotePartBase):
    pass

class QuotePartRead(QuotePartBase):
    id: int     #AutoIncremented PK ID
    quote_id: int   #FK to Quote table (Avoids circular ref by not nesting full Quote schema)
    part: Optional[PartRead] = None   #Nested Part schema (QuoteRow contains one part)

    #Tells Pydantic to read data even if it is not a dict, 
    #but an ORM model (like SQLAlchemy model)
    model_config = ConfigDict(from_attributes=True)   



#========= QUOTE PART REQUEST SCHEMA  (LK added - for HYBRID approach) ============
#==========================================================================
#for HYBRID approach (catalog and custom parts)
from pydantic import BaseModel, Field
from typing import Optional

class QuotePartAdd(BaseModel):
    #1: use existing part (catalog)
    part_id: Optional[int] = Field(None, description="Existing Part ID (optional)")
    #OR 
    #2: create new part (custom)
    part_description: Optional[str] = Field(None, description="New Part Description")
    material_code: Optional[str] = Field(None, description="Material code for new Part")

    #ALWAYS REQUIRED for quote linkage (QuotePart)
    quantity: int = Field(..., gt=0, description="Quantity of this part in the quote")
    cutting_length: float = Field(..., gt=0, description="Cutting length in mm")
    num_pierces: int = Field(..., ge=0, description="Number of pierces")

    """ class Config:
        orm_mode = True """
    model_config = ConfigDict(from_attributes=True)

#--required for QuotePart (to be read)  *Added 19/10
class QuotePartRead(BaseModel):
    id: int   #qp id
    quote_id: int  #id of quote
    part_id: int #id of part 

    #QP fields
    quantity: int   
    cutting_length: float
    num_pierces: int
    calculated_part_time: float

    model_config = ConfigDict(from_attributes=True)

#-- QuotePart UPDATE schema *Added 19/10
#-- quantity, cutting_length or num_pierces (update)
class QuotePartUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)    #qty >=0
    cutting_length: Optional[float] = Field(None, gt=0) #cl >=0
    num_pierces: Optional[int] = Field(None, ge=0) #np >=0

    model_config = ConfigDict(from_attributes=True)



#==========================================================================
#==========================================================================

#NEW V2 - QUOTE SCHEMA (no jwt testing) - 19 Oct 2025
#adjusted to include auto-generated fields logic and flow 
#---------------- Quote Schema ----------------
class QuoteBase(BaseModel):
    turn_around_days: float = Field(..., gt=0, example=5)
    admin_id: Optional[int] = None  #optional for now until JWT added -- 21/10 keeping in - if removed then  "detail": "\"QuoteCreate\" object has no field \"admin_id\"" error msg
    #^^required fields for user/admin input
    #removed autogenerated fields from base (quote_number,order_date,quote_status)

class QuoteCreate(QuoteBase):
    #auto-generated in backend --thus excluded from user/admin input
    quote_number: Optional[str] = None  #Generated when quote created with timestamp
    order_date: Optional[date] = None   #Generated when quote created from now 
    quote_status: Optional[bool] = None #False for new quotes = In Progress, True = Completed

class QuoteRead(QuoteBase):
    #All fields of Quote that will be sent to mobile side to read 
    id: int  
    quote_number: str
    calculated_total_time: Optional[float] = None  #if there is value saved
    predicted_total_time: Optional[float] = None #if there is value saved
    order_date: date
    quote_status: bool 
    """ #??? possibly require admin id to be shown too??
    admin_id: int  #NOTE:  not needed when jwt implemented  """

    model_config = ConfigDict(from_attributes=True)
    #eg. allows get_quote_with_details() to automatically serialize to nested JSON 

""" #nah - omit admin id instead -- later will come from jwt
{
  "id": 1,
  "quote_number": "WXQ20251018175020",
  "turn_around_days": 5.0,
  "order_date": "2025-10-18",
  "quote_status": false,
  "admin_id": 1   #XXX
} """

#for POST (UPDATE) Quote Status
class QuoteStatusUpdate(BaseModel):
    new_quote_status: bool


#MS V1 PYDANTIC SCHEMA - does not include auto-gen fields logic
""" #----------------Quote schema----------------
class QuoteBase(BaseModel):
    quote_number: str = Field(..., max_length=20, example="WXQ12345")  #XXX
    turn_around_days: float = Field(..., gt=0, example=5) #yes - admin will input this
    calculated_total_time: Optional[float] = None           #Basically adds all totalTime in QuoteParts
    predicted_total_time: Optional[float] = None            #Predicted total time for the quote (from ML model)
    order_date: date
    quote_status: bool   #True for new quotes = In Progress, False = Completed
    admin_id: int        #FK to Admins table (From JWT User Service)


class QuoteCreate(QuoteBase):
    pass

class QuoteRead(QuoteBase):
    id: int     #AutoIncremented PK ID 
    quote_parts: Optional[List[QuotePartRead]] = None  #List of QuoteParts associated with this quote (one-to-many relationship)        

    model_config = ConfigDict(from_attributes=True)
    #eg. allows get_quote_with_details() to automatically serialize to nested JSON """







#----------------ML schema (/predict endpoint in ML Service)----------------
class MLObject(BaseModel):
    order_date: str = Field(..., example="2023-10-15")  #YYYY-MM-DD format
    material_code: str = Field(..., max_length=20, example="MS-8")
    calculated_total_time: float = Field(..., gt=0, example=15.5) #Time in minutes for quote (same as actualTime)
    quantity: int = Field(..., gt=0, example=10)


class MLPredictionRequest(MLObject):
    pass

#UPDATED 20/10  -- None added and Optional to prevent validation errors when ML service returns no value temporarily
class MLPredictionResponse(BaseModel):
    predicted_total_time: Optional[float] = Field(None, gt=0, example=14.0) #Predicted time in minutes for quote (from ML model)
    input: Optional[dict] = None   #Echoes back the input data for traceability

    model_config = ConfigDict(from_attributes=True)
        










#----------------Admin schema----------------
#Not used in this service, but in User Service


    

#Notes:
#Fix circular ref
#Do ML schemas -- look at Declan schema's