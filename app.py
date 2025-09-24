from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import os

app = Flask(__name__)

# Configure session
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-secret-key-here-change-in-production")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    # Initialize history if not exists
    if 'history' not in session:
        session['history'] = []
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        
        # Basic security check - only allow numbers and basic operators
        allowed_chars = '0123456789+-*/.()'
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return jsonify({'error': 'Invalid characters in expression'}), 400
        
        # Evaluate the expression
        try:
            result = eval(expression)
            
            # Initialize history if not exists
            if 'history' not in session:
                session['history'] = []
            
            # Add to history (keep only last 2)
            calculation = f"{expression} = {result}"
            session['history'].append(calculation)
            if len(session['history']) > 2:
                session['history'] = session['history'][-2:]
            
            # Make session permanent
            session.permanent = True
            
            return jsonify({
                'result': str(result),
                'history': session['history']
            })
        except:
            return jsonify({'error': 'Invalid expression'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    session['history'] = []
    return jsonify({'success': True, 'history': []})

if __name__ == '__main__':
    app.run(debug=True)