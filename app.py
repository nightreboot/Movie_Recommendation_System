import pickle
import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# -------------------------
# Create requests session with retry strategy
# -------------------------
def create_session_with_retries():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# -------------------------
# Fetch movie poster with error handling
# -------------------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    
    try:
        session = create_session_with_retries()
        data = session.get(url, timeout=10).json()
        poster_path = data.get('poster_path', None)
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        return "https://via.placeholder.com/500"
    except requests.exceptions.Timeout:
        st.warning(f"⏱️ Timeout fetching poster for movie ID {movie_id}")
        return "https://via.placeholder.com/500"
    except requests.exceptions.ConnectionError:
        st.warning(f"🔌 Connection error fetching poster for movie ID {movie_id}")
        return "https://via.placeholder.com/500"
    except requests.exceptions.RequestException as e:
        st.warning(f"❌ Error fetching poster for movie ID {movie_id}: {str(e)}")
        return "https://via.placeholder.com/500"
    except Exception as e:
        st.warning(f"❌ Unexpected error fetching poster: {str(e)}")
        return "https://via.placeholder.com/500"

# -------------------------
# Recommendation function
# -------------------------
def recommend(selected_movie):
    movie_index = movies[movies['title'] == selected_movie].index[0]
    distances = sorted(list(enumerate(similarity[movie_index])),
                       reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]]['id']
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

# -------------------------
# Load Model Data
# -------------------------
movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

movie_list = movies['title'].values

# -------------------------
# Streamlit UI
# -------------------------
st.title("🎬 My Movie Recommender System")

selected_movie = st.selectbox(
    "❤️❤️ Search your Favorite Movie ❤️❤️",
    movie_list
)

if st.button("Show Recommendations"):
    names, posters = recommend(selected_movie)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])