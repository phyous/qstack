import os
from src.app import app, db

if __name__ == '__main__':
    debug = True if os.environ['FLASK_DEBUG'] == '1' else False
    db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=debug)
