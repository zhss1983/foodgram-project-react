import csv
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_BASE = os.path.join(BASE_DIR, 'db.sqlite3')
path_category = os.path.join(BASE_DIR, 'static', 'data', 'category.csv')
path_users = os.path.join(BASE_DIR, 'static', 'data', 'users.csv')
path_genre = os.path.join(BASE_DIR, 'static', 'data', 'genre.csv')
path_titles = os.path.join(BASE_DIR, 'static', 'data', 'titles.csv')
path_review = os.path.join(BASE_DIR, 'static', 'data', 'review.csv')
path_genre_title = os.path.join(BASE_DIR, 'static', 'data', 'genre_title.csv')
path_comments = os.path.join(BASE_DIR, 'static', 'data', 'comments.csv')

path_db = {
    'users_user': path_users,
    'reviews_category': path_category,
    'reviews_genre': path_genre,
    'reviews_title': path_titles,
    'reviews_review': path_review,
    'reviews_title_genre': path_genre_title,
    'reviews_comment': path_comments
}

con = sqlite3.connect(DATA_BASE)
cur = con.cursor()

# name - имя таблици
# path - путь до csv файла
a_file = open(path, 'r', encoding='utf-8')
rows = csv.reader(a_file, delimiter=';')
items = rows.__next__()
print(items)
count = ','.join('?' * len(items))
cur.executemany(f'INSERT INTO {name} VALUES ({count})', rows)
cur.execute(f'SELECT * FROM {name}')
print(cur.fetchall())

con.commit()
con.close()
