# tests/test_admin.py
import pytest
from models import Officer, EvaluationCycle, Score
from scoring import compute_score


def test_dashboard_loads(admin_client, db, app):
    with app.app_context():
        r = admin_client.get('/admin/dashboard')
        assert r.status_code == 200
        assert b'GreekMetrics' in r.data


def test_officers_page_loads(admin_client):
    r = admin_client.get('/admin/officers')
    assert r.status_code == 200


def test_add_officer(admin_client, db, app):
    r = admin_client.post('/admin/officers/add',
                          data={'name': 'Jake Martinez', 'position': 'Social Chair'},
                          follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        officer = Officer.query.filter_by(name='Jake Martinez').first()
        assert officer is not None
        assert officer.position == 'Social Chair'
        assert officer.active is True


def test_add_officer_missing_fields(admin_client):
    r = admin_client.post('/admin/officers/add',
                          data={'name': '', 'position': ''},
                          follow_redirects=True)
    assert b'required' in r.data.lower()


def test_deactivate_officer(admin_client, db, app):
    with app.app_context():
        o = Officer(name='To Deactivate', position='Treasurer')
        db.session.add(o)
        db.session.commit()
        oid = o.id
    admin_client.post(f'/admin/officers/{oid}/deactivate', follow_redirects=True)
    with app.app_context():
        assert Officer.query.get(oid).active is False


def test_evaluate_page_loads(admin_client, db, app):
    with app.app_context():
        o = Officer(name='Eval Officer', position='PR')
        db.session.add(o)
        db.session.commit()
    r = admin_client.get('/admin/evaluate')
    assert r.status_code == 200
    assert b'Eval Officer' in r.data


def test_submit_evaluation(admin_client, db, app):
    with app.app_context():
        o = Officer(name='Score Me', position='Events')
        db.session.add(o)
        db.session.commit()
        oid = o.id

    form_data = {'cycle_name': 'Test Cycle', 'cycle_notes': 'Notes here'}
    for key in [
        'creativity_ideas', 'creativity_initiatives', 'creativity_content',
        'creativity_innovation', 'creativity_variety',
        'execution_timeliness', 'execution_events', 'execution_attendance',
        'execution_budget', 'execution_followthrough',
        'communication_meetings', 'communication_responsiveness',
        'communication_updates', 'communication_clarity', 'communication_collaboration',
    ]:
        form_data[f'officer_{oid}_{key}'] = '7'
    form_data[f'officer_{oid}_notes'] = 'Good job'

    r = admin_client.post('/admin/evaluate', data=form_data, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        score = Score.query.filter_by(officer_id=oid).first()
        assert score is not None
        assert score.weighted_total == 70.0
        assert score.creativity_avg == 7.0


def test_history_page_loads(admin_client):
    r = admin_client.get('/admin/history')
    assert r.status_code == 200
