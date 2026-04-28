# tests/conftest.py
import pytest
from app import create_app, db as _db
from models import Officer, EvaluationCycle, Score

TEST_CONFIG = {
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'ADMIN_PASSWORD': 'testadmin',
    'OFFICER_PASSWORD': 'testofficer',
    'SECRET_KEY': 'test-secret',
    'WTF_CSRF_ENABLED': False,
}


@pytest.fixture(scope='function')
def app():
    application = create_app(TEST_CONFIG)
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def admin_client(client):
    client.post('/login', data={'password': 'testadmin'}, follow_redirects=True)
    return client


@pytest.fixture
def officer_client(client, db, app):
    with app.app_context():
        officer = Officer(name='Test Officer', position='Social Chair')
        db.session.add(officer)
        db.session.commit()
        officer_id = officer.id
    client.post('/login', data={'password': 'testofficer'}, follow_redirects=True)
    client.post('/officer/select', data={'officer_id': officer_id}, follow_redirects=True)
    return client, officer_id
