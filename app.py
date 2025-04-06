import streamlit as st
import pickle
import pandas as pd
import difflib
import requests

def fetch_poster(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=eeffbcc981a2ebb5ef009e742ffe7bef&language=en-US')
    data = response.json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return ""  # Return empty string if no poster is available

def find_closest_title(movie, movie_list):
    match = difflib.get_close_matches(movie, movie_list, n=1, cutoff=0.6)
    return match[0] if match else None

def recommend(movie):
    movie_list = movies['title'].tolist()

    if movie not in movie_list:
        closest_match = find_closest_title(movie, movie_list)
        if closest_match:
            st.warning(f"Movie not found! Did you mean '{closest_match}'?")
            return recommend(closest_match)
        else:
            st.error("Movie not found. Try another title.")
            return [], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_poster = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id  # Ensure 'movie_id' is correct
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_poster.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_poster

st.header('Movie Recommendation System')
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie)

    if names:
        cols = st.columns(5)  # Updated from beta_columns to columns
        for index, col in enumerate(cols):
            if index < len(names):
                with col:
                    st.text(names[index])
                    if posters[index]:
                        st.image(posters[index])
                    else:
                        st.text("Poster not available")
