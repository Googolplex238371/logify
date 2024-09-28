from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import secrets
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String, default = "Dummy User")
  email = db.Column(db.String, unique = True)
  password = db.Column(db.String,default = "",)
  data = db.relationship("Log")
  admin = db.Column(db.Boolean, default = False)
  teacher = db.Column(db.Boolean, default = False)
  teacher_id = db.Column(db.Integer,default=-1)
  verified = db.Column(db.Boolean,default = False)
  otp = db.Column(db.String,default="")
  portfolio = db.Column(db.String,default="")
class Log(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String)
  user_id = db.Column(db.String, db.ForeignKey('user.id'))
  date = db.Column(db.DateTime(timezone=True),default=func.now())
  skill = db.Column(db.String)
  assesor_email = db.Column(db.String)
  valid = db.Column(db.Boolean,default = True)
  approved = db.Column(db.Boolean, default = False)
  feedback = db.Column(db.String(256))
  desc = db.Column(db.String(256))
  file = db.Column(db.Text)
  fileName = db.Column(db.String,default="")
  url = db.Column(db.String,unique = True)
  viewed = db.Column(db.Integer, default = 0)
