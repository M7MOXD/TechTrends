import sqlite3, logging, sys
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Number of Connections
conn_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global conn_count
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    conn_count += 1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "your secret key"

# Define the main route of the web application
@app.route("/")
def index():
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    app.logger.info("Home Request Successfull")
    return render_template("index.html", posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error("Article Not Found")
        return render_template("404.html"), 404
    else:
        app.logger.info(f"Article {post['title']} Retrieved Successfully")
        return render_template("post.html", post=post)


# Define the About Us page
@app.route("/about")
def about():
    app.logger.info("About Request Successfull")
    return render_template("about.html")


# Define the post creation functionality
@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        if not title:
            flash("Title is required!")
        else:
            connection = get_db_connection()
            connection.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
            connection.commit()
            connection.close()
            app.logger.info(f"Article {title} Created Successfully")
            return redirect(url_for("index"))
    app.logger.info("Request Successfull")
    return render_template("create.html")


# Define the Healthz Route
@app.route("/healthz")
def healthz():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}), status=200, mimetype="application/json"
    )
    app.logger.info("Healthz Request Successfull")
    return response


# Define the Metrics Route
@app.route("/metrics")
def metrics():
    connection = get_db_connection()
    post_count = connection.execute("SELECT * FROM posts").fetchall()
    post_count = len(post_count)
    connection.close()
    response = app.response_class(
        response=json.dumps(
            {"status": "success", "code": 0, "data": {"db_connection_count": conn_count, "post_count": post_count}}
        ),
        status=200,
        mimetype="application/json",
    )
    app.logger.info("Metrics Request Successfull")
    return response


# start the application on port 3111
if __name__ == "__main__":
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    format_output = "%(levelname)s: %(name)-2s - [%(asctime)s] - %(message)s"
    handlers = [stderr_handler, stdout_handler]
    logging.basicConfig(format=format_output, handlers=handlers, level=logging.DEBUG)
    app.run(host="0.0.0.0", port="3111")
