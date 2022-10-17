import os
from flask import Flask

app = Flask(__name__)

AWS_INSTANCE_ID = os.environ.get('AWS_INSTANCE_ID')

@app.route('/')
def health_check():
    return "Healthy!"

@app.route('/cluster1')
def instance_id():
    return f"Instance {AWS_INSTANCE_ID} is responding now!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)