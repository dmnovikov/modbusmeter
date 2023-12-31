# Измеритель скорости шины modbus

Использует бибилиотеку minimalmodbus
Написано на Python

**Пока работает только RTU, рабочий скрипт `modbusreadmeter.py`**

## Modbus RTU

Многократно в цикле опрашивает заданное количество адресов (устройств) и заданное количество регистров. Делает задаваемое количество циклов измерений и считает сколько измерений попало в текущую пару "минута:секунда".

 Накапливает данные, убирает первое и посленее измерение (неполные секунды начала и конца) и считает скорость. 
 
Чем больше циклов,тем больше статистики и больше точность. Но в целом, достаточно накопить 5-6 полных циклов измерений в текущую секунду. Пользователь сам опрелеяет количество циклов и если их недостаточно, программка предупреждает.

Также программка считает скорость запроса, 
время функции 
```instrument.read_register(register, functioncode=3)```
и выдает среднее знаечние по всем итерациям



```python

modbusreadmeter.py [-h] [-D PORT] [-b BAUDRATE] [-d BYTESIZE] [-p {N,E,O,M,S}] [-s STOPBITS] [-c CIRCLES] [-a D_ADDRESSES] [-r REGISTERS] [-v]

Измеритель скорости Modbus RTU. Параметры с ключиком -h. По умолчанию ttyS1, 1152008E1

options:
  -h, --help            show this help message and exit
  -D PORT, --port PORT  Название порта
  -b BAUDRATE, --baudrate BAUDRATE
                        Скорость передачи данных
  -d BYTESIZE, --bytesize BYTESIZE
                        Размер байта
  -p {N,E,O,M,S}, --parity {N,E,O,M,S}
                        Бит четности
  -s STOPBITS, --stopbits STOPBITS
                        Количество стоп-бит
  -c CIRCLES, --circles CIRCLES
                        Количество циклов полного опроса устройства
  -a D_ADDRESSES, --d_addresses D_ADDRESSES
                        Адреса устройств для чтения (через запятую)
  -r REGISTERS, --registers REGISTERS
                        Регистры для чтения (через запятую)
  -v, --verbose         Включить подробный вывод
 
 ```

## Вывод программы

По умолчанию читается устройство с адресом "1" и один регистр "1" типа 16INT (16 бит). 

Final Dict: сдловарь накопленных результатов, из него убираем первый и последний элемент и имеем копленные ответы в период времени.

```bash
root@armbian-napi:~/modbusmeter# python3 modbusreadmeter.py 
Адреса устройств для чтения: [1]
Регистры для чтения: [1]
Циклов чтения: 300
Port parameters: {'port': '/dev/ttyS3', 'baudrate': 115200, 'parity': 'E', 'bytesize': 8, 'stopbits': 1, 'timeout': 1}
Final dict: {381: 46, 382: 121, 383: 121, 384: 4}
Skip minkey:381 and maxkey:384
Средняя скорость запроса ВСЕХ регистров в ms: 8.264462809917354
Cкорость одного датчика в ms: 8.264462809917354
Cкорость одного опроса ВСЕХ датчиков: 6.133333333333334
Total errors: 0
```

В даннос примере средняя скорость опроса 8,2миллисекунды, 
скорость отработки функции опроса 6,13

> Изменить адреса, регистры можно через парыметры. Например, 
почитаем устройства 1,3 и регистры 0,1,2

```bash
root@armbian-napi:~/modbusmeter# python3 modbusreadmeter.py -a 1,3 -r 0,1,2
Адреса устройств для чтения: [1, 3]
Регистры для чтения: [0, 1, 2]
Циклов чтения: 300
Port parameters: {'port': '/dev/ttyS3', 'baudrate': 115200, 'parity': 'E', 'bytesize': 8, 'stopbits': 1, 'timeout': 1}
Final dict: {663: 22, 664: 46, 665: 45, 666: 46, 667: 46, 668: 46, 669: 46, 670: 46, 671: 47, 672: 46, 673: 46, 674: 46, 675: 46}
Skip minkey:663 and maxkey:675
Средняя скорость запроса ВСЕХ регистров в ms: 21.73913043478261
Cкорость одного датчика в ms: 7.246376811594203
Cкорость одного опроса ВСЕХ датчиков: 19.04
Total errors: 0

```