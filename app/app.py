from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import random
import os
import json
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)

with open('keys.json') as f:
    keys = json.load(f)
APPID = keys['appid']
USERID = keys['userid']

WIKIPEDIA_API_URL = "https://fi.wikipedia.org/w/api.php"

def fetch_random_pages_with_images():
    valid_pages = []
    max_attempts = 5  # Limit to prevent infinite loops
    attempt = 0
    headers={'User-Agent': f'{APPID} ({USERID})'}
    logging.debug(headers)
    while len(valid_pages) < 3 and attempt < max_attempts:
        attempt += 1
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'random',
            'rnnamespace': 0,
            'rnlimit': 5,  # Fetch more pages to increase the chance of finding images
        }
        response = requests.get(WIKIPEDIA_API_URL, params=params, headers=headers)
        if response.ok:
            data = response.json()
            logging.debug(data)
            pages = data['query']['random']
            for page in pages:
                title = page['title']
                image_response = requests.get(WIKIPEDIA_API_URL, params={
                    'action': 'query',
                    'format': 'json',
                    'titles': title,
                    'prop': 'pageimages',
                    'piprop': 'original',
                }, headers=headers)
                image_data = image_response.json()
                page_data = next(iter(image_data['query']['pages'].values()))
                if 'original' in page_data:
                    valid_pages.append((title, page_data['original']['source']))
                    if len(valid_pages) >= 3:
                        break
    return valid_pages

def fetch_page_summary(title):
    headers={'User-Agent': f'{APPID} ({USERID})'}
    response = requests.get(WIKIPEDIA_API_URL, params={
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'extracts',
        'exintro': True,
        'exchars': 300,  # Limit the summary length
    }, headers=headers)
    data = response.json()
    page_data = next(iter(data['query']['pages'].values()))
    extract = page_data.get('extract', '')

    # Remove HTML tags using BeautifulSoup
    clean_text = BeautifulSoup(extract, "html.parser").get_text()
    return clean_text


@app.route('/', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        user_answer = request.form['answer']
        correct_answer = request.form['correct_answer']
        image_url = request.form['quiz_image']
        elapsed_time = float(request.form['elapsed_time'])  # Time in seconds
        if user_answer == correct_answer:
            result = f"Oikein! Arvasit oikein ajassa {elapsed_time} sekuntia!"
        else:
            result = f"Väärin. Oikea vastaus on: {correct_answer}"
        summary = fetch_page_summary(correct_answer)
        return render_template('result.html', result=result, correct_answer=correct_answer, explanation=summary, image_url=image_url)

    pages_with_images = fetch_random_pages_with_images()
    logging.debug(pages_with_images)
    if pages_with_images and any(img for _, img in pages_with_images):
        correct_page = pages_with_images[0]
        random.shuffle(pages_with_images)
        options = [page[0] for page in pages_with_images]
        logging.info(options)
        return render_template('quiz.html', image_url=correct_page[1], correct_answer=correct_page[0], options=options)
    return "No suitable page found, please refresh."

if __name__ == '__main__':
    app.run(debug=True, port=5500, host="0.0.0.0")

