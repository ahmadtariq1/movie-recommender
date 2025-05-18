import joblib
import json
import itertools
from tqdm import tqdm

def generate_all_recommendations():
    # Load the model
    print("Loading model...")
    model = joblib.load('movie_recommender.joblib')
    
    # Define all possible combinations
    genres = ['Action', 'Drama', 'Comedy', 'Thriller', 'Romance', 'Horror', 'Sci-Fi', 'Adventure', 'Crime']
    runtime_prefs = ['short', 'medium', 'long']
    ages = [8, 11, 15, 18]  # Representative ages for each category
    min_ratings = [7.0, 7.5, 8.0, 8.5]
    top_ns = [5, 10, 15]
    
    recommendations = {}
    
    # Generate combinations
    combinations = list(itertools.product(
        genres,
        runtime_prefs,
        ages,
        min_ratings,
        top_ns
    ))
    
    print(f"Generating recommendations for {len(combinations)} combinations...")
    
    for genre, runtime, age, min_rating, top_n in tqdm(combinations):
        # Create a unique key for this combination
        key = f"{genre}_{runtime}_{age}_{min_rating}_{top_n}"
        
        # Load the model components
        tfidf = model['tfidf']
        cosine_sim = model['cosine_sim']
        movies = model['movies']
        
        # Determine age rating
        if age < 10:
            age_rating = 'all'
        elif 10 <= age < 13:
            age_rating = '10+'
        elif 13 <= age < 17:
            age_rating = '13+'
        else:
            age_rating = '17+'
        
        # Create query string
        query = f"{genre.lower()} {runtime.lower()} {age_rating}"
        
        # Vectorize the query
        query_vec = tfidf.transform([query])
        
        # Compute similarity
        from sklearn.metrics.pairwise import cosine_similarity
        sim_scores = cosine_similarity(query_vec, tfidf.transform(model['features'])).flatten()
        
        # Create a copy of movies dataframe and add similarity scores
        import pandas as pd
        valid_movies = movies.copy()
        valid_movies['similarity'] = sim_scores
        
        # Filter movies by minimum rating
        valid_movies = valid_movies[valid_movies['rating'] >= min_rating]
        
        # Get top N most similar movies
        top_movies = valid_movies.sort_values(
            by=['similarity', 'rating'], 
            ascending=[False, False]
        ).head(top_n)
        
        # Store recommendations
        recommendations[key] = top_movies[['name', 'year', 'genre', 'rating', 'runtime_category', 'tagline']].to_dict('records')
    
    # Save recommendations to JSON file
    print("Saving recommendations...")
    with open('precomputed_recommendations.json', 'w') as f:
        json.dump(recommendations, f)
    
    print("Done! Recommendations saved to precomputed_recommendations.json")

if __name__ == '__main__':
    generate_all_recommendations() 