import pickle
import requests
import sys
import os
import re
import pandas as pd
from difflib import get_close_matches
from flask import Flask, request, jsonify
from flask_cors import CORS

# ✅ Ensure Python finds train2nd.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from train2nd import MovieRecommender  # Import the trained model class

app = Flask(__name__)
CORS(app)

# ✅ Load the trained recommendation model
try:
    with open("movie_recommender.pkl", "rb") as file:
        model = pickle.load(file)

    if not isinstance(model, MovieRecommender):
        raise TypeError("Loaded object is not a MovieRecommender instance")

    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# ✅ Load movie dataset for title matching
try:
    movies_df = pd.read_csv("preprocessed_movies.csv")  # Ensure this file contains movie names with years
    movie_titles = movies_df["title"].tolist()  # Extract movie titles
    print("✅ Movie dataset loaded successfully!")
except Exception as e:
    print(f"❌ Error loading movie dataset: {e}")
    movie_titles = []

# ✅ OMDb API Key
OMDB_API_KEY = "967b4fa"  # Replace with your OMDb API Key


def clean_movie_title(title):
    """Clean up the movie title by removing years and extra numbers."""
    cleaned_title = re.sub(r'\s*\(\d{4}\)', '', title)  # Remove year like "(1999)"
    return cleaned_title.strip()  # Remove extra spaces


def find_closest_movie(input_title):
    """Find the closest matching movie title from the dataset."""
    matches = get_close_matches(input_title, movie_titles, n=1, cutoff=0.6)
    return matches[0] if matches else None  # Return the best match or None


def get_recommendations(movie_name):
    """
    Get movie recommendations based on the trained model.
    """
    try:
        if model is None:
            raise ValueError("Model not loaded properly.")

        # ✅ Find the closest matching movie title
        matched_movie = find_closest_movie(movie_name)
        if not matched_movie:
            return ["Movie not found"]

        recommended_movies = model.recommend(matched_movie)

        if recommended_movies == ["Movie not found"]:
            return []

        # ✅ Remove years from recommendations before returning
        cleaned_recommendations = [clean_movie_title(movie) for movie in recommended_movies]
        return cleaned_recommendations
    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")
        return []


def get_movie_poster(movie_title):
    """
    Fetch movie poster from OMDb API.
    """
    try:
        cleaned_title = clean_movie_title(movie_title)  # Clean the movie title
        omdb_url = f"http://www.omdbapi.com/?t={cleaned_title}&apikey={OMDB_API_KEY}"
        response = requests.get(omdb_url).json()

        # ✅ Debugging: Print the cleaned title and API response
        print(f"🔍 Searching OMDb for '{cleaned_title}'")
        print(f"🔍 OMDb API Response: {response}")

        if "Poster" in response and response["Poster"] != "N/A":
            return response["Poster"]  # ✅ Return poster URL
        print(f"❌ No poster found for {cleaned_title}")
        return None  # ❌ No poster found
    except Exception as e:
        print(f"❌ Error fetching movie poster: {e}")
        return None


@app.route('/recommend', methods=['GET'])
def recommend():
    """
    Flask API endpoint to get movie recommendations and fetch their posters.
    """
    movie_name = request.args.get('movie')
    if not movie_name:
        return jsonify({"error": "Movie title is required"}), 400

    recommended_movies = get_recommendations(movie_name)

    if not recommended_movies or recommended_movies == ["Movie not found"]:
        return jsonify({"error": f"No recommendations found for '{movie_name}'"}), 404

    response_data = []
    for movie in recommended_movies:
        poster_url = get_movie_poster(movie)
        response_data.append({"title": movie, "image_url": poster_url})

    return jsonify({"recommended_movies": response_data})


if __name__ == '__main__':
    from waitress import serve  # Use Waitress for production-level serving
    print("🚀 Starting Flask server on port 5000...")
    serve(app, host="0.0.0.0", port=5000)
