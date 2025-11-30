"""
Test OpenAI Function Calling with LM Studio
Verifies that the AI can properly call tools
"""
import requests
import json

def test_tool_calling():
    """Test that LM Studio can handle function calling"""
    
    url = "http://localhost:8009/chat/test_user/stream"
    
    test_cases = [
        {
            "name": "Simple Greeting (No Tools Expected)",
            "message": "hi",
            "expect_tools": False
        },
        {
            "name": "Gene Question (Should Call analyze_gene)",
            "message": "What is the MLH1 gene and why is it important?",
            "expect_tools": True,
            "expected_tool": "analyze_gene"
        },
        {
            "name": "Shoulder Anatomy (Should Call analyze_organ)",
            "message": "What anatomical structures are in the shoulder?",
            "expect_tools": True,
            "expected_tool": "analyze_organ"
        }
    ]
    
    for test in test_cases:
        print("\n" + "="*70)
        print(f"TEST: {test['name']}")
        print("="*70)
        print(f"Query: {test['message']}")
        print("-"*70)
        
        try:
            response = requests.post(
                url,
                json={"message": test['message']},
                stream=True,
                timeout=60
            )
            
            tools_called = []
            final_result = None
            
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    
                    if decoded.startswith('data: '):
                        try:
                            data = json.loads(decoded[6:])
                            
                            if data.get('status') == 'tool_executing':
                                tool_name = data.get('data', {}).get('tool')
                                if tool_name:
                                    tools_called.append(tool_name)
                                print(f"  ✅ Tool Called: {tool_name}")
                                print(f"     Message: {data.get('message')}")
                            
                            elif data.get('status') == 'done':
                                final_result = data.get('result', {})
                                break
                                
                        except json.JSONDecodeError:
                            pass
            
            # Verify results
            print("\n" + "-"*70)
            print("RESULTS:")
            print(f"  Tools Called: {tools_called if tools_called else 'None'}")
            print(f"  Expected Tools: {test['expect_tools']}")
            
            if test['expect_tools']:
                if tools_called:
                    print(f"  ✅ PASS - Tools were called as expected")
                    if test.get('expected_tool') in tools_called:
                        print(f"  ✅ Correct tool used: {test['expected_tool']}")
                else:
                    print(f"  ❌ FAIL - No tools called (expected {test.get('expected_tool')})")
            else:
                if not tools_called:
                    print(f"  ✅ PASS - No tools called (as expected for greeting)")
                else:
                    print(f"  ⚠️ WARNING - Tools called unnecessarily: {tools_called}")
            
            if final_result:
                response_preview = final_result.get('response', '')[:200]
                print(f"\n  Response Preview: {response_preview}...")
                print(f"  Iterations Used: {final_result.get('iterations_used', 0)}")
                print(f"  Confidence: {final_result.get('confidence_level', 'unknown')}")
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)

if __name__ == "__main__":
    print("Testing OpenAI Function Calling Implementation")
    print("Ensure LM Studio is running with DNA Expert model on port 1234")
    print()
    test_tool_calling()


