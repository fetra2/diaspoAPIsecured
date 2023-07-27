from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, MetaData, Table
from sqlalchemy.types import Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import Base

class Utilisateur(Base):
    __tablename__ = "Utilisateur"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    utl_nom = Column(String)
    utl_login = Column(String, unique=True)
    utl_password = Column(String)
    utl_organisation = Column(String)

Compte_personne=Table('Compte_personne', Base.metadata, 
    Column('compte_id', Integer, ForeignKey('Compte.id')),
    Column('personne_id', Integer, ForeignKey('Personne.id'))
)

class Personne(Base):
    __tablename__ = "Personne"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pers_nom = Column(String(length=255), nullable=True)
    pers_prenom = Column(String(length=255), nullable=True)
    pers_date_nais = Column(DateTime, nullable=True)
    pers_lieu_nais = Column(String(length=255), nullable=True)
    pers_nationalite = Column(String(length=255), nullable=True)
    pers_profession = Column(String(length=255), nullable=True)
    pers_pays = Column(String(length=255), nullable=True)
    pers_adr_actuelle = Column(String(length=255), nullable=True)
    pers_adr_mg = Column(String(length=255), nullable=True)
    pers_home_tel = Column(String(length=255), nullable=True)
    pers_mob_tel = Column(String(length=255), nullable=True)
    pers_email = Column(String(length=255), nullable=True)
    pers_sexe = Column(String(length=255), nullable=True)
    pers_sit_fam = Column(String(length=255), nullable=True)
    pers_type = Column(String(length=255), nullable=True)
    pers_date = Column(Date, nullable=True)

    comptes = relationship("Compte", secondary="Compte_personne", back_populates="titulaires")
    validation_personne = relationship("Validation", back_populates="personne") 

    def __str__(self):
        return self.pers_nom

class Typecompte(Base):
    __tablename__ = "Typecompte"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tc_nom = Column(String(20), nullable=True)
    tc_description = Column(String(45), nullable=True)
    tc_taux = Column(Numeric(precision=3, scale=2)) 

    compte = relationship("Compte", back_populates="typecompte")

    def __str__(self):
        return self.tc_nom

class Validation(Base):
    __tablename__ = "Validation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    val_typecompte = Column(String(20))
    val_reference = Column(DateTime, nullable=True)
    val_actionprise = Column(String(20))
    val_date = Column(DateTime, nullable=True)
    val_notes = Column(String(20), nullable=True)
    val_statut = Column(String(20), nullable=True)
    personne_id = Column(Integer, ForeignKey("Personne.id"))
    #piece_id = Column(Integer, ForeignKey("Piece.id"))

    personne = relationship("Personne", back_populates="validation_personne")
    #piece = relationship("Piece", back_populates="validation_piece")
    def __str__(self):
        return self.cpte_num


class Compte(Base):
    __tablename__ = "Compte"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cpte_num = Column(String(20))
    cpte_date_ouverture = Column(DateTime, nullable=True)
    cpte_date_cloture = Column(DateTime, nullable=True)
    cpte_ref_cloture = Column(String(20), nullable=True)
    cpte_solde = Column(Float, nullable=True)
    typecompte_id = Column(Integer, ForeignKey("Typecompte.id"))
    #validation_id = Column(Integer, ForeignKey("Validation.id"))

    titulaires = relationship("Personne", secondary="Compte_personne", back_populates="comptes")
    operation = relationship("Operation", back_populates="compte")
    typecompte = relationship("Typecompte", back_populates="compte")
    #validation = relationship('Validation', back_populates='compte')#no need migration #make Compte accessible on Operation
    def __str__(self):
        return self.cpte_num


class Partenaire(Base):
    __tablename__ = "Partenaire"

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_nom = Column(String(length=45), nullable=True)
    part_ref = Column(String(length=45), nullable=True)
    part_code = Column(String(length=128), nullable=True)
    part_key = Column(String(length=128), nullable=True)

    def __str__(self):
        return self.part_nom
    class Meta:
        db_table = 'Partenaire'
    def set_part_code(self):
        random_number = random.randint(1, 999999)
        six_digit_number = str(random_number).zfill(6)
        self.part_code = six_digit_number
    def set_part_key(self):
        self.part_key = get_random_secret_key() 

class Operation(Base):
    __tablename__ = "Operation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    op_date = Column(DateTime, nullable=True)
    op_montant = Column(Float, nullable=True)
    op_reference = Column(String(length=45), nullable=True)
    op_type = Column(String(length=45), nullable=True)
    op_etat = Column(String(length=45), nullable=True)
    op_quinze = Column(Integer, nullable=True)
    op_interet = Column(Float, nullable=True)
    op_annee = Column(Integer, nullable=True)

    compte_id = Column(Integer, ForeignKey("Compte.id"))
    partenaire_id = Column(Integer, ForeignKey("Partenaire.id"))

    compte = relationship("Compte", back_populates="operation")
    def __str__(self):
        return self.id