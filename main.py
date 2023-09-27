from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy_utils import create_database, database_exists


from schemas import UtilisateurBase, UtilisateurCredentials, UtilisateurResponse, UtilisateurCreate, CompteResponse, PersonneResponse, OperationResponse, OperationCreate, CompteUpdate, TokenRequest, Token, PartenaireResponse, Partenaire, TokenData
from models import Utilisateur, Base, Personne, Typecompte, Compte, Partenaire, Operation
from crud import create_user, get_user, get_user_by_login, get_user_by_organisation, get_users, get_comptes, get_titulaires_of_compte, get_titulaires_of_compte_by_comptenum, get_operations, get_operation_by_reference, create_operation, get_compteid_by_comptenum, put_ops_update_compte, get_ops_update_compte, get_partenaire_by_code_and_key, get_partenaire_by_nom
from database import get_db
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials, SecurityScopes
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Annotated

#import jwt as jwt2
#from jwt.exceptions import InvalidSignatureError
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from passlib.handlers.django import django_pbkdf2_sha256

import requests

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Create the HTTPBearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT Configuration
SECRET_KEY = "293b903eabe14ad9938c1bc0464bb0ab0e6cd92bdbd05afc66cfc9f8264b0e75" # replace with your own secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#this is just tho hide the following code
    #DATABASE_URL = "postgresql://postgres:root@192.168.88.213:5432/fafana"
    # Create SessionLocal class with sessionmaker
    #SQLAlchemy Models moved to a separate file
    # Create the database if it doesn't exist
    # Create the tables in the database using Alembic
    #Base.metadata.create_all(engine)
    # Create tables
    # Define Pydantic schema for response

#SFastAPI App and Routes
app = FastAPI(title="TD API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[" * "],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get a database session
#GETTERS
'''from requests.auth import AuthBase

class PartenaireAuth(AuthBase):
    def __init__(self, partenaire: Partenaire):
        self.partenaire = partenaire

    def __call__(self, r):
        r.headers['part_code'] = self.partenaire.part_code
        r.headers['part_key'] = self.partenaire.part_key
        return r

async def partenaire_auth(partenaire: Partenaire = Depends(get_partenaire_by_code_and_key),) -> PartenaireAuth:
    return PartenaireAuth(partenaire)

http_auth = HTTPBearer()'''

def verify_password(plain_password, hashed_password):
    #return pwd_context.verify(plain_password, hashed_password)
    return django_pbkdf2_sha256.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    #user = fake_users_db.get(credentials.utl_login)
    user = get_user_by_login(db, username)
    if not user:
        return False
    if not verify_password(password, user.utl_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(tok):
    decoded_token = ""
    try:
        decoded_token = jwt.decode(str(tok), SECRET_KEY, algorithms=[ALGORITHM])
        #print(decoded_token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    return decoded_token      

def check_user_role_by_id(db: Session = Depends(get_db), user_id:str = None):
    user = get_user(db, user_id)
    if user.utl_organisation not in ["DTP"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
        return False
    return True

# Routes

@app.get("/greet/{name}", response_model=dict)
async def greet_user(name: str):
    return {"message": f"Hello, {name}! It's working."}

'''@app.post("/token", response_model=Token)
async def generate_token(form_data: TokenRequest, db: Session = Depends(get_db)):
    partenaire = get_partenaire_by_code_and_key(db, form_data.part_code, form_data.part_key)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"sub": partenaire.id}, 
        access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "expiry_in_minutes": ACCESS_TOKEN_EXPIRE_MINUTES}

@app.get("/test", response_model=list)
async def tester(db: Session = Depends(get_db), token: str= Depends(http_auth)):
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        decoded_token = decode_token(token)
        return [decoded_token]'''

# Route to receive user credentials and return an access token
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
        
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try: 
        partenaire = get_partenaire_by_nom(db, form_data.username)
    except Exception as e:
        # Handle any exceptions that may occur during the query
        print(f"An error occurred: {e}")
        partenaire = None    
    if partenaire:
        partenaire_id = partenaire.id
    else:
        partenaire_id = 0
        # Handle the case where the partenaire is not found

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"sub": str(user.id), "partenaire": partenaire_id}, 
        access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "expiry_in_minutes": ACCESS_TOKEN_EXPIRE_MINUTES}

@app.get("/users/{user_id}", response_model=UtilisateurResponse, dependencies = [Depends(check_user_role_by_id)], include_in_schema=False)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    return get_user(db, user_id)

@app.get("/users/login/{user_login}", response_model=UtilisateurResponse, include_in_schema=False)
async def read_user(user_login: str, db: Session = Depends(get_db)):
    return get_user_by_login(db, user_login)

@app.get("/users", response_model=list[UtilisateurResponse], include_in_schema=False)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)

@app.post("/users", response_model=UtilisateurCreate, include_in_schema=False)
def write_user(user:UtilisateurCreate, db: Session = Depends(get_db)):  
    #db_user = Utilisateur(name=user.name, email=user.email, password=user.password)
    #db.add(db_user)
    #db.commit()
    #db.refresh(db_user)
    return create_user(db, user=user)

@app.get("/comptesdev", response_model=list[CompteResponse], include_in_schema=False)
def read_compte(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):  
    return get_comptes(db, skip=skip, limit=limit)

@app.get("/comptes", response_model=list[CompteResponse], include_in_schema=True)
def read_compte(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str= Depends(oauth2_scheme)):  
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        decoded_token = decode_token(token)
        print (f'partenaire: {decoded_token["partenaire"]}')
        return get_comptes(db, skip=skip, limit=limit)

@app.get("/comptetitulaire/{compte_id}", response_model=list[PersonneResponse], include_in_schema=False)
def read_comptetit(compte_id:int, db: Session = Depends(get_db)):
    titulaires= get_titulaires_of_compte(db, compte_id)
    return titulaires

#accept query param
@app.get("/comptetitulaire/num/", response_model=list[PersonneResponse], include_in_schema=False)
#def read_comptetit(compte_num:str=None, db: Session = Depends(get_db), token: str= Depends(http_auth)):
def read_comptetit(compte_num:str=None, db: Session = Depends(get_db), token: str= Depends(oauth2_scheme)):
    titulaires= get_titulaires_of_compte_by_comptenum(db, compte_num)
    all_titulaires = []
    for titulaire in titulaires:
        response = {
            "compte_num": compte_num,
            "pers_nom": titulaire.pers_nom,
            "pers_prenom": titulaire.pers_prenom,
            "pers_date_nais": titulaire.pers_date_nais,
            "pers_lieu_nais": titulaire.pers_lieu_nais,
            "pers_nationalite": titulaire.pers_nationalite,
            "pers_profession": titulaire.pers_profession,
            "pers_pays": titulaire.pers_pays,
            "pers_adr_actuelle": titulaire.pers_adr_actuelle,
            "pers_adr_mg": titulaire.pers_adr_mg,
            "pers_home_tel": titulaire.pers_home_tel,
            "pers_mob_tel": titulaire.pers_mob_tel,
            "pers_email": titulaire.pers_email,
            "pers_sexe": titulaire.pers_sexe,
            "pers_sit_fam": titulaire.pers_sit_fam,
            "pers_type": titulaire.pers_type
        }
        all_titulaires.append(response)
    return all_titulaires

@app.get("/comptetitulaire/num/{compte_num}", response_model=list[PersonneResponse], include_in_schema=False)
def read_comptetit(compte_num:str=None, db: Session = Depends(get_db)):
    titulaires= get_titulaires_of_compte_by_comptenum(db, compte_num)
    #titulaires = [titulaire for compte in comptes for titulaire in compte.titulaires]
    #print(titulaires)
    return titulaires

@app.post("/comptetitulaire", response_model=list[PersonneResponse], include_in_schema=False)
def read_comptetit(compte_id:int, db: Session = Depends(get_db)):
    titulaires= get_titulaires_of_compte(db, compte_id)
    return titulaires

@app.post("/comptetitulaire/num", response_model=list[PersonneResponse])
def read_comptetit(compte_num:str, db: Session = Depends(get_db), token: str= Depends(oauth2_scheme)):
    titulaires= get_titulaires_of_compte_by_comptenum(db, compte_num)
    return titulaires

@app.get("/compte/{compte_num}", response_model=CompteResponse, include_in_schema=False)
def read_comptetit(compte_num:str=None, db: Session = Depends(get_db)):
    compte= get_compteid_by_comptenum(db, compte_num)
    return compte

@app.get("/ops", response_model=list)
def read_operations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str= Depends(oauth2_scheme)):
    operations= get_operations(db, skip=skip, limit=limit)
    all_operations = []
    for operation in operations:
        response = {
            "id": operation.id,
            "op_date": operation.op_date,
            "op_montant": operation.op_montant,
            "op_reference": operation.op_reference,
            "op_partenaire": operation.partenaire_id,
            "cpte_type": operation.compte.typecompte_id,
            "cpte_num": operation.compte.cpte_num,
            "cpte_id": operation.compte_id
        }
        all_operations.append(response)
    #return all_operations

    #decoded_token = decode_token(token)
    #print (decoded_token["partenaire"]) 
    return operations

@app.get("/ops/{op_ref}", response_model=list, include_in_schema=True)
def read_operation(op_ref:str=None, db: Session = Depends(get_db), token: str= Depends(oauth2_scheme)):
    operations= get_operation_by_reference(db, op_ref)
    all_operations = []
    for operation in operations:
        response = {
            "op_reference": operation.op_reference,
            "op_date": operation.op_date,
            "op_montant": operation.op_montant,
            "cpte_num": operation.compte.cpte_num,
            "op_etat": operation.op_etat,
        }
        all_operations.append(response)
    return all_operations
    #return operations

@app.post("/makedeposite", response_model=OperationCreate)
def write_ops_update_compte(operation:OperationCreate, db: Session = Depends(get_db), token: str= Depends(oauth2_scheme)): 
    decoded_token = decode_token(token)
    #print (decoded_token["partenaire"]) 
    #return put_ops_update_compte(db, operation=operation)#this add operation and update compte
    return create_operation(db, operation=operation, partenaire_id=int(decoded_token["partenaire"]))