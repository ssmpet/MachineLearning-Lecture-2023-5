from flask import Flask , render_template, request
import pro_util as bbb
import os
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():

    return 'Hello Flask'

@app.route('/best_psong')
def best_psong():
    
    filename = os.path.join(app.static_folder, 'data/best_song2.csv')

    df = pd.read_csv(filename)
    df.songId = df.songId.astype(str)

    df = df.sort_values('p_count', ascending=False)[['songId', 'title', 'artist', 'album', 'date', 'img', 'p_count']].head(10)
    songs = df.to_dict('records')

    return render_template('best_psong.html', songs=songs)


if __name__ == '__main__': 
    app.run(debug=True)