from peewee import *
from peewee_plus import *
from datetime import date, datetime
import json

# Define the database connection
db = SqliteDatabase('bcds.db')

# User model
class User(Model):
    id = AutoField(unique=True, primary_key=True)
    name = CharField(max_length=255)
    username = CharField(max_length=255, unique=True)
    password = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

class Administrator(User):
    pass

class Staff(User):
    job_title = CharField()

# Patient model
class Patient(Model):
    id = AutoField(unique=True)
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    dob = DateField()
    gender = CharField(max_length=10)
    email = CharField(max_length=255)
    phone = CharField(max_length=15)
    address = TextField()
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

# Diagnostic result model
class DiagnosticResult(Model):
    id = AutoField(primary_key=True, unique=True)
    patient = ForeignKeyField(Patient, backref='diagnostic_results')
    result_name = CharField(max_length=255)
    result_value = TextField()
    created_at = DateTimeField(default=datetime.now)


    class Meta:
        database = db


#---------FUNCTIONS---------#
# Create function
def create_entity(cls,**kwargs):
    entity = cls.create(**kwargs)
    entity.save()
    return entity

# Update function
def update_entity(entity, **kwargs):
    for key, value in kwargs.items():
        setattr(entity, key, value)
    
    entity.save()
    print("Entity", entity)
    return entity

# Delete function
def delete_entity(cls,id):
    entity = cls.get(cls.id == id)
    entity.delete_instance()

def get_all_entity(entity):
    try:
      entities = [i for i in entity.select().dicts()]
      return entities
    except:
      None
# Read user by ID
def read_user(username):
    try:
        user = Administrator.get_by_id(username)
        return user
    except DoesNotExist:
      try:
        user = Staff.get_by_id(username)
        return user
      except DoesNotExist:
        return None

def read_patient(id):
    try:
        user = Patient.get_by_id(id)
        return user
    except DoesNotExist:
       return None
   
db.create_tables([User, Administrator, Staff, Patient, DiagnosticResult])

try:
  create_entity(Administrator, username='admin', password='admin01', name='Admin')
except IntegrityError:
  pass