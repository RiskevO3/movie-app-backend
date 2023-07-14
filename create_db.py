from backend.controller import db,User,SavedMovie,app,generate_random_token,encode_token

with app.app_context():
    db.drop_all()
    db.create_all()
    user = User(
        username='admin',
        password='admin',
        token=generate_random_token()
    )
    print(encode_token({'token':user.token}))
    db.session.add(user)
    db.session.commit()