"""
Simple single test - watch LM Studio logs
"""
import requests
import json

print("="*70)
print("SIMPLE TEST - Watch LM Studio logs for this request")
print("="*70)
print()

tools = [{
    "type": "function",
    "function": {
        "name": "analyze_gene",
        "description": "Get information about a gene from the genomic database",
        "parameters": {
            "type": "object",
            "properties": {
                "gene_symbol": {
                    "type": "string",
                    "description": "Gene symbol like BRCA1 or MLH1"
                }
            },
            "required": ["gene_symbol"]
        }
    }
}]

request = {
    "model": "dna-models",
    "messages": [
        {"role": "user", "content": "What is the MLH1 gene?"}
    ],
    "tools": tools,
    "tool_choice": "auto",
    "temperature": 0.7,
    "max_tokens": 500
}

print("REQUEST:")
print(json.dumps(request, indent=2))
print()
print("-"*70)
print("Sending request to LM Studio...")
print("-"*70)
print()

response = requests.post(
    "http://localhost:1234/v1/chat/completions",
    json=request,
    timeout=30
)

print("RESPONSE:")
print(f"Status Code: {response.status_code}")
print()

if response.status_code == 200:
    result = response.json()
    
    print("Full Response:")
    print(json.dumps(result, indent=2))
    print()
    print("="*70)
    print("MESSAGE ANALYSIS:")
    print("="*70)
    
    msg = result["choices"][0]["message"]
    print(f"Role: {msg.get('role')}")
    print(f"Content: '{msg.get('content', 'EMPTY')}'")
    print(f"Tool Calls: {msg.get('tool_calls', 'NONE')}")
    print(f"Finish Reason: {result['choices'][0].get('finish_reason')}")
else:
    print(f"Error: {response.text}")

print()
print("="*70)
print("CHECK LM STUDIO LOGS NOW - Copy and paste them")
print("="*70)



