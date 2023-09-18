
import threading
from socket import *
import rsaFunctions
import PIL.Image as Image
from PIL import ImageFile, ImageTk
import PySimpleGUI as sg
import guiControls
import io
from blockHelper import *
import drawer;

ImageFile.LOAD_TRUNCATED_IMAGES = True
PUBLIC_EXPONENT = 17;
SERVER_HOST = 12100
SERVER_PORT = "localhost"

def main():
    """Provide the user with a variety of encryption-related actions"""
    createServer(SERVER_HOST,SERVER_PORT)
    
def createServer(listen_port, listen_on):
    
    #creates server guis
    password, server_name = guiControls.startServerGUI()
    layout = [[sg.Text("Waiting for other users...")]]
    waitWindow = sg.Window("Wait", layout, size=(180,90))
    #creates socket and displays waiting window
    while True:
        waitWindow.read(timeout= 20)
        paddedPass = password.zfill(20)
        address = (listen_on, listen_port)
        s = socket(AF_INET, SOCK_STREAM)
        s.bind(address)
        s.listen(5)
        global c, addr;
        #accepting connection
        c, addr = s.accept()
        break
    
    #creating private and sending public key
    global priv
    priv = rsaFunctions.sendKey(c)
    #recieving info for and creating public key
    e, n = rsaFunctions.recvKey(c)
    global pubKey
    pubKey = (e,n)    
    
    #starting receiving thread
    reciever = threading.Thread(target = recieveMessages)
    
    #recieving password guess
    while(True):
        guess = b''
        for x in range(20):
            guess += c.recv(4)
            #sending response to password guess
        if rsaFunctions.decrypt(priv,guess) != paddedPass:
            c.send(b'F')
        else:
            c.send(b'A')
            break
    waitWindow.close()
    #sending server name to client
    c.send(server_name.encode("ascii"))
    c.send(b'\r\n')
    
    #recieving client name
    global name    
    byte = b''
    while not byte.__contains__(b'\r\n'):
        byte += c.recv(1)
    byte = byte[:-2]
    name = byte.decode("ascii")

    #creating large chat gui layout
    layout = [
        [sg.Titlebar("Chat Client")],
        [
            sg.Multiline(
                f" Hello {server_name}!\n Welcome to your chat!\n\n",
                f"{name} has joined the server!\n\n",
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
    
    #instaniating window at setting layout inside it
    global window
    window= sg.Window("", layout, finalize= False)
    
    while(True):
        event, value = window.read()
        if event in [sg.WIN_CLOSED, "-EXIT-"]:
            window.close()
            break
        if event == "-SEND-":
            #sending message when sent button is pressed
            initial = sendMessages(value['-INPUT-'])
            if initial != "/image":
                message = value["-INPUT-"]
                sg.cprint(
                            f"{server_name} wrote:\n" + message,
                            c=("#383838", "#f697f7"),
                            justification="r",  # left / right,
                )
            window["-INPUT-"].update("")
        elif event == "-DONE-":
            #opening recieved message and displaying it
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
        initial = ""
        if len(message) >= 1:
            #checks to see if the message is a image command
            if(len(message) >= 6):
                for x in range(6):
                    initial += message[x]
                if(initial == "/image"):
                    #creates a drawer object and reads drawn image in chunks
                    drawer.start()
                    c.send(b'image\r\n')
                    blockCount = get_file_block_count("curSentImage.jpg")
                    for x in range (blockCount):
                        sendbytes("curSentImage.jpg", c,x)
                    c.send(b'\r\n\r\n')
                else:
                    #sending a message and encypting it
                    c.sendall(b'message\r\n')
                    rsaFunctions.encrypt(pubKey, message,c)
            else:
                c.send(b'message\r\n')
                rsaFunctions.encrypt(pubKey, message,c)
        return initial

#helper function that helps send bytes                
def sendbytes(fileName, rec_socket, x):
    block = b''
    block += int.to_bytes(len(get_file_block(fileName, x + 1)), 2, 'big')
    block += get_file_block(fileName, x + 1)
    rec_socket.sendto(block, addr)
    
#reciever function that runs using a thread. Always looking for new messages                
def recieveMessages():
    while(True):
        types = c.recv(1)
        if(types):
            while(True):
                data = b''
                fulldata = b''
                while not types.__contains__(b'\r\n'):
                    types += c.recv(1)
                if types == b'image\r\n':
                    while not fulldata.__contains__(b'\r\n\r\n'):
                        size = c.recv(2)
                        fulldata += size
                        for x in range(int.from_bytes(size, 'big', signed=True)):
                            recv = c.recv(1)
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
                            byte += c.recv(1)
                        byte = byte[:-2]
                        decrypted = rsaFunctions.decrypt(priv, byte)
                        #writes recieved message to display
                        sg.cprint(
                        f"{name} wrote: \n" + decrypted,
                        c=("#ffffff", "#858585"),
                        justification="l",
            )
                        data = b''
                        break
        
        
