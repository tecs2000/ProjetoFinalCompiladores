# EQUIPE TOP

# Lucas Leonardo Barros Silva
# Weybson Alves da Silva
# Wesley Alves da Silva
# Mihael Éder Guedes Barreiros 
# Tomás Nascimento Pimentel Barros
# João Victor Soares Ferreira
# Gabriel Felipo Raeli de Melo
# Natan Frederico da Silva Lima

import multiprocessing
import os
import socket
import threading as thread
import time
import tkinter.font as tkFont
from datetime import datetime as dtTime
from tkinter import *
from tkinter import filedialog as fileDlg

from PIL import Image as Img
from PIL import ImageTk as ImgTk
from pygame import mixer as mxer

import Player as Player


class GUI:
    def __init__(self, width, height, user, _target):
        self.sep = "$#"
        self.user = user

        self.min_pics = []
        self.pics = []

        self.send_lock = thread.Lock()
        self.recv_lock = thread.Lock()

        self.window = Tk()
        self.window.title("Waiting...")

        self.canva = Canvas(self.window, width=width, height=height)
        self.canva.grid(columnspan=5)
        self.target_ip = _target

        self.make_widgets()
        t = thread.Thread(target=self.wait_updates, daemon=True)
        t.start()

        mxer.init()
        self.audio_channel = mxer.Channel(0)
        self.playing_audio = False

        self.media_path_dict = dict()
        self.media = dict()

        self.status = ""
        self.conn = None
        self.addr = None
        self.connector = None
        self.connect()

    def make_widgets(self):
        _file = PhotoImage(file=r"file2.png")
        fonte = tkFont.Font(family="Arial", size=10, weight="bold")
        self.text_area = Text(self.canva, border=2, width=110, height=40)
       
        miniatura_anexo = _file.subsample(60)
        self.txt_field = Entry(self.canva, width=50, border=1, bg="#DECDF5")
        self.send_button = Button(
            self.canva,
            text="Send",
            padx=30,
            command=self.send,
            bg="#A8329E",
            fg="white",
            font=fonte,
        )
        self.upload_button = Button(
            self.canva,
            text="Upload",
            padx=20,
            image=miniatura_anexo,
            compound=RIGHT,
            command=self.get_file,
            bg="#A8329E",
            fg="white",
            font=fonte,
        )
        self.clear_button = Button(
            self.canva,
            text="Clear",
            padx=30,
            command=self.erase_chat,
            bg="#A8329E",
            fg="white",
            font=fonte,
        )

        self.upload_button.miniatura_anexo = miniatura_anexo

        self.window.bind("<Return>", self.send)

        self.text_area.bind("<Configure>", self.reset_tab_limits)

        self.window.bind("<F1>", self.pause_audio)
        self.window.bind("<F2>", self.stop_audio)
        self.text_area.config(background="#f598ed")

        self.text_area.grid(column=0, row=0, columnspan=5)
        self.txt_field.grid(column=0, row=1, columnspan=2)
        self.send_button.grid(column=2, row=1)
        self.clear_button.grid(column=4, row=1)
        self.upload_button.grid(column=3, row=1)

    def connect(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.target_ip, 30000))

            self.s_f = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s_f.connect((self.target_ip, 65534))
            self.status = f"Chat do Anel - {self.user}"
            self.connector = self.s

            self.connector_f = self.s_f
        except ConnectionRefusedError:
            self.status = f"Chat do Anel - {self.user}"

            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind(("localhost", 30000))
            self.s.listen(1)
            self.s_f = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s_f.bind(("localhost", 65534))
            self.s_f.listen(1)
            self.conn, self.addr = self.s.accept()
            self.conn_f, self.addr_f = self.s_f.accept()
            
            self.connector = self.conn
            self.connector_f = self.conn_f
        finally:
            self.window.title(self.status)

    def send(self, event=None):
        msg = self.txt_field.get()
        if msg.replace(" ", "") == "":
            return

        if msg[:5] == "!play":
            try:
                type_index = msg[6:].rindex(".")
            except ValueError:
 
                self.txt_field.delete(0, END)
                return

            file_format = msg[6:][type_index + 1 :]
            if file_format in ["wav", "mp3", "ogg"] and msg[6:] in self.media:


                file = self.media[msg[6:]]
                self.reproduce_audio(file)
            else:
                try:

  

                    if file_format in ["mp4"]:
                        p = multiprocessing.Process(
                            target=Player.play_video, args=(msg[6:],)
                        )
                        p.start()
                    elif msg[6:] in self.media_path_dict:
                        os.startfile(msg[6:])
                    else:
                        os.startfile(os.getcwd() + "\\" + msg[6:])
                except:

                    pass
            self.txt_field.delete(0, END)
            return

        msg_max = 40
        if len(msg) > msg_max:
            j = 1
            last_pos = 0
            while j * msg_max < len(msg):
                f = (msg[last_pos : min(last_pos + msg_max, len(msg))])[::-1].find(" ")
                f = last_pos + msg_max - f
                if f != -1:
                    msg = msg[: f - 1] + "\n" + msg[f:]
                    last_pos = f
                j += 1

        msg = msg.replace("\\n", "\n").replace(self.sep, "")
        msg = f"{self.sep}\n{self.user}: {msg}\n{dtTime.now()}\n"
        self.connector.sendall(bytes(msg, "utf-8"))
        msg = msg.replace("\n", "\n\t")
        self.text_area.insert(END, msg[len(self.sep) :])
        self.txt_field.delete(0, END)


    def wait_updates(self):
        while True:
            time.sleep(0.5)
            self.update()

    def reset_tab_limits(self, event):
        event.widget.configure(tabs=(event.width - 8, "right"))

    def update(self):
        aux = []
        try:
            while True:
                self.connector.settimeout(0.001)
                msg = self.connector.recv(1024)
                if not msg:
                    return
                msg = msg.decode("utf-8")
                aux.append(msg)
        except:
            mensagens = "".join(aux).split(self.sep)[1:]
            for msg in mensagens:
                if msg[0] == "!":
                    self.recv_file(msg)
                else:
                    msg = msg.replace("\\n", "\n")
                    self.text_area.insert(END, msg)

    def erase_chat(self, event=None):
        self.text_area.delete(1.0, END)

    def reproduce_audio(self, audio):

        try:
            self.audio_channel.stop()

            self.audio_channel.play(audio)
            self.playing_audio = True
        except KeyError:
            pass

    def pause_audio(self, event=None):

        if not self.audio_channel.get_busy():
            return

        if self.playing_audio:
            self.audio_channel.pause()
        else:
            self.audio_channel.unpause()

        self.playing_audio = not self.playing_audio

    def stop_audio(self, event=None):

        if not self.audio_channel.get_busy():
            return

        self.audio_channel.stop()

    def get_file(self, event=None):
        file_path = fileDlg.askopenfilename()

        if file_path == "":
            return
        type_index = file_path.rindex(".")
        file_format = file_path[type_index + 1 :]
        self.text_area.insert(END, f"\n\t{self.user}:\n\t")
        if file_format in ["wav", "mp3", "ogg"]:
            audio = mxer.Sound(file_path)
            self.media[file_path] = audio

            self.text_area.insert(END, f"#Audio: {file_path.split('/')[-1]}")
        elif file_format in ["mp4"]:
            self.text_area.insert(END, f"#Video: {file_path.split('/')[-1]}")
        else:
            try:
                pic = Img.open(file_path)
                miniature_pic = pic.resize(
                    (325, (325 * pic.height) // pic.width), Img.ANTIALIAS
                )
                my_img = ImgTk.PhotoImage(miniature_pic)
                self.min_pics.append(my_img)

                self.text_area.image_create(END, image=self.min_pics[-1])

            except:
                self.text_area.insert(END, f"#File: {file_path.split('/')[-1]}")

        self.text_area.insert(
            END, f"\n\t{dtTime.now().strftime('%d/%m/%Y, %H:%M:%S')}\n"
        )
        t = thread.Thread(target=lambda: self.send_file(file_path))
        t.start()

    def send_file(self, file_path):
        self.send_lock.acquire()

        size_bytes = os.path.getsize(file_path)
        user = file_path.split("/")[-1].replace(";", "")
        header = (
            self.sep
            + "!"
            + user
            + ";"
            + str(size_bytes)
            + ";"
            + self.user
            + ";"
            + dtTime.now().strftime("%d/%m/%Y, %H:%M:%S")
        )
        self.connector.sendall(bytes(header, "utf-8"))

        file = open(file_path, "rb")
        l = file.read(1024)
        while l:
            self.connector_f.sendall(l)
            l = file.read(1024)
        file.close()

        type_index = file_path.rindex(".")
        file_format = file_path[type_index + 1 :]

        if file_format in ["wav", "mp3", "ogg"]:
            audio = mxer.Sound(file_path)
            self.media[user] = audio
        else:
            self.media_path_dict[user] = file_path


        self.send_lock.release()

    def recv_file(self, header):
        user, size_bytes, sender, time = header[1:].split(";")
        size_bytes = int(size_bytes)
        file = open(user, "wb")
        l = self.connector_f.recv(1024)
        size_bytes -= 1024
        while size_bytes > 0:
            file.write(l)
            l = self.connector_f.recv(min(1024, size_bytes))
            size_bytes -= 1024
        file.write(l)

        file_path = file.user

        file.close()

        type_index = file_path.rindex(".")
        file_format = file_path[type_index + 1 :]
        self.text_area.insert(END, f"\n{sender}:\n")
        if file_format in ["wav", "mp3", "ogg"]:
            audio = mxer.Sound(file_path)
            self.media[file_path] = audio

            self.text_area.insert(END, f"#Audio: {user}")

        elif file_format in ["mp4"]:
            self.text_area.insert(END, f"#Video: {user}")
        else:
            try:
                pic = Img.open(file_path)
                miniature_pic = pic.resize(
                    (325, (325 * pic.height) // pic.width), Img.ANTIALIAS
                )
                my_img = ImgTk.PhotoImage(miniature_pic)
                self.min_pics.append(my_img)

                self.text_area.image_create(END, image=self.min_pics[-1])

            except:
                self.text_area.insert(END, f"#File: {user}")

        self.text_area.insert(END, f"\n{time}\n")

    def start(self):
        self.window.mainloop()


if __name__ == "__main__":
    nome = input("Qual o seu usuário? ")
    interface = GUI(600, 800, nome, "localhost").start()
    print("Katchau ;)")
