from socket import *
import threading
import time

# Get server host IP address and port number
serverIP = input("\n\nEnter the IP Address of the host : ")
serverPort = int(input("Enter the port to connect to : "))

#Get the filename
        
filename = input("\n\nEnter the relative path of the file to be retrieved : ")
# Q2\Server.py

def send_client_request():
    # Create socket
    clientSocket = socket(AF_INET, SOCK_STREAM)

    try:
        # Try connecting to the provided host
        clientSocket.connect((serverIP, serverPort))
        print ("\nConnection Successful!")

        # Send the HTTP request message
        clientSocket.send(("GET /" + filename + " HTTP/1.1\r\n" +
                        "Host: " + gethostbyname(gethostname()) + ":" + str(
                    clientSocket.getsockname()[1]) + "\r\n\r\n").encode())

        print ("\n\n---------------HTTP RESPONSE---------------\n")

        # Receive one HTTP response header line
        response = clientSocket.recv(1024).decode()
        print(response)

        # Check for Session-ID in Set-Cookie header
        if "Set-Cookie: Session-ID=" in response:
            session_id = response.split("Set-Cookie: Session-ID=")[1].split("\r\n")[0]
            print(f"Received Session-ID: {session_id}")

        # Receive the file
        fileData = clientSocket.recv(10000).decode()
        print(fileData)

        print ("---------------END OF HTTP RESPONSE---------------\n")

        # Close the connection
        clientSocket.close()

    except error:
        print ("\n\nError while connecting!")
        clientSocket.close()

def main():
        for _ in range(2000):
            thread = threading.Thread(target=send_client_request)
            thread.start()
            time.sleep(1)
        # time.sleep(1)


if __name__=='__main__':
    main()
