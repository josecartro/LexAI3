"""
Test SSE streaming endpoint
"""
import requests
import json

url = "http://localhost:8009/chat/test_user/stream"
data = {
    "message": "hi",
    "conversation_id": ""
}

print(f"Testing streaming endpoint: {url}")
print(f"Sending message: {data['message']}")
print("-" * 60)

try:
    response = requests.post(
        url, 
        json=data, 
        stream=True,
        timeout=30
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print("-" * 60)
    print("Streaming updates:")
    print("-" * 60)
    
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            print(f"Raw: {decoded_line}")
            
            if decoded_line.startswith('data: '):
                try:
                    data = json.loads(decoded_line[6:])
                    print(f"  ✅ Parsed: {data.get('status')} - {data.get('message', '')}")
                    
                    if data.get('status') == 'done':
                        print(f"  🎉 Complete! Result: {data.get('result', {}).get('response', '')[:100]}")
                        break
                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON error: {e}")
            print()
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()


