import os
import tempfile
import unittest
from unittest.mock import patch
import sqlite3
from app import app, get_db_connection, init_db, ADMIN_USERNAME, ADMIN_PASSWORD
import io
import html  # <-- for unescaping

class TestDealsDealsApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create temporary DB
        cls.db_fd, cls.temp_db_path = tempfile.mkstemp()

        # Patch the DATABASE path in app.py
        cls.patcher = patch('app.DATABASE', cls.temp_db_path)
        cls.patcher.start()

        # Init tables on the test DB
        init_db()

        # Configure the app for testing
        app.config['TESTING'] = True
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
        os.close(cls.db_fd)
        os.remove(cls.temp_db_path)

    def test_home_page(self):
        """Check if home page loads (status 200)."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        """Check if contact page loads (status 200)."""
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)

    def test_admin_login_failed(self):
        """Try wrong credentials, expect 'Invalid credentials.'."""
        response = self.client.post('/admin', data={
            'username': 'wrong',
            'password': 'wrong'
        }, follow_redirects=True)
        self.assertIn(b'Invalid credentials.', response.data)

    def test_admin_login_successful(self):
        """Try correct credentials, expect 'Admin Dashboard'."""
        response = self.client.post('/admin', data={
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD
        }, follow_redirects=True)
        self.assertIn(b'Admin Dashboard', response.data)

    def test_add_product(self):
        """Login as admin and add product. Check success flash."""
        # Login first
        self.client.post('/admin', data={
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD
        }, follow_redirects=True)

        # Add product
        response = self.client.post('/admin/product/new', data={
            'name': 'Test Product X',
            'description': 'Description for test product',
            'price': '5.55',
            'url': 'https://example.com'
        }, follow_redirects=True)
        self.assertIn(b'Product created successfully!', response.data)

        # Verify in DB
        with get_db_connection() as conn:
            product = conn.execute("SELECT * FROM products WHERE name = ?", ("Test Product X",)).fetchone()
            self.assertIsNotNone(product)

    def test_contact_form_submission(self):
        """Submit contact form and see success flash unescaped."""
        response = self.client.post('/contact', data={
            'name': 'TestUser',
            'email': 'test@example.com',
            'message': 'Hello from test'
        }, follow_redirects=True)

        # Convert escaped HTML to normal text
        text = html.unescape(response.data.decode('utf-8'))

        self.assertIn("Thank you for contacting us! We'll get back to you soon.", text)


# Custom test runner for single-line outputs
class SimpleTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        print(f"{test._testMethodName}: successful")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"{test._testMethodName}: failed")

    def addError(self, test, err):
        super().addError(test, err)
        print(f"{test._testMethodName}: error")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        print(f"{test._testMethodName}: skipped")

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestDealsDealsApp)
    runner = unittest.TextTestRunner(resultclass=SimpleTestResult, verbosity=0)
    result = runner.run(suite)

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total_tests - failures - errors - skipped

    print(f"{passed} test(s) passed out of {total_tests}")
