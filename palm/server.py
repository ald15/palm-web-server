'''
PALM web-server v1.0
05.2024 Дорофеев А.
'''

import socket
import time
import os

running = False

class palmServer:
    # Класс веб-сервер
    
    def __init__(self, host:str="127.0.0.1", port:int=80, dir="www", params:dict=None) -> None:
        '''
        Конструктор сервера

        Имя хоста (по умолчанию: 127.0.0.1): host: str
        Порт хоста (по умолчанию: 80): host: int
        Словарь дополнительных параметров: dict
        '''
        # Имя хоста
        self.host = host
        # Порт
        self.port = port
        # Директория сервера
        self.dir = dir
        # Имя хоста клиента
        self.clientHost = None
        # Количество подключений, которое может быть обработано
        self.ConnectionsAmount = 5
        # Количество обработанных HTTP запросов
        self.HTTPReqAmount = 0
        # Название сервера
        self.name = "PALM web-server"
        # Имя файла журнала событий
        self.logFile = "log.txt"
        # Имя файла журнала HTTP запросов
        self.logHTTPReq = "HTTP_requests.txt"
        # Имя файла журнала HTTP ответов
        self.logHTTPRes = "HTTP_responds.txt"
        # Маршруты переадресации
        self.routes = [
            ["/", "index.html"],
            ["/index", "index.html"]
        ]
        # Словарь дополнительных параметров
        if params:
            self.ConnectionsAmount = params["ConnectionsAmount"]
            self.logFile = params["logFile"]
            self.logHTTPReq = params["logHTTPReq"]
            self.logHTTPRes = params["logHTTPRes"]
            self.routes = params["routes"]
        # Сообщения сервера для журнала
        self.logMsgs = {
            # Сообщение для проверки журнала
            "test": ["ОТЛАДКА", "Журанл работает успешно!"],
            # Сообщение для пользовательской отладки
            "test_user": ["ОТЛАДКА", ""], 
            # Сообщение запуска сервера
            "start": ["ИНФО", "Выполняется запуск PALM web-server..."],
            # Сообщение об успешном запуске сервера
            "started": ["ИНФО", f"PALM web-server ({self.host}:{self.port}) был УСПЕШНО ЗАПУЩЕН!"],
            # Сообщение остановки сервера
            "stop": ["ИНФО", "Выполняется остановка PALM web-server..."],
            # Сообщение об успешной остановке сервера
            "stopped": ["ИНФО", "PALM web-server был УСПЕШНО ОСТАНОВЛЕН!"],
            # Сообщение перезапуска сервера
            "restart": ["ИНФО", "Выполняется перезапуск PALM web-server..."],
            # Сообщение об успешном перезапуске сервера
            "restarted": ["ИНФО", "PALM web-server был УСПЕШНО ПЕРЕЗАПУЩЕН!"],
            # Сообщение о подключении клиента к серверу
            "connect": ["ИНФО", f"Новое подключение к серверу!"],
            # Сообщение об отключение клиента от серверп
            "disconnect": ["ИНФО", f"Клиент: {self.clientHost} был УСПЕШНО ОТКЛЮЧЕН!"],
            # Сообщение об обработке запроса
            "handle": ["ИНФО", f"Выполняется обработка запроса..."],
            # Сообщение об успешной обработке запроса
            "handled": ["ИНФО", f"Обработка запроса была УСПЕШНО ВЫПОЛНЕНА!"],
            # Сообщение об изменении маршрута
            "route": ["ИНФО", f"Задан маршрут для данного запроса. Выполняется переадресация..."],
            # Сообщение об успешном перенаправлени ответа
            "routed": ["ИНФО", f"Переадресация была УСПЕШНО ВЫПОЛНЕНА!"],
            # Сообщение об отправке HTTP-ответа
            "respond": ["ИНФО", f"Выполняется отправка HTTP-ответа..."],
            # Сообщение об успешной отправке HTTP-ответа
            "responded": ["ИНФО", f"HTTP-ответ был УСПЕШНО отправлен!"],
            # Сообщение об ошибке
            "error": ["ОШИБКА", "Произошла ошибка:"],
            # Сообщение пользовательское с пустым телом
            "user": ["ИНФО", ""]
        }

    def start(self) -> None:
        '''Метод запуска веб-сервера'''
        self.log("start")
        # Cоздаём объект сокета сервера
        self.server = socket.socket()
        # Устанавливаем время ожидания подключения
        self.server.settimeout(5)
        # Производим привязку сокета сервера к хосту и порту
        self.server.bind((self.host, self.port))
        # Прослушиваем сокет, допускаем не более ConnectionsAmount подключений
        self.server.listen(self.ConnectionsAmount)
        self.log("started")
        # Запускаем обработку основного задания
        self.task()
    
    def task(self) -> None:
        '''Метод основного задания'''
        global running
        # Запускаем бесконечный цикл
        while running:
            print(running)
            # Принимаем входящее соединение
            self.curCon = None
            try:
                self.curCon, self.clientHost  = self.server.accept()
            except socket.timeout:
                if not running: 
                    break
            if running and self.curCon:
                self.log("connect", 0, f" ({self.clientHost})")
                # Запускаем обрабочик HTTP запроса
                self.handler()
            
            
        self.stop()

    def stop(self) -> None:
        '''Метод остановки сервера'''
        self.log("stop")
        time.sleep(5)
        # Закрываем серверный сокет
        self.server.close()
        self.log("stopped")

    def restart(self) -> None:
        '''Метод перезапуска сервера'''
        global running
        self.log("restart")
        # Выключааем сервер
        self.stop()
        # Включаем сервер
        running = True
        self.start()
        self.log("restarted")

    def handler(self) -> None:
        '''Метод обрабочика HTTP запросов'''
        self.log("handle")
        # Инициализация
        self.MIMEType = "html"
        self.HTTPStatus = 404
        self.HTTPStatusText = "ERROR"
        resBody = f"<h1>404 Not Found</h1><p>The requested URL was not found on this server.</p>".encode()
        # Получаем байты данных запроса
        req = self.curCon.recv(1024)
        # Преобразуем байты данных в строку -> HTTP сообщение
        reqMsg = req.decode()         
        self.logHTTP(0, reqMsg)
        # Разбиваем HTTP запрос на строки и анализируем первую строку
        req_lines = reqMsg.split('\n')
        # Получаем тип HTTP запроса и маршрут
        try:
            reqType, reqPath, _ = req_lines[0].split()
        except:
            reqType = None
        if reqType == "GET":
            # Устанавливаем флаг наличия переадресации в значение Ложь
            isRouted = False
            # Выполняем проверку на наличие переадресаций
            for route in self.routes:
                # Сравниваем наш текущий путь с каждым маршрутом из задданно таблицы маршрутов
                if reqPath == route[0]:
                    # Устанавливаем флаг наличия переадресации в значение Истина
                    isRouted = True
                    self.log("route")
                    # Проверяем существует ли запрашиваемый файл (рассматривается только единичная переадресация)
                    path = self.dir + "/" + route[1]
                    if not os.path.exists(path):
                        self.log("error", 0, "указанный файл не существует!")
                        break                    
                    else:
                        self.MIMEType = path.split(".")[-1] if "." in path else "plain"
                        self.HTTPStatus = 200
                        self.HTTPStatusText = "OK"
                        with open(path, "rb+") as f:
                            resBody = f.read()
                    self.log("routed")
                    break
            if not isRouted:
                path = self.dir + reqPath
                if not os.path.exists(path):
                    self.log("error", 0, " неверный маршрут запроса!")
                else: 
                    self.MIMEType = path.split(".")[-1] if "." in path else "plain"
                    self.HTTPStatus = 200
                    self.HTTPStatusText = "OK"
                    with open(path, "rb") as f:
                        resBody = f.read()
        else:
            # Пока что другие методы HTTP запроса не рассматириваются
            pass
        self.log("respond")
        # Формируем сообщение ответа
        resMsg = f"HTTP/1.1 {self.HTTPStatus} {self.HTTPStatusText}\nContent-Type: text/{self.MIMEType}\nServer:\
PALM web-server v1.0 (developed in 2024 by Dorofeev A.)\nContent-Length: {len(resBody)}\n\n"
        # Преобразуем сообщение ответа в байты
        res = resMsg.encode() + resBody
        # Отправляем ответ
        self.curCon.sendall(res)
        self.log("responded")
        # Закрываем соединение с клиентом
        self.curCon.close()  
        self.log("handled")

    def log(self, type:str=None, method:int=0, content:str="") -> None:
        '''
        Метод ведения журнала веб-сервера

        Тип сообщения - type: "test", "test_user", "start", "started", "stop",\
"stoppped", "restart", "restarted", "connect", "disconnect", "handle", "handled",\
"route", "routed", "respond", "responded", "error", "user"
        Метод вывода (0-файл-журнал (по умолчанию), 1-консоль) - method: 0, 1 
        Тело сообщения (по умолчанию: "") - content: str
        '''
        # Не указаны параметры, поэтому не производим запись в журнал
        if type == None: return
        # Текущее время в формате [День.Месяц.Год Часы:Минуты:Секунды]
        curTime = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
        # Сборка сообщения сервера
        # Дата сообщения
        logMsgTime = f"[{curTime}]"
        # Тип сообщения
        logMsgType = "{" + self.logMsgs[type][0] + "}\t>>> "
        # Тело сообщения
        logMsg = logMsgTime + logMsgType + self.logMsgs[type][1] + " " + content
        if method == 0:
            # Записываем сообщение сервера в файл-журнал
            with open(self.logFile, "a+", encoding="utf8") as f:
                f.write(logMsg + "\n")
        elif method == 1:
            # Выводим сообщение сервера в консоль
            print (logMsg)
        else:
            return

    def logHTTP(self, type:int=None, content:str="") -> None:
        '''
        Метод ведения HTTP журнала ответа/запроса

        Тип сообщения (0-запрос, 1-ответ) - type: 0, 1
        Тело сообщения - content: str
        '''
        # Не указаны параметры, поэтому не производим запись в журнал
        if type == None: return
        fileName = ""
        # Определяем на основании типа название файла журнала 
        if type == 0:
            fileName = self.logHTTPReq
        elif type == 1:
             fileName = self.logHTTPReq
        else:
            return
        # Записываем сообщение сервера в файл-журнал
        logMsg = content
        with open(fileName, "a+", encoding="utf8") as f:
            f.write(logMsg + "\n")

    def logClear():
        '''Метод очистки журналов'''
        pass

def main():
    '''Тестирование веб-сервера'''
    global running
    new_server = palmServer("localhost", 81)
    running = True
    new_server.start()

if __name__ == "__main__":
    main()
    input()