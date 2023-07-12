# from backend.controller import app,now_showing_handler



# now_showing_handler()

import requests
import re


def get_contents_from_html(html, class_name):
    movie_details = {}
    title_genre = fr'<div class="{class_name}"(?:\s+\w+="[^"]*")*>(?:\s*<[^>]+>)?(.*?)</div>'
    title_genre_matches = re.findall(title_genre, html)
    if title_genre_matches:
        movie_details['title'] = title_genre_matches[0]
        movie_details['genre'] = title_genre_matches[1]
        duration_trailer = get_duration_and_trailer_from_html(html)
        desc_cast_dir = get_desc_cast_dir(html)
        if not duration_trailer or not desc_cast_dir:
            return False
        movie_details['duration'] = duration_trailer[0]
        movie_details['trailer'] = duration_trailer[1]
        movie_details['description'] = desc_cast_dir[0]
        movie_details['cast'] = desc_cast_dir[1]
        movie_details['director'] = desc_cast_dir[2]
        return movie_details
    return False

def get_desc_cast_dir(html):
    description_pattern = r'<p id="description">(.*?)</p>'
    cast_pattern = r'<p style="margin-bottom: 5px"><strong>Cast</strong>:</p>\s*<p>(.*?)</p>'
    director_pattern = r'<p style="margin-bottom: 5px"><strong>Director</strong>:</p>\s*<p>(.*?)</p>'
    description_match = re.search(description_pattern, html)
    cast_match = re.search(cast_pattern, html)
    director_match = re.search(director_pattern, html)
    description = description_match.group(1) if description_match else None
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



def get_image_url_from_html(html):
    pattern = r'<div class="col-md-3 col-sm-6 col-xs-6">\s*<img src="(.*?)" class="img-responsive pull-left gap-left".*?>\s*</div>'
    match = re.search(pattern, html)
    if match:
        image_url = match.group(1)
        return image_url
    return False


req = requests.get('https://m.21cineplex.com/gui.movie_details.php?sid=&movie_id=22MIM7')
print(get_image_url_from_html(req.text))