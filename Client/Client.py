import tkinter as tk
from tkinter import filedialog
import socket
import threading
import os
import subprocess

def receive_messages():
    while True:
        # Determine if the incoming message is text or file
        msg_type = client.recv(5).decode('utf-8')  # e.g., "TEXT_" or "FILE_"

        msg_length = int(client.recv(10).decode('utf-8'))
        
        if msg_type == "TEXT_":
            msg = client.recv(msg_length).decode('utf-8')
            chat_log_text.insert(tk.END, msg + "\n")
        elif msg_type == "FILE_":
            file_data = client.recv(msg_length)
            # Save received files in the current directory
            with open("received_file", "wb") as f:
                f.write(file_data)
            chat_log_text.insert(tk.END, "Received a file: 'received_file'\n")

def send_text():
    message = message_entry.get()
    name = user_name.get()
    chat_log_text.insert(tk.END, "You: " + message + "\n")
    message = name + ": " + message
    client.sendall("TEXT_".encode('utf-8'))
    client.sendall(str(len(message)).zfill(10).encode('utf-8'))
    client.sendall(message.encode('utf-8'))
    message_entry.delete(0, tk.END)

def send_file(file_path):
    with open(file_path, 'rb') as file:
        file_data = file.read()
        client.sendall("FILE_".encode('utf-8'))
        client.sendall(str(len(file_data)).zfill(10).encode('utf-8'))
        client.sendall(file_data)

def send_message():
    if message_entry.get():
        send_text()
    elif file_path.get():
        send_file(file_path.get())
        file_path.set("")

def open_file():
    file_path.set(filedialog.askopenfilename())

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    
    name_label = tk.Label(settings_window, text="Enter your name:")
    name_label.pack(pady=10, padx=10)
    
    name_entry = tk.Entry(settings_window, textvariable=user_name)
    name_entry.pack(pady=10, padx=10)
    
    def open_directory():
        if os.name == 'nt':  # For Windows
            subprocess.Popen(['explorer', os.getcwd()])
        elif os.name == 'posix':  # For Linux/Mac
            subprocess.Popen(['xdg-open', os.getcwd()])
    
    open_dir_button = tk.Button(settings_window, text="Open Working Directory", command=open_directory)
    open_dir_button.pack(pady=10, padx=10)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(('127.0.0.1', 12345))
    threading.Thread(target=receive_messages, daemon=True).start()  # Start the receive_messages thread
except socket.error as e:
    print(str(e))


root = tk.Tk()
root.title("Client Messenger")
root.geometry("600x400")

# The user's name
user_name = tk.StringVar(value="Anonymous")

# Top Panel
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X)

title_label = tk.Label(top_frame, text="Client Messenger", font=("Arial", 16))
title_label.pack(side=tk.LEFT, padx=10)

settings_button = tk.Button(top_frame, text="Settings", command=open_settings)
settings_button.pack(side=tk.RIGHT, padx=10)

# Chat Log
chat_log_text = tk.Text(root, wrap=tk.WORD, height=15)
chat_log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# Bottom Panel
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

message_entry = tk.Entry(bottom_frame, width=40)
message_entry.pack(side=tk.LEFT, padx=5)

send_button = tk.Button(bottom_frame, text="SEND", command=send_message)
send_button.pack(side=tk.LEFT, padx=5)

file_path = tk.StringVar()
file_display = tk.Entry(bottom_frame, textvariable=file_path, state="readonly", width=20)
file_display.pack(side=tk.LEFT, padx=5)

upload_button = tk.Button(bottom_frame, text="Upload a File", command=open_file)
upload_button.pack(side=tk.LEFT, padx=5)

root.mainloop()