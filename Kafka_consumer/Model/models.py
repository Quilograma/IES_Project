import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from Utils.db import db

class Model(db.Model):
    __tablename__ = 'Models'
    model_id=db.Column(db.Integer, primary_key=True)
    model_pickle=db.Column(db.LargeBinary)
    TrainingStart=db.Column(db.DateTime)
    TrainingEnd=db.Column(db.DateTime)
    page_id=db.Column(db.Integer)
    model_params=db.Column(db.Text)
    q_hat = db.Column(db.Float)
    model_metrics=db.Column(db.Float)

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    
    @classmethod
    def get_by_pageid(cls,page_id):
        return cls.query.get_or_404(page_id)
    
    def to_dict(self):
        return {'page_id':self.page_id,'TrainingStart':str(self.TrainingStart),'TrainingEnd':str(self.TrainingEnd),'model_params':self.model_params,'q_hat':self.q_hat,'MAE':self.model_metrics}


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
