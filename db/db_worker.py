import sqlite3
import datetime
import time

# db = sqlite3.connect("db/libra.db")
# c = db.cursor()

# c.execute("DROP TABLE requests")

# c.execute('''CREATE TABLE IF NOT EXISTS requests(
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     chat_id INTEGER,
#     book_name TEXT,
#     library TEXT,
#     date DATETIME,
#     status TEXT,
#     response TEXT
#     )''')

# c.execute('''CREATE TABLE IF NOT EXISTS librarians(
#     chat_id     INTEGER PRIMARY KEY,
#     library     TEXT,
#     mute        INTEGER
# )''')

# c.execute("""CREATE TABLE IF NOT EXISTS readers(
#     chat_id INTEGER PRIMARY KEY,
#     state TEXT)""")

class db_worker:
    def __init__(self, db_name):
        assert isinstance(db_name, str)
        self.__conn = sqlite3.connect(db_name)
        self.__cursor = self.__conn.cursor()

############################################################################# readers
    def __add_reader(self, chat_id, state):
        assert isinstance(chat_id, int) and isinstance(state, str)
        self.__cursor.execute(
            "INSERT INTO readers (chat_id, state) VALUES (?,?)", (chat_id, state))
        self.__conn.commit()

    def get_reader_state(self, chat_id):
        self.__cursor.execute("SELECT state FROM readers WHERE chat_id = ?", (chat_id,))
        result = self.__cursor.fetchone()
        if not result:
            self.__add_reader(chat_id, "START")
            return "START"
        else:
            return result[0]

    def remove_reader(self, chat_id):
        self.__cursor.execute(
            "DELETE FROM readers WHERE chat_id = ?", (chat_id,))
        self.__conn.commit()

    def set_reader_state(self, chat_id, state):
        self.__cursor.execute("SELECT state FROM readers WHERE chat_id = ?", (chat_id,))
        result = self.__cursor.fetchone()
        if not result:
            self.__add_reader(chat_id, state)
        else:
            self.__cursor.execute("UPDATE readers SET state = ? WHERE chat_id = ?", (state, chat_id))
            self.__conn.commit()
            

############################################################################# req
    def add_request(self, chat_id, book_name, library):
        assert isinstance(chat_id, int)
        assert isinstance(book_name, str)
        date = datetime.datetime.now()
        self.__cursor.execute("INSERT INTO requests (chat_id, book_name, library, date) VALUES (?,?,?,?)",
                              (chat_id, book_name, library, date))
        self.__conn.commit()

    def remove_request(self, request_id):
        assert isinstance(request_id, int)
        self.__cursor.execute("DELETE FROM requests WHERE id = ?", (request_id,))
        self.__conn.commit()

    def get_requests(self, chat_id):
        assert isinstance(chat_id, int)
        self.__cursor.execute(
            "SELECT library FROM librarians WHERE chat_id = ?", (chat_id,))
        library = self.__cursor.fetchone()[0]
        self.__cursor.execute(
            "SELECT * FROM requests WHERE library = ?", (library,))
        return self.__cursor.fetchall()

    def add_response(self,response, request_id):
        assert isinstance(request_id, int)
        self.__cursor.execute("UPDATE requests SET response = ? WHERE id = ?", (response, request_id))
        self.__conn.commit()

############################################################################# libr
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
            "UPDATE librarians SET mute = 1 WHERE chat_id = ?", (chat_id,))
        self.__conn.commit()

    def unmute_librarian(self, chat_id):
        self.__cursor.execute(
            "UPDATE librarians SET mute = 0 WHERE chat_id = ?", (chat_id,))
        self.__conn.commit()

    def get_all_requests(self):
        self.__cursor.execute("SELECT * FROM requests")
        return self.__cursor.fetchall()

    def get_all_librarians(self):
        self.__cursor.execute("SELECT * FROM librarians")
        return self.__cursor.fetchall()

    def close(self):
        self.__conn.close()

# db = db_worker('db/libra.db')
# print(db.get_reader_state(123))
# db.set_reader_state(123, 'ALOHA')
# print(db.get_reader_state(123))
# db.remove_reader(123)
# print(db.get_reader_state(123))
# db.remove_reader(123)
# print(db.show_all_requests())
# print(db.show_all_librarians())
# db.remove_librarian(993803709)
# print(db.show_all_librarians())
# print(db.check_librarian(3))
# db.add_request(132, 'Вася пупкин', 'Пощечина общественному вкусу', 'дом семьи')
# db.add_response('кабачок', 2)
# print(*db.get_all_requests(), sep = '\n')
