import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load pre-computed recommendations
with open('precomputed_recommendations.json', 'r') as f:
    recommendations_data = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    if request.method == 'POST':
        data = request.get_json()
        genre_preference = data.get('genre', '').split(',')[0].strip()  # Take first genre
        runtime_pref = data.get('runtime', 'medium')
        age = int(data.get('age', 18))
        top_n = int(data.get('top_n', 5))
        min_rating = float(data.get('min_rating', 8.0))
        
        try:
            recommendations = get_recommendations(
                genre_preference, 
                runtime_pref, 
                age, 
                top_n=top_n, 
                min_rating=min_rating
            )
            return jsonify({'success': True, 'recommendations': recommendations})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

def get_recommendations(genre_preference, runtime_pref, age, top_n=5, min_rating=8.0):
    """
    Get pre-computed recommendations based on user preferences
    """
    # Round min_rating to nearest available value
    available_ratings = [7.0, 7.5, 8.0, 8.5]
    min_rating = min(available_ratings, key=lambda x: abs(x - min_rating))
    
    # Ensure top_n is one of the available values
    available_top_ns = [5, 10, 15]
    top_n = min(available_top_ns, key=lambda x: abs(x - top_n))
    
    # Map age to representative age
    if age < 10:
        mapped_age = 8
    elif 10 <= age < 13:
        mapped_age = 11
    elif 13 <= age < 17:
        mapped_age = 15
    else:
        mapped_age = 18
    
    # Create the key
    key = f"{genre_preference}_{runtime_pref}_{mapped_age}_{min_rating}_{top_n}"
    
    # Get recommendations
    if key in recommendations_data:
        return recommendations_data[key]
    else:
        # Return closest match if exact key not found
        import difflib
        closest_key = difflib.get_close_matches(key, recommendations_data.keys(), n=1)[0]
        return recommendations_data[closest_key]

if __name__ == '__main__':
    app.run(debug=True)