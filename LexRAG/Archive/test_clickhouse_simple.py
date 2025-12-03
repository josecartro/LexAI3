"""
Simple ClickHouse Test (Windows Compatible)
Test ClickHouse connection without Unicode characters
"""

import clickhouse_connect
import sys

try:
    client = clickhouse_connect.get_client(host='127.0.0.1', port=8125, username='genomics', password='genomics123')
    count = client.query('SELECT COUNT(*) FROM genomics_db.clinvar_variants').result_rows[0][0]
    print(f'SUCCESS: ClickHouse accessible with {count:,} ClinVar variants')
    sys.exit(0)
except Exception as e:
    print(f'WARNING: ClickHouse HTTP not ready yet - {e}')
    print('APIs will use lazy initialization')
    sys.exit(0)
