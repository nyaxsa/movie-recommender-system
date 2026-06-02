import pickle
import time
import streamlit as st
import pandas as pd
import requests
import os
import gdown

if not os.path.exists("similarity.pkl"):
    url = "https://drive.google.com/uc?id=14MD3TBIn3TfYfUuCCe-qYKLfhpo_s4II"
    gdown.download(url, "similarity.pkl", quiet=False)

def fetch_poster(movie_id):
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key=46fc60839fb796c0aa819eb2726b7ab1'.format(movie_id),
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return None
    except Exception:
        return None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]  # fetch top 10

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]]['movie_id']
        poster = fetch_poster(movie_id)
        if poster:  # only add if poster exists
            recommended_movies.append(movies.iloc[i[0]]['title'])
            recommended_movies_posters.append(poster)
        if len(recommended_movies) == 5:  # stop at 5 valid ones
            break
        time.sleep(0.3)

    return recommended_movies, recommended_movies_posters

st.title("Movie Recommender System")

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

selected_movie_name = st.selectbox(
    'Please select a Movie',
    movies['title'].values
)

if st.button('Recommend Movie'):
    with st.spinner('Fetching recommendations...'):
        names, posters = recommend(selected_movie_name)

    if len(names) < 5:
        st.warning("Could only find {} movies with posters.".format(len(names)))

    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    for idx, col in enumerate(cols):
        if idx < len(names):
            with col:
                st.text(names[idx])
                st.image(posters[idx])


