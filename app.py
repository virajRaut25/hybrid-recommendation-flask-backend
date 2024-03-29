from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
import ast

app = Flask(__name__)
CORS(app)

movies_list = pickle.load(open("movies_objf.pkl", 'rb'))
tvshow_list = pickle.load(open("tvshows_objf.pkl", 'rb'))
content_list = pickle.load(open("content_objf.pkl", 'rb'))
cb_model = pickle.load(open("cb_model.pkl", 'rb'))
cb_tvmodel = pickle.load(open("cb_tvshows_model.pkl", 'rb'))
cb_content = pickle.load(open("cb_content.pkl", 'rb'))
cf_model = pickle.load(open("cf_model.pkl", 'rb'))
pt = pd.read_pickle("pt.pkl")
top_df = pd.read_pickle("top_movies.pkl")

genre_list = ['Action',
              'Adventure',
              'Animation',
              'Comedy',
              'Crime',
              'Documentary',
              'Drama',
              'Family',
              'Fantasy',
              'History',
              'Horror',
              'Music',
              'Mystery',
              'Romance',
              'Kids',
              'News',
              'Sci-Fi',
              'TV Movie',
              'Thriller',
              'Reality',
              'Politics',
              'Soap',
              'Talk',
              'War',
              'Western']


def similar_match(movie_name):
    ratio = 0
    similar_name = ""
    for title in content_list['title'].str.lower():
        local_ratio = SequenceMatcher(None, title, movie_name).ratio()
        if local_ratio > ratio:
            similar_name = title
            ratio = local_ratio

    return similar_name


def cb_recommend(name, n=10):
    name = name.lower()
    if len(content_list[content_list['title'].str.lower() == name]) == 0:
        name = similar_match(name)
        if len(content_list[content_list['title'].str.lower() == name]) == 0:
            return []

    index = content_list[content_list['title'].str.lower() == name].index[0]
    cf_movie = None
    distances = sorted(
        list(enumerate(cb_content[index])), reverse=True, key=lambda x: x[1])
    data = []
    for i in distances[0:n]:
        if (cf_movie == None and content_list.iloc[i[0]].type == 'movie'):
            cf_movie = content_list.iloc[i[0]].title
        data.append(content_list.iloc[i[0]].title)

    return data, cf_movie


def cf_recommend(movie_name, n=10):
    # index fetch
    movie_name = movie_name.lower()
    index = np.where(pt.index == movie_name)[0]
    if len(index) == 0:
        movie_name = similar_match(movie_name)
        index = np.where(pt.index == movie_name)[0]
        if len(index) == 0:
            return []

    index = index[0]
    similar_items = sorted(
        list(enumerate(cf_model[index])), key=lambda x: x[1], reverse=True)[0:n]
    data = []
    for i in similar_items:
        temp_df = movies_list[movies_list['title'].str.lower()
                              == pt.index[i[0]]]
        data.append(temp_df.drop_duplicates('title')['title'].values[0])

    return data


def hf_recommend(name):
    cb_list, movie_name = cb_recommend(name)
    cf_list = []
    if movie_name:
        cf_list = cf_recommend(movie_name)
    hf_list = cb_list + cf_list
    hf_list = [i for n, i in enumerate(hf_list) if i not in hf_list[:n]]
    return hf_list


@app.route('/')
def index():
    return f"Flask Backend is Listing at Port {request.host_url.split(':')[-1][:-1]}"


@app.route('/topm')
def top_movies():
    movies_json = top_df.to_dict(orient='records')
    for movie in movies_json:
        id = movies_list[movies_list['title'] == movie['title']].id.iloc[0]
        movie.update(
            {"id": int(id), "poster": movies_list[movies_list['id'] == id].poster.iloc[0]})

    return jsonify(movies_json)


@app.route('/toptv')
def top_tvshows():
    tv_json = tvshow_list.sort_values('popularity', ascending=False).head(20)
    tv_json = tv_json[[
        'id', 'title', 'genres', 'type', 'poster']].to_dict(orient='records')

    return jsonify(tv_json)


@app.route('/recommend_cf/<name>')
def recommendCF(name):
    res = []
    content_type = None
    try:
        content_type = content_list[content_list['title'] == name].type.iloc[0]
    except Exception as e:
        print(e)
    if (content_type == 'movie'):
        recommend_content = cf_recommend(name, 20)
        for rc in recommend_content:
            id = movies_list[movies_list['title'] == rc].id.iloc[0]
            res.append({"id": int(id), "title": rc,
                        "poster": movies_list[movies_list['id'] == id].poster.iloc[0]})

    return jsonify(res)


@app.route('/recommend_cb/<name>')
def recommendCB(name):
    res = []
    recommend_content, movie_name = cb_recommend(name, 20)
    for rc in recommend_content:
        id = content_list[content_list['title'] == rc].id.iloc[0]
        content_type = content_list[content_list['title'] == rc].type.iloc[0]
        res.append({"id": int(id), "title": rc,
                    "poster": content_list[content_list['id'] == id].poster.iloc[0], "type": content_type})

    return jsonify(res)


@app.route('/recommend/<name>')
def recommend(name):
    res = []
    recommend_movie = hf_recommend(name)
    for rm in recommend_movie:
        id = content_list[content_list['title'] == rm].id.iloc[0]
        content_type = content_list[content_list['title'] == rm].type.iloc[0]
        res.append({"id": int(id), "title": rm,
                    "poster": content_list[content_list['id'] == id].poster.iloc[0], "type": content_type, "genres": content_list[content_list['id'] == id]['genres'].iloc[0]})

    return jsonify(res)


@app.route('/genre/<name>')
def genre(name):
    name = ast.literal_eval(name)
    top_genre = content_list[content_list['genres'].map(lambda x: any(
        ele in x for ele in name))].sort_values('popularity', ascending=False).head(30)
    top_genre_json = top_genre[[
        'id', 'title', 'genres', 'type', 'poster']].to_dict(orient='records')

    return top_genre_json


@app.route('/mvgenre/<name>')
def movieGenre(name):
    top_genre_movies = movies_list[movies_list['genres'].map(
        lambda x: name in x)].sort_values('popularity', ascending=False).head(20)
    top_genre_movies_json = top_genre_movies[[
        'id', 'title', 'genres', 'poster']].to_dict(orient='records')

    return top_genre_movies_json


@app.route('/tvgenre/<name>')
def tvGenre(name):
    top_genre_tvshows = tvshow_list[tvshow_list['genres'].map(
        lambda x: name in x)].sort_values('popularity', ascending=False).head(20)
    top_genre_tvshows_json = top_genre_tvshows[[
        'id', 'title', 'genres', 'poster']].to_dict(orient='records')

    return top_genre_tvshows_json


@app.route("/details/<id>")
def getDetails(id):
    id = int(id)
    res = content_list[content_list['id'] == id].iloc[0].to_dict()
    if (np.isnan(res['runtime'])):
        res.update({"runtime": 0})

    return jsonify(res)


@app.route("/getContents/<cont_list>")
def getContents(cont_list):
    cont_list = ast.literal_eval(cont_list)
    res = []
    for cont in cont_list:
        id = content_list[content_list['title'] == cont].id.iloc[0]
        content_type = content_list[content_list['title'] == cont].type.iloc[0]
        res.append({"id": int(id), "title": cont,
                    "poster": content_list[content_list['id'] == id].poster.iloc[0], "type": content_type, "genres": content_list[content_list['id'] == id]['genres'].iloc[0]})

    return jsonify(res)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
