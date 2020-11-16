import sqlite3
import datetime
import time

# db = sqlite3.connect("db/libra.db")
# c = db.cursor()

# c.execute('''CREATE TABLE IF NOT EXISTS requests(
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     chat_id INTEGER,
#     user_name TEXT,
#     book_name TEXT,
#     library TEXT,
#     date DATETIME,
#     book_available INTEGER
#     )''')

# c.execute('''CREATE TABLE IF NOT EXISTS librarians(
#     chat_id     INTEGER PRIMARY KEY,
#     library     TEXT,
#     mute        INTEGER
# )''')


class db_worker:
    def __init__(self, db_name):
        assert isinstance(db_name, str)
        self.__conn = sqlite3.connect(db_name)
        self.__cursor = self.__conn.cursor()

    def add_request(self, chat_id, user_name, book_name, library):
        assert isinstance(chat_id, int) and isinstance(user_name, str)
        assert isinstance(book_name, str)
        date = datetime.datetime.now()
        self.__cursor.execute("INSERT INTO requests (chat_id, user_name, book_name, library, date) VALUES (?,?,?,?,?)",
                              (chat_id, user_name, book_name, library, date))
        self.__conn.commit()

    def remove_request(self, request_id):
        assert isinstance(request_id, int)
        self.__cursor.execute("DELETE FROM requests WHERE id = ?", request_id)
        self.__conn.commit()

    def get_requests(self, chat_id):
        assert isinstance(chat_id, int)
        self.__cursor.execute(
            "SELECT library FROM librarians WHERE chat_id = ?", (chat_id,))
        library = self.__cursor.fetchone()[0]
        self.__cursor.execute(
            "SELECT * FROM requests WHERE library = ?", (library,))
        return self.__cursor.fetchall()

    def check_librarian(self, chat_id):
        self.__cursor.execute(
            "SELECT EXISTS(SELECT chat_id FROM librarians WHERE chat_id = ?)", (chat_id,))
        return bool(sum(self.__cursor.fetchall()[0]))

    def add_librarian(self, chat_id, library):
        assert isinstance(chat_id, int) and isinstance(library, str)
        self.__cursor.execute(
            "INSERT INTO librarians (chat_id, library, mute) VALUES (?,?,?)", (chat_id, library, 0))
        self.__conn.commit()

    def remove_librarian(self, chat_id):
        self.__cursor.execute(
            "DELETE FROM librarians WHERE chat_id = ?", (chat_id,))
        self.__conn.commit()

    def mute_librarian(self, chat_id):
        self.__cursor.execute(
            "UPDATE librarians SET mute = 1 WHERE chat_id = (?)", chat_id)
        self.__conn.commit()

    def unmute_librarian(self, chat_id):
        self.__cursor.execute(
            "UPDATE librarians SET mute = 0 WHERE chat_id = (?)", chat_id)
        self.__conn.commit()

    def show_all_requests(self):
        self.__cursor.execute("SELECT * FROM requests")
        return self.__cursor.fetchall()

    def show_all_librarians(self):
        self.__cursor.execute("SELECT * FROM librarians")
        return self.__cursor.fetchall()

# db = db_worker('db/libra.db')
# print(db.show_all_requests())
# print(db.show_all_librarians())
# db.remove_librarian(993803709)
# print(db.show_all_librarians())
# print(db.check_librarian(3))
