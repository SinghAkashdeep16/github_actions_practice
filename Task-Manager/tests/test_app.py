import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

# Set up a simple test client using in-memory SQLite so we never touch test.db
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
client = app.test_client()


def test_homepage_loads():
    """GET / should return 200"""
    response = client.get('/')
    assert response.status_code == 200


def test_create_task():
    """POST / with content should redirect (302) after creating a task"""
    response = client.post('/', data={'content': 'Test task'})
    assert response.status_code == 302


def test_delete_nonexistent_task():
    """DELETE a task that doesn't exist should return 404"""
    response = client.get('/delete/9999')
    assert response.status_code == 404


def test_update_nonexistent_task():
    """GET update page for a task that doesn't exist should return 404"""
    response = client.get('/update/9999')
    assert response.status_code == 404
