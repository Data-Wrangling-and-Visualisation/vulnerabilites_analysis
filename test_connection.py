import psycopg2; conn = psycopg2.connect('postgresql://nvd_user:secure_password123@localhost/nvd_cve'); print('✅ Connection successful!'); conn.close()
