# routes/officer.py
from flask import (Blueprint, render_template, request,
                   session, redirect, url_for)
from models import Officer, Score, EvaluationCycle
from scoring import score_hex
from routes.auth import officer_required

officer_bp = Blueprint('officer', __name__)


@officer_bp.route('/select', methods=['GET', 'POST'])
def select():
    if session.get('role') not in ('admin', 'officer'):
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        officer_id = request.form.get('officer_id')
        officer = Officer.query.get_or_404(int(officer_id))
        session['officer_id'] = officer.id
        session['officer_name'] = officer.name
        return redirect(url_for('officer.dashboard'))
    officers = Officer.query.filter_by(active=True).order_by(Officer.name).all()
    return render_template('officer/select.html', officers=officers)


@officer_bp.route('/dashboard')
@officer_required
def dashboard():
    officer = Officer.query.get_or_404(session['officer_id'])
    scores = (Score.query
              .filter_by(officer_id=officer.id)
              .join(EvaluationCycle)
              .order_by(EvaluationCycle.created_at.desc())
              .all())
    latest = scores[0] if scores else None
    rank = None
    total_officers = 0
    if latest:
        all_cycle_scores = (Score.query
                            .filter_by(cycle_id=latest.cycle_id)
                            .order_by(Score.weighted_total.desc())
                            .all())
        total_officers = len(all_cycle_scores)
        rank = next((i + 1 for i, s in enumerate(all_cycle_scores)
                     if s.officer_id == officer.id), None)
    history = [(s.cycle.name, s.weighted_total) for s in reversed(scores)]
    return render_template('officer/dashboard.html',
                           officer=officer, latest=latest,
                           rank=rank, total_officers=total_officers,
                           history=history, score_hex=score_hex)
