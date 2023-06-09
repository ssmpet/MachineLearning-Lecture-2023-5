import sqlite3 as sq

# 회원정보 조회
def get_users():
    conn = sq.connect('./static/db/userinfo.db')
    cur = conn.cursor()

    sql = 'select * from user;'
    cur.execute(sql)
    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


# uid 한건만
def get_user_by_uid(uid):
    conn = sq.connect('./static/db/userinfo.db')
    cur = conn.cursor()

    sql = 'select count(*) from user where uid=?;'
    cur.execute(sql, (uid,))
    row = cur.fetchone()
    return row[0]

# uid 한건에 해당하는 모든 정보
def get_user_by_info(uid):
    conn = sq.connect('./static/db/userinfo.db')
    cur = conn.cursor()

    sql = 'select * from user where uid=?;'
    cur.execute(sql, (uid,))
    row = cur.fetchone()
    return row


# 회원가입
def insert_user(params):
    conn = sq.connect('./static/db/userinfo.db')
    cur = conn.cursor()

    sql = 'insert into user(uid, uname, pwd, gender, email, birthday) values( ?, ?, ?, ?, ?, ?);'
    cur.execute(sql, params)
    conn.commit()

    cur.close()
    conn.close()


# 정보수정
def update_user(params):
    conn = sq.connect('./static/db/userinfo.db')
    cur = conn.cursor()

    sql = 'update user set uname=?, pwd=?, gender=?, email=?, birthday=? where uid=?'
    cur.execute(sql, params)
    conn.commit()

    cur.close()
    conn.close()


# 개인 이력 삭제
def delete_user(uid):
    conn = sq.connect('./static/db/userinfo.db')
    cur = conn.cursor()

    sql = 'delete from user where uid =?;'
    cur.execute(sql, (uid,))
    conn.commit()

    cur.close()
    conn.close()