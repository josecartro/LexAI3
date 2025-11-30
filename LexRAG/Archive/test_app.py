
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
