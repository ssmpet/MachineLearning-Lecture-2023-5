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

        artist = request.form['artist']
        title = request.form['title']

        songs = bbb.search_songs(title, artist, app)

        return render_template('result.html', songs=songs)


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':

        songId = request.form['optradio']
        pro_tags, self_song, pro_contents, pro_meong, pro_psongs = bbb.propose(songId, app)

        return render_template('final.html', pro_tags=pro_tags, self_song=self_song, pro_contents=pro_contents, pro_meong=pro_meong, pro_psongs=pro_psongs)

@app.route('/weather_time/<int:kind>')
def weather_time(kind):
    
    # print('weather_time')
    desc, img_name, songs = bbb.get_weather_time(app, kind)
    # print('weather_time1')
    return render_template('weather_time.html', order=kind, desc=desc, img_name=img_name, songs=songs)

if __name__ == '__main__': 
    app.run(debug=False)