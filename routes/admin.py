# routes/admin.py
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash)
from models import Officer, EvaluationCycle, Score
from app import db
from scoring import compute_score, score_hex
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    officers = Officer.query.filter_by(active=True).all()
    cycles = EvaluationCycle.query.order_by(
        EvaluationCycle.created_at.desc()).all()
    latest_cycle = cycles[0] if cycles else None

    latest_scores = []
    chapter_avg = None
    dim_avgs = {'creativity': 0.0, 'execution': 0.0, 'communication': 0.0}
    distribution = {'40-59': 0, '60-69': 0, '70-79': 0, '80-89': 0, '90+': 0}

    if latest_cycle:
        scores = Score.query.filter_by(cycle_id=latest_cycle.id).all()
        score_map = {s.officer_id: s for s in scores}
        for officer in officers:
            s = score_map.get(officer.id)
            latest_scores.append({
                'officer': officer,
                'score': s,
                'color': score_hex(s.weighted_total) if s else '#888',
            })
        if scores:
            chapter_avg = round(
                sum(s.weighted_total for s in scores) / len(scores), 1)
            dim_avgs['creativity'] = round(
                sum(s.creativity_avg for s in scores) / len(scores), 1)
            dim_avgs['execution'] = round(
                sum(s.execution_avg for s in scores) / len(scores), 1)
            dim_avgs['communication'] = round(
                sum(s.communication_avg for s in scores) / len(scores), 1)
            for s in scores:
                t = s.weighted_total
                if t < 60:
                    distribution['40-59'] += 1
                elif t < 70:
                    distribution['60-69'] += 1
                elif t < 80:
                    distribution['70-79'] += 1
                elif t < 90:
                    distribution['80-89'] += 1
                else:
                    distribution['90+'] += 1
    else:
        latest_scores = [
            {'officer': o, 'score': None, 'color': '#888'} for o in officers
        ]

    return render_template('admin/dashboard.html',
                           latest_scores=latest_scores,
                           chapter_avg=chapter_avg,
                           cycles_count=len(cycles),
                           officers_count=len(officers),
                           dim_avgs=dim_avgs,
                           distribution=distribution,
                           latest_cycle=latest_cycle)


@admin_bp.route('/officers')
@admin_required
def officers():
    all_officers = Officer.query.order_by(Officer.name).all()
    return render_template('admin/officers.html', officers=all_officers)


@admin_bp.route('/officers/add', methods=['POST'])
@admin_required
def add_officer():
    name = request.form.get('name', '').strip()
    position = request.form.get('position', '').strip()
    if not name or not position:
        flash('Name and position are required.', 'error')
        return redirect(url_for('admin.officers'))
    db.session.add(Officer(name=name, position=position))
    db.session.commit()
    flash(f'{name} added successfully.', 'success')
    return redirect(url_for('admin.officers'))


@admin_bp.route('/officers/<int:officer_id>/edit', methods=['POST'])
@admin_required
def edit_officer(officer_id):
    officer = Officer.query.get_or_404(officer_id)
    officer.name = request.form.get('name', officer.name).strip()
    officer.position = request.form.get('position', officer.position).strip()
    db.session.commit()
    flash('Officer updated.', 'success')
    return redirect(url_for('admin.officers'))


@admin_bp.route('/officers/<int:officer_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_officer(officer_id):
    officer = Officer.query.get_or_404(officer_id)
    officer.active = False
    db.session.commit()
    flash(f'{officer.name} deactivated.', 'success')
    return redirect(url_for('admin.officers'))


@admin_bp.route('/officers/<int:officer_id>/activate', methods=['POST'])
@admin_required
def activate_officer(officer_id):
    officer = Officer.query.get_or_404(officer_id)
    officer.active = True
    db.session.commit()
    flash(f'{officer.name} reactivated.', 'success')
    return redirect(url_for('admin.officers'))


@admin_bp.route('/evaluate', methods=['GET'])
@admin_required
def evaluate():
    officers = Officer.query.filter_by(active=True).order_by(Officer.name).all()
    return render_template('admin/evaluate.html', officers=officers)


@admin_bp.route('/evaluate', methods=['POST'])
@admin_required
def submit_evaluation():
    cycle_name = request.form.get('cycle_name', '').strip()
    cycle_notes = request.form.get('cycle_notes', '').strip()
    if not cycle_name:
        flash('Evaluation cycle name is required.', 'error')
        return redirect(url_for('admin.evaluate'))

    cycle = EvaluationCycle(name=cycle_name, notes=cycle_notes)
    db.session.add(cycle)
    db.session.flush()

    for officer in Officer.query.filter_by(active=True).all():
        p = f'officer_{officer.id}_'

        def g(key, default=5):
            try:
                return max(1, min(10, int(request.form.get(p + key, default))))
            except (ValueError, TypeError):
                return default

        c = [g('creativity_ideas'), g('creativity_initiatives'),
             g('creativity_content'), g('creativity_innovation'),
             g('creativity_variety')]
        e = [g('execution_timeliness'), g('execution_events'),
             g('execution_attendance'), g('execution_budget'),
             g('execution_followthrough')]
        m = [g('communication_meetings'), g('communication_responsiveness'),
             g('communication_updates'), g('communication_clarity'),
             g('communication_collaboration')]

        c_avg, e_avg, m_avg, total = compute_score(c, e, m)

        db.session.add(Score(
            officer_id=officer.id, cycle_id=cycle.id,
            creativity_ideas=c[0], creativity_initiatives=c[1],
            creativity_content=c[2], creativity_innovation=c[3],
            creativity_variety=c[4],
            execution_timeliness=e[0], execution_events=e[1],
            execution_attendance=e[2], execution_budget=e[3],
            execution_followthrough=e[4],
            communication_meetings=m[0], communication_responsiveness=m[1],
            communication_updates=m[2], communication_clarity=m[3],
            communication_collaboration=m[4],
            creativity_avg=c_avg, execution_avg=e_avg,
            communication_avg=m_avg, weighted_total=total,
            officer_notes=request.form.get(p + 'notes', ''),
        ))

    db.session.commit()
    flash(f'Evaluation "{cycle_name}" submitted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/history')
@admin_required
def history():
    cycles = EvaluationCycle.query.order_by(
        EvaluationCycle.created_at.desc()).all()
    cycle_data = []
    for cycle in cycles:
        scores = Score.query.filter_by(cycle_id=cycle.id).all()
        avg = (round(sum(s.weighted_total for s in scores) / len(scores), 1)
               if scores else None)
        cycle_data.append({'cycle': cycle, 'count': len(scores), 'avg': avg})
    return render_template('admin/history.html', cycle_data=cycle_data)


@admin_bp.route('/history/<int:cycle_id>')
@admin_required
def history_detail(cycle_id):
    cycle = EvaluationCycle.query.get_or_404(cycle_id)
    scores = (Score.query
              .filter_by(cycle_id=cycle_id)
              .join(Officer)
              .order_by(Score.weighted_total.desc())
              .all())
    chapter_avg = (round(sum(s.weighted_total for s in scores) / len(scores), 1)
                   if scores else None)
    return render_template('admin/history_detail.html',
                           cycle=cycle, scores=scores,
                           chapter_avg=chapter_avg, score_hex=score_hex)
