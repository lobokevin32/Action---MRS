import streamlit as st
import pandas as pd
import random
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import requests
import base64
import streamlit.components.v1 as components

TMDB_API_KEY = "585d31561eea5169971dc2855e5f297a"
requests_session = requests.Session()


@st.cache_data
def fetch_poster(title):
    try:
        clean = title.split("(")[0].split("-")[0].strip()
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={clean}"
        res = requests_session.get(url, timeout=4).json()

        if res.get("results") and res["results"][0].get("poster_path"):
            return f"https://image.tmdb.org/t/p/w300{res['results'][0]['poster_path']}"

    except:
        pass

    return "https://via.placeholder.com/300x450?text=No+Poster"


def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded}");
        background-size: cover;
        background-attachment: fixed;
    }}

    /* 👉 CENTER THE ACTION TITLE ONLY */
    h1 {{
        text-align: center !important;
    }}

    /* ✨ Glow Search Bar */
    .stSelectbox > div > div {{
        background: rgba(255,255,255,0.1);
        border: 2px solid cyan;
        border-radius: 10px;
        color: white !important;
        font-weight: bold;
        box-shadow: 0px 0px 15px cyan;
        transition: .3s;
    }}
    .stSelectbox > div:hover > div {{
        transform: scale(1.05);
        box-shadow: 0px 0px 30px cyan;
    }}

    /* ✨ Glow Button */
    .stButton button {{
        background: linear-gradient(90deg,#00f2ff,#0077ff);
        padding: 12px 25px;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        box-shadow: 0px 0px 18px cyan;
        transition: .2s;
    }}
    .stButton button:hover {{
        transform: scale(1.12);
        box-shadow: 0px 0px 35px cyan;
        cursor: pointer;
    }}

    </style>
    """, unsafe_allow_html=True)


set_background("background.jpg")

@st.cache_data
def load_data():
    movies = pd.read_csv("movies.csv")

    ott = ["Netflix","Prime","Hotstar","HBO Max","Hulu","Apple TV+","YouTube","Jio Cinema"]

    movies["rating"] = movies.get("rating",[round(random.uniform(6,9.8),1) for _ in range(len(movies))])
    movies["duration"] = movies.get("duration",[random.randint(90,180) for _ in range(len(movies))])
    movies["platform"] = movies.get("platform",[random.choice(ott) for _ in range(len(movies))])

    movies["tags"] = movies["genres"].fillna("") + " " + movies["description"].fillna("")

    cv = CountVectorizer(stop_words="english")
    similarity = cosine_similarity(cv.fit_transform(movies["tags"]))

    return movies, similarity


movies, similarity = load_data()


def recommend(movie, count):
    if movie not in movies["title"].values:
        return []

    idx = movies[movies["title"] == movie].index[0]
    scores = sorted(range(len(similarity[idx])), key=lambda i: similarity[idx][i], reverse=True)

    result = [movies.iloc[idx]] + [movies.iloc[i] for i in scores[1:count]]
    return result


st.title("🎬 ᗩҁ₮Į◎₪")
st.subheader("ᴀɪ ᴘᴏᴡᴇʀᴇᴅ ᴍᴏᴠɪᴇ ʀᴇᴄᴏᴍᴍᴇɴᴅᴇʀ🍿")

movie_choice = st.selectbox("🔍 Select Movie", [""] + list(movies["title"].values))
num_movies = st.slider("🎯 𝑵𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝑹𝒆𝒄𝒐𝒎𝒎𝒆𝒏𝒅𝒂𝒕𝒊𝒐𝒏𝒔", 5, 25, 10, step=5)


if st.button("🚀 🇬🇪🇳🇪🇷🇦🇹🇪 🇸🇺🇬🇬🇪🇸🇹🇮🇴🇳🇸"):
    results = recommend(movie_choice, num_movies)

    if not results:
        st.warning("⚠ Select a movie.")
    else:
        HTML = """
        <style>
        .grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; }
        .card { position:relative; cursor:pointer; text-align:center; }
        .poster { width:100%; border-radius:10px; transition:.3s; }
        .title { margin-top:6px; font-weight:bold; color:white; }
        .overlay {
            position:absolute; top:0; left:0; width:100%; height:100%;
            background:rgba(0,0,0,.8); color:white; opacity:0;
            padding:10px; border-radius:10px; font-size:12px; transition:.3s;
            overflow:hidden; text-align:left;
        }
        .card:hover .poster { filter:brightness(40%); transform:scale(1.05); }
        .card:hover .overlay { opacity:1; }
        </style>
        <div class="grid">
        """

        for m in results:
            poster = fetch_poster(m["title"])
            overview = m["description"][:180] + "..." if len(m["description"]) > 180 else m["description"]

            HTML += f"""
            <div class="card">
                <img class="poster" src="{poster}">
                <div class="overlay">
                    ⭐ {m['rating']} / 10<br>
                    ⏳ {m['duration']} mins<br>
                    📺 {m['platform']}<br><br>
                    <b>Overview:</b><br>{overview}
                </div>
                <div class="title">{m['title']}</div>
            </div>
            """

        HTML += "</div>"

        components.html(HTML, height=1100, scrolling=True)
