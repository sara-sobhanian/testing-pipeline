import base64
import os
import time
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

# Ensure the instance folder exists (for the database)
os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

# Read admin password from file (Base64)
SECRET_FILE_PATH = os.path.join(app.root_path, 'secret.txt')
if not os.path.exists(SECRET_FILE_PATH):
    raise FileNotFoundError(f"Secret file not found at {SECRET_FILE_PATH}")

with open(SECRET_FILE_PATH, 'r') as f:
    encoded_password = f.read().strip()

ADMIN_USERNAME = 'admin'
try:
    ADMIN_PASSWORD = base64.b64decode(encoded_password).decode('utf-8')
except Exception as e:
    raise ValueError("Failed to decode admin password from secret.txt") from e

DATABASE = os.path.join(app.root_path, 'instance', 'products.db')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Create and return a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database (create tables, etc.)
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            image_path TEXT,
            url TEXT
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cover_photo_path TEXT
        );
    ''')

    # Insert default cover photo path if it doesn't exist
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM settings')
    count = cur.fetchone()[0]
    if count == 0:
        # Use our default cover photo initially
        conn.execute("INSERT INTO settings (cover_photo_path) VALUES ('img/default_cover.jpg')")

    # Make sure 'url' column exists in products
    cur.execute("PRAGMA table_info(products);")
    columns = [col[1] for col in cur.fetchall()]
    if 'url' not in columns:
        conn.execute("ALTER TABLE products ADD COLUMN url TEXT")

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    """Render the home page with cover photo + products."""
    conn = get_db_connection()
    cover_photo = conn.execute("SELECT cover_photo_path FROM settings LIMIT 1").fetchone()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    # Convert DB's cover_photo_path to something we can show in template
    if cover_photo and cover_photo['cover_photo_path']:
        cover_path = cover_photo['cover_photo_path']
    else:
        cover_path = 'img/default_cover.jpg'  # Fallback

    return render_template('home.html', cover_photo=cover_path, products=products)

@app.route('/products')
def products_page():
    """Display a page of all products."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('products.html', products=rows)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Handle Contact Us form."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # TODO: Send an email or do something with the contact info
        flash("Thank you for contacting us! We'll get back to you soon.", 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard for managing products and cover photo."""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    cover_photo = conn.execute("SELECT cover_photo_path FROM settings LIMIT 1").fetchone()
    conn.close()

    # Get DB cover photo or fallback
    if cover_photo and cover_photo['cover_photo_path']:
        cover_path = cover_photo['cover_photo_path']
    else:
        cover_path = 'img/default_cover.jpg'

    return render_template('admin_dashboard.html', products=products, cover_photo=cover_path)

@app.route('/admin/logout')
def admin_logout():
    """Logout the admin."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/admin/product/new', methods=['GET', 'POST'])
@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def manage_product(product_id=None):
    """Create or edit a product."""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()

    # If editing, fetch product
    product = None
    if product_id:
        product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', '0')
        url = request.form.get('url')
        image_file = request.files.get('image')

        # Keep old image path if editing
        image_path = product['image_path'] if product else None

        # If a new file is uploaded
        if image_file and image_file.filename:
            if allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                unique_filename = f"{int(time.time())}_{filename}"
                # We'll store just "img/<unique_filename>" in DB
                image_path = f"img/{unique_filename}"
                # Save the file physically
                save_dir = os.path.join(app.root_path, 'static', 'img')
                os.makedirs(save_dir, exist_ok=True)
                full_path = os.path.join(save_dir, unique_filename)
                image_file.save(full_path)
            else:
                flash("Invalid file type. Allowed types: png, jpg, jpeg, gif.", "danger")
                conn.close()
                return redirect(url_for('manage_product', product_id=product_id) if product_id else url_for('manage_product'))

        if product_id:
            # Update existing product
            conn.execute(
                "UPDATE products SET name = ?, description = ?, price = ?, image_path = ?, url = ? WHERE id = ?",
                (name, description, price, image_path, url, product_id)
            )
            flash("Product updated successfully!", "success")
        else:
            # Insert new product
            try:
                conn.execute(
                    "INSERT INTO products (name, description, price, image_path, url) VALUES (?, ?, ?, ?, ?)",
                    (name, description, float(price), image_path, url)
                )
                flash("Product created successfully!", "success")
            except Exception as e:
                flash(f"Error while creating the product: {str(e)}", "danger")

        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    conn.close()
    return render_template('product_form.html', product=product)

@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """Delete a product from the DB."""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    flash("Product deleted successfully!", "warning")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/cover_photo', methods=['POST'])
def update_cover_photo():
    """Update the site's cover photo from Admin Dashboard."""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    cover_file = request.files.get('cover_photo')
    if cover_file and cover_file.filename:
        if allowed_file(cover_file.filename):
            filename = secure_filename(cover_file.filename)
            unique_filename = f"{int(time.time())}_{filename}"
            new_cover_path = f"img/{unique_filename}"
            save_dir = os.path.join(app.root_path, 'static', 'img')
            os.makedirs(save_dir, exist_ok=True)
            full_path = os.path.join(save_dir, unique_filename)

            try:
                cover_file.save(full_path)
                conn = get_db_connection()
                conn.execute("UPDATE settings SET cover_photo_path = ?", (new_cover_path,))
                conn.commit()
                conn.close()
                flash("Cover photo updated!", "success")
            except Exception as e:
                flash(f"Error uploading cover photo: {str(e)}", "danger")
        else:
            flash("Invalid file type for cover photo. Allowed: png, jpg, jpeg, gif.", "danger")
    else:
        flash("No file selected for upload.", "warning")

    return redirect(url_for('admin_dashboard'))

# Handle large file errors
@app.errorhandler(413)
def request_entity_too_large(error):
    flash("File is too large. Max 16MB.", "danger")
    return redirect(request.url), 413

if __name__ == '__main__':
    app.run(debug=True)
