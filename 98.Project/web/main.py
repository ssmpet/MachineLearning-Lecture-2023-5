import os
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask , render_template, request
import pro_util as bbb

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello Flask'

@app.route('/first', methods=['GET', 'POST'])
def first():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # print('post')
        artist = request.form['artist']
        title = request.form['title']


        songs = bbb.search_songs(title, artist, app)

        # pro_tags, pro_contents, pro_meong, pro_psongs = bbb.propose('songid')

        return render_template('result.html', songs=songs)
        # return render_template('result.html', pro_tags=pro_tags, pro_contents=pro_contents, pro_meong=pro_meong, pro_psongs=pro_psongs)

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        songId = request.form['optradio']
        # print(f'SongId = {songId}')
        pro_tags, pro_contents, pro_meong, pro_psongs = bbb.propose(songId, app)
        # print(pro_tags)
        # print(pro_contents)
        return render_template('final.html', pro_tags=pro_tags, pro_contents=pro_contents, pro_meong=pro_meong, pro_psongs=pro_psongs)


if __name__ == '__main__': 
    app.run(debug=True)