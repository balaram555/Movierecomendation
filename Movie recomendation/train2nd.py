import pickle
import numpy as np
import pandas as pd
import boto3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ✅ Load dataset from S3
s3 = boto3.client('s3')
bucket_name = "moviesdataset1"
file_name = "movies.csv"

s3.download_file(bucket_name, file_name, file_name)
movies_df = pd.read_csv(file_name)

# ✅ Train Movie Recommender
class MovieRecommender:
    def __init__(self, vectorizer, similarity_matrix, movies_df):
        self.vectorizer = vectorizer
        self.similarity_matrix = similarity_matrix
        self.movies_df = movies_df

    def recommend(self, movie_title, num_recommendations=5):
        if movie_title not in self.movies_df['title'].values:
            return ["Movie not found"]

        movie_idx = self.movies_df[self.movies_df['title'] == movie_title].index[0]
        similarity_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        recommended_movie_indices = [i[0] for i in similarity_scores[1:num_recommendations+1]]
        return list(self.movies_df.iloc[recommended_movie_indices]['title'])

# ✅ Convert movie titles to numerical vectors
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(movies_df['title'])

# ✅ Compute similarity matrix
similarity_matrix = cosine_similarity(tfidf_matrix)

# ✅ Create model object
model = MovieRecommender(vectorizer, similarity_matrix, movies_df)

# ✅ Save trained model
model_filename = "movie_recommender.pkl"
with open(model_filename, "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved locally!")

# ✅ Upload trained model to S3
s3.upload_file(model_filename, bucket_name, model_filename)
print(f"✅ Model uploaded to S3: s3://{bucket_name}/{model_filename}")
