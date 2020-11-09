# python-rest-api

Flask backend to ETL raw CSVs with pandas, communicate with database, and provide REST api for managing QIB collections.

## Repos

GitHub repositories link:<br />
  •Back-end: https://github.com/genttunn/python-rest-api.git<br />
  •Front-end: https://github.com/genttunn/feature-manager

### To set up the project

Setup a MySQL server, either online or local. Create a database called‘features-db’<br />
Install node.js<br />
Pull this project’s back-end and front-end from Github<br />
Open the back-end application (python-rest-api), install the requisite packages with pip<br />
Make a file in python-rest-api/feature_manager/ called dbparams.py, fill it like below with the variables being the created MySQL db from above:<br />
mysql_host = *****<br />
mysql_user = *****<br />
mysql_db = *****<br />
mysql_password = *****<br />
connection_string = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format(mysql_user,mysql_password,mysql_host,mysql_db)<br />
<br />
Open a terminal at python-rest-api/ and type pipenv shell to activate pipenvshell <br />
Type pythonto enter yython console there <br />
Type  the  following  commands  one  by  one  to  create the  data  model  in  database  and  insert some basic metadata:<br />
from feature_manager import db<br />
db.create_all()<br />
from feature_manager.routes import *<br />
quick_start()<br />

<br />
Quit Python console and start the back-end application with python app.py<br />
Open a terminal in the front-end application (feature-manager), type npm to install dependencies, then npm start to start the React application. The app is now empty because there are no QIB uploaded yet. These files can be found in python-rest-api/csv/. *Note: upload the qib collections file first before uploading list_patient_outcome.csv
