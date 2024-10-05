from flask import Flask, render_template, Response
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game')
def start_game():
    # Check if main.py exists 
    if os.path.isfile('main.py'):
        # Run main.py 
        subprocess.Popen(['python', 'main.py'])
        return "Game started"
    else:
        return "Game cannot be started"

if __name__ == "__main__":
    app.run(debug=True)
