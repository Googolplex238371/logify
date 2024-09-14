from flask import Blueprint,render_template,request,flash,redirect,url_for,jsonify
from .models import User
from website import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required,logout_user,current_user
import json
import secrets
auth = Blueprint("auth",__name__)
@auth.route('/login',methods=["GET","POST"])
def login():
  if current_user.is_authenticated:
    return redirect(url_for("views.home"))
  x = False #This is a boolean value that checks if the user exists
  if request.method == "POST":
    email = request.form.get("email")
    pwd = request.form.get("password")
    user = User.query.filter_by(email=email).first()
    if user: 
      if not user.verified:
        flash("Please verify your account first",category='warning')
        return redirect(url_for("auth.login"))
      if not check_password_hash(user.password, pwd):
        flash('Incorrect password',category = 'error')
      else: 
          flash('Success',category='success')
          x = True
          login_user(user,remember=True)
    else: 
      flash('Email does not exist',category='error')
    if(x):
      return redirect(url_for('views.home'))
  return render_template("login.html",user=current_user)
@auth.route('/logout')
@login_required
def logout():
  logout_user()
  flash('Logged Out Successfully!',category='success')
  return redirect(url_for("auth.login"))
@auth.route("/get-otp",methods=["GET","POST"]) #This is a web rest api that helps get an otp for a new user, returns either an otp, or user_not_found
def get_otp():
  if request.method == "POST":
    email = json.loads(request.data)["email"]
    user = User.query.filter_by(email=email).first()
    if not user:
      return jsonify({"data":"user_not_found"}) #checks if the user exists
    elif not user.verified:
      return jsonify({"data":"user_not_found"}) #checks if the user is verified
    else:
      user.otp=""
      if user.otp == "":
        otp = secrets.token_hex(3) #random hexadecimal string with length 6
        while User.query.filter_by(otp=otp).first():
          otp = secrets.token_hex(3)
        user.otp = otp
        db.session.commit()
        return jsonify({"data":otp})
      else:
        return jsonify({"data":"user_has_otp"}) #checks if the user has already requested an otp
@auth.route("/forgot",methods=["GET","POST"])
def forgot():
  if current_user.is_authenticated: #redirects to home page if the user is logged in
    return redirect(url_for("views.home"))
  if request.method == "POST":
    flash("An OTP has been sent to your email",category='success')
  return render_template("forgot.html",user=current_user)
@auth.route("/confirm",methods=["GET","POST"])
def confirm():
  if current_user.is_authenticated:
    return redirect(url_for("views.home"))
  if request.method == "POST":
    user = User.query.filter_by(otp=request.form.get("otp")).first()
    if user:
      if user.otp == request.form.get("otp"): #checks if the otps are the same
        if request.form.get("password1") == request.form.get("password2"):
          user.otp = ""
          user.password = generate_password_hash(request.form.get("password1"),method="sha256")
          user.verified = True
          db.session.commit()
          login_user(user)
          flash("Logged in successfully",category="success")
          return redirect(url_for("views.home"))
        else:
          flash("Passwords do not match",category="error")
      else:
        flash("Invalid OTP",category="error")
    else:
      flash("Invalid OTP",category="error")
  return render_template("confirm.html",user=current_user)
