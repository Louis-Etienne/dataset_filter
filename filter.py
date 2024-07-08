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
    subprocess.run(["tev", ":composite", list_path[index]])

def open_file(list_path, list_files):
    print("start thread")
    thread = threading.Thread(target=open_image, args=(list_path, list_files))
    thread.start()

def jump(entry, list_path, list_files, notes, label_index, label_name, text, reasons_var, reasons):
    val = entry.get()
    entry.delete(0, tk.END)
    if val.isdigit():
        num = int(val)
        if num >= 0 and num < len(list_files):
            global index
            index = num -1
            next(list_path, list_files, notes, label_index, label_name, text, reasons_var, reasons)

def next(list_path, list_files, notes, label_index, label_name, text, reasons_var, reasons):
    global index
    if index < len(list_files) -1:
        index = index + 1
        label_index.config(text=f"Index : {index}/{len(list_files)}")
        label_name.config(text=f"name : {list_files[index]}")
        text.delete("1.0", tk.END)
        text.insert(tk.END, notes[list_files[index]]["note"])
        for i,reason in enumerate(reasons):
            reasons_var[i].set(notes[list_files[index]][reason])
        open_file(list_path, list_files)

def back(list_path, list_files, notes, label_index, label_name, text, reasons_var, reasons):
    global index
    if index > 0:
        index = index - 1
        label_index.config(text=f"Index : {index}/{len(list_files)}")
        label_name.config(text=f"name : {list_files[index]}")
        text.delete("1.0", tk.END)
        text.insert(tk.END, notes[list_files[index]]["note"])
        for i,reason in enumerate(reasons):
            reasons_var[i].set(notes[list_files[index]][reason])
        open_file(list_path, list_files)

# Environement setup
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
entry_frame = tk.Frame(root)
entry = tk.Entry(entry_frame, width=10)
entry_label = tk.Label(entry_frame, text="Enter number to jump to index : ")
entry_jump = tk.Button(entry_frame, text="Jump", command=lambda:jump(entry, list_path, list_files, notes, label_index, label_name, text, reasons_var, reasons))
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

back_button = tk.Button(button_frame, text="Back", command=lambda: back(list_path, list_files, notes, label_index, label_name, text, reasons_var, reasons))
next_button = tk.Button(button_frame, text="Next", command=lambda: next(list_path, list_files, notes, label_index, label_name, text, reasons_var, reasons))

def on_text_change(event):
    notes[list_files[index]]["note"] = text.get("1.0", tk.END).strip()
    save_notes(notes)
    text.edit_modified(False)
text.bind('<<Modified>>', on_text_change)

label_index.pack()
entry_frame.pack()
entry_jump.pack(side=tk.RIGHT)
entry.pack(side=tk.RIGHT)
entry_label.pack(side=tk.LEFT)

label_name.pack()
text.pack()
reason_frame.pack()
button_frame.pack(side=tk.BOTTOM)
back_button.pack(side=tk.LEFT)
next_button.pack(side=tk.RIGHT)

# load the first image
index=-1
next(list_path, list_files, notes, label_index, label_name, text, reasons_var, reasons)

# starts the window loop
root.mainloop()





