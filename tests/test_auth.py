# tests/test_auth.py
import pytest


def test_login_page_loads(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b'GreekMetrics' in r.data


def test_admin_login_redirects_to_dashboard(client):
    r = client.post('/login', data={'password': 'testadmin'}, follow_redirects=False)
    assert r.status_code == 302
    assert '/admin/dashboard' in r.headers['Location']


def test_officer_login_redirects_to_select(client):
    r = client.post('/login', data={'password': 'testofficer'}, follow_redirects=False)
    assert r.status_code == 302
    assert '/officer/select' in r.headers['Location']


def test_wrong_password_stays_on_login(client):
    r = client.post('/login', data={'password': 'wrong'}, follow_redirects=True)
    assert r.status_code == 200
    assert b'Invalid password' in r.data


def test_logout_clears_session(admin_client):
    r = admin_client.get('/logout', follow_redirects=False)
    assert r.status_code == 302
    r2 = admin_client.get('/admin/dashboard', follow_redirects=False)
    assert r2.status_code == 302
    assert '/' in r2.headers['Location']


def test_admin_dashboard_requires_auth(client):
    r = client.get('/admin/dashboard', follow_redirects=False)
    assert r.status_code == 302


def test_officer_dashboard_requires_auth(client):
    r = client.get('/officer/dashboard', follow_redirects=False)
    assert r.status_code == 302
