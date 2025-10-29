from sqlalchemy import create_engine, Column, Integer, String, Float, Table, ForeignKey, Boolean, Date, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timezone

'''git checkout backend

READ ME FOR CONNECTION TO DATABASE

First run this command in the terminal:
pip install sqlalchemy pyodbc

In the connection string change the SERVER_NAME to the name of the server. You can see the name of the server when you log in, in the middle of the screen it will say server name.
Change the DATABASE_NAME to the name that you have given to the database that you have created. You can see this by dropping down the databases folder once you have logged in.
You can right click on the database and go to properties at the bottom if you want to just copy the database name.
'''
#run once using:   python -m database_schema.Database_schema

#connection_string = "mssql+pyodbc://SERVER_NAME/DATABASE_NAME?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
#connection_string = "mssql+pyodbc://MATHEW-LAPTOP\\SQLEXPRESS/QuotePredictionDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes" #MS
#connection_string = "mssql+pyodbc://LEVANNAH-SCAR18/tester?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes" #LK
# DATABASE_URL=mssql+pyodbc://SKYE_LAPTOP/QuoteAppPOC?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

""" import os
from dotenv import load_dotenv
load_dotenv()
connection_string = os.getenv("DATABASE_URL") """

connection_string = "mssql+pyodbc://SKYE_LAPTOP/QuoteAppPOC?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes" #LK v2

engine = create_engine(connection_string) #1 Create Engine 
Base = declarative_base() #2 Declare the Base

class Material(Base):
    __tablename__ = "materials"
    #Attributes
    """ id = Column(Integer, primary_key = True)
    material_code = Column(String(20), unique = True, nullable=False) """
    material_code = Column(String(20), primary_key = True,  unique = True, nullable=False)
    #materialName = Column(String, nullable = False)
    #thickness = Column(Float, nullable = False) #only working with 20 thickness default for consistent data sets
    cutting_speed = Column(Float, nullable = False)  #in mm/min
    drilling_time = Column(Float, nullable = False)  #in seconds per pierce
    setup_time = Column(Float, nullable = False)     #in minutes

    #Relationships
    parts = relationship("Part", back_populates="material")


class Part(Base):
    __tablename__ = 'parts'
    #Attributes 
    id = Column(Integer, primary_key=True)
    part_description = Column(String(100), nullable=False) #added 100 limit based on erd
    #material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)    #FK
    material_code = Column(String(20), ForeignKey("materials.material_code"), nullable=False)    #FK

    #Relationships
    material = relationship("Material", back_populates="parts")
    quote_parts = relationship("QuotePart", back_populates="part")


class QuotePart(Base):
    __tablename__ = "quote_parts"
    #Attributes 
    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)   #FK
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)     #FK
    quantity = Column(Integer, nullable=False)
    cutting_length = Column(Float, nullable=False)
    num_pierces = Column(Integer, nullable=False)    
    calculated_part_time = Column(Float)

    #Relationships
    quote = relationship("Quote", back_populates="quote_parts") #needed to link to quote 
    part = relationship("Part", back_populates="quote_parts")

class Quote(Base):
    __tablename__ = "quotes"
    #Attributes
    id = Column(Integer, primary_key = True)
    quote_number = Column(String(20), unique=True, nullable = False)    #changed from int to String
    turn_around_days = Column(Float, nullable = False)
    calculated_total_time = Column(Float)
    predicted_total_time = Column(Float)
    order_date = Column(Date, nullable = False)
    quote_status = Column(Boolean, nullable = False) #True = Complete & False = In Progress
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable = False)   #FK

    #Relationships
    admin = relationship("Admin", back_populates="quotes")
    quote_parts = relationship("QuotePart", back_populates="quote"
                               , cascade="all, delete-orphan")  
                                #added cascade delete -- enable cascade delete between Quote and QuotePart.


class Admin(Base):
    __tablename__ = "admins"
    #Attributes
    id = Column(Integer, primary_key = True)
    username = Column(String(255), nullable = False, unique = True)
    email = Column(String(255), nullable = False, unique = True)
    password = Column(String, nullable = False)

    #22/10 Added - to match User Service - integration 
    is_active = Column(Boolean, default=False, nullable=False)
    failed_login_count = Column(Integer, default=0, nullable=False)

    #Relationships
    quotes = relationship("Quote", back_populates="admin", cascade="all, delete-orphan") 
    tokens = relationship("AdminToken", back_populates="admin", cascade="all, delete-orphan")


class AdminToken(Base):
    __tablename__ = "admin_tokens"
    #Attributes
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)     #FK
    token = Column(String(255), nullable=False, unique=True) #added 255 limit (max not allowed)
    token_type = Column(String(50), nullable=False) #added 50 limit
    expiry = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    #Relationships
    admin = relationship("Admin", back_populates="tokens")

#Uncomment when creating db once (then recomment)
""" #Note - drop_all added if you have already created tables and correct admintoken table  
Base.metadata.drop_all(engine) #to drop incorrect table (AdminToken String issue) before creating correct table
Base.metadata.create_all(engine) """

Session = sessionmaker(bind=engine) #Session Maker (Factory) used in other py files.

""" #Session object (import for each API) -- open and close a new session for each endpoint
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) """
#Add Alias for Session (Session used in QS , SessionLocal used in US)
SessionLocal = Session #added 22/10 -- for UserService integration 

session = Session()
session.commit()
session.close()

#LKtestadmin LKtest@gmail.com LKhashedpwd  #**LK testing