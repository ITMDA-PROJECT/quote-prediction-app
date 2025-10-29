#quote_crud.py  #RENAME this to do that
from sqlalchemy.orm import Session #Sqlalchemy session for db session 
from sqlalchemy.orm import joinedload #for get_quote_with_details -- Quote, QuotePart, Part, Material joins
from datetime import datetime, date

#from typing import List, Optional #when used for pydantic but removed
#from .ml_client import send_prediction_request #for prediction on total quote time -- not needed here but used in quote_mian for prediction endpoint

#Import your DB models and DB Session factory from database_schema.py
#using absolute path for now 
from python_backend.database_schema.Database_schema import Material, Part, Quote, QuotePart, Session as DBSession #Absolute #nned to go back a lvl
#from ..database_schema.Database_schema import Material, Part, Quote, QuotePart, Session as DBSession #Relative
""" from .quote_schema import QuoteCreate, QuotePartCreate #MS schema """
from .quote_schema import QuoteCreate, QuotePartAdd #MS + Hybrid approach



#================= HELPERS ====================================
#----------Helper: get_db dependency (used in FastAPI) ----------
#local alias for the DB Session Maker (factory)
DBSessionLocal = DBSession

#DB dependency - get db     
def get_db():
    db = DBSessionLocal()
    try:
        yield db
    finally:
        db.close()

#----------Helper: calculate_total_time_for_part (QuotePart) ----------
#CALCULATE PART (PART TOTAL TIME) -- which allows to be used in (add_part_to_quote function)
def calculate_total_time_for_part(db: Session, material_code: str, cutting_length_mm: float, num_pierces: int) -> float:
    """
    Calculate the manufacturing time (in minutes) for a single part instance. (QuotePart)
    Looks up material by material_code (string) as material_code is unique and will not be modified.
    """
    #==== GET MATERIAL for part (in part instance = QuotePart)
    #GET Material (based on String material_code - still unique - admin knows this material code) 
    # (ignoring id int field for now - updated - removed material id field as material code will be prepopulated and will not change)
    material = db.query(Material).filter((Material.material_code == material_code)).first() #fixed to material_code 19/10
    
    #NO MATERIAL FOUND in DB - raise ValueError w msg
    if not material:
        raise ValueError(f"Material with code '{material_code}' not found in DB.")
    
    #=== GET MATERIAL VALUES for part (for part time calculation)
    # Read Material values === DB columns use attribute names as in Database_schema.py:
    #material.cutting_speed (mm/min), material.drilling_time (seconds), material.setup_time (minutes)
    cutting_speed = getattr(material, "cutting_speed", None)
    drilling_time_s = getattr(material, "drilling_time", None)
    setup_time_min = getattr(material, "setup_time", None)

    #NO Material values received (either None or 0 *for cuttig speed then raise ValueError)
    if cutting_speed is None or cutting_speed == 0: #if cutting_speed in (None, 0):
        raise ValueError("Material cuttingSpeed missing or zero.")
    if drilling_time_s is None:
        raise ValueError("Material drillingTime missing.")
    if setup_time_min is None:
        raise ValueError("Material setupTime missing.")
    
    #PART TOTAL_MIN CALCULATION
    cutting_time_min = cutting_length_mm / cutting_speed  #cutting_time_min  (dist/speed = time)
    drilling_time_min = (drilling_time_s * num_pierces) / 60.0 #drilling_time_min
    total_min = cutting_time_min + drilling_time_min + setup_time_min 
    return total_min

#RECALC + UPDATE QUOTE TOTAL TIME (done in (U) of QUOTE CRUD)
#PREDICTION UPDATE FOR QUOTE (done in (U) of QUOTE CRUD)

#================================================================

#CRUD FOR TABLES --> Material, Part, Quote, QuotePart

#============================================
#==============MATERIAL CRUD ================
#============================================
#===(C) Materials Created and Imported from excel CompletedTime.xlsx  with import_materials.py script 
"""Run in terminal once for import : python -m python_backend.quotation_service.import_materials """

#===(R) Read Material from DB 
#Read/Get one Material by material_code 
def get_material(db: Session, material_code: str): 
    ''' - db instance of Session passed to perform query
        - Get one specific material by its material code which is of type string/str '''
    return db.query(Material).filter(Material.material_code == material_code).first()

#Read/Get all Materials
#--> (prepopulated values to allow for frontend to show default materials)
def get_all_materials(db: Session): #no offset or limit
    return db.query(Material).all() 
    #no offset or limit (want all materials for population of widgets)

#(U) Update Materials & (D) Delete Materials (not needed as fixed materials prepopulated)

#============================================
#==============PART CRUD================
#============================================

#(C) Create Part (NEW PART)
#Part - id (PK) , part_description, material_code (FK)
def create_part(db: Session, new_part_description: str, new_part_material_code: str):
    #--get material for part 
    material = db.query(Material).filter(Material.material_code == new_part_material_code).first()
    #IF material not found - ValueError (should not occur if front-end has dropdownlist of fixed material codes to choose from)
    if not material:
        raise ValueError("Material code not found")
    
    #--create part and insert/add into part table in db 
    new_part = Part(part_description=new_part_description, material_code=new_part_material_code)
    db.add(new_part) 
    db.commit() 
    db.refresh(new_part) #id auto generated thus allows most recent new_part state to show
    return new_part #return new_part on successful part insert 

#(R) READ PART (1, All) 
#Get one part (by part id) 
def get_part(db: Session, part_id: int):
    return db.query(Part).filter(Part.id == part_id).first()

# Get all Parts 
# (NOTE: not used in initial version of front end but good to include for future if allow for existing parts to be added to catalog and custom)
def get_all_parts(db: Session):
    return db.query(Part).all()

#(U) Update (-- when updating the Part Record (Admin would do this))
def update_part(db: Session, part_id: int, new_description: str, new_material_code: str): 
    #--get part -- to modify/update/edit
    part_to_update = db.query(Part).filter(Part.id == part_id).first()
    #IF no part found - with that part_id (None returned)
    if not part_to_update:
        return None
    
    #-- IF NEW PART DATA (part_description or material_code ) 
    if new_description:
        part_to_update.part_description = new_description #update part_description to new_description
    if new_material_code:
        part_to_update.material_code = new_material_code #update material_code to new_material_code
    
    #UPDATE PART DATA in PART TABLE in DB
    db.commit()
    db.refresh(part_to_update) #refresh to show newest part state (changes reflect)
    return part_to_update #return part_to_update after successful update


#(D) Delete Part (in DB Table Part - not deleting from Quote ) 
def delete_part(db: Session, part_id: int): 
    #--get part to delete (by part_id)
    part_to_delete = db.query(Part).filter(Part.id == part_id).first()

    #if no part that matches/found (by that part_id) - return None
    if not part_to_delete:
        return None

    #Delete part in Part Table in DB 
    db.delete(part_to_delete)
    db.commit()
    return {"message": "Part deleted"} #On successful part deletion - Return success message




#============================================
#==============QUOTE CRUD================
#============================================
#(C) Create Quote (EMPTY QUOTE) 
def create_empty_quote(db: Session, quote_data: QuoteCreate):  #Pydantic QuoteCreate
    """---Creates a new empty quote with no parts initially. 
       ---Then when part is created can be added into this empty quote. 
        * Parameters: 
        -- db: SQLAlchemy session
        -- quote_data:  QuoteCreate - pydantic schema from quote_schema.py 
    """
    #AUTO GENERATED -- quote_number, order_date, 
    #get timestamp for temp solution for auto-generated quote number 
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  #YYYYMMDDHHMMSS
    auto_quote_number = f"WXQ{timestamp}" #using WXQ prefix with timestamp suffix

    new_quote = Quote(
        #quote_number = quote_data.quote_number, #admin enters
        #WXQ+id approach faulty
        #using WXQ+timestamp with seconds for now as temp solution
        quote_number = auto_quote_number,
        turn_around_days = quote_data.turn_around_days, #admin enters
        
        #set calculated_total_time & predicted_total_time = None at empty quote
        calculated_total_time = None,
        predicted_total_time = None,

        #AUTO generated fields -- order date and quote_status 
        order_date= date.today(), #from todays date -- also reordered based on erd
        quote_status = False, #in progress = False (at creation of empty quote)
        
        admin_id = quote_data.admin_id #from quote_main.py where it uses jwt token to get admin_id
    )
    #Add new quote to db, commit changes to db, refresh db to reflect new_quote state/data
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    return new_quote #return new_quote on successful create

#====(R) READ QUOTES
#(R) READ QUOTE -- Get quote (by quote id) (note: quote_number autogenerated)
def get_quote(db: Session, quote_id: int): 
    quote = db.query(Quote).filter(Quote.id == quote_id).first()  #get Quote by quote_id (auto gen) 
    return quote

#(R) READ QUOTE DETAILS  (Q JOINS with QP,P,M)  #EAGER LOADING 
""" #NEWLY ADDED FOR FULL DETAILS ON QUOTE (Q,QP,P,M)
#get_quote_with_details -- incl. Quote, QuotePart, Part, Material joins """
def get_quote_with_details(db: Session, quote_id: int):
    """ Return a single quote including its quote parts, part info, and material info."""
    quote_with_details = (
        db.query(Quote)
        .options(
            joinedload(Quote.quote_parts) #joins Q to QP
            .joinedload(QuotePart.part) #joins QP to P
            .joinedload(Part.material) #joins P to M
        )
        .filter(Quote.id == quote_id) #based on given quote_id
        .first() 
    )
    #if no quote with details -- then valueError
    if not quote_with_details:
        raise ValueError(f"Quote {quote_id} not found")
    return quote_with_details #returns quote with qp,p,m information

""" -- IF LESS DETAILS NEEDED - only Q and QP
#(R) READ QUOTE w QP 
def get_all_quotes_with_quoteparts(db: Session):
    return (
        db.query(Quote)
        .options(joinedload(Quote.quote_parts).joinedload(QuotePart.part))
        .all()
    ) """


#Get all quotes (ALL) - not used
def get_all_quotes(db: Session):
    all_quotes = db.query(Quote).all()
    return all_quotes

#Get all quotes (In progress) 
def get_all_in_progress_quotes(db: Session):
    in_progress_quotes = db.query(Quote).filter((Quote.quote_status == False)).all() #False for In Progress
    return in_progress_quotes

#Get all quotes (Completed) 
def get_all_completed_quotes(db: Session):
    completed_quotes = db.query(Quote).filter((Quote.quote_status == True)).all() #True for Completed
    return completed_quotes

# #----------USED for FILTERED In progress and Completed Quotes -------------
# #Get all quotes (In progress) ***FILTERED  *corrected 19 Oct 2025
# def get_all_in_progress_quotes_filtered(db: Session):
#     """Return in-progress quotes (False) with only selected columns - quote_number, predicted_total_time"""
#     in_progress_quotes_filtered = db.query(Quote.quote_number, Quote.predicted_total_time, Quote).filter((Quote.quote_status == False)).all() #F=In Progress
#     #return in_progress_quotes_filtered #SQLAlchemy error --mixing explicit columns w/model object
#     return [{"quote_number": quote[0], "predicted_total_time": quote[1]} for quote in in_progress_quotes_filtered] #returns list of filtered quotes

# #Get all quotes (Completed)  ***FILTERED *corrected 19 Oct 2025
# def get_all_completed_quotes_filtered(db: Session):
#     """Return completed quotes (True) with only selected columns - quote_number, predicted_total_time"""
#     completed_quotes_filtered = db.query(Quote.quote_number, Quote.predicted_total_time).filter((Quote.quote_status == True)).all() #True for Completed
#     #return completed_quotes_filtered #SQLAlchemy error --mixing explicit columns w/model object
#     return [{"quote_number": quote[0], "predicted_total_time": quote[1]} for quote in completed_quotes_filtered] #returns list of filtered quotes
# #------------------------------------------------------------------------

#----------USED for FILTERED In progress and Completed Quotes -------------
#Get all quotes (In progress) ***FILTERED  *corrected 19 Oct 2025   #recorrected with id 28/10
def get_all_in_progress_quotes_filtered(db: Session):
    """Return in-progress quotes (False) with only selected columns - quote_number, predicted_total_time"""
    in_progress_quotes_filtered = db.query(Quote.id, Quote.quote_number, Quote.predicted_total_time, Quote).filter((Quote.quote_status == False)).all() #F=In Progress
    #return in_progress_quotes_filtered #SQLAlchemy error --mixing explicit columns w/model object
    return [{"id": quote[0], "quote_number": quote[1], "predicted_total_time": quote[2]} for quote in in_progress_quotes_filtered] #returns list of filtered quotes
 
#Get all quotes (Completed)  ***FILTERED *corrected 19 Oct 2025  #recorrected with id 28/10
def get_all_completed_quotes_filtered(db: Session):
    """Return completed quotes (True) with only selected columns - quote_number, predicted_total_time"""
    completed_quotes_filtered = db.query(Quote.id, Quote.quote_number, Quote.predicted_total_time).filter((Quote.quote_status == True)).all() #True for Completed
    #return completed_quotes_filtered #SQLAlchemy error --mixing explicit columns w/model object
    return [{"id": quote[0], "quote_number": quote[1], "predicted_total_time": quote[2]} for quote in completed_quotes_filtered] #returns list of filtered quotes
#------------------------------------------------------------------------

#====UPDATE QUOTE 
""" #Update Quote -- When Quote Status is changed from In progress (False) to Completed (True) 

#When Quote is saved/updated  (after ADDING PART or UPDATING PART or DELETE PARTS)
# --calculated_total_time is  saved   
# ** calculated_total_time (ENTIRE QUOTE - SUM Part in Quote (QuotePart) Total Times)

# **predicted_total_time -- request sent to ML Service -- response includes predicted time for quote
# -- (predicted time only saved when manual action causes request sent)"""

# (U) Update Quote Status -- update status from In Progress (False) to Complete (True)
#in endpoint -- save_updated_quote_status()
def update_quote_status(db: Session, quote_id: int ,new_quote_status: bool ): #quote_id: int  or quote_num: str 
    #--get quote -- to modify/update/edit
    quote_to_update = db.query(Quote).filter(Quote.id == quote_id).first()

    #IF no quote found - with that quote_id (None returned)
    if not quote_to_update:
        raise ValueError("Quote does not exist")
    
    #UPDATE QUOTE STATUS in QUOTE TABLE in DB 
    quote_to_update.quote_status = new_quote_status

    db.commit()
    db.refresh(quote_to_update) #refresh to show newest quote state (changes reflect)
    return quote_to_update #return quote_to_update after successful update


 #-- IF NEW QUOTE DATA (quote_status) - others not changed again
    """ #if turn_around_days 
    if turn_around_days:
        quote_to_update.turn_around_days = new_turn_around_days #update material_code to new_material_code   
    #scrap completion date for now """  

"""
#When Quote is saved/updated  (after ADDING PART or UPDATING PART or DELETE PARTS)
# --calculated_total_time is  saved   
# ** calculated_total_time (ENTIRE QUOTE - SUM Part in Quote (QuotePart) Total Times)

# **predicted_total_time -- request sent to ML Service -- response includes predicted time for quote
# -- (predicted time only saved when manual action causes request sent)"""

# ====== Update Quote Times ======
# (U) Update Quote Calculated Total Time  ( calculated_total_time )
""" #NOTE: Update Calculated time is fast compared to ML prediction thus can update the calculation more frequently to keep data up to date.
#Thus on each time a quotepart is added, quotepart is updated, or a quotepart is deleted
#--->  Quote calculated_total_time needs to be updated to be more accurate (as it depends on the quoteparts in the quote) """

# (RE)CALCULATE QUOTE calculated_total_time & UPDATE IN QUOTE TABLE IN DB 
def recalc_quote_total_time(db: Session, quote_id: int):
    """For a specific quote based on quote_id parameter recieved.
    Recalculate total time for quote (no ML service) by summing up quotepart calculated times 
    and stores it in Quote's calculated_total_time attribute"""

    #get quote by id to recalc+update (if not found, then valueErrpr msg raised)
    quote_to_calc_update = db.query(Quote).filter(Quote.id == quote_id).first() 
    if not quote_to_calc_update:
        raise ValueError(f"Quote {quote_id} not found")
    
    #sum quoteparts' calculated_part_time for quote to get quote's calculated_total_time
    total_time = sum(qp.calculated_part_time for qp in quote_to_calc_update.quote_parts or []) #empty list summed if no quoteparts for quote

    #update quote's calculated total time in db table
    quote_to_calc_update.calculated_total_time = total_time 
    db.commit()
    db.refresh(quote_to_calc_update)
    return quote_to_calc_update 

# (U) Update Quote Predicted Total Time  ( predicted_total_time )
""" #NOTE: update the quote prediction time after a manual event (eg button click) for prediction to be requested, 
# once requested this method is called to store the latest prediction 
# -- after manual event due to delay of ML service times (+-30seconds)"""

def update_quote_prediction(db: Session, quote_id: int, predicted_time: float):
    """Store the predicted time from ML Serive prediction into the Quote table in db."""
    #get quote by id -- to update predicted_total_time
    quote_to_update_prediction = db.query(Quote).filter(Quote.id == quote_id).first() 
    if not quote_to_update_prediction: 
        raise ValueError(f"Quote {quote_id} not found")
    
    #Update predicted_total_time for quote in db table (commit and refresh)
    quote_to_update_prediction.predicted_total_time = predicted_time
    db.commit()
    db.refresh(quote_to_update_prediction)
    return quote_to_update_prediction 


#(D) Delete Quote (based on quote_id)  
""" NEED CASCADE DELETE -- Delete Quote (deletes children QuoteParts too)
- included in Database_schema.py Quote -> QuotePart (SQLAlchemy relationship) """
def delete_quote(db: Session, quote_id: int):
    #get quote to delete (by quote id)
    selected_quote = db.query(Quote).filter(Quote.id == quote_id).first() 
    
    #quote not found by quote id -- return None
    if not selected_quote:
        return None
    db.delete(selected_quote)  #delete the selected quote from db
    db.commit()
    return True #True for successful deletion of quote
   


#============================================
#==============QUOTEPART CRUD ================
#============================================
#(C) Create QuotePart (create link between quote and part by adding part into existing quote)
#19 Oct -- added response model
def add_quote_part(db: Session, quote_id: int, quote_part_data: QuotePartAdd):
    """ Adds a new part to an existing quote.
    PARAMETERS:
     -- db: SQLAlchemy session
     -- quote_id: ID of the quote to link the part to
     -- quote_part_data: QuotePartAdd -- pydantic schema from quote_schema.py
    """
    #19 Oct 2025 - added try except with error fixing 
    try: 
        #-----GET QUOTE TO ADD PART TO--------
        #Get quote by quote id -- if no quote - value error rasied w/message
        quote_to_add_part = db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote_to_add_part:
            raise ValueError(f"Quote with id {quote_id} not found")
        
        #-----CHECK PART DATA (DICTIONARY) ---------
        #1 IF EXISTING PART ADDED TO QUOTE  --> (for a new QuotePart)
        #Find existing part in db -- then add to quote (create link)
        #-- if the part id is in the QuotePartAdd data then get the part id from db
        if quote_part_data.part_id:
            part = db.query(Part).filter(Part.id == quote_part_data.part_id).first() #GET PART --can use id in qp link
            #NO PART -- with part id  (Value error message shown)
            if not part:
                raise ValueError(f"Part id {quote_part_data.part_id} not found")
                

        #2 IF NEW PART (CUSTOM PART) ADDED TO QUOTE  --> (for a new QuotePart)
        # (if theres part details added for custom part)
        # if part description (and material code selected) 
        # -- then create new part and add to quote (link)  (shown after)
        elif quote_part_data.part_description and quote_part_data.material_code:
            #Create new part to db
            part = Part(
                part_description = quote_part_data.part_description,
                material_code = quote_part_data.material_code,
            )
            db.add(part)
            db.commit()
            db.refresh(part) #newpart but name kept as part (as exist and custom need to be "part")
            #^^^!!! COULD CALL create_part crud method instead??

            #or --- CHECK 
            """ #db.add(part)
            #db.flush """
            '''Writes out all pending object creations, deletions 
            and modifications to the database as INSERTs, DELETEs, UPDATEs, etc.'''

        #NO PART DATA IN DICT -- ValueError msg shown
        else:
            raise ValueError("Either part_id or (part_description + material_code) required")

        
        #--- CALCULATION for QP TOTAL TIME   
        calculated_quote_part_time = calculate_total_time_for_part(
            db, part.material_code, 
            quote_part_data.cutting_length, quote_part_data.num_pierces) 

        #----- ADD PART TO QUOTE (CREATE QUOTEPART LINK) -------
        # -- new part created --> add to quote (link) with quotepart sepcific data such as:
        #QP - id (auto gen), quote_id, part_id, quantity, quantity, cutting_length, num_pierces, calculated_part_time* from func
        
        #CREATE QUOTE PART LINK 
        #Create new_quote_part  (to add into db ) -- access value by key in part_data dict
        new_quote_part = QuotePart(quote_id = quote_id, #quote_to_add_part.id, #quote id received in par *quote_id for part to be linked to
                                part_id = part.id, #part_id 
                                
                                quantity = quote_part_data.quantity, #already factored in thus total part time is for all quantity (cutting length accounted)
                                cutting_length = quote_part_data.cutting_length,
                                num_pierces = quote_part_data.num_pierces,

                                #calculated_part_time in db = calculated answer (not in dict)
                                calculated_part_time = calculated_quote_part_time 
                                )

        #Add part into quote (link quote and part table) *Create new QuotePart in db 
        db.add(new_quote_part)
        db.commit()
        db.refresh(new_quote_part) 
        
        #OR -- CHECK
        """ 
        db.add(new_quote_part)
        db.flush()   #generate id before recalc
        """

        #Recalculate quote total after change (of quotepart)
        recalc_quote_total_time(db, quote_id)
        #& commit if use flush at top 
        """  
        db.commit()
        db.refresh(new_quote_part)
        """
        return new_quote_part #successful new quotepart inset - return new quotepart 
    
    except Exception as e:
        print(f"add_quote_part ERROR --> {e}")
        db.rollback()
        raise

    
    

#(R) Read
#
#
#
#


#(U) Update -- TEMP (no pydantic yet -- thus dict used for now) **need to replace
def update_quote_part(db: Session, quote_part_id: int, update_data: dict): 
    #Get quote_part to update  (by quote_part_id)
    quote_part_to_update = db.query(QuotePart).filter(QuotePart.id == quote_part_id).first()
    if not quote_part_to_update:
        raise ValueError("QuotePart not found")

    #CHECK FOR QuotePart DATA (in dict) -- and set quote_part values in db 
    if "quantity" in update_data:
        quote_part_to_update.quantity = update_data["quantity"]
    if "cutting_length" in update_data:
        quote_part_to_update.cutting_length = update_data["cutting_length"]
    if "num_pierces" in update_data:
        quote_part_to_update.num_pierces = update_data["num_pierces"] 

    #recalc updated quotepart's calculated_part_time
    quote_part_to_update.calculated_part_time = calculate_total_time_for_part(
        db, quote_part_to_update.part.material_code, quote_part_to_update.cutting_length, quote_part_to_update.num_pierces
    )

    db.commit()
    db.refresh(quote_part_to_update)
    #Recalculate quote total after change (of quotepart)
    recalc_quote_total_time(db, quote_part_to_update.quote_id)

    return quote_part_to_update
    #FIX !!!^ dict needs to be replaced with pydantic

#(D) Delete
def delete_quote_part(db: Session, quote_part_id: int):
    #get quotepart to delete
    quote_part = db.query(QuotePart).filter(QuotePart.id == quote_part_id).first()
    if not quote_part:
        raise ValueError("QuotePart not found") #valuerror raise if quote_part not found

    #get quote_id -- to allow for recalc after delete
    quote_id = quote_part.quote_id 

    #Delete quotepart
    db.delete(quote_part)
    db.commit()

    #Recalculate quote total after delete (of quotepart)
    recalc_quote_total_time(db, quote_id)
    return True
#==========================================================



#==========================================================
#-----OFFSET + LIMIT (scraps)
"""  
---> return db.query(Quote).all() #no offset or limit
OR with SKIP AND LIMIT 
--> return db.query(Quote).offset(skip).limit(limit).all()
    skip = nr rows to skip (like SQL OFFSET)
    limit = nr rows to return (like SQL LIMIT).
    --eg. list_quotes(skip=10, limit=5) ==> returns quotes 11–15.
"""

#LKtestadmin LKtest@gmail.com LKhashedpwd
#LeviKits levikits@gmail.com levikits