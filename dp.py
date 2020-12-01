import pymysql

# con = pymysql.connect('localhost', 'root', 'a31081993abc', 'games', port=3306)
#
# with con.cursor() as cur:
#     cur.execute("SELECT VERSION()")
#     version = cur.fetchone()
#     print("Database version: {}".format(version[0]))

con = pymysql.connect('localhost', 'root', 'a31081993abc', 'games', port=3306)


def add_games_in_db(data):
    with con.cursor() as cur:
        query = "INSERT INTO `items` (`goods_title`, `release_date`, `genres`, `description`, `systemreq`," \
                "`thumbnail`, `platform`, `lang`, `activation`, `real_price`, `publisher`, `goods_type`, `price`, " \
                "`new_tab`, `leader_tab`, `preorder_tab`, `offer_day`, `in_stock`, `digiseller_id`, `video`, `views`)" \
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,)"
        cur.executemany(query, data)


def add_game_in_db(data):
    with con.cursor() as cur:
        check_query = "SELECT goodsID from items WHERE goods_title = '{}'"
        cur.execute(check_query.format(data[0]))
        check_data = cur.fetchone()
        if check_data is None:
            query = "INSERT INTO `items` (`goods_title`, `release_date`, `genres`, `description`, `systemreq`," \
                "`thumbnail`, `platform`, `lang`, `activation`, `real_price`, `publisher`, `goods_type`, `price`, " \
                "`new_tab`, `leader_tab`, `preorder_tab`, `offer_day`, `in_stock`, `digiseller_id`, `video`, `views`)" \
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,)"
            cur.execute(query, data)


if __name__ == '__main__':
    data = ['The Long Dark']
    add_game_in_db(data)
