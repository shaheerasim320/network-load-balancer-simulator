from socket import *
import time
from concurrent.futures import ThreadPoolExecutor
import threading
class Server:
    def __init__(self,port) -> None:
        self.port=port
        self.server_load=0
        self.response_time=0
        self.total_response_time=0
        self.total_requests=0
        self.executor=ThreadPoolExecutor(max_workers=10000)
        self.stop_event = threading.Event()
    
    def handle_client(self,connectionSocket,session_id,message) -> bool:
        try:
            self.server_load+=1
            start_time=time.time()
            message = message.decode('utf-8')

            print("\n" + message)

            filename = message.split()[1]
            print(filename[1:])
            f = open(filename[1:])
            outputdata = f.read()
            connectionSocket.send(f"HTTP/1.1 200 OK\r\nSet-Cookie: Session-ID={session_id}\r\nServer-Port: {self.port}\r\n\r\n".encode())
            connectionSocket.send(outputdata.encode())
            end_time=time.time()
            connectionSocket.close()

            self.total_requests+=1
            response_time = end_time - start_time
            self.total_response_time+=response_time
            self.update_server_response_time()
            self.server_load-=1
            return True

        except IOError:
            connectionSocket.send("HTTP/1.1 404 Not Found\r\n")
            connectionSocket.close()
            return False


    def start_server(self):
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((gethostname(), self.port))
        serverSocket.listen(1)

    def handle_client_request(self, connectionSocket,session_id,message) -> bool:
        print("Ready To Handle Request")
        result = False
        future = self.executor.submit(self.handle_client, connectionSocket,session_id,message)

        try:
            result = future.result()
        except Exception as e:
            print("An error occurred:", e)
            result = False

        return result
        
    def display_stats(self):
        
        print(f'\n\nStats Of Server On Port {self.port}\n')
        print(f'Total Request Handled By Server: {self.total_requests}\n')
        print(f'Response Time Of Server: {self.response_time}\n\n')
    
    def update_server_response_time(self):
        if self.total_requests==0:
            return
        avg_time=self.total_response_time/self.total_requests
        self.response_time=avg_time
    
    def stop(self):
        self.stop_event.set()  