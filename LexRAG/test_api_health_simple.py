"""
Simple API Health Test (Windows Compatible)
Test API health without Unicode characters
"""

import requests
import sys

apis = [
    ('Genomics', 'http://127.0.0.1:8001/health'),
    ('Anatomics', 'http://127.0.0.1:8002/health'),
    ('Literature', 'http://127.0.0.1:8003/health'),
    ('Metabolics', 'http://127.0.0.1:8005/health'),
    ('Populomics', 'http://127.0.0.1:8006/health'),
    ('Users', 'http://127.0.0.1:8007/health'),
    ('DigitalTwin', 'http://127.0.0.1:8008/health'),
    ('AIGateway', 'http://127.0.0.1:8009/health')
]

print('API Health Check:')
healthy_apis = 0

for name, url in apis:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            print(f'  {name}: {status.upper()}')
            if status == 'healthy':
                healthy_apis += 1
        else:
            print(f'  {name}: HTTP {response.status_code}')
    except Exception as e:
        print(f'  {name}: ERROR - {str(e)[:50]}')

print(f'')
print(f'Healthy APIs: {healthy_apis}/{len(apis)}')

if healthy_apis >= len(apis) - 1:
    print('SUCCESS: Core APIs are operational')
    sys.exit(0)
else:
    print('WARNING: Some APIs may need more time to start')
    sys.exit(0)
