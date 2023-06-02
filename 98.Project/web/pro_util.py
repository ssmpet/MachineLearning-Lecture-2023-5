import numpy as np
import pandas as pd
import os, re, string, joblib, json
import requests

##########################################################
# get_weather : 현재 위치의 날씨 정보 얻어오기
##########################################################
def current_location():
    here_req = requests.get("http://www.geoplugin.net/json.gp")

    crd = {}
    if (here_req.status_code != 200):
        print("현재좌표를 불러올 수 없음")
        return ''
    else:
        location = json.loads(here_req.text)
        crd = {"lat": str(location["geoplugin_latitude"]), "lng": str(location["geoplugin_longitude"])}

    return crd

def get_weather(app):

    crd = current_location()

    if crd == '': return ''

    filename = os.path.join(app.static_folder, 'key/openweather.txt')
    with open(filename) as f:
        weather_key = f.read().strip()

    base_url  = 'https://api.openweathermap.org/data/2.5/weather'
    # icon_deps = 'https://api.openweathermap.org/img/w/'

    url = f"{base_url}?lat={crd['lat']}&lon={crd['lng']}&appid={weather_key}&units=metric&lang=kr"
    result = requests.get(url).json()

    desc = result['weather'][0]['description']

    return desc


##########################################################
# search_songs : 노래 제목과 가수 검색해서 결과값 리턴
##########################################################
def search_songs(key_title, key_artist, app):

    # print(key_title, key_artist)
    filename = os.path.join(app.static_folder, 'data/melon_song_v3.csv')
    # filename = '../data/melon_song_v2.csv'

    try:
        df = pd.read_csv(filename)
    except:
        return []
    
    # df.date.fillna(0, inplace=True)
    # df['date'] = df.date.astype(int).astype(str)
    df.fillna('', inplace=True)
    df.songId = df.songId.astype(str)
    # 노래 제목과 가수로 찾기
    
    key_title = re.sub('['+string.punctuation+']', '', key_title)
    key_artist = re.sub('['+string.punctuation+']', '', key_artist)

    songIds =  df[df.title.str.replace('['+string.punctuation+']','', regex=True).str.contains(key_title, case=False) 
                  & df.artist.str.replace('['+string.punctuation+']','', regex=True).str.contains(key_artist, case=False)][['songId', 'title', 'artist', 'album', 'date', 'img']].to_dict('records')
    
    return songIds

########## end of search_songs ###########################


##########################################################
# propose : 해당 노래에 대해 여러가지로 추천
##########################################################
def propose(find_songId, app):

    def get_recommendation(songId, cos_sim):
        index = indices[songId]
        sim_scores = pd.Series(cos_sim[index])
        song_indices = sim_scores.sort_values(ascending=False).head(31).tail(30).index
        return df.songId.iloc[song_indices]

    # filename = '../data/melon_song_v2.csv'
    # plist_filename1 = '../data/melon_playlist1.csv'
    # plist_filename2 = '../data/melon_playlist2_v2.csv'
    try:

        filename = os.path.join(app.static_folder, 'data/melon_song_v3.csv')
        plist_filename1 = os.path.join(app.static_folder, 'data/melon_playlist1.csv')
        plist_filename2 = os.path.join(app.static_folder, 'data/melon_playlist2_v2.csv')
        cosine_sim_filename = os.path.join(app.static_folder, 'data/melon_cosine_sim.sim')
 
        df = pd.read_csv(filename)
        plist1 = pd.read_csv(plist_filename1)
        plist2 = pd.read_csv(plist_filename2)
        # consine 유사도 파일로 불러오기
        cosine_sim = joblib.load(cosine_sim_filename)

    except:
        return '', {}, [], [], []
    

    # 1. 데이터 처리를 위한 작업
    ###############################################
    plist1.plylstSeq = plist1.plylstSeq.astype(str)
    plist2.songId = plist2.songId.astype(str)

    # df.date.fillna(0, inplace=True)
    # df['date'] = df.date.astype(int).astype(str)
    df.fillna('', inplace=True)
    df['comment_like_total'] = df.comment + df.like
    df['songId'] = df.songId.astype(str)
    df.lyric = df.lyric.str.replace('\r', '')

    # 곡 정보 추가
    ###############################################
    self_song = df[df.songId == find_songId][['title', 'artist', 'album', 'date', 'genre', 'img', 'ly_summary']].to_dict('records')[0]
    # if self_song['date'] != '0' : self_song['date'] = self_song['date'][:4] +'.' + self_song['date'][4:6] + '.' + self_song['date'][6:]
    

    # 2. index 매칭
    ###############################################
    indices = pd.Series(df.index, index=df.songId)


    # 3. 컨텐츠 기반 추천
    ###############################################
    a = get_recommendation(find_songId, cosine_sim).to_frame()
    pro_contents = df[df['songId'].isin(a.songId[1:6])][['songId', 'title', 'artist', 'img']].to_dict('records')
    

    # 4. 숨은 명곡 추천
    ###############################################
    # 찾고 싶은 구간 정하기
    numbers = df['comment_like_total']
    sorted_numbers = np.sort(numbers)
    q1 = np.percentile(sorted_numbers, 25)
    q2 = np.percentile(sorted_numbers, 50)
    filtered_data = df[(df['comment_like_total'] >= q1) & (df['comment_like_total'] < q2)]
    filtered_data = filtered_data[['songId', 'comment_like_total']]

    # 명곡 컨텐츠 추천
    # 유사도 top 30 중 원하는 구간에 있는 songId 추출(유사도순)
    d = a[a['songId'].isin(filtered_data.songId.values)].head(5)
    pro_meong = df[df['songId'].isin(d.songId.values[:5])][['songId', 'title', 'artist', 'img']].to_dict('records')


    # 5. 플레이리스트 추천
    ###############################################
    # 가장 많이 들어간 tag 찾기

    tags = np.unique(' '.join(plist1[plist1.songIds.str.contains(find_songId)]['tag'].values).split(), return_counts=True)
    # argsort : 값이 큰 순서대로 값의 인덱스 정렬 -1 큰 순서대로

    if len(tags[0]) :
        re_count = np.argsort(-tags[1]) 
        if len(re_count) > 2:
            pro_tags = f"{tags[0][re_count][0]}, {tags[0][re_count][1]} 그리고 {tags[0][re_count][2].strip('#')}"
        elif len(re_count) == 2:
            pro_tags = f"{tags[0][re_count][0]} 그리고 {tags[0][re_count][1]}"
        else:
            pro_tags = f"{tags[0][re_count][0]}"

    else:
        pro_tags = ''

    # 가장 많이 들어가 songId 찾기
    songs = np.unique(' '.join(plist1[plist1.songIds.str.contains(find_songId)]['songIds'].values).replace(find_songId + ' ', '').split(), return_counts=True)

    cnt = 0
    song_list = []

    # argsort 값을 sort해서 값의 index를 오름차순으로 '-' 해주면 내림차순으로
    for s_id in songs[0][np.argsort(-songs[1])]:    
        if not df[df.songId.isin([s_id])].empty : # df에 있으면 추가
            cnt += 1
            song_list.append(s_id)
        if cnt == 5 : break
    

    # 해당 songId 들 정보 출력
    # 없으면 플레이리스트2에 있는 songId 에서 정보 가져오기
    pro_psongs = df[df.songId.isin(song_list)][['songId', 'title', 'artist', 'img']]

    if pro_psongs.empty:
        pro_psongs = plist2[plist2.songId.isin(song_list)]

    pro_psongs = pro_psongs.to_dict('records')

    # print(pro_tags, pro_contents, pro_meong, pro_psongs)

    return pro_tags, self_song, pro_contents, pro_meong, pro_psongs
########## end of propose ##############################






# # # 키워드 바꿔가면서 찾아보기
# key_title = '안녕'
# key_artist = '성시경'

# ## 테스트
# songIds = search_songs(key_title, key_artist)
# print(songIds[0]['songId'])

# propose(songIds[0]['songId'])
