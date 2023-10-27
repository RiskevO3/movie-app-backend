
# Movie App Backend Api
Repository tugas movie app untuk mengikuti SEA Compfest,
API ini dibuat dari hasil scrape https://21cineplex.com/.




## Deployment

Untuk mendeploy pada localhost, install package terlebih dahulu dengan:

```bash
  pip install -r requirements.txt
```

Kemudian, untuk membuat static database, kalian dapat menjalankan command:

```bash
  python3 create_db.py
```

Setelah DB terbuat, anda dapat menjalankan command dibawah ini untuk menjalankan lada localhost:5001 :

```bash
  python3 app.py
```
*Jika ingin merubah port, anda dapat merubahnya pada file app.py

## Environment Variables

untuk menjalakan project ini, anda harus mensetup beberapa env variabel, yaitu:

`SECRET_KEY` : secret key aplikasi anda


`SQLALCHEMY_DATABASE_URI` : url string dari database, ex: sqlite:///db.sqlite3


`WEB_URL` : url dari api anda dideploy


`NOW_SHOWING_URL` : url website cinema 21


`COMING_SOON_URL` : url website cinema 21


`MOVIE_DETAIL_URL`: url website cinema 21


`MOVIE_TICKET_URL`: url website cinema 21




## Demo

API URL dapat anda akses pada:

https://movie-app-api-9ne6.onrender.com

