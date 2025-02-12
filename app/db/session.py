from google.cloud.sql.connector import Connector,IPTypes
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy import create_engine,MetaData
from config.settings import Settings
import sqlalchemy 
import pg8000



SQLALCHEMY_DATABASE_URL = Settings.SQLALCHEMY_DATABASE_URL
INSTANCE_CONNECTION_NAME = Settings.INSTANCE_CONNECTION_NAME



if INSTANCE_CONNECTION_NAME is not None:
    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=Settings.POSTGRES_USER,
            password=Settings.POSTGRES_PASSWORD,
            db=Settings.POSTGRES_DB,
            ip_type=IPTypes.PUBLIC,
        )
        return conn
    
    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
APIBase = declarative_base(metadata=MetaData(schema=None))

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
APIBase.query = session.query_property()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

    def __init__(self) -> None:
        self.connection_is_active = False
        self.engine = None

    def get_db_connection(self):
        if self.connection_is_active is False:

            try: 
                
                if INSTANCE_CONNECTION_NAME is not None:
                    connector = Connector()

                    def getconn() -> pg8000.dbapi.Connection:
                        conn: pg8000.dbapi.Connection = connector.connect(
                            INSTANCE_CONNECTION_NAME,
                            "pg8000",
                            user=Settings.POSTGRES_USER,
                            password=Settings.POSTGRES_PASSWORD,
                            db=Settings.POSTGRES_DB,
                            ip_type=IPTypes.PUBLIC,
                        )
                        return conn
                    
                    self.engine = sqlalchemy.create_engine(
                        "postgresql+pg8000://",
                        creator=getconn,
                    )
                else:
                    self.engine = create_engine(SQLALCHEMY_DATABASE_URL)
                
                return self.engine
            except Exception as ex:
                print("Error connecting to DB : ", ex)
        return self.engine

    def get_db_session(self,engine):
        try:
            Session = sessionmaker(bind=engine)
            session = Session()
            return session
        except Exception as ex:
            print("Error getting DB session : ", ex)
            return None