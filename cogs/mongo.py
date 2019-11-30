from pymongo import MongoClient
import sys
import os
sys.path.append(os.getcwd() + '/..')

import auth



client = MongoClient(auth.conn)
ctfdb = client['ctftime'] # Create ctftime database
ctfs = ctfdb['ctfs'] # Create ctfs collection

teamdb = client['ctfteams'] # Create ctf teams database

serverdb = client['serverinfo']