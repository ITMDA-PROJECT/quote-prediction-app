#Script to import materials from an Excel file into the database (for dropdowns on frontend)
#to run in terminal (when in cd of Quote-Prediction-App): 
#     --- cd "C:\......\Quote-Prediction-App"
#then --- python -m python_backend.quotation_service.import_materials

import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from python_backend.database_schema.Database_schema import Material, engine

#Load Excel file (same folder as script)
file_path = os.path.join(os.path.dirname(__file__), "Your_Materials_File.xlsx") #Replace with your excel file name
df = pd.read_excel(file_path)

#Rename columns to match the Material model
df = df.rename(columns={    
    "Material Code": "material_code",
    "Cutting speed (mm/min)": "cutting_speed",
    "Drilling time (s)": "drilling_time",
    "SetUp time (min)": "setup_time"
})
#Drop rows with missing required fields
df = df.dropna(subset=["material_code", "cutting_speed", "drilling_time", "setup_time"])

#Start session
Session = sessionmaker(bind=engine)
session = Session()

#Insert rows into the database
for _, row in df.iterrows():
    # Check if material already exists
    if not session.query(Material).filter_by(material_code=row["material_code"]).first():
        material = Material(
            material_code=row["material_code"],
            cutting_speed=row["cutting_speed"],
            drilling_time=row["drilling_time"],
            setup_time=row["setup_time"]
        )
        session.add(material)

#Commit and close session
session.commit()
session.close()

print("Success! Materials imported successfully!")