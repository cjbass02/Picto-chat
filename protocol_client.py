
import threading
from socket import *
import rsaFunctions
import guiControls
PUBLIC_EXPONENT = 17;
SERVER_HOST = 12100
SERVER_PORT = "10.108.86.171"
import os
import io
import PySimpleGUI as sg
global lock
import PIL.Image as Image
from PIL import ImageFile, ImageTk
from blockHelper import *
import drawer

ImageFile.LOAD_TRUNCATED_IMAGES = True

def main():
    """Provide the user with a variety of encryption-related actions"""
    createClient(SERVER_HOST,SERVER_PORT)
    
        
def createClient(server_host, server_port):
    """
    creates a connection to a server
    immediately after receive a public key tuple
    receive 2 bytes (D) and decode with m = int.from_bytes(D, 'big')
    receive m bytes (D), and then decode with n = int.from_bytes(D, 'big')
    receive '\r\n'
    repeat for public exponent e

    encrypt and send a message
    Create a plaintext ASCII message
    Encrypt
    Send 2 bytes (m) that give the size of the message in bytes
    Send encrypted messsage
    Send '\r\n'
    receive a b'A' and then close the connection
    """
    
    password = guiControls.startClientGUI()
    
    # global tcp_socket
    global tcp_socket
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    global addr
    addr = (server_port, server_host)
    tcp_socket.connect((server_port, server_host))
    reciever = threading.Thread(target = recieveMessages)
    sender = threading.Thread(target = sendMessages)
    
    #create key from data
    global priv
    priv = rsaFunctions.sendKey(tcp_socket)
    e, n = rsaFunctions.recvKey(tcp_socket)
    global pubKey
    pubKey = (e,n)   
    
    
    #sending password guess
    rsaFunctions.encryptPass(pubKey,password,tcp_socket)
    
    #recieving response to password guess
    while(True):
        response = tcp_socket.recv(1)
        if response != b'A':
            password = guiControls.wrongPasswordGUI()
            rsaFunctions.encryptPass(pubKey,password,tcp_socket)
        else:
            break
        
    #recieving the server name    
    global serverName    
    byte = b''
    while not byte.__contains__(b'\r\n'):
        byte += tcp_socket.recv(1)
    byte = byte[:-2]
    serverName = byte.decode("ascii")
    print("\n")
    print("You have entered " + serverName +"'s server!")
    
    #sending the server client name
    global name
    name = guiControls.clientNameGUI()
    tcp_socket.send(name.encode("ascii"))
    tcp_socket.send(b'\r\n')
    
    #setting layout for chat gui
    layout = [
        [sg.Titlebar("Chat Client")],
        [
            sg.Multiline(
                f" Hello {name}!\n Welcome to {serverName}'s chat!\n\n",
                font="Arial",
                no_scrollbar=True,
                size=(50, 20),
                text_color="white",
                background_color= "#383838",
                horizontal_scroll=True,
                autoscroll=True,
                echo_stdout_stderr=True,
                reroute_stdout=True,
                # write_only=True,
                reroute_cprint=True,
                disabled=True,
                # enter_submits=True,
                key="-OUTPUT-",
            ),
        ],
        [
            sg.Multiline(
                font="Arial",
                no_scrollbar=True,
                size=(50, 5),
                horizontal_scroll=False,
                autoscroll=True,
                key="-INPUT-",
            )
        ],
        [
            sg.Button("Send", size=(12, 1), key="-SEND-", button_color="#219F94"),
            sg.Push(),
            sg.Button("Exit", size=(12, 1), key="-EXIT-"),
        ],
    ]
    reciever.start()
    #creating gui window and setting the layout
    global window
    window= sg.Window("", layout, finalize= False)
    while(True):
        event, value = window.read()
        if event in [sg.WIN_CLOSED, "-EXIT-"]:
            window.close()
            break
        if event == "-SEND-":
            #sending message when sent button is pressed
            sendMessages(value['-INPUT-'])
            message = value["-INPUT-"]
            #prints message to the display
            sg.cprint(
                        f"{name} wrote:\n" + message,
                        c=("#383838", "#f697f7"),
                        justification="r",  # left / right,
            )
            window["-INPUT-"].update("")
        elif event == "-DONE-":
            # opens and displays the created image
            im = Image.open("cool.png")
            image = ImageTk.PhotoImage(image = im)   
            layout = [
                        [sg.Image(key='-IMAGE-', size=(im.width,im.height))],
                    ]
            picwindow = sg.Window("epic", layout, margins=(0, 0), finalize=True)
            picwindow['-IMAGE-'].update(data=image)
            picwindow.read()
            
 #handles sending messages           
def sendMessages(message):
        initial = "";
        if len(message) >= 1:
            if(len(message) >= 6):
                for x in range(6):
                    initial += message[x]
                if(initial == "/image"):
                    drawer.start()
                    tcp_socket.send(b'image\r\n')
                    blockCount = get_file_block_count("curSentImage.jpg")
                    for x in range (blockCount):
                        sendbytes("curSentImage.jpg", tcp_socket,x)
                    tcp_socket.send(b'\r\n\r\n')
                else:
                    tcp_socket.sendall(b'message\r\n')
                    rsaFunctions.encrypt(pubKey, message,tcp_socket)
            else:
                tcp_socket.send(b'message\r\n')
                rsaFunctions.encrypt(pubKey, message,tcp_socket)
                
#helper function that helps send bytes                 
def sendbytes(fileName, rec_socket, x):
    block = b''
    block += int.to_bytes(len(get_file_block(fileName, x + 1)), 2, 'big')
    block += get_file_block(fileName, x + 1)
    rec_socket.sendto(block, addr)
                
#reciever function that runs using a thread. Always looking for new messages             
def recieveMessages():
    while(True):
        types = tcp_socket.recv(1)
        if(types):
            while(True):
                data = b''
                fulldata = b''
                while not types.__contains__(b'\r\n'):
                    types += tcp_socket.recv(1)
                if types == b'image\r\n':
                    while not fulldata.__contains__(b'\r\n\r\n'):
                        size = tcp_socket.recv(2)
                        fulldata += size
                        for x in range(int.from_bytes(size, 'big', signed=True)):
                            recv = tcp_socket.recv(1)
                            data += recv
                            fulldata += recv
                            if(fulldata.__contains__(b'\r\n\r\n')):
                                break                  
                     #saves data as a byte array and creates a picture using the info
                    data = data[:-2]
                    arrayData = bytearray(data)
                    imageBytes = b''
                    imageBytes = io.BytesIO(arrayData)
                    im = Image.open(imageBytes)
                    im.save("cool.png")
                    window.write_event_value("-DONE-", 'done')
                    break
                elif types == b'message\r\n':
                        #recieve message
                        byte = b''
                        while not byte.__contains__(b'\r\n'):
                            byte += tcp_socket.recv(1)
                        byte = byte[:-2]
                        decrypted = rsaFunctions.decrypt(priv, byte)
                        #writes recieved message to display
                        sg.cprint(
                        f"{serverName} wrote: \n" + decrypted,
                        c=("#ffffff", "#858585"),
                        justification="l",  # left / right,
            )
                        data = b''
                        break
