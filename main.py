from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog2:passwordbab@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


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

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['POST', 'GET'])
def index():

    #if request.method == 'POST':
    #    blog_name = request.form['title']
    #    blog_body = request.form['body']
    #    new_blog = Blog(blog_name, blog_body)
    #    db.session.add(new_blog)
    #    db.session.commit()

    
    blogs = Blog.query.all()
    return render_template('blog.html',title="Blogs", 
        blogs=blogs) 


@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():

    if request.method == 'POST':
        blog_name = request.form['title']
        blog_body = request.form['body']
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
                error1=rtn_error1, error2=rtn_error2) # and cgi.escape(encoded_error, quote=True))

        # Add the new blog to the database
        new_blog = Blog(blog_name, blog_body)
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

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    #task_id = int(request.form['task-id'])
    #task = Task.query.get(task_id)
    #task.completed = True
    #db.session.add(task)
    #db.session.commit()

    if request.args !="":
        blog_id = request.args.get('id')
        # return Movie.query.filter_by(watched=False).all()
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('blog1.html',title="Blogs", blogs=blogs)   

    blogs = Blog.query.all()
    return render_template('blog.html',title="Blogs", 
        blogs=blogs) 


@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()