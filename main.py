import os
import sys

from website import create_app, db

# Debug print to confirm script is running
print("Script starting...")  # This should always appear when you run the file

app = create_app()

with app.app_context():
    try:
        print("Database connected to:", db.engine.url)
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print("ERROR during database setup:", str(e))

if __name__ == '__main__':
    print("Starting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=5000)  # Normal dev server