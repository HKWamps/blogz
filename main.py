from flask import Flask, request, redirect, session, flash, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = "abc123"
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpw@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

#set up array of input fields (PROMPT, NAME, TYPE, Validation Required)
input_fields = [("Username:", "username", "text") , ("Password:", "password", "password"),
    ("Verify Password:", "verify_pwd", "password")] #, ("Email (optional):","user_email", "text")]

#set up array to hold error messages
error_list=["","","",""]
input_values=["","","",""]
#global_user_id = 0
#set up variable to indicate if error is found
error = ""

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)

    def __init__(self, name):
        self.name = name
        self.completed = False

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1024))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner_id = owner

class User(db.Model):

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(120))
        password = db.Column(db.String(64))
        blogs = db.relationship('Blog', backref='owner')

        def __init__(self, username, password):
            self.username = username
            self.password = password

def logged_in_user():
    if 'username' in session:
        owner = User.query.filter_by(username=session['username']).first()
    return owner
    

@app.before_request
def require_login():
    allowed_routes = ['login', 'validate_signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/signup", methods=['POST', 'GET'])
def validate_signup():

    error = ""

    if request.method == 'POST':
        # look inside the request to figure out what the user typed
        input_username = request.form['username']
        input_pword = request.form['password']
        input_verify = request.form["verify_pwd"]
        # input_email = request.form["user_email"]
        
        #save requested username and email for persistence
        input_values[0]=input_username
        # input_values[3]=input_email

        #check for existing user name

        user = User.query.filter_by(username=input_username).first()
        if user:
            flash("Duplicate User ID")
            error_list[0] = "Please Enter Different Username."
            error = "Please Correct Errors Identified Above and Resubmit"    
            # return redirect('/')


        # User Name Validation
        # if the user typed nothing at all, redirect and tell them the error
        elif (not input_username) or (input_username.strip() == ""):
            error_list[0] = "Please Enter Username."
            error = "Please Correct Errors Identified Above and Resubmit"
        elif (len(input_username) < 3) or (len(input_username) > 20): 
            error_list[0] = "Username MUST be at least 3 and not more than 20 characters with no spaces"
            error = "Please Correct Errors Identified Above and Resubmit"
        else: 
            error_list[0] = ""
        
        # Password Entry Validation
        if (not input_pword) or (input_pword.strip() == ""):
            error_list[1] = "Please Enter Password."
            error = "Please Correct Errors Identified Above and Resubmit"
        elif (len(input_pword) < 3) or (len(input_pword) > 20): 
            error_list[1] = "Password MUST be at least 3 and not more than 20 characters with no spaces"
            error = "Please Correct Errors Identified Above and Resubmit"   
        else:
            error_list[1] = ""
        
        # Verify Password Validation
        if (not input_verify) or (input_verify.strip() == ""):
            error_list[2] = "Please Verify Password."
            error = "Please Correct Errors Identified Above and Resubmit"
        elif input_verify != input_pword:
            error_list[2] = "Passwords provided do not match"
            error = "Please Correct Errors Identified Above and Resubmit"
        else:
            error_list[2] = ""
        
        # E-Mail validation
        # skip checking email if field is empty
        #if not(not(input_email)) or (input_email.strip() != ""):
            
            #call function to check email format
            #rtnValue = isValidEmail(input_email)
            #if  rtnValue != True:
            #    error_list[3] = rtnValue
            #    error = "Please Correct Errors Identified Above and Resubmit"
            



        #if error found, redirect to User Signup page with error message
        if len(error) > 0:
            return render_template('signup.html', input_fields=input_fields, error_list = error_list,
                input_values = input_values)
            #  return redirect("/?error=" + error)


        # if the user wants to add a terrible movie, redirect and tell them the error
        #if new_movie in terrible_movies:
        #    error = "Trust me, you don't want to add '{0}' to your Watchlist".format(new_movie)
        #    return redirect("/?error=" + error)

        # 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
        #new_movie_escaped = cgi.escape(new_movie, quote=True)

        # TODO:
        # Create a template called add-confirmation.html inside your /templates directory
        # Use that template to render the confirmation message instead of this temporary message below
        #return "Confirmation Message Under Construction..."
        #return render_template('add-confirmation.html', new_movie=new_movie)

        #Successful, send to welcome screen

        user = User(username=input_username, password=input_pword)
        db.session.add(user)
        db.session.commit()
        session['username']=user.username
        #global_user_id = user.id
        session['user_id'] = logged_in_user().id #1 #user.id
        return redirect("/newpost")
        # return render_template('newpost.html', username = session['username'])
        # return render_template('signup.html', input_fields=input_fields, error_list = error_list) #, error=encoded_error and cgi.escape(encoded_error, quote=True))

    # Otherwise return new signup form
    return render_template('signup.html', input_fields=input_fields, error_list = error_list,
        input_values = input_values) #, error=encoded_error)


@app.route('/', methods=['POST', 'GET'])
def index():

    #if request.method == 'POST':
    #    blog_name = request.form['title']
    #    blog_body = request.form['body']
    #    new_blog = Blog(blog_name, blog_body)
    #    db.session.add(new_blog)
    #    db.session.commit()

    
    users = User.query.all()
    return render_template('index.html', title="Blog Authors", users=users)

    #blogs = Blog.query.all()
    #return render_template('blog.html',title="Blogs", blogs=blogs) 


@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():

    if request.method == 'POST':
        blog_name = request.form['title']
        blog_body = request.form['body']
        blog_owner = session['user_id']
        #new_blog = Blog(blog_name, blog_body)
        #db.session.add(new_blog)
        #db.session.commit()

        rtn_error1 = ""
        rtn_error2 = ""
        error = False
        
        
        if (len(blog_name) < 1): 
            rtn_error1 = "Please fill in the title"
            error = True
        if (len(blog_body) <1):
            rtn_error2 = "Please fill in the body"
            error = True   
        if error:
            return render_template('newpost.html', title=blog_name, body=blog_body,  
                owner=blog_owner, error1=rtn_error1, error2=rtn_error2) # and cgi.escape(encoded_error, quote=True))

        # Add the new blog to the database
        new_blog = Blog(blog_name, blog_body, blog_owner)
        db.session.add(new_blog)
        db.session.commit()

        blog_id = new_blog.id
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('blog1.html',title="Blogs", blogs=blogs)

        #blogs = Blog.query.all()
        #return render_template('blog.html',title="Blogs", blogs=blogs)    
    
    
    #if request.args !="":
    #    blog_id = request.args.get('id')
        # return Movie.query.filter_by(watched=False).all()
    #    blogs = Blog.query.filter_by(id=blog_id).all()
    #    return render_template('blog.html',title="Blogs", blogs=blogs)       
    
    #completed_tasks = Task.query.filter_by(completed=True).all()
    #blogs = Blog.query.all()
    #return render_template('blog.html',title="Blogs", blogs=blogs) #, completed_tasks=completed_tasks)
    return render_template('newpost.html') #, error1=rtn_error1, error2=rtn_error2)



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            # global_user_id = user.id
            #return user.query.filter_by(username=username).all()
            #session['user_id'] = user
            session['user_id'] = logged_in_user().id #1 #user.id
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    
    if 'username' in session:
        session.pop('username', None)
    return redirect('/blog')
    
    #if session['username']:
    #    del session['username']
    #return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():


    #flash(request.args)
    if request.args:
        if request.args.get('user'):
            b_owner_id = request.args.get('user')
        
             #blogs = Blog.query.filter_by(owner_id=user_id).all()
            blogs = Blog.query.filter_by(owner_id = b_owner_id).all()

        elif request.args.get('id'):
            blog_id = request.args.get('id')
            blogs = Blog.query.filter_by(id = blog_id).all()    
        return render_template('blog.html',title="Blogs", blogs=blogs)   


    blogs = Blog.query.all()
    return render_template('blog.html',title="All Blogs", blogs=blogs) 



if __name__ == '__main__':
    app.run()