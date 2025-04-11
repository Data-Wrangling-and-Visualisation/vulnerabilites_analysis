from backend import db

class Vulnerability(db.Model):
    """Модель для работы с уязвимостями"""
    __tablename__ = 'vulnerabilities'

    cve_id = db.Column(db.String(20), primary_key=True)
    published_date = db.Column(db.DateTime)
    last_modified_date = db.Column(db.DateTime)
    vuln_status = db.Column(db.String(50))
    description = db.Column(db.Text)
    cvss_v2_base_score = db.Column(db.Float)
    cvss_v2_access_vector = db.Column(db.String(50))
    cvss_v2_access_complexity = db.Column(db.String(50))
    cvss_v2_authentication = db.Column(db.String(50))
    cvss_v2_confidentiality_impact = db.Column(db.String(50))
    cvss_v2_integrity_impact = db.Column(db.String(50))
    cvss_v2_availability_impact = db.Column(db.String(50))
    cvss_v2_severity = db.Column(db.String(50))
    cvss_v2_exploitability_score = db.Column(db.Float)
    cvss_v2_impact_score = db.Column(db.Float)
    cvss_v3_base_score = db.Column(db.Float)
    cvss_v3_severity = db.Column(db.String(50))
    cvss_v3_vector = db.Column(db.String(100))
    cvss_v3_attack_vector = db.Column(db.String(50))
    cvss_v3_attack_complexity = db.Column(db.String(50))
    cvss_v3_privileges_required = db.Column(db.String(50))
    cvss_v3_user_interaction = db.Column(db.String(50))
    cvss_v3_scope = db.Column(db.String(50))
    cvss_v3_confidentiality_impact = db.Column(db.String(50))
    cvss_v3_integrity_impact = db.Column(db.String(50))
    cvss_v3_availability_impact = db.Column(db.String(50))
    cvss_v3_exploitability_score = db.Column(db.Float)
    cvss_v3_impact_score = db.Column(db.Float)
    cwe_str = db.Column(db.Text)
    references_str = db.Column(db.Text)

    def to_dict(self):
        """Преобразование объекта в словарь"""
        return {
            'cve_id': self.cve_id,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'last_modified_date': self.last_modified_date.isoformat() if self.last_modified_date else None,
            'vuln_status': self.vuln_status,
            'description': self.description,
            'cvss_v2': {
                'base_score': self.cvss_v2_base_score,
                'severity': self.cvss_v2_severity,
                'access_vector': self.cvss_v2_access_vector,
                'access_complexity': self.cvss_v2_access_complexity,
                'authentication': self.cvss_v2_authentication,
                'confidentiality_impact': self.cvss_v2_confidentiality_impact,
                'integrity_impact': self.cvss_v2_integrity_impact,
                'availability_impact': self.cvss_v2_availability_impact,
                'exploitability_score': self.cvss_v2_exploitability_score,
                'impact_score': self.cvss_v2_impact_score
            },
            'cvss_v3': {
                'base_score': self.cvss_v3_base_score,
                'severity': self.cvss_v3_severity,
                'vector': self.cvss_v3_vector,
                'attack_vector': self.cvss_v3_attack_vector,
                'attack_complexity': self.cvss_v3_attack_complexity,
                'privileges_required': self.cvss_v3_privileges_required,
                'user_interaction': self.cvss_v3_user_interaction,
                'scope': self.cvss_v3_scope,
                'confidentiality_impact': self.cvss_v3_confidentiality_impact,
                'integrity_impact': self.cvss_v3_integrity_impact,
                'availability_impact': self.cvss_v3_availability_impact,
                'exploitability_score': self.cvss_v3_exploitability_score,
                'impact_score': self.cvss_v3_impact_score
            },
            'cwe': self.cwe_str,
            'references': self.references_str
        }