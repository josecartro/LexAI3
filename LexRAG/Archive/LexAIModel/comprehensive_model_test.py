"""
Comprehensive Model Testing Framework
Test DNA Expert model with various configurations to find optimal settings
"""

import requests
import json
import time
import subprocess
import os
import signal
from datetime import datetime

class ModelTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8010"
        self.model_process = None
        self.test_results = []
        
    def start_model_server(self, config):
        """Start model server with specific configuration"""
        
        print(f"Starting model with config: {config['name']}")
        print(f"Command: {config['command']}")
        
        # Kill any existing process
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq *llama*'], 
                          capture_output=True, shell=True)
        except:
            pass
        
        # Wait a moment
        time.sleep(2)
        
        # Start new process
        try:
            self.model_process = subprocess.Popen(
                config['command'].split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            # Wait for model to load
            print(f"Waiting {config['load_time']} seconds for model to load...")
            time.sleep(config['load_time'])
            
            return True
            
        except Exception as e:
            print(f"Failed to start model: {e}")
            return False
    
    def stop_model_server(self):
        """Stop current model server"""
        if self.model_process:
            try:
                self.model_process.terminate()
                time.sleep(2)
            except:
                pass
        
        # Kill any remaining processes
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq *llama*'], 
                          capture_output=True, shell=True)
        except:
            pass
    
    def test_model_response(self, test_case):
        """Test model with specific test case"""
        
        print(f"\\n  Testing: {test_case['name']}")
        print(f"  Prompt: \"{test_case['prompt']}\"")
        
        try:
            # Test chat completions
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": test_case['prompt']}],
                    **test_case['params']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                content = ""
                completion_tokens = 0
                
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    completion_tokens = data.get('usage', {}).get('completion_tokens', 0)
                
                result = {
                    'test_name': test_case['name'],
                    'prompt': test_case['prompt'],
                    'status': 'success',
                    'response_length': len(content),
                    'completion_tokens': completion_tokens,
                    'content': content[:100] + "..." if len(content) > 100 else content,
                    'working': len(content) > 0
                }
                
                print(f"    Status: SUCCESS")
                print(f"    Tokens: {completion_tokens}")
                print(f"    Length: {len(content)} chars")
                print(f"    Response: \"{content[:50]}{'...' if len(content) > 50 else ''}\"")
                
                return result
            else:
                print(f"    Status: FAILED - HTTP {response.status_code}")
                return {
                    'test_name': test_case['name'],
                    'status': 'failed',
                    'error': f"HTTP {response.status_code}",
                    'working': False
                }
                
        except Exception as e:
            print(f"    Status: ERROR - {e}")
            return {
                'test_name': test_case['name'],
                'status': 'error',
                'error': str(e),
                'working': False
            }
    
    def run_comprehensive_tests(self):
        """Run comprehensive model testing with different configurations"""
        
        print("COMPREHENSIVE DNA EXPERT MODEL TESTING")
        print("="*60)
        print("Testing various configurations to find optimal settings")
        print("="*60)
        
        # Test configurations to try
        configs = [
            {
                'name': 'Default (No Chat Format)',
                'command': 'python -m llama_cpp.server --model qwen3-dna-expert.Q4_K_M.gguf --host 0.0.0.0 --port 8010 --n_ctx 2048',
                'load_time': 45
            },
            {
                'name': 'ChatML Format',
                'command': 'python -m llama_cpp.server --model qwen3-dna-expert.Q4_K_M.gguf --host 0.0.0.0 --port 8010 --n_ctx 2048 --chat_format chatml',
                'load_time': 45
            },
            {
                'name': 'Qwen Format',
                'command': 'python -m llama_cpp.server --model qwen3-dna-expert.Q4_K_M.gguf --host 0.0.0.0 --port 8010 --n_ctx 2048 --chat_format qwen',
                'load_time': 45
            }
        ]
        
        # Test cases to try with each configuration
        test_cases = [
            {
                'name': 'Simple Greeting',
                'prompt': 'Hi',
                'params': {'max_tokens': 50, 'temperature': 0.7}
            },
            {
                'name': 'Simple Question',
                'prompt': 'What is 2+2?',
                'params': {'max_tokens': 50, 'temperature': 0.3}
            },
            {
                'name': 'Genetics Question',
                'prompt': 'What is BRCA1?',
                'params': {'max_tokens': 100, 'temperature': 0.5}
            },
            {
                'name': 'No Think Mode',
                'prompt': 'Explain DNA in one sentence. /no_think',
                'params': {'max_tokens': 100, 'temperature': 0.7}
            },
            {
                'name': 'High Temperature',
                'prompt': 'Hello, how are you?',
                'params': {'max_tokens': 100, 'temperature': 1.0, 'top_p': 0.9}
            }
        ]
        
        all_results = []
        
        for config in configs:
            print(f"\\n{'='*60}")
            print(f"TESTING CONFIGURATION: {config['name']}")
            print(f"{'='*60}")
            
            # Start model with this configuration
            if not self.start_model_server(config):
                print("Failed to start model server, skipping...")
                continue
            
            config_results = []
            
            # Test all test cases with this configuration
            for test_case in test_cases:
                result = self.test_model_response(test_case)
                result['config'] = config['name']
                config_results.append(result)
                all_results.append(result)
                
                # Brief pause between tests
                time.sleep(1)
            
            # Stop model server
            self.stop_model_server()
            time.sleep(5)  # Wait before next config
        
        # Generate comprehensive report
        self.generate_test_report(all_results)
        return all_results
    
    def generate_test_report(self, results):
        """Generate comprehensive test report"""
        
        print(f"\\n{'='*80}")
        print("COMPREHENSIVE TEST REPORT")
        print(f"{'='*80}")
        print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Group results by configuration
        configs = {}
        for result in results:
            config_name = result.get('config', 'Unknown')
            if config_name not in configs:
                configs[config_name] = []
            configs[config_name].append(result)
        
        # Report by configuration
        for config_name, config_results in configs.items():
            working_tests = [r for r in config_results if r.get('working', False)]
            
            print(f"\\n{config_name}:")
            print(f"  Working tests: {len(working_tests)}/{len(config_results)}")
            
            for result in config_results:
                status = "✅ WORKING" if result.get('working') else "❌ FAILED"
                tokens = result.get('completion_tokens', 0)
                print(f"    {result['test_name']}: {status} ({tokens} tokens)")
                
                if result.get('working') and result.get('content'):
                    print(f"      Response: \"{result['content'][:60]}\"")
        
        # Find best configuration
        best_config = None
        best_score = 0
        
        for config_name, config_results in configs.items():
            working_count = len([r for r in config_results if r.get('working', False)])
            if working_count > best_score:
                best_score = working_count
                best_config = config_name
        
        print(f"\\n{'='*80}")
        print("RECOMMENDATIONS")
        print(f"{'='*80}")
        
        if best_config and best_score > 0:
            print(f"BEST CONFIGURATION: {best_config}")
            print(f"Working tests: {best_score}/5")
            print("\\nRECOMMENDATION: Use this configuration for the frontend")
        else:
            print("NO WORKING CONFIGURATION FOUND")
            print("RECOMMENDATION: Try different model or llama.cpp version")
            print("ALTERNATIVE: Use LM Studio server mode instead")
        
        # Save results to file
        with open('model_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\\nDetailed results saved to: model_test_results.json")

def main():
    """Run comprehensive model testing"""
    
    print("STARTING COMPREHENSIVE MODEL TESTING")
    print("Goal: Find working configuration for DNA Expert model")
    print("="*60)
    
    tester = ModelTester()
    
    try:
        results = tester.run_comprehensive_tests()
        
        working_results = [r for r in results if r.get('working', False)]
        
        if working_results:
            print(f"\\n🎉 SUCCESS: Found {len(working_results)} working configurations!")
            print("The model CAN generate responses with the right settings")
        else:
            print("\\n❌ NO WORKING CONFIGURATIONS FOUND")
            print("Recommendation: Use LM Studio server mode or different approach")
            
    except KeyboardInterrupt:
        print("\\nTesting interrupted by user")
    finally:
        tester.stop_model_server()

if __name__ == "__main__":
    main()



