from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from crawler import search_repository
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    repo_url = data['repo_url']
    results = search_repository(repo_url)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
