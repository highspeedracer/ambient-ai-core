from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Create the Database Engine (This creates a file called ambient.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./ambient.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Define the Patient Table
class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    emergency_contact_name = Column(String)
    emergency_contact_phone = Column(String)

# 3. Define the Health Metrics Table
class HealthMetric(Base):
    __tablename__ = "health_metrics"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"))
    date = Column(String, index=True)
    steps = Column(Integer)
    avg_heart_rate = Column(Integer)
    sleep_hours = Column(Float)
    bathroom_visits = Column(Integer)

# 4. Command to build the tables
def init_db():
    print("Building Enterprise Database Schema...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database built successfully: 'ambient.db'")

if __name__ == "__main__":
    init_db()