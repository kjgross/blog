import mistune
from flask import request, redirect, url_for
from flask import render_template

from blog import app
from database import session
from models import Post

from flask import flash
from flask.ext.login import login_user, current_user
from werkzeug.security import check_password_hash
from models import User

from flask.ext.login import login_required, logout_user


@app.route("/")
@app.route("/page/<int:page>")
def pages(page=1, paginate_by=10):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Post).count()

    start = page_index * paginate_by
    end = start + paginate_by

    total_pages = (count - 1) / paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post)
    posts = posts.order_by(Post.datetime.desc())
    posts = posts[start:end]

    return render_template("pages.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )


@app.route("/")
@app.route("/post/<int:post>")
def posts(post=1, paginate_by=1):
    # Zero-indexed  
    page_index = post #- 1

    count = session.query(Post).count()

    start = page_index * paginate_by
    end = start + paginate_by

    total_pages = (count - 1) / paginate_by + 1
    has_next = page_index > 0
    has_prev = page_index < total_pages - 1

    posts = session.query(Post)
    posts = posts.order_by(Post.datetime)
    posts = posts[start:end]

    return render_template("posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        post=post,
        total_pages=total_pages
    )    


@app.route("/post/add", methods=["GET"])
@login_required
def add_post_get():
    return render_template("add_post.html")

@app.route("/post/add", methods=["POST"])
@login_required
def add_post_post():
    post = Post(
        title=request.form["title"],
        content=mistune.markdown(request.form["content"]),
        author=current_user
    )
    session.add(post)
    session.commit()
    return redirect(url_for("posts"))


@app.route("/post/edit/<int:post_id>", methods=["GET"])
@login_required
def edit_post_get(post_id):

	posts = session.query(Post)
	posts = posts[post_id]

	return render_template("edit_post.html",
    	post=posts
	)

@app.route("/post/edit/<int:post>", methods=["POST"])
@login_required
def edit_post_post(post):
	posts = session.query(Post)
	posts = posts[post]
    # post = Post(
    #     title=request.form["title"],
    #     content=request.form["content"]
    # )
	posts.title=request.form["title"]
	posts.content=request.form["content"]

    #session.merge(post)
	session.commit()
	return redirect(url_for("posts"))


@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("posts"))  


@app.route("/logout", methods=["GET"])
@login_required
def logout():
	logout_user()
	return redirect(url_for("posts"))



@app.route("/post/delete/<int:post_id>", methods=["GET"])
@login_required
def delete_post_get(post_id):

	posts = session.query(Post)
	posts = posts[post_id]

	return render_template("delete_post.html",
    	post_id=posts
	)

@app.route("/post/delete/<int:post>", methods=["POST"])
@login_required
def delete_post_post(post):
    posts= session.query(Post)
    posts= posts[post]

    session.delete(posts)
    session.commit()
    return redirect(url_for("posts"))




