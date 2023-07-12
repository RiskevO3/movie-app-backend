from backend import app
import requests
import re


def get_thumbnail(html):
    pattern = r'<div class="col-md-3 col-sm-6 col-xs-6">\s*<img src="(.*?)" class="img-responsive pull-left gap-left".*?>\s*</div>'
    match = re.search(pattern, html)
    if match:
        image_url = match.group(1)
        image_url = re.sub(r'https://web3.21cineplex.com', app.config['WEB_URL'], image_url)
        return image_url
    return False

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


def get_movie_detail(movie_id):
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
        if not duration_trailer or not desc_cast_dir or not image_url:
            return False
        movie_details['duration'] = duration_trailer[0]
        movie_details['trailer'] = duration_trailer[1]
        movie_details['description'] = desc_cast_dir[0]
        movie_details['cast'] = desc_cast_dir[1]
        movie_details['director'] = desc_cast_dir[2]
        movie_details['image'] = image_url
        return {'success':True,'data':movie_details},200
    return {'success': False}, 200

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

def movie_handler(url):
    res = requests.get(url)
    if res.status_code == 200:
        result = extract_movie(res.text)
        if result:
            return {'success':True,'data':result},200
    return {'success': False}, 200


def check_movie_video(movie_id):
    res = requests.get(f'https://web3.21cineplex.com/movie-trailer/{movie_id}.mp4')
    if res.status_code == 200:
        return {'success':True},200
    return {'success': False}, 200

@app.route('/<path:url_path>')
def proxy_movie_trailer(url_path):
    original_url = "https://web3.21cineplex.com/" + url_path
    response = requests.get(original_url)
    headers = response.headers
    content_type = headers.get('content-type')
    # Mengembalikan respons dengan konten dan tipe konten yang sama
    return response.content, 200, {'Content-Type': content_type}
