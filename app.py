from flask import Flask, render_template, request, session, make_response, url_for, redirect
from sourceCode.common.database import Database
from sourceCode.models.blog import Blog
from sourceCode.models.post import Posts
from sourceCode.models.user import User

app = Flask(__name__)
app.secret_key = 'Nothing'


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/')
def home():
    blogs = Blog.find_all()
    return render_template('home.html', blogs=blogs)


@app.route('/login')
def login_form():
    return render_template('login.html')


@app.route('/register')
def register_form():
    return render_template('register.html')


@app.route('/logout')
def logout():
    User.logout()
    return redirect(url_for('home'))


@app.route('/auth/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']

    User.register(email, password)

    return redirect(url_for('login_form'))


@app.route('/auth/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    if User.login_check(email, password):
        User.login(email=email)
        return redirect(url_for('home'))
    else:
        session['email'] = None
        return redirect(url_for('login_form'))


@app.route('/profile')
def profile():
    user = User.find_by_email(session['email'])
    blogs = user.get_blogs()
    if user is not None:
        return render_template('profile.html', blogs=blogs,
                           email=user.email)
    else:
        return redirect(url_for('home'))


@app.route('/blogs/new', methods=['POST', 'GET'])
def new_blog():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.find_by_email(session['email'])

        blog = Blog(title, user._id, user.email, description)
        blog.save_to_mongo()

        return redirect(url_for('profile'))


@app.route('/blogs/delete/<string:blog_id>')
def delete_blog(blog_id):
    blog = Blog.from_mongo(blog_id)
    blog.delete_blog()
    return redirect(url_for('profile'))


@app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()
    user = User.find_by_email(session['email'])

    return render_template('blog_posts.html', posts=posts,
                           title=blog.title, blog_id=blog._id,
                           current_user=user.email if user is not None else None,
                           author=blog.author)


@app.route('/posts/new/<string:blog_id>', methods=['POST', 'GET'])
def new_post(blog_id):
    if request.method == 'GET':
        return render_template('new_post.html', blog_id=blog_id)
    else:
        title = request.form['title']
        content = request.form['content']
        user = User.find_by_email(session['email'])

        post = Posts(title, blog_id, user.email, content)
        post.save_to_mongo()

        return make_response(blog_posts(blog_id))


@app.route('/posts/delete/<string:post_id>')
def delete_post(post_id):
    post = Posts.from_mongo(post_id)
    post.delete_post()
    return make_response(blog_posts(post.blog_id))


if __name__ == '__main__':
    app.run(debug=True)
