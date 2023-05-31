import numpy as np
import pandas as pd
import os, re, string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

##########################################################
# search_songs : 노래 제목과 가수 검색해서 결과값 리턴
##########################################################
def search_songs(key_title, key_artist, app):
# def search_songs(key_title, key_artist):

    print(key_title, key_artist)
    filename = os.path.join(app.static_folder, 'data/melon_song_v2.csv')
    # filename = '../data/melon_song_v2.csv'

    try:
        df = pd.read_csv(filename)
    except:
        return []
    
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
# def propose(find_songId):

    def get_recommendation(songId, cos_sim):
        index = indices[songId]
        sim_scores = pd.Series(cos_sim[index])
        song_indices = sim_scores.sort_values(ascending=False).head(31).tail(30).index
        return df.songId.iloc[song_indices]

    # filename = '../data/melon_song_v2.csv'
    # plist_filename1 = '../data/melon_playlist1.csv'
    # plist_filename2 = '../data/melon_playlist2_v2.csv'
    filename = os.path.join(app.static_folder, 'data/melon_song_v2.csv')
    plist_filename1 = os.path.join(app.static_folder, 'data/melon_playlist1.csv')
    plist_filename2 = os.path.join(app.static_folder, 'data/melon_playlist2_v2.csv')

    try:
        df = pd.read_csv(filename)
        plist1 = pd.read_csv(plist_filename1)
        plist2 = pd.read_csv(plist_filename2)
    except:
        return [], [], []
    

    # 1. 데이터 처리를 위한 작업
    ###############################################
    plist1.plylstSeq = plist1.plylstSeq.astype(str)
    plist2.songId = plist2.songId.astype(str)

    df.date.fillna(0, inplace=True)
    df['date'] = df.date.astype(int).astype(str)
    df.fillna('', inplace=True)
    df['comment_like_total'] = df.comment + df.like
    df['songId'] = df.songId.astype(str)
    df.lyric = df.lyric.str.replace('\r', '')

    
    # 2. 학습할 데이터열 생성
    ###############################################
    # df['total'] = df.morphs + (' ' + df.title) + (' ' + df.artist) * 2 + (' ' + df.composer) * 2 + (' ' + df.lyricist) * 2 + (' ' + df.genre) * 3
    # df.set_index('songId', inplace=True)
    # df.reset_index(inplace=True)

    indices = pd.Series(df.index, index=df.songId)

    tvect = TfidfVectorizer(stop_words='english')
    total_tv = tvect.fit_transform(df.total)
    cosine_sim = cosine_similarity(total_tv)

   
    # 3. 컨텐츠 기반 추천 넘겨줄 것
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
    
    # 명곡 컨텐츠 넘겨줄 것
    # 유사도 top 30 중 원하는 구간에 있는 songId 추출(유사도순)
    d = a[a['songId'].isin(filtered_data.songId.values)].head(5)
    pro_meong = df[df['songId'].isin(d.songId.values[:5])][['songId', 'title', 'artist', 'img']].to_dict('records')


    # 5. 플레이리스트 추천
    ###############################################
    # 가장 많이 들어간 tag 찾기
    tags = np.unique(' '.join(plist1[plist1.songIds.str.contains(find_songId)]['tag'].values).split(), return_counts=True)
    df_tags = pd.DataFrame({'tag' : tags[0], 'count' : tags[1]})
    pro_tags = ' '.join(df_tags.sort_values('count', ascending=False).head(2)['tag'])

    # 가장 많이 들어가 songId 찾기
    songs = np.unique(' '.join(plist1[plist1.songIds.str.contains(find_songId)]['songIds'].values).replace(find_songId, '').split(), return_counts=True)
    df_songs = pd.DataFrame({'songId' : songs[0], 'count' : songs[1]})
    song_list = df_songs.sort_values('count', ascending=False).head(5)['songId'].values


    # 해당 songId 들 정보 출력
    # 없으면 플레이리스트2에 있는 songId 에서 정보 가져오기
    pro_psongs = df[df.songId.isin(song_list)][['songId', 'title', 'artist', 'img']]

    if pro_psongs.empty:
        pro_psongs = plist2[plist2.songId.isin(song_list)]

    pro_psongs = pro_psongs.to_dict('records')

    # print(pro_tags, pro_contents, pro_meong, pro_psongs)

    return pro_tags, pro_contents, pro_meong, pro_psongs
########## end of propose ##############################






# # 키워드 바꿔가면서 찾아보기
# key_title = '아무 일도, 아무것도'
# key_artist = '송이한'

# ## 테스트
# songIds = search_songs(key_title, key_artist)
# print(songIds[0]['songId'])

# propose(songIds[0]['songId'])
