import sys
import os
from dotenv import load_dotenv

# Path to your project folder
path = '/home/sayana2011/sayana_press'
if path not in sys.path:
    sys.path.append(path)

# Load environment variables from .env file
load_dotenv(os.path.join(path, '.env'))

# Import your Flask app
from app import app as application
