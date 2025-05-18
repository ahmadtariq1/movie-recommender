import os
import json
import logging
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize recommendations_data as empty dict
recommendations_data = {}

# Try to load pre-computed recommendations
try:
    logger.info("Loading recommendations data...")
    # Get the absolute path to the JSON file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'precomputed_recommendations.json')
    logger.info(f"Looking for recommendations file at: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        recommendations_data = json.load(f)
    logger.info(f"Successfully loaded recommendations data with {len(recommendations_data)} entries")
except Exception as e:
    logger.error(f"Error loading recommendations: {str(e)}")

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return "An error occurred while loading the page. Please try again later.", 500

@app.route('/recommend', methods=['POST'])
def recommend():
    if request.method == 'POST':
        # Check if recommendations are loaded
        if not recommendations_data:
            logger.error("Recommendations data not available")
            return jsonify({
                'success': False,
                'error': 'Recommendations data not available. Please try again later.'
            }), 503

        try:
            data = request.get_json()
            if not data:
                raise ValueError("No JSON data received")

            # Extract and validate inputs
            genre_preference = data.get('genre', '').strip()
            if not genre_preference:
                raise ValueError("Genre preference is required")

            runtime_pref = data.get('runtime', 'medium')
            if runtime_pref not in ['short', 'medium', 'long']:
                runtime_pref = 'medium'

            age = int(data.get('age', 18))
            if not (1 <= age <= 120):
                age = 18

            top_n = int(data.get('top_n', 5))
            if top_n not in [5, 10, 15]:
                top_n = 5

            min_rating = float(data.get('min_rating', 8.0))
            if min_rating not in [7.0, 7.5, 8.0, 8.5]:
                min_rating = 8.0

            recommendations = get_recommendations(
                genre_preference, 
                runtime_pref, 
                age, 
                top_n=top_n, 
                min_rating=min_rating
            )
            return jsonify({'success': True, 'recommendations': recommendations})
        except ValueError as ve:
            logger.warning(f"Validation error: {str(ve)}")
            return jsonify({
                'success': False,
                'error': str(ve)
            }), 400
        except Exception as e:
            logger.error(f"Error in recommend endpoint: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'An error occurred while processing your request.'
            }), 500

def get_recommendations(genre_preference, runtime_pref, age, top_n=5, min_rating=8.0):
    """
    Get pre-computed recommendations based on user preferences
    """
    if not recommendations_data:
        raise Exception("Recommendations data not loaded")

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
    logger.info(f"Looking for recommendations with key: {key}")
    
    # Get recommendations
    if key in recommendations_data:
        return recommendations_data[key]
    else:
        # Return closest match if exact key not found
        import difflib
        closest_matches = difflib.get_close_matches(key, recommendations_data.keys(), n=1)
        if not closest_matches:
            logger.warning(f"No recommendations found for key: {key}")
            return []
        logger.info(f"Using closest match: {closest_matches[0]}")
        return recommendations_data[closest_matches[0]]

if __name__ == '__main__':
    app.run(debug=True)