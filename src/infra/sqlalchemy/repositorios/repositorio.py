from src.infra.sqlalchemy.models import models
from sqlalchemy.orm import Session



class RepositorioBases():
    def __init__(self, db:Session):
        self.db = db
        
    def criar(self, nome_escolhido, chaves_csv, user_id):
        db_base = models.Bases(name = nome_escolhido,
                                chaves = chaves_csv,
                                user_id = user_id
                                )
        self.db.add(db_base)
        self.db.commit()
        self.db.refresh(db_base)
        return db_base
    



#________________________________________________________________________________________________

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

DATABASE_URL = "mysql+mysqlconnector://crm_impulse_user:dBVd(PlP]Z)3@crm-impulse.c7a0kiga29ky.us-east-2.rds.amazonaws.com/crm-impulse"

engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)

SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


#______________________________________________________________________________________________________
class RepositorioInfos():
    def __init__(self, db:Session):
        self.db = db


    @staticmethod
    def get_new_session():
        """Método para criar uma nova sessão isolada."""
        return SessionLocal1()

    def criar1(self, base_id, list_data):
        db_infos = [models.Infos(infos=data, bases_id=base_id) for data in list_data]
        self.db.bulk_save_objects(db_infos)
        self.db.commit()
        return db_infos
    

    def criar_com_session_privada(self, base_id, list_data):
        with self.get_new_session() as session:
            db_infos = [models.Infos(infos=data, bases_id=base_id) for data in list_data]
            session.bulk_save_objects(db_infos)
            session.commit()

