import sys
import subprocess
import re
import urllib.request

def tracing_as(arg):
    ip_reg= re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    try:
        output=subprocess.check_output(f'tracert {arg}',shell=True).decode('cp866')
        ip_addresses = re.findall(ip_reg,output)
        ip_addresses.pop(0)
        work_with_ip_addresses(ip_addresses)
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')
def get_inf(addres):
    with urllib.request.urlopen(f'https://ipinfo.io/{addres}') as f:
        inf=f.read().decode('utf-8')

    if 'bogon' in inf:
        return('bogon','-','-')
    else:
        ind_country=inf.find('"country": ')+len('"country": ')+1
        country=inf[ind_country:ind_country+2]
        ind_org=inf.find('"org": "')+len('"org": "')
        org=inf[ind_org:].split('\n')[0]
        ind=org.find(' ')
        asn=org[:ind]
        provider=org[ind+1:-2]

        return(asn,country,provider)

def work_with_ip_addresses(addresses):
    space_num=5
    space_ip=22
    space_country=4
    space_asn=20
    for i in range (len(addresses)):

        (asn,country,provider)=get_inf(addresses[i])
        num=str(i+1)
        print(num+' '*(space_num-len(num))+addresses[i]+' '*(space_ip-len(addresses[i]))+asn+' '*(space_asn-len(asn))+country +' '*space_country+provider)




def main():
    if len(sys.argv)<2:
        print("Необходимо передать в качестве аргумента ip-адрес или доменное имя")
    else:
        tracing_as(sys.argv[1])

if __name__ == '__main__':
    main()


