import pytest
import sys
import os

# CONTEXT: Add the Task-Manager root to the path so Python can find app.py
# when pytest runs from inside the tests/ subfolder.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Todo


# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def client():
    """
    Creates a fresh test Flask client before each test and tears it down after.
    Uses an in-memory SQLite DB so tests never touch the real test.db file
    and each test always starts with a clean empty database.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()         # create tables in the in-memory DB
        yield app.test_client() # hand the client to the test
        db.drop_all()           # clean up after each test


# ─────────────────────────────────────────────
# INDEX ROUTE TESTS
# ─────────────────────────────────────────────

def test_index_get_empty(client):
    """
    GET / with no tasks in DB should return 200 and render the page.
    Checks the app is running and the index template loads correctly.
    """
    response = client.get('/')
    assert response.status_code == 200


def test_index_post_creates_task(client):
    """
    POST / with a task content should add the task to the DB and
    redirect back to / (status 302). Verifies the full create flow.
    """
    response = client.post('/', data={'content': 'Buy groceries'})
    # expect redirect to /
    assert response.status_code == 302

    # verify the task was actually saved to the DB
    with app.app_context():
        db.create_all()
        task = Todo.query.first()
        assert task is not None
        assert task.content == 'Buy groceries'


def test_index_post_empty_content_fails(client):
    """
    POST / with empty content should NOT create a task.
    SQLAlchemy has nullable=False on content so this should fail gracefully.
    """
    response = client.post('/', data={'content': ''})
    # app returns an error string or a 500 — either way not a clean redirect
    assert response.status_code != 302


def test_index_shows_existing_tasks(client):
    """
    GET / when tasks exist in DB should return 200.
    Verifies the query and template render don't crash with data present.
    """
    # seed a task directly into DB
    with app.app_context():
        db.create_all()
        task = Todo(content='Test task')
        db.session.add(task)
        db.session.commit()

    response = client.get('/')
    assert response.status_code == 200


# ─────────────────────────────────────────────
# DELETE ROUTE TESTS
# ─────────────────────────────────────────────

def test_delete_existing_task(client):
    """
    GET /delete/<id> for an existing task should delete it and redirect to /.
    Verifies the task is removed from the DB after deletion.
    """
    # seed a task to delete
    with app.app_context():
        db.create_all()
        task = Todo(content='Task to delete')
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.get(f'/delete/{task_id}')
    assert response.status_code == 302  # redirect after delete

    # verify task is gone from DB
    with app.app_context():
        db.create_all()
        deleted = Todo.query.get(task_id)
        assert deleted is None


def test_delete_nonexistent_task_returns_404(client):
    """
    GET /delete/<id> for an id that doesn't exist should return 404.
    Uses get_or_404 in the route so Flask handles this automatically.
    """
    response = client.get('/delete/9999')
    assert response.status_code == 404


# ─────────────────────────────────────────────
# UPDATE ROUTE TESTS
# ─────────────────────────────────────────────

def test_update_get_renders_form(client):
    """
    GET /update/<id> for an existing task should return 200 and render
    the update form template without crashing.
    """
    with app.app_context():
        db.create_all()
        task = Todo(content='Original content')
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.get(f'/update/{task_id}')
    assert response.status_code == 200


def test_update_post_saves_new_content(client):
    """
    POST /update/<id> with new content should update the task in the DB
    and redirect back to /. Verifies the full update flow end to end.
    """
    with app.app_context():
        db.create_all()
        task = Todo(content='Old content')
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.post(f'/update/{task_id}', data={'content': 'New content'})
    assert response.status_code == 302  # redirect after update

    # verify the content was actually updated in the DB
    with app.app_context():
        db.create_all()
        updated_task = Todo.query.get(task_id)
        assert updated_task.content == 'New content'


def test_update_nonexistent_task_returns_404(client):
    """
    GET /update/<id> for an id that doesn't exist should return 404.
    Uses get_or_404 in the route so Flask handles this automatically.
    """
    response = client.get('/update/9999')
    assert response.status_code == 404
