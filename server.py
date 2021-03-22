import socket
import threading
import encrypt

#LocalIP = socket.gethostbyname_ex(socket.gethostname())[2][2]
LocalIP = "localhost"

encryption = int(input("Choose encryption: 0->none    1->symmetric     2->asymmetric\n"))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((LocalIP, 7856))
s.listen(2)

print("use this IP in clients: " + LocalIP)

SIZE = 512

clientSocket0, address0 = s.accept()
clientSocket1, address1 = s.accept()

if encryption == 0:
    clientSocket0.send(bytes("0,0", "utf-8"))
    clientSocket1.send(bytes("1,0", "utf-8"))

elif encryption == 1:
    # create Key
    en = encrypt.Encrypt()
    sym = en.GenerateSymetricKey()

    print("0," + sym.decode("utf-8"))
    clientSocket0.send(bytes("0,1," + sym.decode("utf-8"), "utf-8"))
    clientSocket1.send(bytes("1,1," + sym.decode("utf-8"), "utf-8"))

else:
    clientSocket0.send(bytes("0,2", "utf-8"))
    clientSocket1.send(bytes("1,2", "utf-8"))
    # get clients public keys
    public0 = clientSocket0.recv(SIZE)
    public1 = clientSocket1.recv(SIZE)
    clientSocket0.send(public1)
    clientSocket1.send(public0)


def client0Thread():
    while True:
        try:
            x = clientSocket0.recv(SIZE)
            if x == "finished":
                return
            clientSocket1.send(x)
        except:
            return


def client1Thread():
    while True:
        try:
            x = clientSocket1.recv(SIZE)
            if x == "finished":
                return
            clientSocket0.send(x)
        except:
            return


thread0 = threading.Thread(target=client0Thread)
thread1 = threading.Thread(target=client1Thread)

thread0.start()
thread1.start()

thread0.join()
thread1.join()

clientSocket0.close()
clientSocket1.close()
