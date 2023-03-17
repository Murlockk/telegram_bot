import json
import requests
from deep_translator import GoogleTranslator as Gt
from transliterate import translit
from bs4 import BeautifulSoup as Bs

from config import currency, chart


class ConvertionException(Exception):  # Источник: https://habr.com/ru/company/piter/blog/537642/
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:    # Какая-либо не пойманная # ошибка
            self.message = 'Видимо Ваш запрос поняли не правильно, пожалуйста, повторите..'

    def __str__(self):
        if self.message:
            return f'Ошибка ввода, {self.message} '


class PopularCoin:
    translate_coil_names = []  # Список, содержащий названия криптовалюты на русском языке.
    coil_names_list = []       # Список, содержащий названия популярной криптовалюты.
    mobile_names_list = []     # Список, содержащий сокращения популярной криптовалюты.
    keys = {}                  # Организовать обновление импорта словаря после его заполнения не удалось.

    @classmethod
    def get_names(cls):
        """Функция возвращающая информацию о названиях популярных криптовалют на русском и английском языке,
        а так же принятые сокращения данных валют"""
        return cls.translate_coil_names, cls.coil_names_list, cls.mobile_names_list

    @classmethod
    def search_names(cls):
        r = requests.get('https://www.cryptocompare.com')
        soup = Bs(r.text, "html.parser")
        mobile_names = soup.findAll("div", class_="thumb-coin")  # Выполняем отбор по тегу и классу
        for _coin in mobile_names:
            cls.mobile_names_list.append(str(_coin).split()[-2][7:10])  # Исключаем лишнюю информацию. Формируем список

        coin_names = soup.findAll("div", class_="coins-name")  #
        for _coin in coin_names:
            for first_word in _coin:
                cls.coil_names_list.append(first_word[1:-1:])  # Исключаем лишнюю информацию. Формируем список
                break

        to_translate = cls.coil_names_list
        for i in to_translate:
            translated_word = Gt(source='auto', target='ru').translate(i)
            if len(translated_word.split()) > 1 or len(translated_word) == 3:  # Исправляем не корректный перевод
                translated_word = translit(i, 'ru')     # Монеты с коротким и сложным названием переводим как имена С.
            cls.translate_coil_names.append(translated_word)  # формируем список названий популярных монет на русском
        cls.creating_keys()

    @classmethod  # Setter
    def creating_keys(cls):  # Заполняем кейс актуальными названиями монет. Ключами являются сокращенные наименования
        cls.keys = dict(zip(cls.mobile_names_list, zip(cls.coil_names_list, cls.translate_coil_names)))

    @classmethod
    def values_func(cls):
        cls.set_keys()  # Пользователь может первым действием выбрать просмотр списка монет, поэтому данная проверка
        # необходима
        text = 'Доступные валюты:'
        for key in cls.keys:
            text = '\n'.join((text, key + " - " + cls.keys[key][0]))
        return text

    @classmethod
    def set_keys(cls):
        """Функция создания, а в дальнейшем -- проверки наличия сформированного словаря с популярной криптовалютой"""
        if cls.keys == {}:  # Если программой еще не пользовались, то keys пуст.
            name_list = PopularCoin()
            name_list.search_names()  # При первом запуске, список актуальной криптовалюты заполняется


class DecodingClass:
    UNITS = [
        "ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь",
        "девять", "десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать",
        "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"
    ]
    TENS = ["", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят",
            "девяносто"]

    SCALES = ["сто", "тысяч", "миллион", "миллиард", "триллион"]

    cache_coin = []

    @classmethod
    def get_keys(cls):
        return PopularCoin.keys

    @classmethod
    def caching(cls):
        """Чтобы каждый раз не совершать перебор словарей, кешируем БД. Кешируется один раз."""
        if not cls.cache_coin:  # Формируется при первом запуске. Замедляет первое вычисление, но делает кл. автономнее
            for _mobile_names in cls.get_keys():  # O(10) Перебор. 10 сокращенных названий
                for _names in cls.get_keys()[_mobile_names]:  # O(2) * 10 перебор. 10 переборов по 2 значения
                    cls.cache_coin.append(_names)  # O(2) * 10 добавление.   50 при n = 30.. O(1.7n)

    @classmethod
    def decoder(cls, arg: list[str]):
        """Расшифровываем запрос пользователя учитывая некоторые ошибки, произвольный формат ввода."""
        cls.caching()
        quote, base, amount, text_num = [], [], None, ''  # Учитываем что может быть введено две валюты или криптовалюты
        for word in arg:
            order = ''.join(arg).lower()
            if order in chart:
                return 'chart', None, None  # Прерываем декодирование и выводим информацию о последней конвертации
            activity = False  # Счетчик, при изменении которого цикл переходит к следующей итерации, т.к. слово опознано
            if word.isdigit():
                if amount is None:
                    amount = int(word)  # Особенность ввода. Или пользователь вводит числа, или пишет буквами
                    continue            # Совмещение int и str в дальнейшем выведет исключение
                else:
                    raise ConvertionException(f'не удалось обработать количество конвертируемой валюты:'
                                              f' (оцениваем {amount} или {word} единиц?)')
            if len(word) >= 3:  # Отсекаем часть предлогов и союзов (сколько в!.., BTC и!на! USD), короткие числа.
                if amount is None and word in arg:  # Ищем числа, если нашли int выше, итерации над str не совершаем.
                    word = word.lower()             # Избегаем лишних операций с word в условиях
                    if (word in cls.SCALES) or (word in cls.TENS) or (word in cls.UNITS):
                        text_num += word + " "      # строим строку для конвертации в число
                        continue
                word = word.upper()             # Избегаем лишних операций с word в условиях
                if word[:3:] in cls.get_keys():     # Доп.возможности ввода (ввод Btc,btc..= BTC)
                    quote.append(word)
                    continue  # Если слово опознано, не проверяем его по другим критериям
                elif word[:3:] in currency:         # Пытаемся понять ввод, узнаем валюту по 3 буквам(key)
                    base.append(word[:3:])
                    continue  # Если слово опознано, не проверяем его по другим критериям
                word = word.capitalize()        # Избегаем лишних операций с word в цикле
                for name in cls.cache_coin:
                    if word[:3:] == name[:3:]:      # Доп.возможности ввода (Бит.Bitk.+падежи)
                        quote.append(list(cls.get_keys())[int(cls.cache_coin.index(name) // 2)])  # Добавляем соотв ключ
                        activity = True
                        break          # Если слово опознано в кеше -- не проверяем другие элементы..
                if activity:
                    continue           # Если слово в цикле опознано, переходим к следующей итерации. Ускоряем процесс
                word = word.lower()    # Избегаем лишних операций с word в цикле
                for key in currency:
                    if word[:3:] in currency[key].lower():
                        base.append(key)  # Пытаемся понять ввод, узнаем валюту по 3 буквам.(рублеЙ = RUB, юане = CNY)
                        activity = True
                        break     # Если слово опознано, не проверяем другие элементы словаря валют
                if activity:
                    continue      # Если слово в цикле опознано, переходим к следующей итерации. Ускоряем процесс

        if text_num != "":        # Если числительные были опознаны..
            if amount is None:    # И не нашлось элементов int
                amount = cls.text2int(text_num)  # Преобразуем числительные в тип int
            else:
                raise ConvertionException('Не удалось обработать количество конвертируемой валюты')
        elif amount is None:  # Если количество не указано ни в каком виде, принимаем его за 1
            amount = 1        # Если пользователь не ввел числа и числительные не найдены -- принимаем количество = 1
        return *cls.linker(quote, base), amount

    @classmethod  # Источник: https://ru.stackoverflow.com/questions/806931/
    def text2int(cls, text_num: str, numwords=None):
        """Преобразовывает некоторые числа записанные прописью в их десятичные аналоги (три->3)"""
        if numwords is None:
            numwords = {}
        if not numwords:
            for idx, word in enumerate(cls.UNITS):
                numwords[word] = (1, idx)
            for idx, word in enumerate(cls.TENS):
                numwords[word] = (1, idx * 10)
            for idx, word in enumerate(cls.SCALES):
                numwords[word] = (10 ** (idx * 3 or 2), 0)
        current = result = 0
        for word in text_num.split():
            scale, increment = numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
        return result + current

    @staticmethod
    def linker(quote: list, base: list):
        """Функция определяет объект и субъект оценки"""
        len_b, len_q = len(base), len(quote)
        len_q_b = len_q + len_b
        if len_q_b == 2:
            if len_b == 2:      # Значит пользователю нужно сравнить 2 валюты
                base_ = base.pop()   # Последняя в тексте станет оценивающей
                quote_ = base.pop()  # Первая -- оцениваемой
                if base_ == quote_:
                    raise ConvertionException(f'нельзя сравнить две одноименные валюты ({quote_})')
            elif len_q == 2:  # Значит пользователю нужно сравнить 2 криптовалюты
                base_ = quote.pop()
                quote_ = quote.pop()
                if base_ == quote_:
                    raise ConvertionException(f'нельзя сравнить две одноименные криптовалюты ({quote_})')
            else:                  # Введены одна криптовалюта и одна валюта
                quote_ = quote.pop()
                base_ = base.pop()
        else:  # Сразу отсеиваем варианты len(base + quote) > 2, а также случай len(base + quote) == 0...--> исключение
            if len_q == 1 and base == []:    # Пользователь ввел только 1 криптовалюту
                quote_ = quote.pop()
                base_ = "USD"                      # Будем понимать это как желание сравнить с долларом (стандарт)
            elif len_b == 1 and quote == []:   # Пользователь ввел только 1 валюту
                quote_ = base.pop()
                if quote_ == "USD":     # Если валютой окажется доллар -- сравним с рублем
                    base_ = "RUB"
                else:
                    base_ = "USD"       # Иначе будем сравнивать с долларом
            else:
                if len_q_b == 0:
                    mes1 = 'мало'
                    _ = "."
                else:
                    mes1 = 'много'
                    _ = ": "
                mes2 = ", ".join(quote + base)
                raise ConvertionException(f'было передано слишком {mes1} аргументов{_}{mes2}')
        return quote_, base_


class CryptoConverter:
    @staticmethod
    def convert(obj: str, sub: str):
        """Функция производящая оценку, с помощью стороннего источника"""
        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={obj}&tsyms={sub}')
        total_base = json.loads(r.content)[sub]
        return total_base

    @staticmethod
    def convert_info(result: list[str]):
        obj, sub = result
        r = requests.get(f'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={obj}&tsyms={sub}')
        total_base = json.loads(r.content)['DISPLAY'][obj][sub]
        sym_obj, sym_sub = total_base.get('FROMSYMBOL'), total_base.get('TOSYMBOL')
        max_24, min_24 = total_base.get('HIGH24HOUR').split().pop(), total_base.get('LOW24HOUR').split().pop()
        change = float(total_base.get('CHANGEPCT24HOUR'))
        if change <= 0:
            _ = 'выросла'
        else:
            _ = 'упала'
        mes_1 = f'Цена {obj} за 24 часа {_} на {abs(change)}%'
        mes_2 = f'Максимальная ставка {sym_obj} = {max_24} {sym_sub}'
        mes_3 = f'Минимальная ставка {sym_obj} = {min_24} {sym_sub}'
        link = f'купить или продать {sym_obj}: https://www.cryptocompare.com/coins/{obj}/overview/{sub}'
        comment = [link, mes_3, mes_2, mes_1]
        return comment
