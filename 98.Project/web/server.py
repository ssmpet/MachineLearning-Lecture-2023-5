from flask import Flask , render_template, request, session, flash, redirect
import pro_util as bbb
import user_dao, user_searched_dao
import hashlib, base64, json

app = Flask(__name__)
app.secret_key = 'ehwjsgoTwyvmfhwprtm12345'
app.config['SESSION_COOKIE_PATH'] = '/'


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

        try:
            songId = request.form['optradio']
        except:
            return render_template('final.html', pro_tags='', self_song=[], pro_contents=[], pro_meong=[], pro_psongs=[])

        if 'uid' in session : 
            uid = session['uid']
        else:
            uid = ''

        pro_tags, self_song, pro_contents, pro_meong, pro_psongs = bbb.propose(uid, songId, app)

        return render_template('final.html', pro_tags=pro_tags, self_song=self_song, pro_contents=pro_contents, pro_meong=pro_meong, pro_psongs=pro_psongs)
    else:
    
        return "잘못된 접근 방식입니다."


@app.route('/my_result/<songId>')
def my_result(songId):

    if songId == '' :
        return "잘못된 접근 방식입니다."

    pro_tags, self_song, pro_contents, pro_meong, pro_psongs = bbb.propose('', songId, app)

    return render_template('final.html', pro_tags=pro_tags, self_song=self_song, pro_contents=pro_contents, pro_meong=pro_meong, pro_psongs=pro_psongs)


@app.route('/weather_time/<int:kind>')
def weather_time(kind):

    desc, img_name, songs = bbb.get_weather_time(app, kind)

    return render_template('weather_time.html', kind=kind, desc=desc, img_name=img_name, songs=songs)


@app.route('/login_check', methods=['POST']) 
def login_check():

    if request.method == 'POST':
        uid = request.form['uid']
        pwd = request.form['pwd']

        user_info = user_dao.get_user_by_info(uid)
        if user_info :
            db_pwd = user_info[2]

            pwd_sha256 = hashlib.sha256(pwd.encode())
            hased_pwd = base64.b64encode(pwd_sha256.digest()).decode('utf-8')
            if hased_pwd == db_pwd:   
                return "1"
            else:
                return "-1"
        else:
            return "0"
    else:
        return "잘못된 접근 방식입니다."

@app.route('/uid_check', methods=['POST']) 
def uid_check():

    if request.method == 'POST':
        uid = request.form['uid']
        user_info = user_dao.get_user_by_uid(uid)
        # print(user_info)
        if user_info:
            return "1"
        return "0"
    else:
        return "잘못된 접근 방식입니다."


@app.route('/login', methods=['GET', 'POST']) 
def login():

    if request.method == 'GET':
        
        return render_template('login.html')

    else:

        uid = request.form['uid']
        pwd = request.form['pwd']

        user_info = user_dao.get_user_by_info(uid)

        if user_info :

            db_pwd = user_info[2]

            pwd_sha256 = hashlib.sha256(pwd.encode())
            hased_pwd = base64.b64encode(pwd_sha256.digest()).decode('utf-8')

            if hased_pwd == db_pwd:     

                flash(f'{user_info[1]}님 환영합니다.', category="info")   # 초기 화면으로 보내줌
                session['uid'] = uid                   # 세션값을 설정함으로써 사용자가 로그인하였음을 알게 함
                session['uname'] = user_info[1]
                session['birthday'] = user_info[3]
                session['gender'] = user_info[4]
                session['email'] = user_info[5]
                return redirect('/first')
            else:
                flash('비밀번호가 틀립니다.', category="error")   # 로그인 화면을 다시 보내줌
                return redirect('/login')

        else:
            flash('가입되어 있지 않은 사용자 ID입니다. 회원가입을 해 주세요.', category="info")    # 회원 가입 페이지로 안내 or 다시 로그인
            return redirect('/signup')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # print('signup')
    if request.method == 'GET':

        return render_template('signup.html')

    else:

        uid = request.form['uid']

        if user_dao.get_user_by_uid(uid) :
            flash('이미 사용자 ID가 있습니다. 다른 ID를 이용하세요.')
            return redirect('/signup')

        pwd = request.form['pwd']
        pwd2 = request.form['pwd2']

        if pwd != pwd2 :
            flash('패스워드가 일치하지 않습니다.')
            return redirect('/signup')

        uname = request.form['uname']
        email = request.form['email']
        gender = request.form['gender']
        email = request.form['email']
        birthday = request.form['birthday']

        pwd_sha256 = hashlib.sha256(pwd.encode())
        hased_pwd = base64.b64encode(pwd_sha256.digest()).decode('utf-8')

        user_dao.insert_user((uid, uname, hased_pwd, int(gender), email, birthday))

        session['uid'] = uid
        session['uname'] = uname
        session['gender'] = gender
        session['email'] = email
        session['birthday'] = birthday

        return redirect('/first')

@app.route('/update', methods=['GET', 'POST'])
def update():
    
    if request.method == 'GET':
        return render_template('update.html')
    else:

        pwd = request.form['pwd']
        pwd2 = request.form['pwd2']
        if pwd != pwd2 :
            flash('패스워드가 일치하지 않습니다.')
            return redirect('/update')
        
        uname = request.form['uname']
        gender = request.form['gender']
        email = request.form['email']
        birthday = request.form['birthday']

        pwd_sha256 = hashlib.sha256(pwd.encode())
        hased_pwd = base64.b64encode(pwd_sha256.digest()).decode('utf-8')
        user_dao.update_user((uname, hased_pwd, int(gender), email, birthday, session['uid']))

        session['uname'] = uname
        session['gender'] = gender
        session['email'] = email
        session['birthday'] = birthday

        return redirect('/first')


@app.route('/user_delete/<uid>')
def user_delete(uid):
    user_dao.delete_user(uid)
    session.clear()
    return redirect('/first')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/first')

@app.route('/mypage')
def mypage():

    if 'uid' in session:
        uid = session['uid']
    else:
        return "잘못된 접근 방식입니다."

    songs = user_searched_dao.get_user_by_search_record(uid)
    return render_template('mypage.html', songs=songs)

if __name__ == '__main__': 
    app.run(debug=True)