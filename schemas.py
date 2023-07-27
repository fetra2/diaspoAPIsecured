from pydantic import BaseModel
from datetime import datetime,date

class UtilisateurBase(BaseModel):
    utl_nom: str
    utl_login: str

class UtilisateurCredentials(BaseModel):
    utl_login: str
    utl_password: str

class UtilisateurResponse(BaseModel):
    id: int
    utl_nom: str
    utl_login: str
    class Config:
        orm_mode = True


class UtilisateurCreate(UtilisateurBase):
    utl_nom: str
    utl_login: str
    utl_password: str
    class Config:
        orm_mode = True

'''    pers_lieu_nais: str
    pers_nationalite: str
    pers_profession: str
    pers_pays: str
    pers_adr_actuelle: str
    pers_adr_mg: str
    pers_home_tel: str
    pers_mob_tel: str
    pers_email: str
    pers_sexe: str
    pers_sit_fam: str'''
class PersonneBase(BaseModel):
    pers_nom: str
    pers_prenom: str
    class Config:
        orm_mode = True

class PersonneResponse(PersonneBase):
    pers_nom: str
    pers_prenom: str
    pers_date_nais: date
    pers_lieu_nais: str
    pers_nationalite: str
    pers_profession: str
    pers_pays: str
    pers_adr_actuelle: str
    pers_adr_mg: str
    pers_home_tel: str
    pers_mob_tel: str
    pers_email: str
    pers_sexe: str
    pers_sit_fam: str
    class Config:
        orm_mode = True

class TypecompteResponse(BaseModel):
    id: int
    tc_nom: str
    tc_description: str 
    tc_taux: str
    class Config:
        orm_mode = True

class CompteResponse(BaseModel):
    id: int
    cpte_num: str
    typecompte:  TypecompteResponse=None
    cpte_solde: float=None
    class Config:
        orm_mode = True

class CompteBase(BaseModel):
    id: int
    cpte_num: str
    typecompte: TypecompteResponse=None
    class Config:
        orm_mode = True


class OperationBase(BaseModel):
    op_montant: float
    op_reference: str
    class Config:
        orm_mode = True
   
class OperationResponse(BaseModel):
    id: int
    op_montant: float
    op_reference: str
    compte: CompteResponse=None
    partenaire_id: int 
    class Config:
        orm_mode = True

class OperationCreate(OperationBase):
    compte_num: str
    partenaire_id: int
    op_montant: float
    op_reference:str
    class Config:
        orm_mode = True
   

class CompteUpdate(BaseModel):
    cpte_solde: float

class TokenRequest(BaseModel):
    part_code: str
    part_key: str

class TokenData(BaseModel):
    username: str | None = None
    password: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expiry_in_minutes: str

class Partenaire(BaseModel):
    part_code: str
    part_key: str
    
class PartenaireResponse(BaseModel):
    part_nom: str