from backend.controller import app,movie_handler,get_movie_detail,check_movie_video

@app.route('/nowshowing')
def now_showing():
    return movie_handler(url=app.config['NOW_SHOWING_URL'])

@app.route('/comingsoon')
def coming_soon():
    return movie_handler(url=app.config['COMING_SOON_URL'])

@app.route('/moviedetail/<movie_id>')
def movie_detail(movie_id):
    return get_movie_detail(movie_id=movie_id)

@app.route('/checkvideo/<movie_id>')
def check_video(movie_id):
    return check_movie_video(movie_id=movie_id)