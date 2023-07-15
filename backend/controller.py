from functools import wraps
from backend import app
from backend.models import User,SavedMovie,MovieSeat,MovieTicket,db
from flask import request
import jwt
import requests
import re
import uuid


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            print(request.headers["Authorization"])
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "success": False,
                "message": "Unauthorized"
            }, 200
        try:
            data=decode_token(token)
            if not data:
                return {
                "success": False,
                "message": "Unauthorized"
            }, 200
            print(data['token'])
            current_user=User.query.filter_by(token=data['token']).first()
            if not current_user:
                return {
                "success": False,
                "message": "Unauthorized"
            }, 200
        except Exception as e:
            print(e)
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500
        return f(current_user, *args, **kwargs)
    return decorated

def encode_token(params):
    try:
        return jwt.encode(params,app.config['SECRET_KEY'],algorithm='HS256')
    except Exception as e:
        print(e)
        return False

def decode_token(token):
    try:
        return jwt.decode(token,app.config['SECRET_KEY'],algorithms=['HS256'])
    except Exception as e:
        print(e)
        return False

def generate_random_token():
    try:
        while True:
            token = str(uuid.uuid4())
            user = User.query.filter_by(token=token).first()
            if not user:
                return token
    except:
        return False
    
def register_handler(data):
    try:
        if not data.get('username') and data.get('password'):
            return {'success':False,'message':'harap isi seluruh field yang dibutuhkan!'},200
        if not len(data['username']) > 3 and len(data['password']) > 3:
            return {'success':False,'message':'username dan password minimal 3 karakter!!'},200
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            user = User(
                username=data['username'],
                password=data['password'],
                token=generate_random_token()
            )
            db.session.add(user)
            db.session.commit()
            return {'success':True,'data':{'authToken':encode_token({'token':user.token}),'username':user.username,'balance':user.balance}},200
        return {'success':False,'message':'username sudah terdaftar!'},200
    except Exception as e:
        print(e)
        return {'success':False,'message':'Something went wrong!'},200
    
def login_handler(data):
    print(data)
    if not data.get('username') and data.get('password'):
        return {'success':False,'message':'harap isi seluruh field yang dibutuhkan!'},200
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password_correction(data['password']):
        token = generate_random_token()
        if token:
            user.token = token
            db.session.commit()
            return {'success':True,'data':{'authToken':encode_token({'token':user.token}),'username':user.username,'balance':user.balance}},200
    return {'success':False},200
    
def logout_handler(current_user):
    current_user.token = generate_random_token()
    db.session.commit()
    return {'success':True},200

def find_detail_age_minimum(html):
    pattern = r'<img src="images/([^"]+)" width="50" height="50"/>'
    match = re.search(pattern, html)
    if match:
        filename = match.group(1)
        number_match = re.search(r'(\d+)', filename)
        if number_match:
            number = number_match.group(1)
            return number + '+'
        else:
            return 'semua umur'
    else:
        return 'semua umur'

def get_thumbnail(html):
    pattern = r'<div class="col-md-3 col-sm-6 col-xs-6">\s*<img src="(.*?)" class="img-responsive pull-left gap-left".*?>\s*</div>'
    match = re.search(pattern, html)
    if match:
        image_url = match.group(1)
        image_url = re.sub(r'https://web3.21cineplex.com', app.config['WEB_URL'], image_url)
        return image_url
    return False

def get_movie_price(movie_id):
    res = requests.get(f'{app.config["MOVIE_TICKET_URL"]}{movie_id}')
    if res.status_code != 200:
        return None
    html = res.text
    pattern = r'<span class="p_price">([^<]+)</span>'
    match = re.search(pattern, html)
    if match:
        price_str = match.group(1)
        price_str = re.sub(r'[^\d]+', '', price_str)
        return int(price_str)
    else:
        return None

def get_desc_cast_dir(html):
    img_pattern = r'<img src="(.*?)" class="img-responsive pull-left gap-left".*?>'
    img_match = re.search(img_pattern, html)
    description_pattern = r'<p id="description">(.*?)</p>'
    cast_pattern = r'<p style="margin-bottom: 5px"><strong>Cast</strong>:</p>\s*<p>(.*?)</p>'
    director_pattern = r'<p style="margin-bottom: 5px"><strong>Director</strong>:</p>\s*<p>(.*?)</p>'
    description_match = re.search(description_pattern, html)
    cast_match = re.search(cast_pattern, html)
    director_match = re.search(director_pattern, html)
    description = description_match.group(1).replace("<p>","") if description_match else None
    cast = cast_match.group(1) if cast_match else None
    director = director_match.group(1) if director_match else None
    if description and cast and director:
        return description, cast, director
    return False

def get_duration_and_trailer_from_html(html):
    duration_pattern = r'<p><span class="glyphicon glyphicon-time".*?>\s*(\d+)\s*Minutes</p>'
    trailer_pattern = r'<button onclick="location.href = \'(https://web3.21cineplex.com/movie-trailer/.*?)\';" class="btn icon-btn btn-success".*?> TRAILER </button>'
    duration_match = re.search(duration_pattern, html)
    trailer_match = re.search(trailer_pattern, html)
    duration = duration_match.group(1) if duration_match else '-'
    trailer = trailer_match.group(1) if trailer_match else None
    if duration and trailer:
        return duration, trailer
    return False


def get_movie_detail(movie_id,current_user):
    url=f"{app.config['MOVIE_DETAIL_URL']}{movie_id}"
    res = requests.get(url)
    if res.status_code != 200:
        return {'success': False}, 200
    html = res.text
    class_name='col-xs-8 col-sm-11 col-md-11'
    movie_details = {}
    title_genre = fr'<div class="{class_name}"(?:\s+\w+="[^"]*")*>(?:\s*<[^>]+>)?(.*?)</div>'
    title_genre_matches = re.findall(title_genre, html)
    if title_genre_matches:
        movie_details['id'] = movie_id
        movie_details['title'] = title_genre_matches[0]
        movie_details['genre'] = title_genre_matches[1]
        duration_trailer = get_duration_and_trailer_from_html(html)
        desc_cast_dir = get_desc_cast_dir(html)
        image_url = get_thumbnail(html)
        age_minimum = find_detail_age_minimum(html)
        if not duration_trailer or not desc_cast_dir or not image_url or not age_minimum:
            return False
        movie_details['age_minimum'] = age_minimum
        movie_details['duration'] = duration_trailer[0]
        movie_details['trailer'] = duration_trailer[1]
        movie_details['description'] = desc_cast_dir[0]
        movie_details['cast'] = desc_cast_dir[1]
        movie_details['director'] = desc_cast_dir[2]
        movie_details['image'] = image_url
        movie_details['price'] = get_movie_price(movie_id)
        movie_details['saved'] = True if movie_details['id'] in [movie.movie_id for movie in current_user.saved_movies] else False
        return {'success':True,'data':movie_details},200
    return {'success': False}, 200

def get_wishlist_handler(current_user):
    try:
        movies = [movie.to_json() for movie in current_user.saved_movies]
        return {'success':True,'data':movies},200
    except:
        return {'success':False},200
    
def extract_movie(html):
    data = []
    pattern = r'<div class="grid_movie">\s*<a\s*href="([^"]*)">\s*<img\s*id=\'([^"]*)\'\s*src="([^"]*)".*?<div class="title">([^<]*)<\/div>'
    matches = re.findall(pattern, html, re.DOTALL)
    if matches:
        for match in matches:
            if match[1] != '{movie_id}':
                image_url = re.sub(r'https://web3.21cineplex.com', app.config['WEB_URL'], match[2])
                data.append({
                    'id': match[1],
                    'image': image_url,
                    'title': match[3]
                })
        return data
    return False

def insert_movie_seat(movie_id):
    try:
        movie_seat = MovieSeat.query.filter_by(movie_id=movie_id).first()
        if not movie_seat:
            movie_seat = MovieSeat(
                movie_id=movie_id,
                price=get_movie_price(movie_id)
            )
            db.session.add(movie_seat)
            for ticket in range(1,65):
                ticket = MovieTicket(
                    ticket_number=ticket,
                )
                movie_seat.ticket.append(ticket)
                db.session.add(ticket)
            db.session.commit()
        return True
    except:
        return False

def movie_handler(url,current_user):
    res = requests.get(url)
    if res.status_code == 200:
        result = extract_movie(res.text)
        if result:
            if url == app.config['NOW_SHOWING_URL']:
                for movie in result:
                    insert_movie = insert_movie_seat(movie['id'])
                    if not insert_movie:
                        return {'success': False}, 200
            movie_wishlist = [movie.to_short_json() for movie in current_user.saved_movies]
            print(movie_wishlist)
            return {'success':True,'data':[movie for movie in result if movie not in movie_wishlist]},200
    return {'success': False}, 200


def check_movie_video(movie_id):
    res = requests.get(f'https://web3.21cineplex.com/movie-trailer/{movie_id}.mp4')
    if res.status_code == 200:
        return {'success':True},200
    return {'success': False}, 200

def check_authentication(data):
    if not data.get('authToken'):
        return {'success':False},200
    token = decode_token(data['authToken'])
    if token:
        user = User.query.filter_by(token=token['token']).first()
        if user:
            return {'success':True,'username':user.username,'balance':user.balance},200
    return {'success':False},200
    

def insert_wishlist_handler(current_user,movie_id):
    movie = SavedMovie.query.filter_by(movie_id=movie_id,user_id=current_user.id).first()
    if not movie:
        movie_detail = get_movie_detail(movie_id=movie_id,current_user=current_user)
        movie = SavedMovie(
            movie_id=movie_detail[0]['data']['id'],
            movie_title=movie_detail[0]['data']['title'],
            movie_poster=movie_detail[0]['data']['image'],
            movie_duration=movie_detail[0]['data']['duration'],
            movie_genre=movie_detail[0]['data']['genre'],
            movie_director=movie_detail[0]['data']['director'],
            movie_cast=movie_detail[0]['data']['cast'],
            movie_synopsis=movie_detail[0]['data']['description'],
            movie_trailer=movie_detail[0]['data']['trailer'],
            user_id=current_user.id
        )
        db.session.add(movie)
        db.session.commit()
        return {'success':True},200
    return {'success':False},200

def delete_wishlist_handler(current_user,movie_id):
    movie = SavedMovie.query.filter_by(movie_id=movie_id,user_id=current_user.id).first()
    if movie:
        db.session.delete(movie)
        db.session.commit()
        return {'success':True},200
    return {'success':False},200


def topup_handler(current_user,data):
    if not data.get('amount'):
        return {'success':False},200
    current_user.balance += int(data['amount'])
    db.session.commit()
    return {'success':True,'balance':current_user.balance},200

def withdraw_balance_handler(current_user,data):
    print('aaaa')
    if current_user.balance < 500000:
        print(1)
        return {'success':False,'message':'Saldo tidak lebih dari 500000'},200
    if not data.get('amount'):
        print(2)
        return {'success':False},200
    if current_user.balance < int(data['amount']):
        print(3)
        return {'success':False,'message':'Saldo tidak cukup!'},200
    current_user.balance -= int(data['amount'])
    if current_user.balance < 500000:
        print(4)
        return {'success':False,'message':'Saldo tidak lebih dari 500000 setelah withdraw'},200
    db.session.commit()
    return {'success':True,'balance':current_user.balance},200

def get_seat_list_handler(movie_id,current_user):
    movie_seat = MovieSeat.query.filter_by(movie_id=movie_id).first()
    if movie_seat:
        movie = get_movie_detail(current_user=current_user,movie_id=movie_id)[0]['data']
        movie_title = movie['title']
        print(movie_title)
        return {'success':True,
                'data':[ticket.to_json() for ticket in movie_seat.ticket],
                'movie_title':movie_title,
                'price':movie_seat.price,
                },200
    return {'success':False},200

def book_ticket_handler(current_user,data):
    try:
        if not data.get('list_seat') or not data.get('movie_id'):
            return {'success':False},200
        if len(data['list_seat']) > 6:
            return {'success':False,'message':'Maksimal 6 tiket!'},200
        movie_seat = MovieSeat.query.filter_by(movie_id=data['movie_id']).first()
        if movie_seat.price > current_user.balance:
            return {'success':False,'message':'Saldo tidak cukup!'},200
        current_user.balance -= movie_seat.price * len(data['list_seat'])
        for ticket_number in data['list_seat']:
            movie_ticket = MovieTicket.query.filter_by(movie_seat_id=movie_seat.id, ticket_number=ticket_number).first()

            print(movie_ticket)
            if not movie_ticket or movie_ticket.user_id:
                return {'success':False,'message':'Tiket sudah dibeli!'},200
            movie_ticket.user_id = current_user.id
            current_user.movie_ticket.append(movie_ticket)
        db.session.commit()
        return {'success':True,'balance':current_user.balance},200
    except Exception as e:
        print(e)
        return {'success':False,'message':'error mak'},200
    
def get_booked_ticket_handler(current_user):
        tickets = [ticket.full_json() for ticket in current_user.movie_ticket]
        res_tickets = []
        for ticket in tickets:
            movie_seat = MovieSeat.query.filter_by(id=ticket['movie_seat_id']).first()
            ticket['price'] = movie_seat.price
            movie_detail = get_movie_detail(current_user=current_user,movie_id=movie_seat.movie_id)[0]['data']
            ticket['image'] = movie_detail['image']
            ticket['title'] = movie_detail['title']
            res_tickets.append(ticket)
        return {'success':True,'data':res_tickets},200

def reffund_ticket_handler(current_user,data):
    if not data.get('ticket_id'):
        return {'success':False},200
    movie_ticket = MovieTicket.query.filter_by(id=data['ticket_id']).first()
    if movie_ticket:
        if movie_ticket.user_id != current_user.id:
            return {'success':False,'message':'Tiket tidak ditemukan!'},200
        movie_ticket.user_id = None
        current_user.balance += movie_ticket.movie_seat.price
        db.session.commit()
        return {'success':True,'balance':current_user.balance},200