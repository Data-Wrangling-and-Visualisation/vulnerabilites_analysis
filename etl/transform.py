from datetime import datetime

def transform(raw_data):
    """Трансформация сырых данных"""
    processed = []
    for item in raw_data:
        cve = item.get('cve', {})
        processed.append({
            'cve_id': cve.get('id'),
            'published_date': datetime.strptime(cve.get('published'), '%Y-%m-%dT%H:%M:%S.%f'),
            'last_modified_date': datetime.strptime(cve.get('lastModified'), '%Y-%m-%dT%H:%M:%S.%f'),
            'vuln_status': cve.get('vulnStatus'),
            'description': cve.get('descriptions', [{}])[0].get('value', ''),
            'cvss_v2_base_score': float(cve.get('metrics', {}).get('cvssMetricV2', [{}])[0].get('cvssData', {}).get('baseScore', 0)),
            'cvss_v2_severity': cve.get('metrics', {}).get('cvssMetricV2', [{}])[0].get('baseSeverity', ''),
            'cvss_v3_base_score': float(cve.get('metrics', {}).get('cvssMetricV31', [{}])[0].get('cvssData', {}).get('baseScore', 0)),
            'cvss_v3_severity': cve.get('metrics', {}).get('cvssMetricV31', [{}])[0].get('baseSeverity', ''),
            'cwe_ids': ', '.join([w['description'][0]['value'] for w in cve.get('weaknesses', [])]),
            'references': ', '.join([r['url'] for r in cve.get('references', [])])
        })
    return processed