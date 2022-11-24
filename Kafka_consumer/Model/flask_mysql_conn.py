from flask import Flask
import yaml
from flask_sqlalchemy import SQLAlchemy
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

db = SQLAlchemy(app)

class Visitor(db.Model):
    __tablename__ = 'Visitors'
    id = db.Column(db.Integer, primary_key=True)
    accessed_at=db.Column(db.DateTime)
    user_id=db.Column(db.Integer)
    page_id=db.Column(db.Integer)