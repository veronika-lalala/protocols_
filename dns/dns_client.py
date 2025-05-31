import socket
from dnslib import DNSRecord, DNSQuestion, QTYPE

class Client:
    def __init__(self):
        self.host='127.0.0.1'
        self.port=53

    def run(self):
        print("dddd")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((self.host,self.port))
            while True:
                query = input("Введите запрос: домен и  тип(A/AAAA/NS/PTR) через пробел или 'q' для выхода: ")
                if query.lower() == 'q':
                    break
                parts = query.split()
                domain = parts[0]
                if len(parts)==1:
                    request = DNSRecord(q=DNSQuestion(parts[0], QTYPE.A))

                elif len(parts)>1:
                    if parts[1] == 'A':
                        request = DNSRecord(q=DNSQuestion(domain, QTYPE.A))
                    elif parts[1] == 'AAAA':
                        request = DNSRecord(q=DNSQuestion(domain, QTYPE.AAAA))  # Исправлено на латинские A
                    elif parts[1] == 'NS':
                        request = DNSRecord(q=DNSQuestion(domain, QTYPE.NS))
                    elif parts[1] == 'PTR':
                        try:
                            #парсим нормально ip
                            ip = parts[0].rstrip('.')
                            ip_parts = ip.split('.')
                            if len(ip_parts) != 4:
                                raise ValueError("Неверный формат IPv4")

                            ptr_query = '.'.join(reversed(ip_parts[:3])) + '.in-addr.arpa.'
                            request = DNSRecord(q=DNSQuestion(ptr_query, QTYPE.PTR))
                        except Exception as e:
                            print(f"Ошибка в формате IP: {e}")
                            continue
                    else:
                        print("Неверный запрос")
                        continue
                else:
                    print("Неверный запрос")
                    continue


                s.send(request.pack())
                response, _ = s.recvfrom(1024)
                print(DNSRecord.parse(response))

            s.close()
if __name__ == '__main__':
    client=Client()
    client.run()