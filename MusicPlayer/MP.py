from pygame import *
import os
import threading
import time

from tkinter import *
import tkinter as tk
from tkinter import ttk
from ttkthemes import themed_tk as tk

from tkinter import filedialog
import tkinter.messagebox
from mutagen.mp3 import MP3
from pygame import mixer


root = tk.ThemedTk()
root.get_themes()
root.set_theme("plastik")


global index
index=0


statusbar = ttk.Label(root, text="Groove Music", relief=SUNKEN, anchor=W, font='Times 10 italic')
statusbar.pack(side=BOTTOM, fill=X)


# Create the menubar
menubar = Menu(root)
root.config(menu=menubar)


# Create the submenu
subMenu = Menu(menubar, tearoff=0)


playlist = []
songname = []
selected_song = 0


def browse_file():
    global filename_path
    init_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    filename_path = filedialog.askopenfilename(initialdir =  init_path,title = "Select file",filetypes = (("Audio Files","*.mp3 *.wav *.ogg"),("All files","*.*")))
    add_to_playlist(filename_path)
    mixer.music.queue(filename_path)    


def add_to_playlist(filename):
    filename = os.path.basename(filename)
    index = 0
    playlistbox.insert(index, filename)
    playlist.insert(index, filename_path)
    songname.insert(index,filename)
    playlistbox.select_clear(0,END)
    playlistbox.selection_set(index)
    index += 1


menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browse_file)
subMenu.add_command(label="Exit", command=root.destroy)

subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=subMenu)

mixer.init()  # initializing the mixer

root.title("Groove Music")
root.iconbitmap(r'images/player.ico')


leftframe = Frame(root)
leftframe.pack(side=LEFT,padx=10,pady=10)
rootHeight = root.winfo_height()
rootWidth = root.winfo_width()
playlistbox = Listbox(leftframe,height=15,width=30)
playlistbox.pack()


def update_list(*args):
    search_term = search_var.get()
    lbox_list = songname
    playlistbox.delete(0, END)
    for item in lbox_list:
            if search_term.lower() in item.lower():
                playlistbox.insert(END, item)
    
               

addBtn = ttk.Button(leftframe,text="+ Add",command=browse_file)
addBtn.pack(side=LEFT,padx=10,pady=10)

def del_song():
    selected_song = playlistbox.curselection()
    selected_song = int(selected_song[0])
    playlistbox.delete(selected_song)
    playlist.pop(selected_song)


delBtn = ttk.Button(leftframe, text="- Del",command=del_song)
delBtn.pack(side=LEFT,padx=10,pady=10)

rightframe = Frame(root)
rightframe.pack(pady=30)

topframe = Frame(rightframe)
topframe.pack()

lengthlabel = ttk.Label(topframe, text='Total Length : --:--')
lengthlabel.pack(pady=5)

currenttimelabel = ttk.Label(topframe, text='Current Time : --:--', relief=GROOVE)
currenttimelabel.pack()


def show_details(play_song):
    file_data = os.path.splitext(play_song)

    if file_data[1] == '.mp3':
        audio = MP3(play_song)
        total_length = audio.info.length
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()

    # div - total_length/60, mod - total_length % 60
    mins, secs = divmod(total_length, 60)
    mins = round(mins)
    secs = round(secs)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)
    lengthlabel['text'] = "Total Length" + ' - ' + timeformat

    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()

def start_count(t):
    global paused
    # mixer.music.get_busy(): - Returns FALSE when we press the stop button (music stop playing)
    # Continue - Ignores all of the statements below it. We check if music is paused or not.
    current_time = 0
    while current_time <= t and mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(current_time, 60)
            mins = round(mins)
            secs = round(secs)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            currenttimelabel['text'] = "Current Time" + ' - ' + timeformat
            time.sleep(1)
            current_time += 1
    if current_time >= t: 
        play_next_song()


def play_music():
    global paused
    if paused:
        mixer.music.unpause()
        statusbar['text'] = "Music Resumed"
        paused = FALSE
    else:
        try:
            stop_music()
            time.sleep(1)
            selected_song = playlistbox.curselection()
            selected_song = int(selected_song[0]) 
            play_it = playlist[selected_song]
            mixer.music.load(play_it)
            mixer.music.play()

            statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
            show_details(play_it)
        except:
            tkinter.messagebox.showerror('File not found', 'Groove Music could not find the file. Please check again.')


def stop_music():
    mixer.music.stop()
    statusbar['text'] = "Music Stopped"


paused = FALSE


def pause_music():
    global paused
    paused = TRUE
    mixer.music.pause()
    statusbar['text'] = "Music Paused"


def rewind_music():
    play_music()
    statusbar['text'] = "Music Rewinded"


def set_vol(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)
    # set_volume of mixer takes value only from 0 to 1. Example - 0, 0.1,0.55,0.54.0.99,1


muted = FALSE


def mute_music():
    global muted
    if muted:  # Unmute the music
        mixer.music.set_volume(0.7)
        volumeBtn.configure(image=volumePhoto)
        scale.set(70)
        muted = FALSE
    else:  # mute the music
        mixer.music.set_volume(0)
        volumeBtn.configure(image=mutePhoto)
        scale.set(0)
        muted = TRUE

def play_next_song():
    selected_song = playlistbox.curselection()
    selected_song = int(selected_song[0])
    playlistbox.select_clear(0,END)
    print(len(playlist))
    print(selected_song)
    if len(playlist)-1 > selected_song :
        playlistbox.selection_set(selected_song+1)
        play_music()

    
def play_prev_song():
    selected_song = playlistbox.curselection()
    selected_song = int(selected_song[0])
    playlistbox.select_clear(0,END)
    if selected_song < len(playlist):
        playlistbox.selection_set(selected_song-1)
        play_music()

def get_next_song():
    global index
    if index <= len(playlist):
        return index + 1
    else:
        return 0 

                
def nextsong():
    global index
    get_next_song()
    playit = playlist[index]
    mixer.music.load(playit)
    mixer.music.play()
    statusbar['text'] = "Playing music" + ' - ' + os.path.basename(playit)
    show_details(playit)
    play_next_song()


def get_prev_song():
    global index
    if index >= 0:
        return index - 1
    else:
        return len(playlist) - 1

def prevsong():
    global index
    get_prev_song()
    playit = playlist[index]
    mixer.music.load(playit)
    mixer.music.play()
    statusbar['text'] = "Playing music" + ' - ' + os.path.basename(playit)
    play_prev_song()

    
middleframe = Frame(rightframe)
middleframe.pack(pady=30, padx=30)

playPhoto = PhotoImage(file='images/play.png')
playBtn = Button(middleframe,image=playPhoto, command=play_music,border = 0)
playBtn.grid(row=0, column=2, padx=10)

stopPhoto = PhotoImage(file='images/stop.png')
stopBtn = Button(middleframe, image=stopPhoto, command=stop_music,border = 0)
stopBtn.grid(row=0, column=1, padx=10)

pausePhoto = PhotoImage(file='images/pause.png')
pauseBtn = Button(middleframe, image=pausePhoto, command=pause_music,border = 0)
pauseBtn.grid(row=0, column=3, padx=10)

nextPhoto = PhotoImage(file='images/next.png')
nextBtn = Button(middleframe,image=nextPhoto,command=nextsong,border = 0)
nextBtn.grid(row=0,column=4,padx=10,pady=10)

prevPhoto = PhotoImage(file='images/prev.png')
prevBtn = Button(middleframe,image=prevPhoto,command=prevsong,border = 0)
prevBtn.grid(row=0,column=0,padx=10,pady=10)

# Bottom Frame for volume, rewind, mute etc.

bottomframe = Frame(rightframe)
bottomframe.pack()

rewindPhoto = PhotoImage(file='images/rewind.png')
rewindBtn = ttk.Button(bottomframe, image=rewindPhoto,command=rewind_music)
rewindBtn.grid(row=0, column=0,padx=10)

mutePhoto = PhotoImage(file='images/mute.png')
volumePhoto = PhotoImage(file='images/volume.png')
volumeBtn = ttk.Button(bottomframe, image=volumePhoto,command=mute_music)
volumeBtn.grid(row=0, column=1,padx=10)

scale = ttk.Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)  # implement the default value of scale when music player starts
mixer.music.set_volume(0.7)
scale.grid(row=0, column=2, pady=15, padx=30)


def on_closing():
    stop_music()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

