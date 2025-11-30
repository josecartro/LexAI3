"""
Test LM Studio Structured Output
Use structured output to get proper responses from DNA Expert model
"""

import requests
import json

def test_structured_output():
    """Test structured output with DNA Expert model"""
    
    print("TESTING STRUCTURED OUTPUT WITH DNA EXPERT")
    print("="*50)
    print("Using LM Studio structured output format")
    print("Based on: https://lmstudio.ai/docs/developer/openai-compat/structured-output")
    
    # Define response schema
    response_schema = {
        "type": "object",
        "properties": {
            "response": {
                "type": "string",
                "description": "The main response to the user's question"
            },
            "confidence": {
                "type": "string", 
                "enum": ["high", "medium", "low"],
                "description": "Confidence level of the response"
            },
            "genomics_topic": {
                "type": "boolean",
                "description": "Whether this is related to genomics/genetics"
            },
            "follow_up_suggestions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Suggested follow-up questions"
            }
        },
        "required": ["response", "confidence", "genomics_topic"]
    }
    
    test_cases = [
        {
            "prompt": "Hi",
            "description": "Simple greeting test"
        },
        {
            "prompt": "What is BRCA1?",
            "description": "Genomics question test"
        },
        {
            "prompt": "How are you doing?",
            "description": "Conversation test"
        }
    ]
    
    working_responses = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\\n{i}. {test['description']}")
        print(f"   Prompt: \"{test['prompt']}\"")
        
        try:
            # Use structured output format
            request_data = {
                "model": "dna-models",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful DNA expert assistant. Always respond in the requested JSON format."
                    },
                    {
                        "role": "user", 
                        "content": test['prompt']
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.7,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "dna_expert_response",
                        "schema": response_schema
                    }
                }
            }
            
            response = requests.post(
                'http://127.0.0.1:1234/v1/chat/completions',
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    tokens = data.get('usage', {}).get('completion_tokens', 0)
                    
                    print(f"   Status: SUCCESS ({tokens} tokens)")
                    print(f"   Raw content: {content[:100]}...")
                    
                    # Try to parse JSON response
                    try:
                        parsed_response = json.loads(content)
                        print(f"   ✅ Structured response:")
                        print(f"      Response: \"{parsed_response.get('response', 'No response')[:60]}...\"")
                        print(f"      Confidence: {parsed_response.get('confidence', 'unknown')}")
                        print(f"      Genomics topic: {parsed_response.get('genomics_topic', False)}")
                        
                        working_responses += 1
                        
                    except json.JSONDecodeError:
                        print(f"   ❌ Invalid JSON response")
                else:
                    print(f"   ❌ No choices in response")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\\n{'='*50}")
    print("STRUCTURED OUTPUT TEST RESULTS")
    print(f"{'='*50}")
    print(f"Working responses: {working_responses}/{len(test_cases)}")
    
    if working_responses > 0:
        print("\\n✅ SUCCESS: Structured output works!")
        print("Can use this format for reliable responses")
        print("Frontend should use structured output format")
    else:
        print("\\n❌ FAILED: Structured output not working")
        print("May need different approach or model configuration")
    
    return working_responses > 0

if __name__ == "__main__":
    success = test_structured_output()
    
    if success:
        print("\\nRECOMMENDATION: Use structured output in frontend")
    else:
        print("\\nRECOMMENDATION: Try different response format")
    
    input("\\nPress Enter to continue...")
