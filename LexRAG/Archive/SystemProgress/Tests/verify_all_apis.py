import requests

print("VERIFYING ALL LEXRAG APIS BEFORE BENCHMARK")
print("="*60)

apis = [
    ("LexAPI_Genomics", 8001, "Axes 2,3,4,6"),
    ("LexAPI_Anatomics", 8002, "Axis 1"),
    ("LexAPI_Literature", 8003, "Cross-Axis"),
    ("LexAPI_Metabolics", 8005, "Axis 5"),
    ("LexAPI_Populomics", 8006, "Axis 7")
]

working = 0
for name, port, axes in apis:
    try:
        r = requests.get(f"http://localhost:{port}/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            service = data.get('service', 'unknown')
            print(f"[OK] {name} (Port {port}) - {axes}")
            print(f"     Service: {service}")
            working += 1
        else:
            print(f"[ERROR] {name} (Port {port}): HTTP {r.status_code}")
    except:
        print(f"[OFFLINE] {name} (Port {port}): Not responding")

print(f"\nRESULT: {working}/5 APIs operational")
if working == 5:
    print("READY: All APIs running - proceed with test-set.md benchmark")
else:
    print("NOT READY: Start missing APIs before benchmark")
