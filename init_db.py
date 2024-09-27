# No terminal Python
from app import db, app
from models import Group


with app.app_context():
    db.create_all()

    # No terminal Python
    user = Group(group_name='Grupo1', password='senha123')
    db.session.add(user)
    db.session.commit()
