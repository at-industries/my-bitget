# MyBitget
MyBitget - это утилитарная библиотека для работы с биржей Bitget.

## Общая информация
### Возможности
1. Асинхронное взаимодействие с биржей.
2. Подключение прокси.
3. Логирование результатов.
4. Работа с публичными данными (получение цен активов).
5. Работа со Spot аккаунтом (отправка токенов).
6. Работа с суб-аккаунтами (трансферы между аккаунтами).

### Методы
1. `PUBLIC_get_coin_info` - получение общей информации о конкретной монете.
2. `PUBLIC_get_chain_info` - получение общей информации о конкретной сети актива.
3. `PUBLIC_get_symbol_info` - получение общей информации о торгуемой паре.
4. `PUBLIC_get_ticker_info` - получение актуальной информации о торгуемой паре.
5. `PUBLIC_get_price` - получение цены актива.
6. `SPOT_is_connected` - проверка подключения к Spot аккаунту.
7. `SPOT_get_account_info` - получение общей информации Spot аккаунта.
8. `SPOT_get_balance` - получение баланса Spot аккаунта.
9. `SPOT_convert_usd_to_native` - перевод суммы USD в нативную монету сети.
10. `SPOT_post_withdrawal` - ончейн вывод средств на кошелек.
11. `SPOT_check_withdrawal` - проверка ончейн вывода на успех.
12. `SUBACCOUNT_get_subaccounts` - получение списка всех суб-аккаунтов.
13. `SUBACCOUNT_get_balance` - получение баланса на суб-аккаунте.
14. `SUBACCOUNT_transfer_to_main` - перевод средств с основного аккаунта на суб-аккаунт.

### Особенности
1. Методы библиотеки разделены на 4 основных типа:
- Методы работы с публичными данными - это методы, которые работают с публичными данными биржи (для публичных ендпоинтов API ключи не нужны). Названия данных методов начинаются на `PUBLIC_`.
- Методы работы со Spot аккаунтом - это методы, которые работают с Spot аккаунтом. Названия данных методов начинаются на `SPOT_`.
- Методы работы с суб-аккаунтами - это методы, которые работают суб-аккаунтами. Названия данных методов начинаются на `SUBACCOUNT_`.
- Утилитарные методы - это методы, которые выполняют утилитарные функции. Данные методы располагаются в самом конце класса.
2. Почти все методы класса возвращают кортежи с целым числом в качестве первого элемента, где:
- `0`: статус успеха (успешное завершение метода; второй элемент кортежа содержит результат)
- `-1`: статус ошибки (неуспешное завершение метода; второй элемент кортежа содержит ошибку)

## Примеры
### Импорт библиотек
Перед началом импортируем библиотеку `asyncio` для запуска асинхронных функций и сам класс `MyBitget`.
```python
import asyncio
from my_bitget import MyBitget
```

### Создание экземпляра класса `MyBitget`
Создаем экземпляр класса `MyBitget` с обязательным параметрами `api_key`, `secret_key`, `passphrase` и опциональным параметром `asynchrony`. Подробнее о параметрах — в комментариях конструктора класса `MyBitget`. 
```python
my_bitget = MyBitget(
    api_key='YOUR-API-KEY',
    secret_key='YOUR-SECRET-KEY',
    passphrase='YOUR-PASSPHRASE',
    asynchrony=True,
)
```

### Пример использования метода `PUBLIC_get_price`
Метод `PUBLIC_get_price` получает цену актива по его тикеру. В нашем примере мы запрашиваем цену монеты `BTC`.
```python
async def example_00():
    status, result = await my_bitget.PUBLIC_get_price(ticker='BTC')
    if status == 0:
        print(f'00 | Price: {result}')
    else:
        print(f'00 | Error while getting price: {result}')

asyncio.run(example_00())
```

### Пример использования метода `SPOT_is_connected`
Метод `SPOT_is_connected` проверяет подключение к `Spot` аккаунту Bitget. Метод присылает (0, True), если подключение успешное, и (-1, Exception("...")), если нет.
```python
async def example_01():
    status, result = await my_bitget.SPOT_is_connected()
    if status == 0:
        print(f'01 | Connection: {result}')
    else:
        print(f'01 | Error while checking connection: {result}')

asyncio.run(example_01())
```

### Пример использования метода `SPOT_get_balance`
Метод `SPOT_get_balance` получает баланс `Spot` аккаунта (как для конкретного токена, так и всех активов сразу). В нашем примере мы получаем баланс монеты `BTC`. Чтобы получить баланс всех (ненулевых) активов, параметр `ticker` заполнять не нужно.
```python
async def example_02():
    status, result = await my_bitget.SPOT_get_balance(ticker='BTC')
    if status == 0:
        print(f'02 | Balance: {result}')
    else:
        print(f'02 | Error while getting balance: {result}')

asyncio.run(example_02())
```

### Пример использования метода `SPOT_post_withdrawal`
Метод `SPOT_post_withdrawal` выводит средства с биржи на сторонний кошелек. В нашем примере мы выводим `0.01` монеты `ETH` на кошелек `0xB293cFf00bA3f110C839fBDB59186BD944B144D5` в сети `Base`.
- Узнать список всех сетей можно в методе `PUBLIC_get_coin_info`.
- Перевести доллар в нативную монету сети можно методом `SPOT_convert_usd_to_native`.
```python
async def example_03():
    status, result = await my_bitget.SPOT_post_withdrawal(
        ticker='ETH',
        chain='BASE',
        address='0xB293cFf00bA3f110C839fBDB59186BD944B144D5',
        amount=0.01,
    )
    if status == 0:
        print(f'03 | Withdrawal Id: {result}')
    else:
        print(f'03 | Error while posting withdrawal: {result}')

asyncio.run(example_03())
```

### Пример использования метода `SUBACCOUNT_get_subaccounts`
Метод `SUBACCOUNT_get_subaccounts` получает список имен всех созданных суб-аккаунтов.

```python
async def example_04():
    status, result = await my_bitget.SUBACCOUNT_get_subaccounts()
    if status == 0:
        print(f'04 | Subaccounts: {result}')
    else:
        print(f'04 | Error while getting subaccounts: {result}')

asyncio.run(example_04())
```

### Пример использования метода `SUBACCOUNT_transfer_to_main`
Метод `SUBACCOUNT_transfer_to_main` переводит средства с суб-аккаунта на основной `Spot` аккаунт. В нашем примере мы переводим `100USDC` с суб-аккаунта под именем `SUBACCOUNT-NAME`.
```python
async def example_05():
    status, result = await my_bitget.SUBACCOUNT_transfer_to_main(
        subaccount_name='SUBACCOUNT-NAME',
        ticker='USDC',
        amount=100.0,
    )
    if status == 0:
        print(f'05 | Transfer Id: {result}')
    else:
        print(f'05 | Error while transferring tokens from subaccount to main account: {result}')

asyncio.run(example_05())
```
