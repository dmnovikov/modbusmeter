import time
import minimalmodbus
import serial
import argparse
from datetime import datetime
from statistics import mean 
from pyModbusTCP.client import ModbusClient

errors=0
count_dict={}

current_sec=0
prev_sec=0

registers_number=1
default_circles=300

default_device_addr = [1]
default_registers_array = [1]


def read_device_data(device_address, instrument, registers_array):
    global current_sec
    global prev_sec
    global count_dict
    global errors
    global verbose
    results=[]
    try:
        start_time=datetime.now()
        for register in registers_array:
            #print(f"Register={register}")
            results.append(instrument.read_register(register, functioncode=3))
        timestamp = datetime.now()

        speed=int( (timestamp - start_time).microseconds/1000 )
        
        current_sec = timestamp.minute*60 + timestamp.second
        if current_sec == prev_sec:
            if current_sec in count_dict:
                count_dict[current_sec] += 1
            else:
                count_dict[current_sec] = 0
        
        #print(f"DICT: {count_dict}")
        if verbose: print(f"T: {timestamp}; Results from device {device_address}: {results}; request speed in ms:{speed}") 
        #print(f"Start:{start_time.microsecond}, Stop:{timestamp.microsecond}, Spped: {speed}")
        prev_sec = current_sec
        start_time=0
        return results,speed

    except minimalmodbus.ModbusException as e:
        errors += 1
        print(f"Error reading data from device {device_address}: {e}")
        return [],-1

def read_device_data_tcp(device_address, modbus_client, registers_array):
    global current_sec
    global prev_sec
    global count_dict
    global errors
    global verbose
    results=[]
    try:
        start_time=datetime.now()
        for register in registers_array:
            regs = modbus_client.read_holding_registers(register, 1)
            results.append(regs)
        timestamp = datetime.now()

        speed=int( (timestamp - start_time).microseconds/1000 )
        
        current_sec = timestamp.minute*60 + timestamp.second
        if current_sec == prev_sec:
            if current_sec in count_dict:
                count_dict[current_sec] += 1
            else:
                count_dict[current_sec] = 0
        
        #print(f"DICT: {count_dict}")
        if verbose: print(f"T: {timestamp}; Results from device {device_address}: {results}; request speed in ms:{speed}") 
        #print(f"Start:{start_time.microsecond}, Stop:{timestamp.microsecond}, Spped: {speed}")
        prev_sec = current_sec
        start_time=0
        return results,speed


    except Exception as e:
        errors += 1
        print(f"Error reading data from device {device_address}: {e}")
        return [],-1


def read_all_devices(devices_addresses, serial_port_parameters, registers_array):
    speed_sum=0
    for device_address in devices_addresses:
        instrument = minimalmodbus.Instrument(
            serial_port_parameters['port'],
            device_address,
            mode='rtu',
            close_port_after_each_call=False,
            debug=False
        )
        instrument.serial = serial.Serial(**serial_port_parameters)
        results,speed = read_device_data(device_address, instrument, registers_array)
        speed_sum+=speed
    return  speed_sum/len(devices_addresses)

def read_all_devices_tcp(devices_addresses, modbus_client, registers_array):
    speed_sum=0
    for device_address in devices_addresses:
        
        # Создание объекта инструмента Modbus с указанием порта (TCP)
        #instrument = minimalmodbus.Instrument('127.0.0.1', 502)  # Замените IP-адрес и порт на ваши значения

        results,speed = read_device_data_tcp(device_address, modbus_client, registers_array)
        speed_sum+=speed
    return  speed_sum/len(devices_addresses)

def main():

    parser = argparse.ArgumentParser(description= "Измеритель скорости Modbus RTU. Параметры с ключиком -h. По умолчанию ttyS1, 1152008E1")

    errors = 0
    
    global count_dict
    global current_sec
    global prev_sec
    global default_registers_array
    global default_device_addr
    global verbose

    currnet_sec = datetime.now().second
    prev_sec = datetime.now().second
    count_dict = {}
    

    parser.add_argument("-D", "--port", type=str, default="/dev/ttyS3", help="Название порта")
    parser.add_argument("-b", "--baudrate", type=int, default=115200, help="Скорость передачи данных")
    parser.add_argument("-d", "--bytesize", type=int, default=8, help="Размер байта")
    parser.add_argument("-p", "--parity", type=str, default="E", choices=['N', 'E', 'O', 'M', 'S'], help="Бит четности")
    parser.add_argument("-s", "--stopbits", type=int, default=1, help="Количество стоп-бит")
    parser.add_argument("-c", "--circles", type=int, default=default_circles, help="Количество циклов полного опроса устройства")
    parser.add_argument("-a", "--d_addresses", type=str, help="Адреса устройств для чтения (через запятую)")
    parser.add_argument("-r", "--registers", type=str, help="Регистры для чтения (через запятую)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Включить подробный вывод")    
    parser.add_argument("-H", "--host", type=str, help="Использовать Modbus tcp")    

    args = parser.parse_args()

    port_name = args.port
    baudrate = args.baudrate
    bytesize = args.bytesize
    parity = args.parity
    stopbits = args.stopbits
    circles = args.circles
    verbose = args.verbose

    if args.registers:
        registers_array = [int(register) for register in args.registers.split(',')]
    else:
        registers_array=default_registers_array

    if args.d_addresses: 
        device_addresses = [int(addr) for addr in args.d_addresses.split(',')]
    else:
        device_addresses = default_device_addr

    if args.host:
        host=args.host
    
    print(f"Адреса устройств для чтения: {device_addresses}")
    print(f"Регистры для чтения: {registers_array}")
    print(f"Циклов чтения: {circles}")
   



    serial_port_parameters = {
        'port': port_name,
        'baudrate': baudrate,
        'parity': parity,
        'bytesize': bytesize,
        'stopbits': stopbits,
        'timeout': 1
    }

    if not host: 
        print(f"Port parameters: {serial_port_parameters}") 
    
        try:
            test_serial = serial.Serial(**serial_port_parameters)
            test_serial.close()
        
        except serial.SerialException as e:
            print(f"Ошибка откртия порта")
        return e
    else:
        modbus_client = ModbusClient(host, port=502) 
        if not modbus_client.open():
            print("Не удалось открыть соединение")
            exit()
        print(f"Connected: modbus TCP Host: {host}")

    gavg_req_speed = 0
    
    for i in range(1, circles+1):
        if verbose: print(f"Цикл прогона: {i} из {circles}")

        if not host:
            avg_req_speed = read_all_devices(device_addresses, serial_port_parameters, registers_array)
        else: 
            avg_req_speed = read_all_devices_tcp(device_addresses, modbus_client, registers_array)  
        
        if verbose: print(f"Средняя моментальная скорость запроса: {avg_req_speed}")
        gavg_req_speed+=avg_req_speed
            
    print(f"Final dict: {count_dict}")

    if len(count_dict) < 3 :
        print("Мало данных для определение скорости, необходимо увеличить количество циклов") 
    else:
       minkey=min(count_dict)
       maxkey=max(count_dict)

       print(f"Skip minkey:{minkey} and maxkey:{maxkey}")

       del count_dict[minkey]
       del count_dict[maxkey]

       average_speed_ms = 1000/mean(count_dict.values())
       gavg_req_speed = gavg_req_speed / circles

       print(f"Средняя скорость запроса ВСЕХ регистров в ms: {average_speed_ms}")
       print(f"Cкорость одного датчика в ms: {average_speed_ms/len(registers_array)}")
       print(f"Cкорость одного опроса ВСЕХ датчиков: {gavg_req_speed}")

       
    print(f"Total errors: {errors}")


if __name__ == "__main__":
    main()
