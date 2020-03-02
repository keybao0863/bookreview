from app import db

#Define User data model.
class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)

    #User authentication fields.
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
