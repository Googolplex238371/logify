from flask import Blueprint,render_template,redirect,url_for,request,flash,jsonify
from flask_login import login_required,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from .models import User,Log
import secrets
import random
from . import db
import requests
import json
import os

views = Blueprint("views",__name__)

@views.route('/',methods=["GET","POST"])
@login_required
def home():
  if current_user.admin:
    file_size = os.path.getsize("website/database.db")
    return render_template("admin_home.html",user=current_user,file_size=file_size)
  elif current_user.teacher:
    students_data = User.query.filter_by(teacher_id=current_user.id).all()
    students = [[student.name,student.email] for student in students_data]
    for i in range(len(students)):
      student = User.query.filter_by(email=students[i][1]).first()
      logs = []
      for log in Log.query.filter_by(user_id=student.id).all():
        logs.append([log.name,log.skill,log.assesor_email,log.desc,log.feedback,log.file,log.fileName,log.date,log.valid,log.approved])
      logs= logs[::-1]
      students[i].append(logs)
    return render_template("teacher_home.html",user=current_user,students=students)
  else:
    if request.method == "POST":
      log =  Log(user_id = current_user.id,skill = request.form.get("skill"),assesor_email =request.form.get("email"),desc = request.form.get("desc"),file=request.form.get("file"),name=request.form.get("name"),url=request.form.get("url"),fileName=request.form.get("filename"))
      db.session.add(log)
      db.session.commit()
      flash("Log Added Successfully!",category="success")
      return redirect(url_for("views.home"))
    return render_template("student_home.html",user=current_user)
@views.route('/view-logs')
@login_required
def student_logs():
  if current_user.admin or current_user.teacher:
    return redirect(url_for("views.nopage"))
  logs = []
  for log in Log.query.filter_by(user_id=current_user.id).all():
    logs.append([log.name,log.skill,log.assesor_email,log.desc,log.feedback,log.valid,log.approved,log.date])
  return render_template("student_logs.html",user=current_user,logs=logs)

@views.route('/portfolio/<email>')
def portfolio(email):
  user = User.query.filter_by(email=email).first()
  if not user:
    return redirect(url_for("views.nopage"))
  if user.admin or user.teacher:
    return redirect(url_for("views.nopage"))
  logs = []
  for log in Log.query.filter_by(user_id=user.id).all():
    if log.approved:
      logs.append([log.name,log.skill,log.assesor_email,log.desc,log.feedback,log.file,log.fileName,log.date])
  return render_template("portfolio.html",user=current_user,logs=logs,name=user.name,portfolio = current_user.portfolio)

@views.route('/view-users',methods=["GET","POST"])
@login_required
def view_users():
  if not current_user.admin or current_user.teacher:
    print(current_user.teacher)
    return redirect(url_for("views.nopage"))
  else:
    data = []
    for i in db.session.query(User).all():
      data.append([i.id,i.name,i.email,i.admin,i.teacher])
    return render_template("view_users.html",user=current_user,data=data)
@views.route('/approve/<url>',methods=["GET","POST"])
def approve(url):
  log = Log.query.filter_by(url=url).first()
  if log and not log.approved and log.valid:
    if request.method == "POST":
      if request.form.get("valid") == "yes":
        log.approved = True
      else:
        log.valid = False
      log.feedback = request.form.get("feedback")
      db.session.commit()
      return redirect(url_for("views.home"))
    return render_template("approve.html",log=log,user=current_user)
  else:
    return redirect(url_for("views.nopage"))
@views.route('/add-users',methods=["GET","POST"])
@login_required
def add_users():
  if request.method == "POST":
    role = request.form.get("role")
    user = User(name=request.form.get("name"),password=generate_password_hash(request.form.get("pwd")),email=request.form.get("email"),admin = role=="admin",teacher=role=="teacher",otp = request.form.get("pwd"))
    if role == "student":
      teacher_email = request.form.get("teacher_email")
      teacher_id = User.query.filter_by(email=teacher_email).first().id
      user.teacher_id = teacher_id
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('views.add_users'))
  return render_template("add_users.html",user=current_user)
@views.route('/404')
def nopage():
  return render_template("404.html",user=current_user)
@views.route('/add-log',methods=['GET','POST'])
def add_log():
  if request.method == "POST":
    url = secrets.token_hex(16)
    duplicate = Log.query.filter_by(url=url).first()
    while duplicate:
      url = secrets.token_hex(16)
    print(url)
    return jsonify({"data":url})
  else:
    return redirect(url_for("views.nopage"))
@views.route('/notifications')
@login_required
def notifications():
  if current_user.teacher:
    students = User.query.filter_by(teacher_id=current_user.id).all()
    logs = []
    for student in students:
      for log in Log.query.filter_by(user_id=student.id).all():
        if log.viewed <=1:
          log.viewed+=1
        logs.append([User.query.filter_by(id=log.user_id).first().name,log.name,log.skill,log.date,log.viewed])
    db.session.commit()
    logs = logs[::-1]
    return render_template("notifications.html",user=current_user,logs=logs)
  else:
    return redirect(url_for("views.nopage"))
@views.route("get-logs",methods=["GET","POST"])
def get_logs():
  if request.method == "POST":
    if current_user.teacher:
      logs = 0
      students = User.query.filter_by(teacher_id=current_user.id).all()
      for student in students:
        for log in Log.query.filter_by(user_id=student.id).all():
          if log.viewed <1:
            logs+=1
      if logs == 0:
        logs = ""
      return jsonify({"data":logs})
    else:
      return jsonify({})
  else:
    return redirect(url_for("views.nopage"))
@views.route('/check-user',methods=["GET","POST"])
def check_user():
  if request.method == "POST":
    d = json.loads(request.data)
    email = d["email"]
    name = d["name"]
    try:
      if d["role"] == "student":
        teacher_email = d["teacher_email"]
        teacher = User.query.filter_by(email=teacher_email).first()
        if not teacher:
          return jsonify({"data":"teacher_not_found"})
        else:
          if not teacher.teacher:
            return jsonify({"data":"teacher_not_teacher"})
      test = User.query.filter_by(email=email).first()
      if not test:
        pwd = secrets.token_hex(4)
        user = User.query.filter_by(otp=pwd).first()
        while user:
          pwd = secrets.token_hex(4)
        print(pwd)
        if d["role"] == "Student":
          return jsonify({"result":"true","pwd":pwd,"email":email,"role":d["role"],"teacher_email":d["teacher_email"],"name":name})
        else:
          return jsonify({"result":"true","pwd":pwd,"email":email,"role":d["role"],"name":name})
      else:
        return jsonify({"result":"false"})
    except:
      return jsonify({"result":"true","pwd":""})
  else:
    return redirect(url_for("views.nopage"))
@views.route('/upload-users',methods=['GET',"POST"])
@login_required
def upload_users():
  if not current_user.admin:
    return redirect(url_for("views.nopage"))
  if request.method == "POST":
    data = request.form.get("data").split(";")
    for i in data:
      print(i)
      row = i.split(",")
      if row == [""]:
        break
      if row[2] != "Student":
          user = User(teacher=row[2]=="Teacher",otp=row[3],email=row[0],password=generate_password_hash(row[3]),admin=row[2]=="Admin",name=row[1])
          db.session.add(user)
          db.session.commit()
    for i in data:
      print(i)
      row = i.split(",")
      if row == [""]:
        break
      teacher_id = -1
      if row[2] == "Student":
          teacher_id = User.query.filter_by(email=row[4]).first().id
          print(teacher_id)
          user = User(otp=row[3],email=row[0],password=generate_password_hash(row[3]),teacher_id=teacher_id,name=row[1])
          db.session.add(user)
          db.session.commit()
    flash("Users added successfully",category="success")
    return redirect(url_for("views.upload_users"))
  return render_template("upload_users.html",user=current_user)
@views.route("/ai-portfolio",methods=["GET","POST"])
@login_required
def suggested():
  if current_user.teacher or current_user.admin:
    return redirect(url_for("views.nopage"))
  else:
    logs = []
    for log in Log.query.filter_by(user_id=current_user.id).all():
        logs.append([log.name,log.skill,log.assesor_email,log.desc,log.feedback,log.date])
    if request.method == "POST":
      current_user.portfolio = request.form.get("portfolio")
      db.session.commit()
    return render_template("suggest.html",user=current_user,logs=logs)
