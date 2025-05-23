from src.infra.sqlalchemy.models import models
from sqlalchemy.orm import Session
from sqlalchemy import func



class RepositorioBases():
    def __init__(self, db:Session):
        self.db = db
        
    def criar(self, nome_escolhido, chaves_csv, user_id):
        db_base = models.Bases(name = nome_escolhido,
                                chaves = chaves_csv,
                                user_id = user_id,
                                carregada = False,
                                n_clientes = 0
                                )
        self.db.add(db_base)
        self.db.commit()
        self.db.refresh(db_base)
        return db_base
    

    def carregar(self, id):
        db_base = self.db.query(models.Bases).filter(models.Bases.id == id).first()     
        db_base.carregada = True
        self.db.commit()
        self.db.refresh(db_base)
        return db_base

#________________________________________________________________________________________________

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

database_url = "postgresql://postgres:sb-postgres@sendblack.cc5ig0oq6pc6.us-east-1.rds.amazonaws.com/postgres"

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=20,        # Tamanho do pool de conexões
    max_overflow=20,     # Número máximo de conexões adicionais
    pool_recycle=3600,   # Reciclar conexões após 3600 segundos (1 hora)
    pool_timeout=30      # Tempo máximo de espera para uma conexão do pool (30 segundos)
)


SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

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


class RepositorioCampaign():
    def __init__(self, db:Session):
        self.db = db


    def atualizar_disparos(self, base_id):
        lista_campanhas = self.db.query(models.Campaign).filter(models.Campaign.base_id == base_id).all()
        qtd_infos = self.db.query(func.count(models.Infos.id)).filter(models.Infos.bases_id == base_id).scalar()

        db_base = self.db.query(models.Bases).filter(models.Bases.id == base_id).first()  
        print(db_base)  
        db_base.n_clientes = qtd_infos
        print(db_base)
        self.db.commit()
        self.db.refresh(db_base)
        for campanha in lista_campanhas:
            campanha.disparos_ate = qtd_infos
            self.db.commit()
            self.db.refresh(campanha)
            return campanha