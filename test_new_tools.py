"""
Test the 3 new high-value tools
"""
import requests
import json

print("="*70)
print("TESTING 3 NEW HIGH-VALUE TOOLS")
print("="*70)

base_url = "http://localhost:8009"

# Test 1: analyze_splice_impact
print("\n" + "="*70)
print("TEST 1: analyze_splice_impact")
print("="*70)

test_message = "Analyze the splice impact of BRCA1 gene and show which tissues are most affected"

try:
    response = requests.post(
        f"{base_url}/chat/test_user/stream",
        json={"message": test_message},
        stream=True,
        timeout=60
    )
    
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith('data: '):
                try:
                    data = json.loads(decoded[6:])
                    status = data.get('status')
                    message = data.get('message', '')
                    
                    if status == 'tool_executing':
                        print(f"  🔧 {message}")
                    elif status == 'tool_complete':
                        print(f"  ✅ {message}")
                    elif status == 'done':
                        result = data.get('result', {})
                        tools = result.get('tools_executed', [])
                        print(f"\n✅ Tools executed: {tools}")
                        response_text = result.get('response', '')[:300]
                        print(f"📝 Response preview: {response_text}...")
                        break
                except:
                    pass
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: phenotype_to_differential
print("\n" + "="*70)
print("TEST 2: phenotype_to_differential")
print("="*70)

test_message = "I have a patient with seizures, hypotonia, and developmental delay. What syndromes should I consider?"

try:
    response = requests.post(
        f"{base_url}/chat/test_user/stream",
        json={"message": test_message},
        stream=True,
        timeout=60
    )
    
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith('data: '):
                try:
                    data = json.loads(decoded[6:])
                    status = data.get('status')
                    message = data.get('message', '')
                    
                    if status == 'tool_executing':
                        print(f"  🔧 {message}")
                    elif status == 'tool_complete':
                        print(f"  ✅ {message}")
                    elif status == 'done':
                        result = data.get('result', {})
                        tools = result.get('tools_executed', [])
                        print(f"\n✅ Tools executed: {tools}")
                        response_text = result.get('response', '')[:300]
                        print(f"📝 Response preview: {response_text}...")
                        break
                except:
                    pass
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Simple tool count verification
print("\n" + "="*70)
print("TEST 3: Verify 16 tools are registered")
print("="*70)

try:
    # Import tool definitions to count
    import sys
    sys.path.insert(0, 'd:/LexAI3/LexRAG/LexAPI_AIGateway')
    from code.tool_definitions import LEXRAG_TOOLS, get_human_readable_tool_name
    
    print(f"✅ Total tools registered: {len(LEXRAG_TOOLS)}")
    print("\nTool list:")
    for i, tool in enumerate(LEXRAG_TOOLS, 1):
        name = tool['function']['name']
        readable = get_human_readable_tool_name(name)
        print(f"  {i:2}. {name:30} → {readable}")
        
except Exception as e:
    print(f"❌ Error importing tools: {e}")

print("\n" + "="*70)
print("TESTS COMPLETE")
print("="*70)

