from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from werkzeug.security import generate_password_hash, check_password_hash
from python_backend.database_schema.Database_schema import Admin, AdminToken, SessionLocal
#from database_schema.Database_schema import Admin, AdminToken, SessionLocal

from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from typing import Optional

# load environment variables (from .env file)
'''
(.env file is ignored by git)
.env file should include:

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=      -our_app_email@gmail.com-
SMTP_PASS=      -our_app_email_password-
SECRET_KEY=     -supersecretjwtkey-
DATABASE_URL=   -DB_URL-
'''

#error with integration -- using manual load for now until fixed #22/1
#os.environ["SMTP_PORT"] = "587"

#Force load of the shared .env before reading variables
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env") #explicitly points to python_backend/.env
load_dotenv(dotenv_path=dotenv_path)

#TEMP CHECK ------ 22/10  --uncommented for debugging
print("DEBUG: .env loaded:")
print("SMTP_PORT:", os.getenv("SMTP_PORT"))
print("SECRET_KEY:", os.getenv("SECRET_KEY"))
#---------

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SECRET_KEY = os.getenv("SECRET_KEY")

# dependency: get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# pydantic request models (defines the format of incoming data)
class AdminSignup(BaseModel):
    username: str = Field(strip_whitespace=True, min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)

class LoginRequest(BaseModel):
    username_or_email: str = Field(strip_whitespace=True, min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=256)

class ResendRequest(BaseModel):
    email: EmailStr

class AdminUpdate(BaseModel):
    username: Optional[str] = Field(strip_whitespace=True, min_length=3, max_length=64)
    email: Optional[EmailStr]
    password: Optional[str] = Field(min_length=8, max_length=256)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

# ---------- Helper Functions ----------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        admin_id = payload.get("admin_id")
        token_type = payload.get("type")
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    if token_type != "login":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    db = SessionLocal()
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    db.close()

    if not admin or not admin.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return admin

def now_utc():
    return datetime.now(timezone.utc)

def sanitize_username(u: str) -> str:
    return u.strip()

def sanitize_email(e: str) -> str:
    return e.strip().lower()

def create_jwt(data: dict, expires_in_minutes: int = 60):
    payload = data.copy()
    payload["exp"] = now_utc() + timedelta(minutes=expires_in_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def send_email(to_email: str, subject: str, body_html: str):
    msg = MIMEText(body_html, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

def delete_expired_tokens(db: Session, admin_id: Optional[int] = None):
    """
    Remove expired tokens from the DB. If admin_id is provided, limit removal to that admin.
    We perform a delete here to keep the AdminToken table compact.
    """
    q = db.query(AdminToken).filter(AdminToken.expiry <= now_utc())
    if admin_id:
        q = q.filter(AdminToken.admin_id == admin_id)
    q.delete(synchronize_session=False)
    db.commit()

def delete_used_tokens(db: Session, admin_id: int, token_type: str):
    db.query(AdminToken).filter(
        AdminToken.admin_id == admin_id,
        AdminToken.token_type == token_type,
        AdminToken.used == True
    ).delete(synchronize_session=False)
    db.commit()

def mark_other_tokens_used(db: Session, admin_id: int, token_type: str, keep_token_id: Optional[int]=None):
    """
    When a token is verified, mark other unused tokens of the same type for that admin as used.
    This prevents old links from being used later.
    """
    q = db.query(AdminToken).filter(
        AdminToken.admin_id == admin_id,
        AdminToken.token_type == token_type,
        AdminToken.used == False
    )
    if keep_token_id:
        q = q.filter(AdminToken.id != keep_token_id)
    q.update({"used": True}, synchronize_session=False)
    db.commit()

def store_token(db: Session, admin_id: int, token: str,token_type: str, minutes_valid: int = 60) -> AdminToken:
    """
    Store a token in AdminToken table and return the entry.
    We first mark any existing unused tokens of the same type as used.
    """
    db.query(AdminToken).filter(
        AdminToken.admin_id == admin_id,
        AdminToken.token_type == token_type,
        AdminToken.used == False
    ).update({"used": True}, synchronize_session=False)
    db.commit()

    new_token = AdminToken(
        admin_id=admin_id,
        token=token,
        token_type=token_type,
        expiry=now_utc() + timedelta(minutes=minutes_valid),
        used=False
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return new_token

# ---------- FastAPI App ----------

app = FastAPI()

# ---------- Signup Endpoint ----------

@app.get("/")
def test_connection():
    return {"message": "Success: Valid Connection to User Service"}

@app.post("/signup")
def signup(admin: AdminSignup):
    db: Session = SessionLocal()

    try:
        # sanitize/normalize inputs
        username = sanitize_username(admin.username)
        email = sanitize_email(admin.email)

        # check if username/email already exists
        existing_admin = db.query(Admin).filter((Admin.username == username) | (Admin.email == email)).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="Username or e-mail already exists")
        
        # hash password
        hashed_password = generate_password_hash(admin.password)

        # create new admin (inactive)
        new_admin = Admin(
            username=admin.username,
            email=admin.email,
            password=hashed_password,
            is_active=False,
            failed_login_count=0
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        # create verification token
        token = create_jwt({
            "admin_id": new_admin.id,
            "type": "verify_email"
        }, expires_in_minutes=60)

        # store token
        store_token(db, new_admin.id, token, token_type="verify_email", minutes_valid=60)

        # send verification email
        verify_link = f"http://localhost:8000/verify-email?token={token}"
        email_body = f'''
            <h3>Welcome {new_admin.username}!</h3>
            <p>Please verify your email by clicking the link below:</p>
            <a href="{verify_link}">Verify Email</a>
            <p>This link will expire in 1 hour.</p>
        '''
        try:
            send_email(new_admin.email, "Verify your account", email_body)
        except:
            raise HTTPException(status_code=400, detail="Email Failed")

        # successfull return
        return{"message": "Admin created! Please check your email to verify your account"}

    finally:
        # close db session
        db.close()


# ---------- Verify Email Endpoint ----------

@app.get("/verify-email")
def verify_email(token: str):
    db: Session = SessionLocal()
    try:
        # Decode token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            admin_id = payload.get("admin_id")
            token_type = payload.get("type")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token")
        
        if token_type != "verify_email":
            raise HTTPException(status_code=400, detail="Invalid token type")
        
        # Find token entry in DB (must be unused and not expired)
        token_entry = db.query(AdminToken).filter(
            AdminToken.token == token,
            AdminToken.used == False,
            AdminToken.expiry > now_utc()
        ).first()

        if not token_entry:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        # mark token as used + activate admin
        token_entry.used = True
        db.commit()

        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=400, detail="Admin not found")
        
        admin.is_active = True
        admin.failed_login_count = 0    # reset failed attempts on verification
        db.commit()

        # Mark other tokens of same type used (so other links no longer work)
        mark_other_tokens_used(db, admin_id=admin_id, token_type="verify_email", keep_token_id=token_entry.id)

        # Remove expired tokens for this admin
        delete_expired_tokens(db, admin_id=admin_id)

        # Delete used tokens
        delete_used_tokens(db, admin_id=admin_id, token_type="verify_email")

        return{"message": "Email verified! Your account is now active."}
    
    finally:
        db.close()


# ---------- Resend Verification ----------

@app.post("/resend-verification")
def resend_verification(req: ResendRequest):
    db: Session = SessionLocal()
    try:
        email = sanitize_email(req.email)
        admin = db.query(Admin).filter(Admin.email == email).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        if admin.is_active:
            return {"message": "Account already active. You can log in."}
        
        # Clean expired tokens and mark other unused tokens used
        delete_expired_tokens(db, admin_id=admin.id)

        # Create a new verification token and store it (this marks old unused tokens used)
        token = create_jwt({"admin_id": admin.id, "type": "verify_email"}, expires_in_minutes=60)
        store_token(db, admin.id, token, token_type="verify_email", minutes_valid=60)

        # Send email
        verify_link = f"http://localhost:8000/verify-email?token={token}"
        email_body = f'''
            <h3>{admin.username}!</h3>
            <p>Please verify your email by clicking the link below:</p>
            <a href="{verify_link}">Verify Email</a>
            <p>This link will expire in 1 hour.</p>
        '''
        send_email(admin.email, "Verify your account", email_body)

        return {"message": "Verification email sent. Please check your inbox."}
    finally:
        db.close()


# ---------- Login Endpoint ----------

@app.post("/login")
def login(req: LoginRequest):
    db: Session = SessionLocal()
    try:
        identifier = req.username_or_email.strip()
        password = req.password

        # Try to find admin by username or email
        admin = db.query(Admin).filter(
            (Admin.username == identifier) | (Admin.email == sanitize_email(identifier))
        ).first()

        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        
        # If account inactive, deny login
        if not admin.is_active:
            raise HTTPException(status_code=403, detail="Account inactive. Please verify your email or re-activate your account.")
        
        # Verify password
        if not check_password_hash(admin.password, password):
            # Increment failed login counter
            admin.failed_login_count = (admin.failed_login_count or 0) + 1
            db.commit()

            # If reached threshold -> deactivate account and send reactivation email
            if admin.failed_login_count >= 5:
                admin.is_active = False
                db.commit()

                # Create reactivation token and store
                token = create_jwt({"admin_id": admin.id, "type": "reactivate_account"}, expires_in_minutes=60)
                store_token(db, admin.id, token, token_type="reactivate_account", minutes_valid=60)

                # Send reactivation email
                reactivate_link = f"http://localhost:8000/reactivate-account?token={token}"
                email_body = f'''
                    <h3>Hello {admin.username}</h3>
                    <p>Your account has been temporarily locked after multiple failed login attempts.</p>
                    <p>Click the link below if you want to reactivate your account:</p>
                    <p><a href="{reactivate_link}">Reactivate Account</a></p>
                    <p>This link will expire in 1 hour.</p>
                '''
                send_email(admin.email, "Reactivate your account", email_body)

            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Successful login: reset failed login count
        admin.failed_login_count = 0
        db.commit()

        # create a login token (24 hours)
        login_token = create_jwt({"admin_id": admin.id, "type": "login"}, expires_in_minutes=60 * 24)
        store_token(db, admin.id, login_token, token_type="login", minutes_valid=60 * 24)
        return {"message": "Login successful", "token": login_token, "userId": admin.id, "username": admin.username}
    
    #Send token to db
    
    finally:
        db.close()


# ---------- Reactivate-account Endpoint ----------

@app.get("/reactivate-account")
def reactivate_account(token: str):
    db: Session = SessionLocal()
    try:
        # Decode token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            admin_id = payload.get("admin_id")
            token_type = payload.get("type")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token")

        if token_type != "reactivate_account":
            raise HTTPException(status_code=400, detail="Invalid token type")
        
        # Validate token in DB
        token_entry = db.query(AdminToken).filter(
            AdminToken.token == token,
            AdminToken.used == False,
            AdminToken.expiry > now_utc()
        ).first()

        if not token_entry:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        # Mark token used and reactivate account
        token_entry.used = True
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")

        admin.is_active = True
        admin.failed_login_count = 0
        db.commit()

        # Mark other reactivation tokens used
        mark_other_tokens_used(db, admin_id=admin_id, token_type="reactivate_account", keep_token_id=token_entry.id)

        # Delete expired tokens
        delete_expired_tokens(db)

        # Delete used tokens
        delete_used_tokens(db, admin_id=admin_id, token_type="reactivate_account")

        return {"message": "Account reactivated! You can now log in."}
    
    finally:
        db.close()

# ---------- Forgot Password Endpoint ----------

@app.post("/forgot-password")
def forgot_password(req: ResendRequest):
    db: Session = SessionLocal()
    try:
        email = sanitize_email(req.email)
        admin = db.query(Admin).filter(Admin.email == email).first()
        
        # Don't reveal if user exists (to prevent enumeration)
        if not admin:
            return {"message": "A reset link has been sent. Check your inbox!"}

        # Create token and store
        token = create_jwt({"admin_id": admin.id, "type": "reset_password"}, expires_in_minutes=30)
        store_token(db, admin.id, token, token_type="reset_password", minutes_valid=30)

        reset_link = f"myapp://reset/reset-password?token={token}"
        email_body = f"""
            <h3>Reset your password</h3>
            <p>Click below to reset your password:</p>
            <a href="{reset_link}">Reset Password</a>
            <p>This link expires in 30 minutes.</p>
        """
        send_email(admin.email, "Password Reset Request", email_body)
        return {"message": "A reset link has been sent. Check your inbox!"}
    finally:
        db.close()

# ---------- Reset Password Endpoint ----------

@app.post("/reset-password")
def reset_password(req: ResetPasswordRequest):
    db: Session = SessionLocal()
    try:
        # Decode token
        try:
            payload = jwt.decode(req.token, SECRET_KEY, algorithms=["HS256"])
            admin_id = payload.get("admin_id")
            token_type = payload.get("type")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token")

        if token_type != "reset_password":
            raise HTTPException(status_code=400, detail="Invalid token type")

        # Verify token record in DB
        token_entry = db.query(AdminToken).filter(
            AdminToken.token == req.token,
            AdminToken.used == False,
            AdminToken.expiry > now_utc()
        ).first()
        if not token_entry:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        # Update password
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")

        admin.password = generate_password_hash(req.new_password)
        admin.failed_login_count = 0
        admin.is_active = True
        token_entry.used = True
        db.commit()

        # Mark other tokens as used
        mark_other_tokens_used(db, admin_id, "reset_password", token_entry.id)
        delete_expired_tokens(db, admin_id)
        return {"message": "Password reset successfully"}
    finally:
        db.close()


# ---------- Update Account Endpoint ----------

@app.put("/update")
def update_admin(data: AdminUpdate, current_admin = Depends(get_current_admin)):
    db: Session = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.id == current_admin.id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        #Update fields if provided
        if data.username:
            admin.username = sanitize_username(data.username)

        if data.email:
            admin.email = sanitize_email(data.email)

        if data.password:
            admin.password = generate_password_hash(data.password)

        db.commit()
        return {"message": "Account updated successfully",
                "updated_data": {
                    "username": admin.username,
                    "email": admin.email
                }
            }
    
    finally:
        db.close()

# ---------- Delete Account Endpoint ----------

@app.delete("/delete")
def delete_admin(current_admin = Depends(get_current_admin)):
    db: Session = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.id == current_admin.id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        #Delete tokens tied to admin account
        db.query(AdminToken).filter(AdminToken.admin_id == admin.id).delete()

        #Delete admin account
        db.delete(admin)
        db.commit()

        return {"message": "Account deleted successfully"}
    finally:
        db.close()

# ---------- Get Account Details Endpoint ----------
@app.get("/account_details")
def get_current_admin_data(current_admin = Depends(get_current_admin)):
    return {
        "username": current_admin.username,
        "email": current_admin.email
    }
