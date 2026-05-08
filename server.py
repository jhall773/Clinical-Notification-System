#!/usr/bin/env python3

# Simple network socket demo - SERVER
#
# Set script as executable via: chmod +x server.py
# Run via: ./server.py <PORT>

#Port Number (use same one that client uses!)
#I used serverPort =  55000 

import socket
import sys
import threading
import tkinter
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import time # Needed for synchonyzing threads

port = 55000 

shutdown = threading.Event() # Shuts down the server application if all the clients are gone.

def Notification_Protocol(length, text):
    str = f"CHAT/1.0 TEXT\r\nMsg-len: {length}\r\n{text}\r\n\r\n" #message is in location [4]
    return str

# List of all the Clients in the Chatroom
clients = []
global client_added # Returns if a client has been recently added (used for a message pop-up to inform the front desk someone entered the system)
client_added = True

def add_client(client_socket):
    global client_added
    client_added = True

    clients.append(client_socket)

def delete_client(client_socket):
    # Close client socket
    try:      
        index = clients.index(client_socket) # Take client out of server's list
        clients.pop(index)
        client_socket.close()  # Close that client's connection to the server

    except socket.error as msg:
        print("Error: unable to close() socket")
        print("Description: " + str(msg))

# functions used to define and send different notification messages
def Broadcast(message):
    encoded_message = bytes(message, 'ascii')

    if(len(clients) == 0):
        # Add this "clients left" warning to the message window, so that the Front Desk knows to close the app.
        msg = "All clients left the notification system already. Please restart the application and wait for new clients to enter the system..."
        messagebox.showwarning(message=msg, parent=ui_message)
        eventDeleteDisplay()
    else:
        for client in clients:
            try:
                client.sendall(encoded_message)
                print("Sending Notification to Client")

            except:
                print("Issue with sending!!!")
                delete_client(client) # Happens when the client's 'handle_server_sends' function closes a socket when naturally (not unexpectedly) leaving

                if(len(clients) == 0):
                    # Add this "clients left" warning to the message window, so that the Front Desk knows to close the app.
                    msg = "All clients left the notification system already. Please restart the application and then wait for new clients to enter the system..."
                    messagebox.showerror(message=msg, parent=ui_message)
                    eventDeleteDisplay()

def sendA1CMessage():
    global main_UI, ui_message

    # Play Notification Sound
    main_UI.bell()

    # Get the current timestamp for the message
    from datetime import datetime
    current_time = datetime.now().strftime('%I:%M %p')

    msg = f"Patient has finished A1C test. {current_time}"

    # Add this data to the Front Desk's 'Notification History' window
    display_msg = f"You sent a 'Patient finished A1C test' Notification at: {current_time}"

    ui_message.insert(tkinter.INSERT, '%s\n' % (display_msg)) # Allow the Front Desk to see their past sent notifications.
    ui_message.yview(tkinter.END)  # Auto-scrolling

    length = len(msg)
    send_msg = Notification_Protocol(length=length, text=msg)

    Broadcast(send_msg)


def sendArrivalMessage():
    global main_UI, ui_message

    # Play Notification Sound
    main_UI.bell()

    #Get the current timestamp for the message
    from datetime import datetime
    current_time = datetime.now().strftime('%I:%M %p')

    msg = f"New patient has arrived for their appointment. {current_time}"

    # Add this data to the Front Desk's 'Notification History' window
    display_msg = f"You sent a 'New Patient Arrival' Notification at: {current_time}"
    
    ui_message.insert(tkinter.INSERT, '%s\n' % (display_msg)) # Allow the Front Desk to see their past sent notifications.
    ui_message.yview(tkinter.END)  # Auto-scrolling

    length = len(msg)
    send_msg = Notification_Protocol(length=length, text=msg)

    Broadcast(send_msg)
# Ending of functions used to define and send different notification messages
    

def handle_client_comms():
    global main_UI
    global client_added
    global shutdown

    show_buttons = False # Determines if anyone has joined, so that the buttons for sending to clients.
    button_frame = tkinter.Frame(main_UI) # Creates a frame for the buttons to display in outside of the 'ui_message' window
    button_frame.pack(side="top", padx=10, pady=10)

    # Create the buttons used to send notifications
    A1C_button = tkinter.Button(master=button_frame, command=sendA1CMessage, text="Patient Finished A1C", width = 25, height = 5)
    New_Patient_button = tkinter.Button(master=button_frame, command=sendArrivalMessage, text="New Patient Arrival", width = 25, height = 5)

    # Clear the initial startup message "Waiting for other computers to join the system" in the 'ui_message' window
    #ui_message.delete(index1='1.0', index2='2.0')

    while (not shutdown.is_set()):  
        # Send Notification Data

        if len(clients) > 0:
            show_buttons = True # If there is a client, display the buttons to send notifications to that client (or clients)

            if client_added == True:
                # Add this data to the message window
                display_message = "A new client has entered the notification system."
                messagebox.showinfo(message=display_message, parent=ui_message)
                ui_message.yview(tkinter.END)  # Auto-scrolling
                client_added = False

            if show_buttons:
                A1C_button.grid(column=0, row=0, padx=10)
                New_Patient_button.grid(column=1, row=0, padx=10)
#End of handle_client_comms()

def start_UI():
    global main_UI
    main_UI = tkinter.Tk()

    # main_UI's Initial Display()
    main_UI.wm_title("Front Desk Notification System")
    main_UI.resizable('1','1')
    main_UI.protocol("WM_DELETE_WINDOW", eventDeleteDisplay)

    # These are the 4 app messages that will be displayed over the lifetime of the UI Window using "ui_message",
    # After destroying the previous message object (with ui_message.destroy())
    global ui_message, startup_msg
    ui_message = ScrolledText(
                master=main_UI,
                wrap=tkinter.WORD,
                width=50,  # In chars
                height=20) # In chars     

    # Compute display position for all objects
    ui_message.pack(side=tkinter.TOP, fill=tkinter.BOTH)

    # Tkinter: When you start the program, put this print message in the root "main" Tkinter Window, informing the user:
    startup_msg = f"Waiting for other computers to join the system..."
    ui_message.insert(tkinter.INSERT, '%s\n' % (startup_msg))
    # Starts the UI
    main_UI.mainloop()

    print("stopping UI...")
    shutdown.set()          # Shutdown the application
# End of start_UI()

def listener():
    # Create TCP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Error: could not create socket")
        print("Description: " + str(msg))
        sys.exit()

    # Bind to listening port
    try:
        host=''  # Bind to all interfaces
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address for clients
        s.bind((host,port))
    except socket.error as msg:
        print("Error: unable to bind on port %d" % port)
        print("Description: " + str(msg))
        sys.exit()
    
    while(not shutdown.is_set()):
        # Listen
        try:
            backlog=5  # Number of incoming connections that can wait
                        # to be accept()'ed before being turned away
            s.listen(backlog)
        except socket.error as msg:
            print("Error: unable to listen()")
            print("Description: " + str(msg))
            sys.exit()    

        print("Listening socket bound to port %d" % port)

        # Accept an incoming request
        try:
            (client_s, client_addr) = s.accept()
            # If successful, we now have TWO sockets
            #  (1) The original listening socket s, still active
            #  (2) The new socket client_s connected to the client
        except socket.error as msg:
            print("Error: unable to accept()")
            print("Description: " + str(msg))
            sys.exit()

            print("Accepted incoming connection from client")
            print("Client IP, Port = %s" % str(client_addr))
        
        if client_s not in clients:
            add_client(client_s)

            display_message = "A new client has entered the notification system."
            print("msg sent to clients: ", display_message)
            
            print("Here! Clients list has this many: ", len(clients))
    print("Listener loop Break!") 
# End of listener()

# Event handler - User closed program via window manager or CTRL-C
def eventDeleteDisplay():
    print("UI: Closing")

    # Continuing closing window now
    global main_UI
    main_UI.destroy()
#End of eventDeleteDisplay()
            

def main():
    # Function to show the server application's UI
    threadUI = threading.Thread(target=start_UI)

    threadUI.start()
    time.sleep(.05)

    threadListener = threading.Thread(target=listener)
    threadListener.daemon = True
    threadListener.start()
    time.sleep(.05)

    # Function to recieve the messages from the client socket.
    threadBrodcast = threading.Thread(target=handle_client_comms)
    threadBrodcast.daemon = True
    threadBrodcast.start()
        
if __name__ == "__main__":
    sys.exit(main())
