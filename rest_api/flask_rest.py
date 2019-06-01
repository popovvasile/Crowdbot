from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/crowdbot', methods=['POST'])
def postJsonHandler():
    print(request.data)
    content = request.get_json()
    print(content)
    return 'JSON posted'


app.run(host='0.0.0.0', port=8000)
