import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Configure the upload folder
app.config['UPLOAD_FOLDER'] = 'static/img/product_img'







# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///crimsonmart.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show Homepage of Crimson Mart"""

    user_id = session["user_id"]
    user_data = db.execute(
        "SELECT * FROM users WHERE id = ?",
        user_id
    )

    product_data = db.execute("SELECT * FROM products")
    cart_count_db = db.execute("SELECT COUNT(*) FROM cart WHERE user_id=?", user_id)
    cart_count = cart_count_db[0]["COUNT(*)"]

    return render_template(
        "index.html",
        user_data=user_data,
        product_data= product_data,
        cart_count = cart_count
    )





@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        password = request.form.get("password")
        number = request.form.get("number")
        email = request.form.get("email")
        confirm_password = request.form.get("confirmpassword")

        if password != confirm_password:
            flash("Passwords do not Match","danger")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)

        try:
            # Check if the combination of first name and last name exists
            user_exists = db.execute("SELECT id FROM users WHERE first_name = ? AND last_name = ?",firstname, lastname)

            if user_exists:
                flash("User with this first name and last name already exists", "danger")
            else:
                newly_registered_user = db.execute("INSERT INTO users(first_name, last_name, username, password, email,number) VALUES (?, ?, ?, ?, ?,?)",firstname, lastname, username, hashed_password, email,number )
                flash("User Created Successfully","success")
                # allow user to login after registration
                session["user_id"] = newly_registered_user



        except:
             flash("An error occurred while registering the user", "danger")
        # Redirect user to home page
        return redirect("/")





@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":


        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
         flash("Invalid username and/or password","danger")
         return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Successfully Logged In","success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/about")
@login_required
def about():
    """Show about of Crimson Mart"""

    user_id = session["user_id"]
    user_data = db.execute(
        "SELECT * FROM users WHERE id = ?",
        user_id
    )

    cart_count_db = db.execute("SELECT COUNT(*) FROM cart WHERE user_id=?", user_id)
    cart_count = cart_count_db[0]["COUNT(*)"]
    return render_template(
        "about.html",
        user_data=user_data, cart_count=cart_count
    )

@app.route("/contact")
@login_required
def contact():
    """Show Contact of Crimson Mart"""

    user_id = session["user_id"]
    user_data = db.execute(
        "SELECT * FROM users WHERE id = ?",
        user_id
    )
    cart_count_db = db.execute("SELECT COUNT(*) FROM cart WHERE user_id=?", user_id)
    cart_count = cart_count_db[0]["COUNT(*)"]

    return render_template(
        "contact.html",
        user_data=user_data, cart_count=cart_count
    )

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    user_id = session["user_id"]
    """Show Sell of Crimson Mart"""
    if request.method == "GET":

        user_id = session["user_id"]

        user_data = db.execute(
        "SELECT * FROM users WHERE id = ?",
        user_id
    )
        cart_count_db = db.execute("SELECT COUNT(*) FROM cart WHERE user_id=?", user_id)
        cart_count = cart_count_db[0]["COUNT(*)"]
        return render_template("sell.html", user_data = user_data,cart_count=cart_count)

    else:
        image=""

        if not request.files:

            flash("No image has been Uploaded","danger")
            return redirect("/sell")
        file = request.files['file']
        if file.filename == '':
            flash("No image has been Uploaded","danger")
            return redirect("/sell")
        if file:
            # Save the file to the 'img' folder
            filename = secure_filename(file.filename)
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"{current_time}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

             # Store the path in the database

            image = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)


        user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        first_name = user_data[0]["first_name"]
        last_name = user_data[0]["last_name"]


        product_name = request.form.get("product_name")
        description = request.form.get("description")
        original_price = request.form.get("original_price")
        listing_price = request.form.get("listing_price")
        full_name = first_name + " " + last_name

        db.execute(
            "INSERT INTO products(user_id,created_by,product_name,product_image,description,listing_price,original_price) VALUES(?,?,?,?,?,?,?)",
            user_id,
            full_name,
            product_name,
            image,
            description,
            listing_price,
            original_price
        )

        flash("Listing Created Successfully","success")
        cart_count_db = db.execute("SELECT COUNT(*) FROM cart WHERE user_id=?", user_id)
        cart_count = cart_count_db[0]["COUNT(*)"]
        return render_template("sell.html", user_data=user_data,cart_count=cart_count)



@app.route("/product_detail", methods=["GET", "POST"])
@login_required
def product_detail():
    user_id = session["user_id"]
    """Show product detail of Crimson Mart"""

    if request.method == "POST":
        product_id = request.form.get("product_id")
        user_data = db.execute(
        "SELECT * FROM users WHERE id = ?",
        user_id
          )

        author_id_data = db.execute(
        "SELECT user_id FROM products WHERE product_id = ?",
        product_id
          )

        author_id = author_id_data[0]["user_id"]
        author_data = db.execute(
        "SELECT * FROM users WHERE id = ?",
        author_id
          )
        single_product_data = db.execute("SELECT * FROM products WHERE product_id = ?", product_id)
        cart_count_db = db.execute("SELECT COUNT(*) FROM cart WHERE user_id=?", user_id)
        cart_count = cart_count_db[0]["COUNT(*)"]

        return render_template("single-product.html", single_product_data=single_product_data, user_data=user_data,author_data= author_data,cart_count=cart_count)



@app.route("/add_cart", methods=["GET", "POST"])
@login_required
def add_cart():
    user_id = session["user_id"]
    """Add product to Cart"""

    if request.method == "POST":
        product_id = request.form.get("product_id")
        user_data = db.execute(
        "SELECT * FROM users WHERE id = ?",
        user_id
          )


        product_data = db.execute(
        "SELECT * FROM products WHERE product_id = ?",
        product_id
          )

        product_name = product_data[0]["product_name"]
        product_image = product_data[0]["product_image"]
        product_price = product_data[0]["listing_price"]

        db.execute(
            "INSERT INTO cart(product_id,product_name,product_image,product_price,user_id) VALUES(?,?,?,?,?)",
            product_id,
            product_name,
            product_image,
            product_price,
            user_id

        )
        single_product_data = product_data

        author_id_data = db.execute(
        "SELECT user_id FROM products WHERE product_id = ?",
        product_id
          )

        author_id = author_id_data[0]["user_id"]
        author_data = db.execute(
        "SELECT * FROM users WHERE id = ?",
        author_id
          )
        cart_count_db = db.execute("SELECT COUNT(*) FROM cart WHERE user_id=?", user_id)
        cart_count = cart_count_db[0]["COUNT(*)"]

        flash("Added to Cart Successfully","success")
        return render_template("single-product.html", user_data=user_data,single_product_data=product_data,author_data= author_data, cart_count=cart_count)
        # return redirect("/product_detail")


@app.route("/cart")
@login_required
def cart():
    user_id = session["user_id"]
    """Show Cart Page"""
    user_data = db.execute(
        "SELECT * FROM users WHERE id = ?",
        user_id
          )


    product_data = db.execute(
        "SELECT * FROM cart WHERE user_id = ?",
        user_id
          )
    cart_count_db = db.execute("SELECT COUNT(*) FROM cart WHERE user_id=?", user_id)
    cart_count = cart_count_db[0]["COUNT(*)"]

    total_price_db = db.execute(
        "SELECT SUM(product_price) FROM cart WHERE user_id = ?",
        user_id
          )
    total_price = total_price_db[0]["SUM(product_price)"]


    return render_template("cart.html", user_data=user_data,product_data=product_data, cart_count=cart_count,total_price = total_price)



@app.route("/delete", methods=["POST"])
@login_required
def delete():
    """Delete product in Cart"""
    if request.method=="POST":
         user_id = session["user_id"]

         product_id = request.form.get("product_key")

         db.execute("DELETE FROM cart WHERE user_id=? AND id=?", user_id, product_id)


         flash("Product Deleted","danger")
         return redirect("/cart")


@app.route("/checkout")
@login_required
def checkout():
    user_id = session["user_id"]
    """Show Cart Page"""
    user_data = db.execute(
        "SELECT * FROM users WHERE id = ?",
        user_id
          )


    product_data = db.execute(
        "SELECT * FROM cart WHERE user_id = ?",
        user_id
          )
    cart_count_db = db.execute("SELECT COUNT(*) FROM cart WHERE user_id=?", user_id)
    cart_count = cart_count_db[0]["COUNT(*)"]

    total_price_db = db.execute(
        "SELECT SUM(product_price) FROM cart WHERE user_id = ?",
        user_id
          )
    total_price = total_price_db[0]["SUM(product_price)"]


    return render_template("checkout.html", user_data=user_data,product_data=product_data, cart_count=cart_count,total_price = total_price)


@app.route("/clear_cart", methods=["POST"])
@login_required
def clear_cart():
    """Delete all product in Cart"""
    if request.method=="POST":
         user_id = session["user_id"]



         db.execute("DELETE FROM cart WHERE user_id=? ", user_id)


         flash("Order Placed Successfully","success")
         return redirect("/checkout")














