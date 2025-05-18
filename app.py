import os
import joblib
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load the model
model = joblib.load('movie_recommender.joblib')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    if request.method == 'POST':
        data = request.get_json()
        genre_preference = data.get('genre', '')
        runtime_pref = data.get('runtime', 'medium')
        age = int(data.get('age', 18))
        top_n = int(data.get('top_n', 5))
        min_rating = float(data.get('min_rating', 8.0))
        
        try:
            recommendations = recommend_movies(
                genre_preference, 
                runtime_pref, 
                age, 
                top_n=top_n, 
                min_rating=min_rating
            )
            return jsonify({'success': True, 'recommendations': recommendations})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

def recommend_movies(genre_preference, runtime_pref, age, top_n=5, min_rating=8.0):
    """
    Recommend movies based on genre preference, runtime preference, and age
    
    Parameters:
    - genre_preference: string (e.g., "Drama, Crime")
    - runtime_pref: string ("short", "medium", or "long")
    - age: integer (user's age)
    - top_n: number of recommendations to return
    - min_rating: minimum IMDB rating to consider
    
    Returns:
    - List of recommended movie dictionaries with details
    """
    # Load the model components
    tfidf = model['tfidf']
    cosine_sim = model['cosine_sim']
    movies = model['movies']
    
    # Determine age rating based on user's age
    if age < 10:
        age_rating = 'all'
    elif 10 <= age < 13:
        age_rating = '10+'
    elif 13 <= age < 17:
        age_rating = '13+'
    else:
        age_rating = '17+'
    
    # Clean genre input
    cleaned_genre = ' '.join([g.strip().lower() for g in genre_preference.split(',')])
    
    # Create query string
    query = f"{cleaned_genre} {runtime_pref.lower()} {age_rating}"
    
    # Vectorize the query
    query_vec = tfidf.transform([query])
    
    # Compute similarity between query and all movies
    from sklearn.metrics.pairwise import cosine_similarity
    sim_scores = cosine_similarity(query_vec, tfidf.transform(model['features'])).flatten()
    
    # Create a copy of movies dataframe and add similarity scores
    import pandas as pd
    valid_movies = movies.copy()
    valid_movies['similarity'] = sim_scores
    
    # Filter movies by minimum rating
    valid_movies = valid_movies[valid_movies['rating'] >= min_rating]
    
    # Get top N most similar movies
    recommendations = valid_movies.sort_values(
        by=['similarity', 'rating'], 
        ascending=[False, False]
    ).head(top_n)
    
    # Prepare output
    return recommendations[['name', 'year', 'genre', 'rating', 'runtime_category', 'tagline']].to_dict('records')

if __name__ == '__main__':
    app.run(debug=True)