from flask import jsonify, request
from .data_fetcher import NVDDataFetcher
import psycopg2
from config import DB_PARAMS

from backend.models.vulnerabilities import Vulnerability
from backend.api import api_blueprint

@api_blueprint.route('/vulnerabilities')
def get_vulnerabilities():
    """Получение списка уязвимостей с возможностью фильтрации"""
    try:
        severity = request.args.get('severity')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        query = Vulnerability.query
        if severity:
            query = query.filter(
                (Vulnerability.cvss_v3_severity == severity) | 
                (Vulnerability.cvss_v2_severity == severity)
            )
            
        vulnerabilities = query.order_by(Vulnerability.published_date.desc()) \
                             .limit(limit).offset(offset).all()
        
        return jsonify({
            'count': query.count(),
            'vulnerabilities': [vuln.to_dict() for vuln in vulnerabilities]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/update', methods=['POST'])
def update_data():
    """Ручка для обновления данных"""
    try:
        fetcher = NVDDataFetcher()
        count = fetcher.update_database()
        return jsonify({
            'status': 'success',
            'count': count,
            'message': f'Added {count} new vulnerabilities'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/stats')
def get_stats():
    """Получение статистики по уязвимостям"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # Статистика по severity
                cur.execute("""
                    SELECT 
                        COALESCE(cvss_v3_severity, cvss_v2_severity) as severity,
                        COUNT(*) as count
                    FROM vulnerabilities
                    GROUP BY severity
                    ORDER BY count DESC;
                """)
                severity_stats = [{'severity': row[0], 'count': row[1]} for row in cur.fetchall()]
                
                # Последнее обновление
                cur.execute("SELECT MAX(last_modified_date) FROM vulnerabilities;")
                last_update = cur.fetchone()[0]
                
                # Общее количество
                cur.execute("SELECT COUNT(*) FROM vulnerabilities;")
                total_count = cur.fetchone()[0]
                
        return jsonify({
            'severity_stats': severity_stats,
            'last_update': last_update.isoformat() if last_update else None,
            'total_count': total_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
from flask import jsonify
from backend.models.vulnerabilities import Vulnerability
from . import api_blueprint
from .. import db
from sqlalchemy import func

@api_blueprint.route('/trend')
def trend_data():
    # Группируем по дате публикации
    rows = (
        db.session.query(
            func.date(Vulnerability.published_date).label('date'),
            func.count().label('count')
        )
        .group_by(func.date(Vulnerability.published_date))
        .order_by(func.date(Vulnerability.published_date))
        .all()
    )
    return jsonify([{'date': str(r.date), 'count': r.count} for r in rows])

@api_blueprint.route('/cwe')
def cwe_data():
    # Простая агрегация по CWE (строка cwe_str — через запятую)
    counts = {}
    for (cwe_str,) in db.session.query(Vulnerability.cwe_str).all():
        for c in (cwe_str or "").split(', '):
            if c:
                counts[c] = counts.get(c, 0) + 1
    # Топ‑10
    top10 = sorted(counts.items(), key=lambda x: -x[1])[:10]
    return jsonify([{'cwe': c, 'count': n} for c, n in top10])
