#!/usr/bin/env python3

# Simple network socket demo - CLIENT
#
# Set script as executable via: chmod +x client.py
# Run via:  ./client.py <IP> <PORT>
#
# To connect to a server on the same computer, <IP> could
# either be 127.0.0.1 or localhost (they have the same meaning)

#Port Number (use same one that client uses!)
#I used serverPort =  55000

import socket
#import socket module 

import sys
import winsound
import threading
import tkinter
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

# Basic global variables:
leaving = False # Variable that determines if the client is leaving or not. This helps it close its socket and alert the server.

foreign_msg = "" # Message recieved when being sent by someone else

my_socket = socket.socket() # This client's socket used for all of its connections

# Note: The front desk's server message protocol below (in server.py lines 23-25):
"""
def TXT_Protocol(len, text):
    str = f"CHAT/1.0 TEXT\r\nMsg-len: {length}\r\n{text}\r\n\r\n" #message is in location [4]
    return str
"""

def handle_server_recieves(my_socket):
    global ui
    while True:
        # Receive data
        try:
            buffer_size=2048
            raw_bytes = my_socket.recv(buffer_size)
        except socket.error as msg:
            print("Error: unable to recv()")
            print("Description: " + str(msg))
            sys.exit()

        print("Client is recieving data!\n")
        string_unsplit = raw_bytes.decode('ascii')
        print("Received %d bytes from server" % len(raw_bytes))
        print("Message contents:\n" + string_unsplit)

        string_unicode = raw_bytes.decode('ascii').split()

        if(len(raw_bytes) > 0): # If this condition is not met, the client didn't actually recieve anything

            if ( (string_unicode[1]) == "TEXT"):
                recieved_msg_place = 4 # 4 is the index for the start of the text being sent. The first 4 indicies are related to the message type and the 'Msg-len' header.
                recieved_msg = ""
                while recieved_msg_place < len(string_unicode):
                    recieved_msg = recieved_msg + " " + string_unicode[recieved_msg_place]
                    recieved_msg_place += 1

                message = f"{recieved_msg}"
                print("Adding you to my chat room message window!")
                print("foreign msg: ", message)

                # Play Notification Sound
                winsound.Beep(frequency=2000, duration=1000)

                # Could also use Tkinter's buit in 'bell()' function.
                # However, there is no sound control with the 'bell()' function and the sound is a bit weak and can easily go unnoticed. 
                # This is why the Windows specific sound function above is used.

                # Add this data to the message window
                ui.ui_messages.insert(tkinter.INSERT, "%s\n" % (message)) # Print the message from the Front Desk server.
                ui.ui_messages.yview(tkinter.END)  # Auto-scrolling
# End handle_server_recieves()


# Function to run the UI
def UI():
    print("Running GUI Demo")

    # Instantiate class for UI
    global ui
    ui = clientUI()

    # Run the UI, and capture CTRL-C to terminate
    try:
        ui.start()
        return ui
    except KeyboardInterrupt:
        print("Caught CTRL-C, shutting down client")
        ui.eventDeleteDisplay()
    
    print("GUI Demo exiting")
# End of UI() function

# Start of clientUI Class
class clientUI():
    def __init__(self):
        self.first_click = True

    def start(self):
        print("Starting clientUI...")
        self.initDisplay()

        self.ui_messages.insert(tkinter.END, "Waiting to add notification messages from the server...\n")

        # This call to mainloop() is blocking and will last for the lifetime
        # of the GUI.
        self.ui_top.mainloop()

        # Should only get here after destroy() is called on ui_top
        print("Stopping clientUI...")

        global leaving
        leaving = True

    def initDisplay(self):
        self.ui_top = tkinter.Tk()
        self.ui_top.wm_title("GUI Demo")
        self.ui_top.resizable('1','1')
        self.ui_top.protocol("WM_DELETE_WINDOW", self.eventDeleteDisplay)
        
        self.ui_messages = ScrolledText(
            master=self.ui_top,
            wrap=tkinter.WORD,
            width=50,  # In chars
            height=25)  # In chars

        # Compute display position for all objects
        self.ui_messages.pack(side=tkinter.TOP, fill=tkinter.BOTH)


    # Event handler - User closed program via window manager or CTRL-C
    def eventDeleteDisplay(self):
        print("UI: Closing")

        # Continuing closing window now
        self.ui_top.destroy()

    # Event handler - User clicked inside the "ui_input" field
    def eventInputClick(self, event):
        if(self.first_click):
            # If this is the first time the user clicked,
            # clear out the tutorial message currently in the box.
            # Otherwise, ignore it.
            self.ui_input.delete("0.0", tkinter.END)
            self.first_click = False
# End of clientUI Class


def startUP():
    
    from tkinter import simpledialog

    server_ip = simpledialog.askstring(title="Getting Server Address", prompt="Please enter the server's IP address: ")
    print("Server IP Address entered: ", server_ip)

    if(server_ip == None):
        print("Error: Cannot Use Application Without the Server's IP Address")
        messagebox.showerror(message="Error: Sorry, you cannot use this application without the Server's IP Address.")
        sys.exit()

    port = 55000

    # Create my Client Socket and send data
    try:
        my_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Error: could not create socket")
        print("Description: " + str(msg))
        messagebox.showerror(message="Error: Sorry, this Server appears to be unavailable. Please restart the application after making sure that the target Server is up and running.")
        sys.exit()

    print("Connecting to server at " + server_ip + " on port ", str(port))
     
    # Connect to server
    try:
        my_Socket.connect((server_ip , port))
        return my_Socket
    except socket.error as msg:
        print("Error: Could not open connection")
        messagebox.showerror(message="Error: Sorry, could not make a connection to this address. Please reopen the application and try again.")
        print("Description: " + str(msg))
        sys.exit()
    
    print("Connection established")
#End of StartUP()


def main():
    print("Running in main()...")
    global my_socket
    my_socket = startUP()
    threadUI = threading.Thread(target=UI)
    threadUI.start()
    thread_Recv = threading.Thread(target=handle_server_recieves, args=(my_socket,))
    thread_Recv.daemon = True # This means, the client application will terminate when the UI closes.
    thread_Recv.start()
    print("Exiting main()...")

if __name__ == "__main__":
    sys.exit(main())