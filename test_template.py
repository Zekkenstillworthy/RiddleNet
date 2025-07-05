from flask import Flask, render_template
import os

app = Flask(__name__)

# Set template folder
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app.template_folder = template_dir

@app.route('/test-leaderboard')
def test_leaderboard():
    try:
        # Try to render the leaderboard template with minimal data
        return render_template('user/leaderboard.html', 
                             user={'username': 'test'},
                             leaderboard=[])
    except Exception as e:
        return f"Error rendering template: {e}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
