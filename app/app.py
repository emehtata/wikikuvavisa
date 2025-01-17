from flask import Flask, render_template, request, g
from bs4 import BeautifulSoup
import requests
import argparse
import random
import os
import json
import logging
import secrets
import sqlite3
import __version__

DATABASE = 'quiz_results.db'

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)

with open('keys.json') as f:
    keys = json.load(f)
APPID = keys['appid']+f"-{secrets.token_hex(3)}"
USERID = keys['userid']

WIKIPEDIA_API_URL = "https://fi.wikipedia.org/w/api.php"

def get_version():
    return __version__.version

def get_db():
    try:
        conn = sqlite3.connect(DATABASE)
        logging.debug(f"Connected to database: {DATABASE}")
        conn.row_factory = sqlite3.Row  # Enables dict-like access to rows for easier debugging
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error when connecting to the database: {e}")
        raise

def init_db():
    try:
        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    page_name TEXT PRIMARY KEY,
                    image_url TEXT,
                    best_time REAL
                )
            ''')
            conn.commit()
            logging.info("Database initialized and results table created if it didn't exist.")
    except sqlite3.Error as e:
        logging.error(f"Error initializing database: {e}")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def save_result(page_name, image_url, elapsed_time):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            # Check if a result for this page already exists
            logging.debug(f"Checking existing results for page: {page_name}")
            cur.execute('SELECT best_time FROM results WHERE page_name = ?', (page_name,))
            row = cur.fetchone()
            if row:
                logging.debug(f"Found existing time for {page_name}: {row[0]} seconds")
            else:
                logging.debug(f"No existing record found for {page_name}")

            # Update if better time, or insert new
            if row is None or elapsed_time < row[0]:
                cur.execute('REPLACE INTO results (page_name, image_url, best_time) VALUES (?, ?, ?)',
                            (page_name, image_url, elapsed_time))
                conn.commit()
                logging.info(f"Result saved: {page_name}, time: {elapsed_time:.2f}s")
            else:
                logging.info(f"Better time not achieved for {page_name} (current best: {row[0]:.2f}s)")
    except sqlite3.Error as e:
        logging.error(f"Database error when saving result for page '{page_name}': {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

def get_top_results(limit=10):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT page_name, image_url, best_time
                FROM results
                ORDER BY best_time ASC
                LIMIT ?
            ''', (limit,))
            return cur.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error fetching top results: {e}")
        return []


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
            save_result(correct_answer, image_url, elapsed_time)
        else:
            result = f"Väärin. Oikea vastaus on: {correct_answer}"
        summary = fetch_page_summary(correct_answer)

        return render_template('result.html', result=result,
            correct_answer=correct_answer, explanation=summary, image_url=image_url, version=get_version(), top_results=get_top_results())

    pages_with_images = fetch_random_pages_with_images()
    logging.debug(pages_with_images)
    if pages_with_images and any(img for _, img in pages_with_images):
        correct_page = pages_with_images[0]
        random.shuffle(pages_with_images)
        options = [page[0] for page in pages_with_images]
        logging.info(options)
        return render_template('quiz.html', image_url=correct_page[1], correct_answer=correct_page[0], options=options, version=get_version())
    return "No suitable page found, please refresh."

@app.route('/results')
def show_results():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('SELECT page_name, image_url, best_time FROM results ORDER BY best_time ASC')
        rows = cur.fetchall()
    return render_template('results.html', results=rows)

def main():
    parser = argparse.ArgumentParser(description="Run the application.")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode")
    args = parser.parse_args()
    debug_mode = args.debug
    logging.info(f"Version {get_version()} starting...")
    init_db()
    app.run(debug=debug_mode, port=5500, host="0.0.0.0")

if __name__ == '__main__':
    main()
