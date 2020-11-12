import sqlite3

db = sqlite3.connect('libra.db')
conn = sqlite3.connect('libra.db')

conn.execute('''CREATE TABLE requests(
    id INTEGER PRIMARY KEY AUTOINCREMENT
    user_chat_id
    )''')

class bd_worker:
    def __init__(self):
        pass

    def add_request(self):
        pass

    def remove_request(self):
        pass

    def get_requests(self):
        pass

    def add_librarian(self):
        pass

    def remove_librarian(self):
        pass

    def mute_librarian(self):
        pass

    def unmute_librarian(self):
        pass

