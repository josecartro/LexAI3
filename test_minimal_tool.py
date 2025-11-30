"""
Minimal test - no system prompt, just user message + tools
"""
import requests
import json

# Minimal tool
tools = [{
    "type": "function",
    "function": {
        "name": "get_gene_info",
        "description": "Get information about a gene",
        "parameters": {
            "type": "object",
            "properties": {
                "gene": {"type": "string", "description": "Gene name"}
            },
            "required": ["gene"]
        }
    }
}]

# Test WITHOUT system prompt
print("TEST 1: No system prompt, just user + tools")
print("-"*70)

response = requests.post(
    "http://localhost:1234/v1/chat/completions",
    json={
        "model": "dna-models",
        "messages": [
            {"role": "user", "content": "Tell me about the BRCA1 gene"}
        ],
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.7,
        "max_tokens": 500
    },
    timeout=30
)

result = response.json()
msg = result["choices"][0]["message"]

print(f"Content: '{msg.get('content', 'NONE')}'")
print(f"Tool calls: {msg.get('tool_calls', 'NONE')}")
print(f"Finish reason: {result['choices'][0].get('finish_reason')}")

print("\n" + "="*70)

# Test WITH simple system prompt
print("TEST 2: With simple system prompt")
print("-"*70)

response2 = requests.post(
    "http://localhost:1234/v1/chat/completions",
    json={
        "model": "dna-models",
        "messages": [
            {"role": "system", "content": "You are a helpful DNA expert. Use available tools when you need data."},
            {"role": "user", "content": "Tell me about the BRCA1 gene"}
        ],
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.7,
        "max_tokens": 500
    },
    timeout=30
)

result2 = response2.json()
msg2 = result2["choices"][0]["message"]

print(f"Content: '{msg2.get('content', 'NONE')}'")
print(f"Tool calls: {msg2.get('tool_calls', 'NONE')}")
print(f"Finish reason: {result2['choices'][0].get('finish_reason')}")

print("\n" + "="*70)

# Test WITHOUT tools at all
print("TEST 3: Same question WITHOUT tools provided")
print("-"*70)

response3 = requests.post(
    "http://localhost:1234/v1/chat/completions",
    json={
        "model": "dna-models",
        "messages": [
            {"role": "user", "content": "Tell me about the BRCA1 gene"}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    },
    timeout=30
)

result3 = response3.json()
msg3 = result3["choices"][0]["message"]

print(f"Content length: {len(msg3.get('content', ''))}")
print(f"Content preview: '{msg3.get('content', 'NONE')[:200]}'")
print(f"Finish reason: {result3['choices'][0].get('finish_reason')}")


