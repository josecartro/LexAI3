"""
Test complex medical question with multiple tool calls
"""
import requests
import json

url = "http://localhost:8009/chat/test_user/stream"

complex_question = """A 48-year-old woman of Chilean origin living in Sweden has:
- recurrent kidney stones from her early 30s
- new hypertension
- episodic headaches and sweating
- mild hypercalcemia
- family history: father died suddenly at 52; paternal aunt had "thyroid surgery" in her 40s
CT now shows bilateral adrenal masses and a thyroid nodule. Plasma metanephrines are elevated. PTH is high.

Question:
What single inherited syndrome explains all of this?
Name the gene(s) and describe the exact DNA-level mechanism (oncogene vs tumor-suppressor, two-hit vs dominant gain-of-function).
Explain why her Chilean ancestry might change which mutation is most likely (founder effects / allele frequencies).
Connect each tumor to its embryologic tissue origin and anatomy."""

print("="*80)
print("TESTING COMPLEX QUESTION WITH MULTIPLE TOOL CALLS")
print("="*80)
print(f"\nQuestion: {complex_question[:150]}...")
print("\n" + "-"*80)
print("Sending to AIGateway streaming endpoint...")
print("-"*80)
print()

try:
    response = requests.post(
        url,
        json={"message": complex_question},
        stream=True,
        timeout=120
    )
    
    tools_called = []
    progress_updates = []
    final_result = None
    
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            
            if decoded.startswith('data: '):
                try:
                    data = json.loads(decoded[6:])
                    status = data.get('status')
                    message = data.get('message', '')
                    
                    if status == 'tool_executing':
                        tool = data.get('data', {}).get('tool', 'unknown')
                        tools_called.append(tool)
                        print(f"  🔧 {message}")
                    
                    elif status == 'tool_complete':
                        print(f"  ✅ {message}")
                    
                    elif status in ['thinking', 'querying_model', 'finalizing']:
                        progress_updates.append(message)
                        if len(progress_updates) % 3 == 0:
                            print(f"  💭 {message}")
                    
                    elif status == 'done':
                        final_result = data.get('result', {})
                        break
                        
                except json.JSONDecodeError:
                    pass
    
    print("\n" + "="*80)
    print("RESULTS:")
    print("="*80)
    
    if final_result:
        response_text = final_result.get('response', '')
        tools_executed = final_result.get('tools_executed', [])
        iterations = final_result.get('iterations_used', 0)
        
        print(f"\n✅ Tools Executed: {len(tools_executed)}")
        for tool in tools_executed:
            print(f"   - {tool}")
        
        print(f"\n✅ Iterations Used: {iterations}")
        print(f"\n✅ Response Length: {len(response_text)} characters")
        
        if response_text:
            print(f"\n📝 Response Preview (first 500 chars):")
            print("-"*80)
            print(response_text[:500])
            if len(response_text) > 500:
                print("...")
                print(f"\n... (total {len(response_text)} characters)")
            
            print("\n" + "="*80)
            print("✅ SUCCESS - Model synthesized comprehensive response!")
            print("="*80)
        else:
            print("\n❌ FAIL - Empty response despite tool execution")
            print("="*80)
    else:
        print("\n❌ FAIL - No result received")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

