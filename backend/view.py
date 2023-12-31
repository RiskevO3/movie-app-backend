from backend.controller import\
    app,\
    token_required,\
    movie_handler,\
    get_movie_detail,\
    check_movie_video,\
    login_handler,\
    check_authentication,\
    logout_handler,\
    insert_wishlist_handler,\
    delete_wishlist_handler,\
    get_wishlist_handler,\
    register_handler,\
    topup_handler,\
    withdraw_balance_handler,\
    get_seat_list_handler,\
    book_ticket_handler,\
    get_booked_ticket_handler,\
    reffund_ticket_handler

from flask import request
import json
import requests

@app.route('/login',methods=['POST'])
def login():
    data = json.loads(request.data.decode('UTF-8'))
    return login_handler(data=data)

@app.route('/register',methods=['POST'])
def register():
    data = json.loads(request.data.decode('UTF-8'))
    return register_handler(data=data)

@app.route('/logout')
@token_required
def logout(current_user):
    return logout_handler(current_user=current_user)

@app.route('/nowshowing')
@token_required
def now_showing(current_user):
    return movie_handler(url=app.config['NOW_SHOWING_URL'],current_user=current_user)

@app.route('/comingsoon')
@token_required
def coming_soon(current_user):
    return movie_handler(url=app.config['COMING_SOON_URL'],current_user=current_user)

@app.route('/auth',methods=['POST'])
def auth():
    data = json.loads(request.data.decode('UTF-8'))
    return check_authentication(data=data)

@app.route('/moviedetail/<movie_id>')
@token_required
def movie_detail(current_user,movie_id):
    return get_movie_detail(movie_id=movie_id,current_user=current_user)

@app.route('/bookedticket')
@token_required
def booked_ticket(current_user):
    return get_booked_ticket_handler(current_user=current_user)

@app.route('/reffundticket',methods=['POST'])
@token_required
def reffund_ticket(current_user):
    data = json.loads(request.data.decode('UTF-8'))
    return reffund_ticket_handler(current_user=current_user,data=data)

@app.route('/wishlist')
@token_required
def wishlist(current_user):
    return get_wishlist_handler(current_user=current_user)

@app.route('/checkvideo/<movie_id>')
@token_required
def check_video(current_user,movie_id):
    return check_movie_video(movie_id=movie_id)

@app.route('/insertwishlist',methods=['POST'])
@token_required
def insert_wishlist(current_user):
    movie_id = json.loads(request.data.decode('UTF-8'))
    print(movie_id)
    movie_id = movie_id['id']
    return insert_wishlist_handler(current_user=current_user,movie_id=movie_id)

@app.route('/deletewishlist',methods=['POST'])
@token_required
def delete_wishlist(current_user):
    movie_id = json.loads(request.data.decode('UTF-8'))['id']
    return delete_wishlist_handler(current_user=current_user,movie_id=movie_id)

@app.route('/seatlist/<movie_id>')
@token_required
def seat_list(current_user,movie_id):
    return get_seat_list_handler(current_user=current_user,movie_id=movie_id)

@app.route('/bookticket',methods=['POST'])
@token_required
def book_ticket(current_user):
    data = json.loads(request.data.decode('UTF-8'))
    return book_ticket_handler(current_user=current_user,data=data)

@app.route('/topup',methods=['POST'])
@token_required
def topup(current_user):
    data = json.loads(request.data.decode('UTF-8'))
    return topup_handler(current_user=current_user,data=data)

@app.route('/withdraw',methods=['POST'])
@token_required
def withdraw(current_user):
    data = json.loads(request.data.decode('UTF-8'))
    print(data)
    return withdraw_balance_handler(current_user=current_user,data=data)

@app.route('/<path:url_path>')
def proxy_movie_trailer(url_path):
    original_url = "https://web3.21cineplex.com/" + url_path
    response = requests.get(original_url)
    headers = response.headers
    content_type = headers.get('content-type')
    # Mengembalikan respons dengan konten dan tipe konten yang sama
    return response.content, 200, {'Content-Type': content_type}