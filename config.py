DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'nvd_cve',
    'user': 'postgres',
    'password': '5623Daruc&'
}

NVD_API_CONFIG = {
    'base_url': 'https://services.nvd.nist.gov/rest/json/cves/2.0',
    'resultsPerPage': 2000,
    'rate_limit_delay': 6
}