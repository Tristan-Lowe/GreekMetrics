# models.py
from datetime import datetime
from app import db


class Officer(db.Model):
    __tablename__ = 'officers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    position = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='officer', lazy=True,
                              cascade='all, delete-orphan')


class EvaluationCycle(db.Model):
    __tablename__ = 'evaluation_cycles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='cycle', lazy=True,
                              cascade='all, delete-orphan')


class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('officers.id'), nullable=False)
    cycle_id = db.Column(db.Integer, db.ForeignKey('evaluation_cycles.id'), nullable=False)

    # Creativity (33%)
    creativity_ideas        = db.Column(db.Integer, nullable=False)
    creativity_initiatives  = db.Column(db.Integer, nullable=False)
    creativity_content      = db.Column(db.Integer, nullable=False)
    creativity_innovation   = db.Column(db.Integer, nullable=False)
    creativity_variety      = db.Column(db.Integer, nullable=False)

    # Execution (34%)
    execution_timeliness    = db.Column(db.Integer, nullable=False)
    execution_events        = db.Column(db.Integer, nullable=False)
    execution_attendance    = db.Column(db.Integer, nullable=False)
    execution_budget        = db.Column(db.Integer, nullable=False)
    execution_followthrough = db.Column(db.Integer, nullable=False)

    # Communication (33%)
    communication_meetings       = db.Column(db.Integer, nullable=False)
    communication_responsiveness = db.Column(db.Integer, nullable=False)
    communication_updates        = db.Column(db.Integer, nullable=False)
    communication_clarity        = db.Column(db.Integer, nullable=False)
    communication_collaboration  = db.Column(db.Integer, nullable=False)

    # Computed
    creativity_avg    = db.Column(db.Float, nullable=False)
    execution_avg     = db.Column(db.Float, nullable=False)
    communication_avg = db.Column(db.Float, nullable=False)
    weighted_total    = db.Column(db.Float, nullable=False)

    officer_notes = db.Column(db.Text, default='')
