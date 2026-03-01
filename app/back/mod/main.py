# Iniciar app -> venv\Scripts\activate
# uvicorn main:app --reload

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

##-------------------------------------------------------------------
##-- Imports img
import os
import shutil
from fastapi import File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean
from pydantic import BaseModel
from typing import List

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y SEGURIDAD
# ==========================================
SECRET_KEY = "abremesoyyo" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# ==========================================
# 2. CONFIGURACIÓN DE BASE DE DATOS (SQLite)
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./app_ia.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Base de Datos (SQLAlchemy)
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

##------------------------------------------
## Modelo para guardar imagenes
class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    image_path = Column(String)
    nombre = Column(String)
    limpio = Column(Boolean, default=True)

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 3. ESQUEMAS DE PYDANTIC (Validación de datos)
# ==========================================
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ==========================================
# 4. FUNCIONES AUXILIARES (Auth & JWT)
# ==========================================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependencia para proteger rutas: verifica el token y devuelve el usuario
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# ==========================================
# 5. APLICACIÓN FASTAPI Y RUTAS
# ==========================================
app = FastAPI(title="API Backend IA y BigData")

##------------------------------------------------------
## Carpetas para imagenes
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configurar CORS (Para que Angular pueda acceder)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Comprobar si el usuario existe
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    # Hashear y guardar
    hashed_pw = get_password_hash(user.password)
    new_user = UserDB(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario creado exitosamente"}

@app.post("/api/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Buscar usuario
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token JWT si todo es correcto
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# 6. RUTA PROTEGIDA (Tus Modelos de IA) Ejemplo
# ==========================================
@app.post("/api/predict")
def run_ia_model(data: dict, current_user: UserDB = Depends(get_current_user)):
    """
    Ruta protegida. Solo se puede acceder si JWT válido.
    """
    # Lógica modelo a imp
    
    # Ejemplo de respuesta
    return {
        "usuario_solicitante": current_user.username,
        "input_recibido": data,
        "prediction": "El modelo ejecutó correctamente. Resultado: 98.5% de precisión",
        "status": "success"
    }

#-------------------------------------------------------------------
# ==========================================
# 7. CRUD DE COLECCIÓN (ÍTEMS E IMÁGENES)
# ==========================================

@app.get("/api/items")
def get_items(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(ItemDB).filter(ItemDB.user_id == current_user.id).all()
    return items

@app.post("/api/items")
async def create_item( 
    image: UploadFile = File(...), 
    nombre: str = Form("Nombre por defecto"),
    current_user: UserDB = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    file_location = f"uploads/{current_user.id}_{image.filename}"
    
    # Lectura asíncrona
    with open(file_location, "wb+") as file_object:
        contenido = await image.read() 
        file_object.write(contenido)
    
    new_item = ItemDB(
        user_id=current_user.id,
        image_path=f"http://localhost:8000/{file_location}",
        nombre=nombre
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.put("/api/items/{item_id}")
def update_item(item_id: int, data: dict, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id, ItemDB.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    # Actualizar nombre
    if "nombre" in data:
        item.nombre = data["nombre"]
    # Actualizar el estado
    if "limpio" in data:
        item.limpio = data["limpio"]
        
    db.commit()
    return {"message": "Actualizado correctamente", "item": item}

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id, ItemDB.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    # Borrar el archivo físico
    file_path = item.image_path.replace("http://localhost:8000/", "")
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(item)
    db.commit()
    return {"message": "Eliminado correctamente"}

# Poner todo como limpio
@app.put("/api/items/bulk/clean-all")
def clean_all_items(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(ItemDB).filter(ItemDB.user_id == current_user.id).update({ItemDB.limpio: True})
    db.commit()
    return {"message": "Toda la ropa está limpia"}

class ItemsConfirm(BaseModel):
    ids: List[int]

# Ensuciar ropa tras seleccionarla como conjunto
@app.put("/api/items/bulk/dirty")
def mark_items_dirty(data: ItemsConfirm, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(ItemDB).filter(ItemDB.id.in_(data.ids), ItemDB.user_id == current_user.id).update({ItemDB.limpio: False}, synchronize_session=False)
    db.commit()
    return {"message": "Prendas enviadas a la lavadora"}