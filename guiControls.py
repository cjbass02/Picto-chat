import PySimpleGUI as sg
import protocol_server
import threading
import protocol_client
def mainGUI():
    layout = [[sg.Titlebar("Connection Type")],
                [sg.Text("Please select if you want to join or host a server.")],
                [
                sg.Button("HOST", size = (12,1), key = "-SERVER-", button_color="#219F94"),
                sg.Button("JOIN", size = (12,1), key = "-CLIENT-", button_color="#219F94"),
                ]
            ]
    window = sg.Window("", layout, finalize = False)
    while(True):
        event, value = window.read()
        if event in [sg.WIN_CLOSED, "-EXIT-"]:
            window.close()
            break
        if event == "-SERVER-":
            window.close()
            protocol_server.main()
            break
        if event == "-CLIENT-":
            window.close()
            protocol_client.main()
            break
    
def startClientGUI():
    layout = [[sg.Titlebar("Password")],
              [sg.Text("Enter password:")],
              [
                  sg.Input("", (20,.5), key = "-PASS-"),
                  sg.Button("Submit", key = "-SUBMIT-")
               ]
              ]
    window = sg.Window("", layout, finalize= False)
    while(True):
        event, value = window.read()
        if event in [sg.WIN_CLOSED, "-EXIT-"]:
            break
        if event == "-SUBMIT-":
            password = value['-PASS-']
            window.close()
            return password
    window.close()

def wrongPasswordGUI():
    layout = [[sg.Titlebar("WRONG PASSWORD")],
            [sg.Text("WRONG PASSWORD TRY AGAIN:")],
            [
                sg.Input("", (20,.5), key = "-PASS-"),
                sg.Button("Submit", key = "-SUBMIT-")
            ]
            ]
    window = sg.Window("", layout, finalize= False)
    while(True):
        event, value = window.read()
        if event in [sg.WIN_CLOSED, "-EXIT-"]:
            break
        if event == "-SUBMIT-":
            password = value['-PASS-']
            window.close()
            return password
    window.close()
    
def startServerGUI():
    layout = [[sg.Titlebar("Password")],
              [sg.Text("Create Server password:")],
              [sg.Input("", (20,.5), key = "-PASS-")],
              [sg.Text("Enter your name:")],
              [sg.Input("",(20,.5), key = "-NAME-")],
              [sg.Button("Submit", key = "-SUBMIT-")],
              ]
    window = sg.Window("", layout, finalize= True)
    while(True):
        event, value = window.read()
        if event in [sg.WIN_CLOSED, "-EXIT-"]:
            window.close()
            break
        if event == "-SUBMIT-":
            password, name = value['-PASS-'], value['-NAME-']
            window.close()
            return password, name

def clientNameGUI():
    layout = [[sg.Titlebar("Password")],
              [sg.Text("Correct Password. Please Enter Your Name:")],
              [sg.Input("",(20,.5), key = "-NAME-")],
              [sg.Button("Submit", key = "-SUBMIT-")],
              ]
    window = sg.Window("", layout, finalize= True)
    while(True):
        event, value = window.read()
        if event in [sg.WIN_CLOSED, "-EXIT-"]:
            window.close()
            break
        if event == "-SUBMIT-":
            name = value['-NAME-']
            window.close()
            return name
    
    
    
            
