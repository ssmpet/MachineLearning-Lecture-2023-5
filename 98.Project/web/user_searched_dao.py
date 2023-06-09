import sqlite3 as sq

# 검색기록
def insert_user_record(params):
    conn = sq.connect('./static/DB/usearched.db')
    cur = conn.cursor()

    sql = 'insert into user_searched(uid, stime, songId, img, title, artist, album) values( ?, ?, ?, ?, ?, ?, ?);'
    cur.execute(sql, params)
    conn.commit()

    cur.close()
    conn.close()


# uid 한건에 해당하는 모든 정보
def get_user_by_search_record(uid):
    conn = sq.connect('./static/DB/usearched.db')
    cur = conn.cursor()

    sql = 'select * from user_searched where uid=? ORDER BY sid DESC LIMIT 9;'
    cur.execute(sql, (uid,))
    rows = cur.fetchall()
    return rows


# 탈퇴
def delete_user(uid):
    conn = sq.connect('./static/DB/usearched.db')
    cur = conn.cursor()

    sql = 'delete from user_searched where uid =?;'
    cur.execute(sql, (uid,))
    conn.commit()

    cur.close()
    conn.close()