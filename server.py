import random
import socket
import time

#python threads - importing evetthing(*) from thread
from _thread import *
import threading

from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024) #데이터(최대1024)를 받아서, date, addr에 넣어줌 --> 튜플type으로 리턴 --> 이렇게 [ bits, [IP, Port] ].

      data = str(data)                 #받은 데이터를 string으로 변경

      if addr in clients:              # addr가 clients안에있으면 (dictionary)
         if 'heartbeat' in data:       # 'heartbeat' (object property)가 data 안에 있으면.  
            clients[addr]['lastBeat'] = datetime.now()  #lastBeat을 datetime.now() 으로 업데이트
            
      else:                            #addr이 없을때
         if 'connect' in data:

           # clients[addr] = {}         
           # clients[addr]['lastBeat'] = datetime.now()
           # clients[addr]['color'] = 0
           # message = {"cmd": 0,"player":{"id":str(addr)}} #id 받아서 새로 추가    # "cmd": 0 - new player connected.

            oldClientsInfo = {"cmd" : 2, "player" : []} #cmd :2 - 기존 클라 정보를 다 들고있음 - dictionary, "player" : []- 배열
            for c in clients:
               player = {} # player dictionary 만듬
               player["id"] = str(c) #c에는 clients의 key - ip, port가 들어있는걸 string converting 해서 player 의 id key에 줌
               player["color"] = clients[c]["color"] #clients의 c라는 key값으로 color라는 value를 가져옴  c - ip, port.
               oldClientsInfo["player"].append(player)  # player dictionary의 값들을 oldClientsInfo의 player key에 넣어줌
            oci = json.dumps(oldClientsInfo)    #oldClientsInfo를 json으로 만들어서 oci에 넣어줌
            sock.sendto(bytes(oci,'utf8'), (addr[0], addr[1])) #oci를 쏜다 클라한테, addr[0] - ip, addr[1] - port

            clients[addr] = {} #새로운 클라의 정보를 넣어줄 공간, 속을 비워줌
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = {"R" : 1, "G" : 1, "B" : 1} #새로운 색상을 줄 공간을 만듬. color의 key에 또다른 dictionary를 넣어줌
            clients[addr]['position'] = {"x" : 0, "y" : 0, "z" : 0} #새로운 포지션을 줄 공간을 만듬

            # for c in clients: #send 패킷 utf8타입의 m을 bytes로 형변환해서, c = [ip, port]
            #    sock.sendto(bytes(m,'utf8'), (c[0],c[1]))

def cleanClients():
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            clients_lock.acquire()
            del clients[c]    #deleting the memory
            clients_lock.release()
      time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      print (clients)
      for c in clients:
         player = {}
         clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
         player['id'] = str(c)
         player['color'] = clients[c]['color']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(1)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create a new socket, type: udp
   s.bind(('', port))                                   #bind socket to local ip '' and port(12345)

   #start_new_thread(쓰레딩할 함수이름, 함수에 pass to 하고싶은거 - argument)
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,())

   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
