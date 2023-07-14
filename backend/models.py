from backend import app,db,bcrypt


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    token = db.Column(db.String(300),unique=True,nullable=False)
    username = db.Column(db.String(100),unique=True,nullable=False)
    password_hash = db.Column(db.String(300))
    balance = db.Column(db.Integer,default=0)
    saved_movies = db.relationship('SavedMovie',backref='user',lazy=True)
    movie_ticket = db.relationship('MovieTicket',backref='user',lazy=True)
    @property
    def password(self):
        return self.password
    @password.setter
    def password(self,plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('UTF-8')
    def check_password_correction(self,attempted_password):
        return bcrypt.check_password_hash(self.password_hash,attempted_password)

class MovieSeat(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    movie_id = db.Column(db.String(15))
    price = db.Column(db.Integer)
    ticket = db.relationship('MovieTicket',backref='movie_seat',lazy=True)

class MovieTicket(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    ticket_number = db.Column(db.Integer,nullable=False)
    movie_seat_id = db.Column(db.Integer,db.ForeignKey('movie_seat.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def to_json(self):
        return {
            'seat_number':self.ticket_number,
            'is_sold':True if self.user_id else False,
            'is_book':True if self.user_id else False
        }
    
    def full_json(self):
        return {
            'ticket_id':self.id,
            'seat_number':self.ticket_number,
            'movie_seat_id':self.movie_seat_id,
        }


class SavedMovie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    movie_id = db.Column(db.String(100),nullable=False)
    movie_title = db.Column(db.String(100),nullable=False)
    movie_poster = db.Column(db.String(100),nullable=False)
    movie_duration = db.Column(db.String(100),nullable=False)
    movie_genre = db.Column(db.String(100),nullable=False)
    movie_director = db.Column(db.String(100),nullable=False)
    movie_cast = db.Column(db.String(300),nullable=False)
    movie_synopsis = db.Column(db.String(1000),nullable=False)
    movie_trailer = db.Column(db.String(100),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def to_json(self):
        return {
            'id': self.movie_id,
            'title': self.movie_title,
            'image': self.movie_poster,
            'duration': self.movie_duration,
            'genre': self.movie_genre,
            'director': self.movie_director,
            'cast': self.movie_cast,
            'description': self.movie_synopsis,
            'trailer': self.movie_trailer
        }
    
    def to_short_json(self):
        return {
            'id': self.movie_id,
            'title': self.movie_title,
            'image': self.movie_poster
        }
