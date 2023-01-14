from flask import Flask
import yaml
import os

with open(os.path.join(os.path.dirname(__file__), 'db_conn.yml'), 'r') as f:
    try:
        db=yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(exc)

app = Flask(__name__)
#mysql+driver://username:password@host:port/database_name
connection_str='mysql+pymysql://'+db['mysql_user']+':'+db['mysql_password']+'@'+db['mysql_host']+'/'+db['mysql_db']
app.config['SQLALCHEMY_DATABASE_URI']=connection_str
app.config['SECRET_KEY'] = os.urandom(24)