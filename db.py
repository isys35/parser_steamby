import pymysql

# con = pymysql.connect('localhost', 'root', 'a31081993abc', 'games', port=3306)
#
# with con.cursor() as cur:
#     cur.execute("SELECT VERSION()")
#     version = cur.fetchone()
#     print("Database version: {}".format(version[0]))

HOST = 'localhost'
USERNAME = 'root'
PASSWORD = 'a31081993abc'
DB_NAME = 'games'
PORT = 3306


def add_games_in_db(data):
    con = pymysql.connect(HOST, USERNAME, PASSWORD, DB_NAME, port=PORT)
    with con.cursor() as cur:
        query = "INSERT INTO `items` (`goods_title`, `release_date`, `genres`, `description`, `systemreq`," \
                "`thumbnail`, `platform`, `lang`, `activation`, `real_price`, `publisher`, `goods_type`, `price`, " \
                "`new_tab`, `leader_tab`, `preorder_tab`, `offer_day`, `in_stock`, `digiseller_id`, `video`, `views`)" \
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,)"
        cur.executemany(query, data)


def add_game_in_db(data):
    con = pymysql.connect(HOST, USERNAME, PASSWORD, DB_NAME, port=PORT)
    with con.cursor() as cur:
        check_query = "SELECT goodsID from items WHERE goods_title = %s"
        cur.execute(check_query, [data[0]])
        check_data = cur.fetchone()
        if check_data is None:
            query = "INSERT INTO `items` (`goods_title`, `release_date`, `genres`, `description`, `systemreq`," \
                    "`thumbnail`, `platform`, `lang`, `activation`, `real_price`, `publisher`, `goods_type`, `price`, " \
                    "`new_tab`, `leader_tab`, `preorder_tab`, `offer_day`, `in_stock`, `digiseller_id`, `video`, `views`)" \
                    " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(query, data)
        else:
            query = "UPDATE items SET goods_title=%s, release_date=%s, genres=%s," \
                    "description=%s, systemreq=%s, thumbnail=%s, platform=%s, lang=%s," \
                    "activation=%s, real_price=%s, publisher=%s, goods_type=%s, price=%s," \
                    "new_tab=%s, leader_tab=%s, preorder_tab=%s, offer_day=%s, in_stock=%s," \
                    "digiseller_id=%s, video=%s, views=%s WHERE goodsID={}".format(check_data[0])
            cur.execute(query, data)
    con.commit()


def get_genres():
    con = pymysql.connect(HOST, USERNAME, PASSWORD, DB_NAME, port=PORT)
    with con.cursor() as cur:
        query = "SELECT genreID,genreName FROM genres"
        cur.execute(query)
        genres_dict = {genre[1]: genre[0] for genre in cur.fetchall()}
        return genres_dict


if __name__ == '__main__':
    print(get_genres())