from app import db
from app.models import User #type: ignore

admin = User(
    username='admin',
    email='admin@example.com',
    is_admin=True
)
admin.set_password('your_secure_password')

db.session.add(admin)
db.session.commit()

print("Admin user created.")
