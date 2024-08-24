from app import db, app

with app.app_context():
    db.drop_all() #this will delete all data!
    db.create_all()

