"""
Direct test of LM Studio with OpenAI function calling
"""
import requests
import json

# Simple tool definition
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_gene",
            "description": "Analyze a gene using genomic database",
            "parameters": {
                "type": "object",
                "properties": {
                    "gene_symbol": {
                        "type": "string",
                        "description": "Gene symbol like BRCA1"
                    }
                },
                "required": ["gene_symbol"]
            }
        }
    }
]

test_cases = [
    {
        "name": "Simple Greeting (No Tools)",
        "messages": [{"role": "user", "content": "hi"}],
        "use_tools": False
    },
    {
        "name": "Weather Question (Should Call get_weather)",
        "messages": [{"role": "user", "content": "What's the weather in Stockholm?"}],
        "use_tools": True
    },
    {
        "name": "Gene Question (Should Call analyze_gene)",
        "messages": [{"role": "user", "content": "Tell me about the MLH1 gene"}],
        "use_tools": True
    }
]

print("Testing LM Studio Function Calling")
print("="*70)

for test in test_cases:
    print(f"\nTEST: {test['name']}")
    print("-"*70)
    
    request_body = {
        "messages": test["messages"],
        "temperature": 0.5,
        "max_tokens": 500
    }
    
    if test["use_tools"]:
        request_body["tools"] = tools
        request_body["tool_choice"] = "auto"
    
    print(f"Request with tools: {test['use_tools']}")
    
    try:
        response = requests.post(
            "http://localhost:1234/v1/chat/completions",
            json=request_body,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Show response structure
            choice = result.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            print(f"\nResponse message keys: {list(message.keys())}")
            print(f"Content: {message.get('content', 'None')[:200]}")
            print(f"Tool calls: {message.get('tool_calls', 'None')}")
            
            if message.get('tool_calls'):
                print("\n✅ SUCCESS - Model called tools!")
                for tc in message['tool_calls']:
                    print(f"   Tool: {tc['function']['name']}")
                    print(f"   Args: {tc['function']['arguments']}")
            else:
                if test["use_tools"]:
                    print("\n❌ FAIL - No tool calls (expected tools)")
                else:
                    print("\n✅ SUCCESS - Direct response (no tools needed)")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

print("\n" + "="*70)
print("TEST COMPLETE")


