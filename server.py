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

def IsFloat(s):
   try:
      float(s)
      return True
   except ValueError:
      return False

def connectionLoop(sock):
   while True:
      #데이터(최대1024)를 받아서, date, addr에 넣어줌 --> 튜플type으로 리턴 --> 이렇게 [ bits, [IP, Port] ].
      #-> get date (maximun 1024) and give to date and addr variables. (Retrun tuple)
      data, addr = sock.recvfrom(1024) 

      #받은 데이터를 string으로 변경
      #-> convert to string
      data = str(data)                 

      # addr가 clients안에있으면 (dictionary)
      # ->if addr(ip, port) is in clients = means do not need to make new clients
      if addr in clients:      

         # 'heartbeat' (object property)가 data 안에 있으면. 
         # -> if 'heartbeat'(object property) is in data       
         if 'heartbeat' in data:      

            #lastBeat을 datetime.now() 으로 업데이트
            #-> update lastBeat   
            clients[addr]['lastBeat'] = datetime.now()  

         # clients send position to server
         elif 'position' in data:
            Pos = []
            for num in data.split():
               if IsFloat(num):
                  Pos.append(float(num))

            #### here variables name should be same with clients ####
            clients[addr]['position']["x"] = Pos[0]
            clients[addr]['position']["y"] = Pos[1]
            clients[addr]['position']["z"] = Pos[2]

      #addr이 없을때
      #-> if no addr = means new clients!
      else:                            
         if 'connect' in data:
           ########################################### Give my addr to me ##############################################
            connectedClient = {"cmd" : 3, "id": str(addr)}
            cc = json.dumps(connectedClient)
            sock.sendto(bytes(cc,'utf8'), (addr[0], addr[1]))

           ########################################### Give old clients' information to new clients ##############################################
            #cmd :2 - 기존 클라 정보를 다 들고있음 - dictionary, "player" : []- 배열
            #-> cmd is in clients (enum), and it holds all the information of old clients
            oldClientsInfo = {"cmd" : 2, "players" : []} 
            for c in clients:
               # player dictionary 만듬
               # -> new dictionary of player
               player = {} 

               #c에는 clients의 key - ip, port가 들어있는걸 string converting 해서 player 의 id key에 줌
               #-> in c, there are clients' keys(ip, port) and convert it to player["id"]
               player["id"] = str(c) 

               #clients의 c라는 key값으로 color라는 value를 가져옴  c - ip, port.
               #-> get color and give it to player
               player["color"] = clients[c]["color"] 
               #-> get position and give it to player
               player["position"] = clients[c]["position"] 
              
               # player dictionary의 값들을 oldClientsInfo의 player key에 넣어줌
               # ->append to dictionary
               oldClientsInfo["players"].append(player)  

            #oldClientsInfo를 json으로 만들어서 oci에 넣어줌
            #-> this is the code cane make oldClientsInfo to Json
            oci = json.dumps(oldClientsInfo)    

            #oci를 쏜다 클라한테, addr[0] - ip, addr[1] - port
            #-> send to clients
            sock.sendto(bytes(oci,'utf8'), (addr[0], addr[1])) 

          #############################################Give new clients' information to old clients####################################
            newClientsInfo = {
               "cmd" : 0, 
              "id" : str(addr), 
              "color" : {"R": 1, "G" : 1, "B" : 1},
              "position" : {"x" : 0, "y" : 0, "z" : 0}
            }

            nci = json.dumps(newClientsInfo)

            for c in clients:
               sock.sendto(bytes(nci,'utf8'), (c[0], c[1])) # give information


          ###########################################################################################################################
            #새로운 클라의 정보를 넣어줄 공간, 속을 비워줌
            #-> for new clients' information. empty inside
            clients[addr] = {} 
            clients[addr]['lastBeat'] = datetime.now()

            #새로운 색상을 줄 공간을 만듬. color의 key에 또다른 dictionary를 넣어줌
            #-> a space for new color and position
            clients[addr]['color'] = {"R" : 1, "G" : 1, "B" : 1}
            clients[addr]['position'] = {"x" : 0, "y" : 0, "z" : 0} 

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
         #give color and positions here
         player['color'] = clients[c]['color']
         player['position'] = clients[c]['position']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(0.3) 

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create a new socket, type: udp
   s.bind(('', port))                                   #bind socket to local ip '' and port(12345)

   #start_new_thread(function name, argument)
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,())

   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
