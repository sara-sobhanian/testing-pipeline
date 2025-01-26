# DealsDeals.org — A Professional E-Commerce Flask App

## Overview

**DealsDeals.org** is a fully-featured Flask-based e-commerce application that allows users to browse products, view detailed information, and contact the site administrators. Administrators can manage products, including adding, editing, deleting, and specifying external URLs for each product.

### Features

- **User-Facing Pages:**
  - **Home Page:** Displays a dynamic cover photo and a showcase of all available products.
  - **Products Page:** Lists all products in a responsive grid layout.
  - **Contact Us:** Provides a form for users to send inquiries or feedback.

- **Admin Functionalities:**
  - **Secure Admin Login:** Only authorized users can access the admin dashboard.
  - **Product Management:** Create, edit, delete products, and assign external URLs.
  - **Cover Photo Management:** Update the homepage cover photo.

- **Responsive Design:** Ensures optimal viewing experience across devices.

- **Secure File Uploads:** Handles image uploads with validation and unique naming to prevent conflicts.

## Setup

### 1. **Clone the Repository**

```bash
git clone https://github.com/pooyanazad/Dealsdeals-Website.git
cd dealsdeals/app
```

### 2. **Create a Virtual Environment (Recommended)**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Set Up secret.txt**

#### Create secret.txt:

In the root directory of your project (`dealsdeals_app/`), create a file named `secret.txt`.

#### Add Admin Password:

Encode your desired admin password using Base64. For example, to encode `myHardestPasswordEver4You`:

```bash
echo -n "myHardestPasswordEver4You" | base64
```

This will output:

```bash
bXlIYXJkZXN0UGFzc3dvcmRFdmVyNFlvdQ==
```

#### Insert Encoded Password:

Copy the encoded string into `secret.txt`:

```bash
echo "bXlIYXJkZXN0UGFzc3dvcmRFdmVyNFlvdQ==" > secret.txt
```

### 5. **Initialize the Database**

The application initializes the SQLite database automatically on the first run. Ensure that the `instance/` directory exists.

```bash
mkdir -p instance
```

### 6. **Run the Application**

```bash
python app.py
```

#### Access the App:

Open your browser and navigate to `http://127.0.0.1:5000/` to view the home page.

### 7. **Run Tests**

```bash
python test_app.py
```

#### Ensure All Tests Pass:

You should see output indicating that all tests have succeeded.

## Usage

### Admin Access

#### Navigate to Admin Login:

Go to `http://127.0.0.1:5000/admin` to access the admin login page.

#### Login Credentials:

- **Username:** admin
- **Password:** The password you encoded and placed in `secret.txt` (e.g., `myHardestPasswordEver4You`).

#### Admin Dashboard:

After logging in, you'll be redirected to the admin dashboard where you can:

- **Add New Products:** Click on "Add New Product" to create a new product listing. Specify the product's name, description, price, image, and external URL.
- **Edit Products:** Modify existing products by clicking the "Edit" button next to each product.
- **Delete Products:** Remove products by clicking the "Delete" button (with confirmation).
- **Update Cover Photo:** Change the homepage cover photo by uploading a new image.

### User Access

#### Home Page:

- **Cover Photo:** Displays the current cover photo at the top.
- **Product Showcase:** Shows all available products in a responsive grid. Clicking on a product redirects to its specified external URL.

#### Products Page:

Lists all products in a grid format similar to the home page.

#### Contact Us:

Provides a form for users to send messages or inquiries. Currently, form submissions trigger a success message. Integrate an email service to handle actual message sending.

## Additional Recommendations

### 1. Secure Secret Key

For enhanced security, especially in a production environment, set the `SECRET_KEY` as an environment variable instead of hardcoding it in `config.py`.

#### Modify `config.py`:

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-is-a-very-secret-key'
    DEBUG = True  # Set to False in production
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
```

#### Set Environment Variable:

```bash
export SECRET_KEY='your-very-secret-key'
```

### 2. Use a Production Server

While Flask’s built-in server is suitable for development, consider using a production-ready server like Gunicorn or uWSGI for deploying your application.

```bash
pip install gunicorn
gunicorn app:app
```

### 3. Database Migrations

For more complex applications, consider using Flask-Migrate to handle database migrations seamlessly.

```bash
pip install Flask-Migrate
```

### 4. Image Optimization

Optimize uploaded images to reduce load times and improve website performance. Libraries like Pillow can be integrated for this purpose.

#### Example Usage:

```python
from PIL import Image

# After saving the image
img = Image.open(full_image_path)
img.thumbnail((800, 800))
img.save(full_image_path)
```

### 5. Enhance Security

- **Password Hashing:** Instead of storing the admin password in Base64, consider hashing it using libraries like `bcrypt` or Werkzeug's security module.
- **HTTPS:** Serve your application over HTTPS to encrypt data transmission.

### 6. Expand Functionality

- **User Accounts:** Allow users to create accounts, manage their profiles, and track orders.
- **Shopping Cart:** Implement a shopping cart system for users to add and purchase products.
- **Payment Integration:** Integrate payment gateways like Stripe or PayPal for secure transactions.

### 7. Implement Unit Tests

Expand your test coverage to include more scenarios, such as file uploads, form validations, and edge cases.

### 8. Regular Backups

Regularly back up your database and important files to prevent data loss.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries or support, please contact pooyan.azadparvar@gmail.com.

---

## Summary of Changes

- **Database Schema:** Added a `url` field to the `products` table to store external links for each product.
- **Flask Routes:** Updated routes to handle the new `url` field during product creation and editing.
- **Templates:** Modified `product_form.html`, `home.html`, `products.html`, and `admin_dashboard.html` to include and utilize the `url` field, making products clickable and redirecting to specified URLs.
- **.gitignore:** Updated to exclude `secret.txt` and all files within `static/img/`, ensuring sensitive information and test photos are not pushed to GitHub.
- **README.md:** Provided a concise and informative `README.md` detailing setup instructions, usage, and additional recommendations.

---

Feel free to integrate these changes into your project. If you encounter any issues or need further assistance, don't hesitate to ask!
