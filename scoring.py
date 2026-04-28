# scoring.py

def compute_score(creativity_scores, execution_scores, communication_scores):
    """Compute weighted officer performance score.
    Each list contains 5 integers (1-10). Returns
    (creativity_avg, execution_avg, communication_avg, weighted_total).
    weighted_total is on a 10-100 scale.
    """
    c_avg = sum(creativity_scores) / 5
    e_avg = sum(execution_scores) / 5
    m_avg = sum(communication_scores) / 5
    weighted = (c_avg * 0.33 + e_avg * 0.34 + m_avg * 0.33) * 10
    return round(c_avg, 2), round(e_avg, 2), round(m_avg, 2), round(weighted, 1)


def score_hex(total):
    """Return hex color string based on weighted_total threshold."""
    if total >= 80:
        return '#4ade80'
    elif total >= 65:
        return '#facc15'
    return '#f87171'
