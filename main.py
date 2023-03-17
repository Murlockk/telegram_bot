import config
from config import currency
from utils import CryptoConverter, PopularCoin, DecodingClass


def main_func(compilation: list[str]):
    PopularCoin.set_keys()
    obj, sub, amount = DecodingClass.decoder(compilation)  # Расшифровываем запрос пользователя
    if obj == "chart":
        return get_coin_box()
    total_base = CryptoConverter.convert(obj, sub)         # Отправляем готовые данные в конвертор
    text = f'Цена {amount} {obj} в {currency[sub]} составляет {total_base * amount}'
    coin_box(obj, sub)
    return text  # Вывод передается в терминал или в телеграм бот. Конвертор может быть внедрен куда-либо еще


def coin_box(obj, sub=None):
    """Функция складывает последние выбранные монеты в config.box, по этим данным, при запросе дополнительной информации
    'строятся' графики."""
    config.box = obj + ' ' + sub    # Не научился обновлять импорт. Хотелось бы использовать без ссылки на config


def get_coin_box():
    last_coin = config.box.split()  # -//-
    comment = CryptoConverter.convert_info(last_coin)
    return last_coin + comment
