from flask_rest_service import app
import requests
import os
port = int(os.environ.get('PORT', 5000))
app.debug = True
app.run(host='0.0.0.0', port = port)
