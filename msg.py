start_message = "Привет! Этот бот может:\n📚/find_book - помочь вам найти книгу в библиотеках города Благовещенска"#\n🎭/events - узнать о мероприятиях в библиотеках"
other_input = "Я вас не понимаю😥\n📚/find_book - найти книгу\n🎭/events - узнать о мероприятиях в библиотеках "
book_name = 'отлично! теперь отправь мне фамилию автора и название книги'

digit_stikers = ['0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','7️⃣','8️⃣','9️⃣']

books_list_req_tip = 'Чтобы забронировать одну из книг, выбери кнопку с соответствующей цифрой'

not_found = 'По вашему запросу ничего не найдено, повторите попытку'

please_wait = 'Ваш запрос выполняется, пожалуйста подождите. Среднее время ответа - 8 секунд'

wait_gif_url = 'https://i.giphy.com/1EuLa4HzCWffO.gif'

lib_hello = "Здравствуйте! "
lib_token_help = "Чтобы зарегистрироваться в библиотеке как сотрудник и получать запросы на книги введите токен вашей библиотеки"
lib_help = """
Все общение с ботом строится на вызове команд. Полный список команд всегда можно посмотреть вызвав /help
или начав набирать коммнаду с символа слэш.
Бот поддерживает следующие комманды:
/get_all - бот выдаст вам все текущие не закрытые запросы, поступившие в вашу библиотеку
/mute - бот не будет отправлять вам запросы, постпающие в реальном времени
/unmute - отменяет команду выше
/del_me - бот удалит вас из списка библиотекарей, следовательно вы не сможете отвечать на запросы
"""
lib_mute = "Теперь запросы не будут прихолить вам в реальном времени. Чтобы отключить это наберите команду /unmute"
lib_unmute = "Теперь все запросы будут приходить сразу, как пользователь их отправит. Чтобы отключить это отправьте команду /mute"