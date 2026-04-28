# tests/test_officer.py
import pytest
from models import Officer, EvaluationCycle, Score
from scoring import compute_score


def test_officer_select_page_loads(client, db, app):
    with app.app_context():
        o = Officer(name='Jake M', position='Social')
        db.session.add(o)
        db.session.commit()
    client.post('/login', data={'password': 'testofficer'})
    r = client.get('/officer/select')
    assert r.status_code == 200
    assert b'Jake M' in r.data


def test_officer_select_requires_login(client):
    r = client.get('/officer/select', follow_redirects=False)
    assert r.status_code == 302


def test_officer_dashboard_loads(client, db, app):
    with app.app_context():
        o = Officer(name='Test Officer', position='Social')
        db.session.add(o)
        db.session.commit()
        oid = o.id
    client.post('/login', data={'password': 'testofficer'})
    client.post('/officer/select', data={'officer_id': oid})
    r = client.get('/officer/dashboard')
    assert r.status_code == 200
    assert b'Test Officer' in r.data


def test_officer_dashboard_shows_score(client, db, app):
    with app.app_context():
        o = Officer(name='Scored Officer', position='VP')
        db.session.add(o)
        db.session.flush()
        cycle = EvaluationCycle(name='Test Cycle')
        db.session.add(cycle)
        db.session.flush()
        c_avg, e_avg, m_avg, total = compute_score([8]*5, [7]*5, [9]*5)
        s = Score(
            officer_id=o.id, cycle_id=cycle.id,
            creativity_ideas=8, creativity_initiatives=8, creativity_content=8,
            creativity_innovation=8, creativity_variety=8,
            execution_timeliness=7, execution_events=7, execution_attendance=7,
            execution_budget=7, execution_followthrough=7,
            communication_meetings=9, communication_responsiveness=9,
            communication_updates=9, communication_clarity=9,
            communication_collaboration=9,
            creativity_avg=c_avg, execution_avg=e_avg,
            communication_avg=m_avg, weighted_total=total,
        )
        db.session.add(s)
        db.session.commit()
        oid = o.id

    client.post('/login', data={'password': 'testofficer'})
    client.post('/officer/select', data={'officer_id': oid})
    r = client.get('/officer/dashboard')
    assert str(total).encode() in r.data


def test_officer_cannot_see_admin_dashboard(client, db, app):
    with app.app_context():
        o = Officer(name='Not Admin', position='Social')
        db.session.add(o)
        db.session.commit()
        oid = o.id
    client.post('/login', data={'password': 'testofficer'})
    client.post('/officer/select', data={'officer_id': oid})
    r = client.get('/admin/dashboard', follow_redirects=False)
    assert r.status_code == 302
