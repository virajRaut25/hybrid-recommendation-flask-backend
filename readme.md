# Flask Movie and TV Show Recommendation API

This Flask application provides an API for recommending movies and TV shows based on collaborative filtering (CF) and content-based (CB) approaches. It also fetches movie and TV show posters from an external API.

## Endpoints

- `/topm`: Returns a list of top movies with their posters.
- `/toptv`: Returns a list of top TV shows with their posters.
- `/recommend_cf/<name>`: Recommends similar content using collaborative filtering based on the input movie or TV show name.
- `/recommend_cb/<name>`: Recommends similar content using content-based filtering based on the input movie or TV show name.
- `/recommend/<name>`: Recommends content using a hybrid approach combining CF and CB.
- `/genre/<name>`: Returns top content based on a specific genre.
- `/mvgenre/<name>`: Returns top movies based on a specific genre.
- `/tvgenre/<name>`: Returns top TV shows based on a specific genre.
- `/details/<id>`: Returns details of a specific movie or TV show.
- `/getContents/<cont_list>`: Returns details of multiple movies or TV shows based on their names.

## Functions

- `similar_match(movie_name)`: Finds a similar movie name using SequenceMatcher.
- `fetch_mvposter(movie_id)`: Fetches the poster URL for a given movie ID.
- `fetch_tvposter(tv_id)`: Fetches the poster URL for a given TV show ID.
- `cb_recommend(name, n)`: Recommends content using content-based filtering.
- `cf_recommend(movie_name, n)`: Recommends content using collaborative filtering.
- `hf_recommend(name)`: Recommends content using a hybrid CF and CB approach.
- `getMVTrailer(id)`: Fetches the trailer URL for a given movie ID.
- `getTVTrailer(id)`: Fetches the trailer URL for a given TV show ID.

The repository for this application does not contains pickle files, as the files exceeds the Git Large File Storage (LFS) limit.
