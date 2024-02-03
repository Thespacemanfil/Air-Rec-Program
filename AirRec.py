from bing_image_downloader import downloader
import random, os, glob
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

def menu():
    with open('paths.txt', 'w'): pass
    print("---Aircraft Recognition Program---")
    match input("Guide or slideshow?\n").lower():
        case "slideshow":
            match input("competition, casual, learn or custom mode?\n").lower():
                case "competition": path = "C:/aircraft_recognition_program/images/"; slideshow_length = 30; slideshow_time = 10; instant_reveal = False; intermission_time = 0; variance = 2; txt_file = "Competition.txt"; text_size = 50; extension = " airplane"; timer = True; slideshow(path,slideshow_length,slideshow_time,instant_reveal,intermission_time,variance,txt_file,text_size,extension,timer)
                case "casual": path = "C:/aircraft_recognition_program/images/"; slideshow_length = 20; slideshow_time = 10; instant_reveal = False; intermission_time = 5; variance = 2; txt_file = "Competition.txt"; text_size = 50; extension = " aircraft"; timer = True; slideshow(path,slideshow_length,slideshow_time,instant_reveal,intermission_time,variance,txt_file,text_size,extension,timer)
                case "learn": path = "C:/aircraft_recognition_program/images/"; slideshow_length = 10; slideshow_time = 999; instant_reveal = True; intermission_time = 0; variance = 2; txt_file = "Competition.txt"; text_size = 50; extension = " aircraft"; timer = False; slideshow(path,slideshow_length,slideshow_time,instant_reveal,intermission_time,variance,txt_file,text_size,extension,timer)
                case _:
                    path = "C:/aircraft_recognition_program/images/";
                    slideshow_length = int(input("Amount of slides? -1 slides will run through all aircraft in the list\n"))
                    slideshow_time = int(input("Seconds per slide?\n"))
                    if input("Reveal answers immediately yes/no\n").lower() == "yes": instant_reveal = True
                    else: instant_reveal = False
                    intermission_time = int(input("Seconds of intermission?\n"))
                    variance = 3
                    text_size = 50
                    txt_file = input("Which list of aircraft do you want to draw from? " + str(glob.glob("*.txt")) + "\n")
                    extension = " " + input("Search modifier? (not necessary) e.g real aircraft, top view\n").rstrip()
                    if input("Visible countdown timer yes/no\n").lower() == "yes": timer = True
                    else: timer = False
                    slideshow(slideshow_length,slideshow_time,instant_reveal,intermission_time,variance,txt_file,text_size,extension,timer)
        case "test": path = "C:/aircraft_recognition_program/images/"; slideshow_length = 3; slideshow_time = 3; instant_reveal = True; intermission_time = 2; variance = 2; txt_file = "basic.txt"; text_size = 50; extension = " aircraft"; timer = True; slideshow(path,slideshow_length,slideshow_time,instant_reveal,intermission_time,variance,txt_file,text_size,extension,timer)
        case "Guide": print("https://aviationgeeks.co.uk/air-rec/air-cadet-list/")
        case _: menu()

def slideshow(path,slideshow_length,slideshow_time,instant_reveal,intermission_time,variance,txt_file,text_size,extension,timer):
    selected_aircraft = aircraft_selector(txt_file,slideshow_length)
    image_downloader(selected_aircraft,extension,path,variance)
    run_slideshow(slideshow_time,path,text_size,timer,instant_reveal,selected_aircraft,intermission_time,extension)
    show_list_of_aircraft(selected_aircraft,text_size)
    menu()

def aircraft_selector(txt_file,slideshow_length):
    with open(txt_file, 'r') as file:
        aircraft_list = file.read().splitlines()

    if slideshow_length <= len(aircraft_list) and slideshow_length > 0:
        selected_aircraft = random.sample(aircraft_list, slideshow_length)
        return selected_aircraft
    elif slideshow_length == -1:
        return aircraft_list
    else: print("INVALID SLIDESHOW LENGTH")

def image_downloader(selected_aircraft,extension,path,variance):
    for aircraft in selected_aircraft:
        query = aircraft + extension
        downloader.download(query, limit=variance, output_dir=path, adult_filter_off=False, force_replace=False, timeout=60, filter="photo", verbose=False)
        
def show_image(remaining_time,timer,instant_reveal,text_size,filename,image_path,slideshow_time,intermission,intermission_time):
    root = tk.Tk()
    root.title("Aircraft Image")
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{w}x{h}")  
    
    if not intermission:
        img = Image.open(image_path)
        resize_image = img.resize((w, h))
        photo = ImageTk.PhotoImage(resize_image)
        label = ttk.Label(root, image=photo)
        label.pack(fill=tk.BOTH, expand=tk.YES)
        
    def place_timer_label():
        root.update()  # Update the window to get the correct dimensions
        if timer:
            timer_label.place(x=root.winfo_width()-100, y=20)
        elif hasattr(timer_label, 'place'):
            timer_label.place_forget()
    
    def place_aircraft_name():
        if instant_reveal:
            if intermission and intermission_time > 0:
                aircraft_label.place(x=w/2, y=h/2, anchor="center")
            elif not intermission and intermission_time == 0:
                aircraft_label.place(x=w/2, y=35, anchor="center")
        elif hasattr(aircraft_label, 'place'):
            aircraft_label.place_forget()
    
    timer_label = ttk.Label(root, text=str(remaining_time), font=('Arial', text_size), foreground='orange')
    place_timer_label()
    
    aircraft_label = ttk.Label(root, text=filename, font=('Arial', text_size), foreground='white', background='black')
    place_aircraft_name()
    
    def update_timer():
        nonlocal remaining_time  # Use nonlocal to modify the outer variable
        remaining_time -= 1
        timer_label.config(text=str(remaining_time))
        if remaining_time > 0:
            root.after(1000, update_timer)

    update_timer()
    
    def close_window():
        root.destroy()
    
    if intermission:
        root.configure(bg='black')
        root.after(remaining_time*1000, close_window)
    else:
        root.after(slideshow_time*1000, close_window)

    root.mainloop()

def run_slideshow(slideshow_time, path, text_size, timer, instant_reveal, selected_aircraft, intermission_time, extension):
    for aircraft in selected_aircraft:
        remaining_time = slideshow_time
        folder_path = os.path.join(path + aircraft + extension) # get the folder path for each aircraft
        images = [f for f in os.listdir(folder_path) if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg")] # list the image files in the folder
        if not images: print(f"Image not found: {aircraft}"); break
        random_image = random.choice(images) # pick a random image
        image_path = os.path.join(folder_path, random_image) # get the full image path
        with open("paths.txt", "a") as f:
            f.write(image_path + "\n")
        
        show_image(remaining_time, timer, instant_reveal, text_size, aircraft, image_path, slideshow_time, False, intermission_time)
        
        if intermission_time > 0: show_image(intermission_time, timer, instant_reveal, text_size, aircraft, image_path, slideshow_time, True, intermission_time)

def open_image(photo_references, image_path, aircraft_name):
    root = tk.Toplevel()  # Use Toplevel instead of Tk
    root.title(f"{aircraft_name} - Image Viewer")

    try:
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=photo)
        label.image = photo  # Keep a reference to the image to prevent garbage collection
        label.pack()

        # Store photo reference globally
        photo_references.append(photo)

        # Display the aircraft name
        aircraft_label = tk.Label(root, text=aircraft_name, font=('Arial', 14))
        aircraft_label.pack()

    except Exception as e: print(f"Error: {e}")

    root.mainloop()

def show_list_of_aircraft(selected_aircraft,text_size):
    def on_aircraft_click(event):
        photo_references = []
        index = listbox.nearest(event.y)
        with open("paths.txt") as file:
            paths = file.readlines()
            if 0 <= index < len(paths):
                pather = paths[index].strip()  # Get the path at the clicked index
                selected_aircraft_name = selected_aircraft[index]  # Get the aircraft name
                open_image(photo_references, pather, selected_aircraft_name)

    root = tk.Tk()
    root.title("List of Selected Aircraft")
    listbox = tk.Listbox(root, font=('Arial', text_size), selectbackground='lightblue', selectforeground='black')
    listbox.pack(fill=tk.BOTH, expand=tk.YES)
    
    for i, aircraft in enumerate(selected_aircraft, start=1):
        listbox.insert(tk.END, f"{i}. {aircraft}")  # Include the index and full aircraft name
    
    listbox.bind('<Double-1>', on_aircraft_click)  # Bind double click event to callback
    root.mainloop()

menu()