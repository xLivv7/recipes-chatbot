import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.environ.get("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(String, primary_key=True) 
    name_pl = Column(String, nullable=False)

class Nutrient(Base):
    __tablename__ = 'nutrients'
    ingredient_id = Column(String, ForeignKey('ingredients.id'), primary_key=True)
    energy_kcal_100g = Column(Float)
    protein_g_100g = Column(Float)
    fat_g_100g = Column(Float)
    carbs_g_100g = Column(Float)

class DietPolicy(Base):
    __tablename__ = 'diet_policies'
    ingredient_id = Column(String, ForeignKey('ingredients.id'), primary_key=True)
    # flagi 0/1 jako int dla uniknięcia problemów przy importowaniu danych z CSV
    is_vegetarian_ok = Column(Integer, default=1)
    is_vegan_ok = Column(Integer, default=0)
    is_meat = Column(Integer, default=0)
    is_fish = Column(Integer, default=0)
    is_keto_ok = Column(Integer, default=1)

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True) 

class ClientSku(Base):
    __tablename__ = 'client_skus'
    id = Column(String, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    concept_id = Column(String, ForeignKey('ingredients.id')) 
    name_pl = Column(String)
    energy_kcal_100 = Column(Float)
    protein_g_100 = Column(Float)
    fat_g_100 = Column(Float)
    carbs_g_100 = Column(Float)

class SkuSelectionRule(Base):
    __tablename__ = 'sku_selection_rules'
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    concept_id = Column(String, ForeignKey('ingredients.id'))
    rule_order = Column(Integer)
    condition_type = Column(String) # np. 'user_pref'
    condition_value = Column(String) # np. 'vegan'
    preferred_sku_id = Column(String, ForeignKey('client_skus.id'))

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(String, primary_key=True)
    title_pl = Column(String, nullable=False)
    category = Column(String)
    dish_type = Column(String)
    time_min = Column(Integer)
    servings = Column(Float) 
    ingredients_data = Column(JSONB) 
    steps_pl = Column(JSONB)