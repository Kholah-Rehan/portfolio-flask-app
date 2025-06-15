from flask import Flask,render_template,request,session,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
from werkzeug.utils import secure_filename
import json
import os
import math

with open('config.json','r') as c:
    params=json.load(c)["params"]
local_server=True
app = Flask(__name__,template_folder='C:/Users/PMLS/PycharmProjects/pythonProject11/ragg/tempelates')
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER']=params['upload_location']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME= params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']

)
mail=Mail(app)
if(local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']
app.secret_key = 'your_unique_secret_key'  # Set a unique secret key
db=SQLAlchemy(app)

class Contacts(db.Model):
    sno= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email=db.Column(db.String(20),nullable=False)
    phone_no = db.Column(db.String(12),nullable=False)
    mess= db.Column(db.String(120),nullable=False)
    date= db.Column(db.String(12),default=datetime.utcnow)

class Posts(db.Model):
    sno= db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline=db.Column(db.String(80), nullable=False)
    slug=db.Column(db.String(25),nullable=False)
    content = db.Column(db.Text,nullable=False)
    date= db.Column(db.String(12),default=datetime.utcnow)
    img_file=db.Column(db.String(25),nullable=True)


@app.route("/")
def home():
    posts = Posts.query.all()
    last = math.ceil(len(posts) / int(params['no_of_post']))

    page = request.args.get('page', 1, type=int)  # Get page as an integer
    if page < 1:
        page = 1  # Ensure page is at least 1

    # Calculate the start and end indices for slicing
    start = (page - 1) * int(params['no_of_post'])
    end = start + int(params['no_of_post'])
    posts = posts[start:end]

    # Prepare pagination links
    prev = url_for('home', page=page - 1) if page > 1 else "#"
    next = url_for('home', page=page + 1) if page < last else "#"

    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)
@app.route("/about")
def about():
    return render_template('about.html', params=params)
@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if request.method == 'POST':
        """modify/update the information for <user_id>"""
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        """ sno name email phone_no mess date"""
        entry=Contacts(name=name,email=email, phone_no=phone, mess=message)
        db.session.add(entry)
        db.session.commit()
        #sending the mail here
        a=email
        mail.send_message("test message from codethirst ",
                          sender=a,#sender from input
                          recipients=[params['gmail_user']],#recepient
                          body=message +"\n" +phone
                          )



        # Redirect to the contact page or home page
        return redirect(url_for('contact'))

    return render_template('contact.html',params=params)
@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()

    return render_template("post.html",params=params,post=post)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params,posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get("pass")


        if username == params["admin_user"] and userpass == params["admin_password"]:
            session['user'] = username
            posts=Posts.query.all()
            return render_template("dashboard.html", params=params,posts=posts)
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html", params=params)
@app.route("/edit/<string:sno>", methods=['POST', 'GET'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            # Get the form data
            matchrequestquerry = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno == "0":
                # Create a new post
                post = Posts(title=matchrequestquerry, slug=slug, content=content, date=date, tagline=tagline, img_file=img_file)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=matchrequestquerry
                post.slug=slug
                post.content=content
                post.img_file=img_file
                post.date=date
                db.session.commit()
                return (redirect('/edit/'+sno))



        post=Posts.query.filter_by(sno=sno).first()
        return render_template("edit.html", params=params,sno=sno,post=post)

    return render_template("dashboard.html",params=params)  # Redirect if user is not authorized

@app.route("/uploader",methods=['GET','POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
        if (request.method=="POST"):
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "upload succesfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')
@app.route("/delete/<string:sno>",methods=['GET','POST'] )
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


app.run(debug=True)