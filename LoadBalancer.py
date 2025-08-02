from Server import Server
from socket import *
import time
import threading
import random

class LoadBalancer:
    def __init__(self) -> None:
        self.base_port=5433
        self.server_threads=[]
        self.servers=[]
        self.unavailable_servers=[]
        self.low_traffic_count=0
        self.high_traffic_count=0
        self.low_traffic_threshold=10
        self.high_traffic_threshold=80
        self.cooldown_period=5
        self.min_severs_mandatory=3
        self.max_servers_to_remove=2 
        self.max_servers_to_add=2 
        self.client_sessions={}
        

        for _ in range(9):
            self.add_server()
        
        for s_inst,thread in self.server_threads:
            thread.join(0.1)
        
        self.start_load_balancer()
    
    def add_server(self):
        port=self.base_port+len(self.servers)
        server_instance=Server(port) 
        self.servers.append(server_instance) 

        server_thread=threading.Thread(target=server_instance.start_server)
        server_thread.start()
        self.server_threads.append((server_instance,server_thread))
        print(f"Added new server on port {port}")
        
    def load_balancer(self) -> None:

        print ("\n" + gethostbyname(gethostname()))

        mainServerSocket = socket(AF_INET, SOCK_STREAM)
        mainServerSocket.bind((gethostname(), 5432))
        mainServerSocket.listen(100)

        while True:
            print('\n\nReady to serve...')

            connectionSocket, address = mainServerSocket.accept()

            request_thread = threading.Thread(target=self.send_request, args=(connectionSocket,))
            request_thread.start()
                  

    def send_request(self,connectionSocket):
        message=self.receive_message(connectionSocket)
        session_id=self.extract_session_id(message.decode())
        if not session_id:
            session_id=self.generate_session_id()
        selected_server=self.select_server_session_id(session_id)
        result=selected_server.handle_client_request(connectionSocket,session_id,message)
        if(not result):
            self.handle_failed_request(selected_server,connectionSocket)
    
    def receive_message(self, connectionSocket):
        message = connectionSocket.recv(1024) 
        return message
    
    def extract_session_id(self,message):
        if message:
            for line in message.split("\r\n"):
                if "Session-ID=" in line: 
                    session_id = line.split("Session-ID=")[1]
                    return session_id
        return None 
    def select_server_session_id(self,session_id):
        if(session_id in self.client_sessions):
            return self.client_sessions[session_id]
        selected_server=self.select_server()
        self.client_sessions[session_id]=selected_server
        return selected_server
        
    def select_server(self) -> Server:
        selected_server = None
        min_load = float('inf')
        min_response_time = float('inf')

        for server in self.servers:
            if(server.server_load < min_load or (server.server_load == min_load and server.response_time < min_response_time)) and server not in self.unavailable_servers:
                selected_server = server  
                min_load = server.server_load 
                min_response_time = server.response_time 

        return selected_server

    def handle_failed_request(self, selected_server, connectionSocket):
        self.unavailable_servers.append(selected_server)
        retries = 0
        retry_limit = len(self.servers) - len(self.unavailable_servers) 
        retry_status = False

        while retries < retry_limit:
            new_server = self.select_server()
            if(new_server):
                result = new_server.handle_client_request(connectionSocket)
                if result:
                    self.unavailable_servers.clear()
                    retry_status = True
                    break
            retries += 1  

        if(not retry_status):
            print("Unable To Handle Request. All Servers Failed.")
    
    def show_server_stats(self) -> None:
        while True:
            print('\n-----------------------------------------------Stats Starts---------------------------------------------')
            for server in self.servers:
                server.display_stats()
            print('---------------------------------------------------Stats End---------------------------------------------\n')
            time.sleep(120)

    def monitor_traffic(self):
        while True:
            traffic=self.get_traffic_percentage()
            print(f'The Traffic Percentage Is {traffic}')
            if(traffic<self.low_traffic_threshold):
                self.low_traffic_count+=1
                if self.low_traffic_count>=self.cooldown_period:
                    self.scale_down_servers()
            else:
                self.low_traffic_count=0

            if(traffic>self.high_traffic_threshold):
                self.high_traffic_count+=1
                if self.high_traffic_count>=self.cooldown_period:
                    self.scale_up_servers()
            else:
                self.high_traffic_count=0

            time.sleep(60)
            
            
    def get_traffic_percentage(self) -> float:
        total_traffic=sum([server.server_load for server in self.servers])
        total_capacity=sum([server.executor._max_workers for server in self.servers])
        traffic_percentage=(total_traffic/total_capacity)*100
        return traffic_percentage

    def scale_down_servers(self):
        removed_servers = 0
        while(len(self.servers)>self.min_severs_mandatory):
            if(removed_servers<self.max_servers_to_remove):
                removed_server_port = self.servers.pop().port
                self.remove_server(removed_server_port) 
                removed_servers += 1
            else:
                break 
        
        if removed_servers == 0:
            print("Minimum Mandatory Servers Running Only")
        else:
            print(f"Scaled down: {removed_servers} server(s) removed.")
        self.low_traffic_count=0

    def scale_up_servers(self):
        for _ in range(self.max_servers_to_add):
            self.add_server()
        print(f"Scaled Up: {self.max_servers_to_add} servers added.")

    def remove_server(self,port):
        for (server_instance,thread)in self.server_threads:
            if(server_instance.port==port):
                server_instance.stop()  
                thread.join() 
                print(f'Server Has Been Shut Down On Port {port}') 
                break
    
    def generate_session_id(self):
        random_part = random.randint(1000, 9999)
        time_part = int(time.time_ns())
        session_id = f"{random_part}{time_part}"
        return session_id
    
    def start_load_balancer(self):
        server_stats=threading.Thread(target=self.show_server_stats,daemon=True)
        server_stats.start()
        traffic_volume=threading.Thread(target=self.monitor_traffic,daemon=True)
        traffic_volume.start()
        self.load_balancer()

def main():
    loadBalancer=LoadBalancer()


if __name__=='__main__':
    main()