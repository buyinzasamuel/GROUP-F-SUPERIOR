import os
from website import create_app, db

app = create_app()

with app.app_context():
   print("Database connected to:", db.engine.url)
   #print("App name:", db.engine.url)
   db.create_all()

if __name__ == '__main__':
   #debug_mode = bool(strtobool(os.environ.get('FLASK_DEBUG', 'False')))
   #app.run(debug=debug_mode)
   app.run(debug=True)  # Set debug=True for development
