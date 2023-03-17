from config import sup_w, fin_w, val_w, support_text, finish_text, remark
from main import main_func
from utils import PopularCoin, ConvertionException


def terminal_func():
    """Функция отвечающая за ввод пользователем """
    while True:
        compilation = input(f"{'-'*45}\n| {sup_w[-1]}: {sup_w[0]}, {val_w[-1]}: {val_w[0]}, {fin_w[-1]}: {fin_w[0]} |\n"
                            f"{'-'*45}\nВаш запрос: ").split()  # Ввод
        option = "".join(compilation).lower()
        if option in fin_w:
            print("Завершение работы...")                      # Выход из цикла
            break
        elif option in val_w:
            print(PopularCoin.values_func().replace('\n', ', '))  # Отображение популярной криптовалюты списком
            continue
        elif option in sup_w:   # Информация по вводу пользователя
            print(support_text, finish_text, remark)
            continue
        try:
            result = (main_func(compilation))  # Отображение результата
            if type(result) == list:   # Результат становится list, когда пользователь просит подробную информацию
                for _ in range(4):     # Выводим доп. информацию, добавленную в utils.CryptoConverter.convert_info
                    print(result.pop())
            else:
                print(result)
        except ConvertionException as e:
            print(e)


if __name__ == "__main__":  # Функционал поддерживается в терминале
    terminal_func()
