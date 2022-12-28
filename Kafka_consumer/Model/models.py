import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from Utils.db import db

class User(db.Model):
    __tablename__ = 'Users'
    username = db.Column(db.String(30),primary_key=True,nullable=False)
    password = db.Column(db.Text,nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self,_username,new_password):
        user=self.get_by_username(_username)
        user.password=new_password
        db.session.commit()

    @classmethod
    def get_by_username(cls,_username):
        return cls.query.filter_by(username=_username).first()

class Visitor(db.Model):
    __tablename__ = 'Visitors'
    id = db.Column(db.Integer, primary_key=True)
    accessed_at=db.Column(db.DateTime)
    user_id=db.Column(db.Integer)
    page_id=db.Column(db.Integer)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls,id):
        return cls.query.get_or_404(id)
    
    @classmethod
    def get_by_page(cls,_page_id):
        return cls.query.filter_by(page_id=_page_id).all()

    @classmethod
    def get_by_user(cls,_user_id):
        return cls.query.filter_by(user_id=_user_id).all()
            
    def to_dict(self):
      return {"id": self.id, "accessed_at": str(self.accessed_at),'user_id':self.user_id,'page_id':self.page_id}
