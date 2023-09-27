from sqlalchemy.orm import Session

from models import Utilisateur, Base, Personne, Typecompte, Compte, Partenaire, Operation
from schemas import UtilisateurCreate, OperationCreate, CompteUpdate, CompteResponse

import logging
from fastapi import HTTPException
import datetime
from sqlalchemy import func

#to know which route has been called
logging.basicConfig(level=logging.INFO)

def get_user(db: Session, user_id: int):
    logging.info(f"Received request to get user by ID: {user_id}")
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur not found")
    return user

def get_user_by_login(db: Session, login: str):
    logging.info(f"Received request to get user by username: {login}")
    user = db.query(Utilisateur).filter(Utilisateur.utl_login == login).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur not found")
    return user    

def get_user_by_organisation(db: Session, organisation: str):
    logging.info(f"Received request to get user by organisation: {organisation}")
    user = db.query(Utilisateur).filter(Utilisateur.utl_organisation == organisation).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur not found")
    return user    


def get_users(db: Session, skip: int = 0, limit: int = 100):
    user = db.query(Utilisateur).offset(skip).limit(limit).all()
    #user = db.query(Utilisateur).all()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur not found")    
    return user

def create_user(db: Session, user:UtilisateurCreate):
    existing_user = db.query(Utilisateur).filter(Utilisateur.utl_login == user.utl_login).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Login already registered") 
    db_user = Utilisateur(utl_nom=user.utl_nom, utl_login=user.utl_login, utl_password=user.utl_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_comptes(db: Session, skip: int = 0, limit: int = 100):
    comptes = db.query(Compte).offset(skip).limit(limit).all()
    #user = db.query(Utilisateur).all()
    if not comptes:
        raise HTTPException(status_code=404, detail="Comptes not found")    
    return comptes

def get_titulaires_of_compte(db: Session, compte_id:int):
    compte_id = compte_id
    #compte = db.query(Compte).offset(skip).limit(limit).all()
    titulaires = db.query(Personne).join(Personne.comptes).filter(Compte.id==compte_id).all()
    #titulaire = titulaires[0]
    #comptes = titulaire.comptes
    if not titulaires:
        raise HTTPException(status_code=404, detail="Personne not found")    
    return titulaires

def get_titulaires_of_compte_by_comptenum(db: Session, compte_num:str):
    compte_num = compte_num
    #compte = db.query(Compte).offset(skip).limit(limit).all()
    titulaires = db.query(Personne).join(Personne.comptes).filter(Compte.cpte_num==compte_num).all()
    #titulaire = titulaires[0]
    #comptes = titulaire.comptes
    if not titulaires:
        raise HTTPException(status_code=404, detail="Personne not found")    
    return titulaires

def get_compteid_by_comptenum(db: Session, compte_num:str):
    compte_num = compte_num
    compte = db.query(Compte).filter(Compte.cpte_num==compte_num).first()
    if not compte:
        raise HTTPException(status_code=404, detail="Personne not found")    
    return compte

def get_operations(db: Session, skip: int = 0, limit: int = 100):
    operations = db.query(Operation).join(Compte).offset(skip).limit(limit).all()
    if not operations:
        raise HTTPException(status_code=404, detail="Operation not found")    
    return operations

def get_operation_by_reference(db: Session, op_ref: str):
    operations = db.query(Operation).join(Compte).filter(Operation.op_reference==op_ref).all()
    if not operations:
        raise HTTPException(status_code=404, detail="Operation not found")    
    return operations

def create_operation(db: Session, operation:OperationCreate, partenaire_id: int):
    existing_ops = db.query(Operation).filter(Operation.op_reference == operation.op_reference).first()
    if existing_ops:
        raise HTTPException(status_code=400, detail="reference already registered") 
    
    try:
        compte_to_update = db.query(Compte).filter(Compte.cpte_num == operation.compte_num).first()
    except:
         raise HTTPException(status_code=400, detail="Compte not found")
    if compte_to_update is not None:
        #partenaire_id=operation.partenaire_id,
        
        db_ops = Operation(
            compte_id=compte_to_update.id,
            op_montant=operation.op_montant,
            op_reference=operation.op_reference,
            partenaire_id=partenaire_id,
            op_type="versement",
            op_etat="verse",
            op_date=datetime.datetime.now(),
            op_annee=datetime.datetime.now().year,
        )
        try:
            db.add(db_ops)
            db.commit()
        except:
            raise HTTPException(status_code=400, detail="Cannot make this operation")
    else:
        raise HTTPException(status_code=400, detail="Compte not found") 

    db.refresh(db_ops)
    #return db_ops
    return { 
        "partenaire_id": db_ops.partenaire_id,
        "op_montant": db_ops.op_montant,
        "op_reference":db_ops.op_reference,
        "op_etat":db_ops.op_etat,
        "compte_num": operation.compte_num
        }

def put_ops_update_compte(db: Session, operation:OperationCreate):
    #check that Operation.op_reference does not exist yet
    existing_ops = db.query(Operation).filter(Operation.op_reference == operation.op_reference).first()
    if existing_ops:
        raise HTTPException(status_code=400, detail="reference already registered") 

    compte_to_update = db.query(Compte).filter(Compte.cpte_num == operation.compte_num).first()
    
    if compte_to_update is not None:
        #operation.op_etat= "verse"#add operartion etat to verse
        db_ops = Operation(
            compte_id=compte_to_update.id,
            op_montant=operation.op_montant,
            op_reference=operation.op_reference,
            partenaire_id=operation.partenaire_id,
            op_etat="verse",
            op_quinze=6,
            op_interet=0.4,
            op_annee=datetime.datetime.now().year
        )
        db.add(db_ops)

        new_solde = 0
        logging.info(f"Compte solde: {compte_to_update.cpte_solde}")
        if compte_to_update.cpte_solde is not None:
            new_solde = compte_to_update.cpte_solde + operation.op_montant
        else:
            new_solde = new_solde + operation.op_montant 

        compte_to_update.cpte_solde = new_solde
        db.add(compte_to_update)
        db.commit()
    else:
        raise HTTPException(status_code=400, detail="Compte not found") 

    db.refresh(db_ops)
    return { 
        "partenaire_id": db_ops.partenaire_id,
        "op_montant": db_ops.op_montant,
        "op_reference":db_ops.op_reference,
        "op_etat":db_ops.op_etat,
        "compte_num": operation.compte_num
        }


def get_ops_update_compte(db: Session, operation:CompteResponse):
    compte_to_update = db.query(Compte).filter(Compte.id == operation.compte_id).first()
    if compte_to_update is None:
        raise HTTPException(status_code=400, detail="Compte not found") 
    else:
       logging.info(f"Received request to get compte by ID: {compte_to_update.cpte_solde}")
    return compte_to_update

def get_partenaire(db: Session, partenaire_id: int):
    partenaire = db.query(Partenaire).filter_by(id=partenaire_id).first()
    if partenaire is None:
        raise HTTPException(status_code=400, detail="Partenaire not found") 
    else:
        logging.info(f"Received request to get partenaire by ID: {partenaire_id}")
        return partenaire

def get_partenaire_by_code_and_key(db: Session, part_code: str, part_key: str):
    partenaire = db.query(Partenaire).filter_by(part_code=part_code, part_key=part_key).first()
    if not partenaire:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return partenaire

def get_partenaire_by_nom(db: Session, part_nom: str):
    #make filter to be case insensitive
    partenaire = db.query(Partenaire).filter(func.lower(Partenaire.part_nom) == part_nom.lower()).first()
    if not partenaire:
        raise HTTPException(status_code=401, detail="Invalid partenaire name")
    return partenaire