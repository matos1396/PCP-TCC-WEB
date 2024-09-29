# No terminal Python
from app import db, app
from models import Grupo


with app.app_context():
    db.create_all()

    # No terminal Python
    user = Grupo(grupo_nome='Grupo1', password='senha123')
    db.session.add(user)
    db.session.commit()
