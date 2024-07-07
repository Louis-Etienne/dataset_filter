import glob
import pyperclip as pc
import subprocess
import re
import PySimpleGUI as sg
import threading
import tkinter as tk
import json
import os

def isolate_exr(path):
    last_index = path.rfind("\\")
    return path[last_index+1:]

def read_notes(list_files, reasons):
    if not os.path.isfile('notes.json'):
        
        dict_notes = {}
        for file in list_files:
            dict_notes[file] = {"note":""}
            for reason in reasons:
                dict_notes[file][reason] = 0
        save_notes(dict_notes)
        return dict_notes
    else:
        with open('notes.json') as f:
            return json.load(f)

def save_notes(notes):
    with open('notes.json', 'w') as f:
            json.dump(notes, f, indent=4)

def open_image(list_path, list_files):
    pc.copy(list_files[index])
    subprocess.run(["tev", ":composite", list_path[index]])

def open_file(list_path, list_files):
    print("start thread")
    thread = threading.Thread(target=open_image, args=(list_path, list_files))
    thread.start()

# Set up environement values
reasons = ['Misplaced', 'Too big', 'Too small', 'Weird shadow', 'Too bright', 'Noisy envamp', 'Looks off', 'Other']
list_path = glob.glob("D:/@Université/STAGES/STAGE1/globus_sharing/GT_emission_envmap/*/*.exr")
list_files = [isolate_exr(f) for f in list_path]
notes = read_notes(list_files, reasons)
index = 0

# UI shenanigans
root = tk.Tk()
root.geometry("500x400")
root.title('Filtering app')

button_frame = tk.Frame(root)
label_index = tk.Label(root, text= f"Index : {index}/{len(list_files)}")
label_name = tk.Label(root, text=f"name : {list_files[index]}")
text = tk.Text(root, height=5, width=50)

def on_reason_change():
    for i, reason in enumerate(reasons):
        notes[list_files[index]][reason] = reasons_var[i].get()
    save_notes(notes)

reason_frame = tk.Frame(root)
reasons_var = [tk.IntVar() for i in range(len(reasons))]
reasons_buttons = [tk.Checkbutton(reason_frame, text=reasons[i], variable=reasons_var[i], onvalue=1, offvalue=0, command=on_reason_change) for i in range(len(reasons)) ]
for button in reasons_buttons:
    button.pack()







back_button = tk.Button(button_frame, text="Back", command=lambda: back(list_path, list_files, notes, label_index, label_name, text, reasons_var))
next_button = tk.Button(button_frame, text="Next", command=lambda: next(list_path, list_files, notes, label_index, label_name, text, reasons_var))

def on_text_change(event):
    notes[list_files[index]]["note"] = text.get("1.0", tk.END).strip()
    save_notes(notes)
    text.edit_modified(False)
text.bind('<<Modified>>', on_text_change)

label_index.pack()
label_name.pack()
text.pack()
reason_frame.pack()
button_frame.pack(side=tk.BOTTOM)
back_button.pack(side=tk.LEFT)
next_button.pack(side=tk.RIGHT)

# load the first image
index=-1
next(list_path, list_files, notes, label_index, label_name, text, reasons_var)

# starts the window loop
root.mainloop()





