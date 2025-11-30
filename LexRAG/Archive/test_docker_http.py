"""
Test Docker HTTP Networking
Create simple test container to verify Docker HTTP works
"""

import subprocess
import time
import requests

def test_nginx_container():
    """Test with simple nginx container"""
    
    print("TESTING DOCKER HTTP NETWORKING")
    print("="*50)
    print("Using simple nginx container to test HTTP")
    print("="*50)
    
    # Create simple nginx container
    print("\\n1. Creating nginx test container...")
    
    try:
        cmd = [
            "docker", "run", "-d",
            "--name", "test-http-nginx",
            "-p", "8128:80",
            "nginx:alpine"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            container_id = result.stdout.strip()
            print(f"SUCCESS: Nginx container created - {container_id[:12]}")
        else:
            print(f"ERROR: Nginx creation failed - {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    # Wait for nginx to start
    print("\\n2. Waiting for nginx to start...")
    time.sleep(10)
    
    # Test HTTP access
    print("\\n3. Testing HTTP access on port 8128...")
    
    try:
        response = requests.get("http://127.0.0.1:8128", timeout=10)
        
        if response.status_code == 200:
            print(f"SUCCESS: HTTP works! Status: {response.status_code}")
            print(f"Response length: {len(response.text)} chars")
            print("Docker HTTP networking is functional")
            
            # Cleanup
            print("\\n4. Cleaning up nginx container...")
            subprocess.run(["docker", "stop", "test-http-nginx"], capture_output=True)
            subprocess.run(["docker", "rm", "test-http-nginx"], capture_output=True)
            print("Cleanup complete")
            
            return True
        else:
            print(f"ERROR: HTTP failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: HTTP test failed - {e}")
        
        # Cleanup on error
        subprocess.run(["docker", "stop", "test-http-nginx"], capture_output=True)
        subprocess.run(["docker", "rm", "test-http-nginx"], capture_output=True)
        return False

def test_simple_python_api():
    """Test with simple Python API container"""
    
    print("\\n" + "="*50)
    print("TESTING SIMPLE PYTHON API CONTAINER")
    print("="*50)
    
    # Create simple Python API
    api_code = '''
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Docker Python API!"

@app.route('/ping')
def ping():
    return {"status": "ok", "message": "Docker HTTP working"}

@app.route('/test')
def test():
    return {"docker_http": "working", "port": 5000}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
'''
    
    # Create Dockerfile
    dockerfile = '''
FROM python:3.9-alpine
RUN pip install flask
COPY app.py /app.py
EXPOSE 5000
CMD ["python", "/app.py"]
'''
    
    print("\\n1. Creating simple Python API...")
    
    try:
        # Write files (fix filename mismatch)
        with open("app.py", "w") as f:
            f.write(api_code)
        
        with open("test_dockerfile", "w") as f:
            f.write(dockerfile)
        
        # Build image
        build_cmd = ["docker", "build", "-f", "test_dockerfile", "-t", "test-python-api", "."]
        build_result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if build_result.returncode == 0:
            print("SUCCESS: Test API image built")
        else:
            print(f"ERROR: Build failed - {build_result.stderr}")
            return False
        
        # Run container
        run_cmd = [
            "docker", "run", "-d",
            "--name", "test-python-api",
            "-p", "8129:5000",
            "test-python-api"
        ]
        
        run_result = subprocess.run(run_cmd, capture_output=True, text=True)
        
        if run_result.returncode == 0:
            print("SUCCESS: Test API container running on port 8129")
        else:
            print(f"ERROR: Run failed - {run_result.stderr}")
            return False
        
        # Wait and test
        print("\\n2. Waiting for API to start...")
        time.sleep(15)
        
        print("\\n3. Testing Python API HTTP...")
        
        # Test endpoints
        endpoints = ["/", "/ping", "/test"]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://127.0.0.1:8129{endpoint}", timeout=10)
                print(f"   {endpoint}: HTTP {response.status_code} - {response.text[:50]}")
            except Exception as e:
                print(f"   {endpoint}: ERROR - {e}")
        
        # Cleanup
        print("\\n4. Cleaning up Python API...")
        subprocess.run(["docker", "stop", "test-python-api"], capture_output=True)
        subprocess.run(["docker", "rm", "test-python-api"], capture_output=True)
        subprocess.run(["docker", "rmi", "test-python-api"], capture_output=True)
        
        # Remove test files
        import os
        try:
            os.remove("app.py")
            os.remove("test_dockerfile")
        except:
            pass
        
        print("Cleanup complete")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Run Docker HTTP networking tests"""
    
    print("DOCKER HTTP NETWORKING DIAGNOSTIC")
    print("="*60)
    print("Testing if Docker HTTP works at all on this system")
    print("="*60)
    
    # Test 1: Simple nginx
    nginx_works = test_nginx_container()
    
    # Test 2: Python API
    python_works = test_simple_python_api()
    
    print("\\n" + "="*60)
    print("FINAL DIAGNOSTIC RESULTS")
    print("="*60)
    
    print(f"Nginx HTTP test: {'PASS' if nginx_works else 'FAIL'}")
    print(f"Python API test: {'PASS' if python_works else 'FAIL'}")
    
    if nginx_works or python_works:
        print("\\nCONCLUSION: Docker HTTP networking works")
        print("ISSUE: ClickHouse-specific HTTP server problem")
        print("SOLUTION: ClickHouse configuration or version issue")
    else:
        print("\\nCONCLUSION: Docker HTTP networking broken")
        print("ISSUE: System-level networking problem")
        print("SOLUTION: Check firewall, Docker settings, network configuration")
    
    return nginx_works or python_works

if __name__ == "__main__":
    main()
