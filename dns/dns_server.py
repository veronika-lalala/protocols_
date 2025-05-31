import socket
import threading
import time
import pickle
from dnslib import DNSRecord, QTYPE

from dns_cache import DNSCache


class DNSServer:
    def __init__(self):
        self.cache = DNSCache()
        self.upstream_server = '192.168.1.254'
        self.running = False
        self.socket = None
        self.cache.load()



    def start(self):
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', 53))
        print(f"Кэширующий DNS сервер стартовал на 53 (использует {self.upstream_server})")

        try:
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(512)
                    threading.Thread(target=self.handle_request, args=(data, addr)).start()
                except socket.error as e:
                    print(f"Socket error: {e}")
        except KeyboardInterrupt:
            print("Сервер прерван")
        finally:
            self.running = False
            self.cache.save()
            if self.socket:
                self.socket.close()

    def handle_request(self, data, addr):
        try:
            request = DNSRecord.parse(data)
            qname = request.q.qname
            qtype = request.q.qtype
            print(f'Получил запрос:{qname}  '
                  f'{qtype}')

            cached_records = self.cache.get_records(qname, qtype)
            if cached_records:
                print(f"Есть кэш {qname} {QTYPE[qtype]}")
                reply = request.reply()
                for rr in cached_records:
                    reply.add_answer(rr)
                self.socket.sendto(reply.pack(), addr)
                return

            print(f"Кэша нет для  {qname} {QTYPE[qtype]}, запросил у {self.upstream_server}...")

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.settimeout(2)
                    s.sendto(data, (self.upstream_server, 53))
                    response, _ = s.recvfrom(512)
                    dns_response = DNSRecord.parse(response)
                    for section in [dns_response.rr, dns_response.auth, dns_response.ar]:
                        for rr in section:
                            print(f"Добавляемая запись: name={rr.rname}, type={QTYPE[rr.rtype]}, ttl={rr.ttl}")
                            self.cache.add_record(rr)

                    self.socket.sendto(response, addr)
            except (socket.timeout, socket.error) as e:
                print(f"Ошибка старшего сервера dns: {e}")
                reply = request.reply()
                reply.header.rcode = 2
                self.socket.sendto(reply.pack(), addr)

        except Exception as e:
            print(f'Ошибка обработки запроса: {e}')
            reply = DNSRecord.parse(data).reply()
            reply.header.rcode = 2
            self.socket.sendto(reply.pack(), addr)




if __name__ == '__main__':
    server = DNSServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server stopped")
