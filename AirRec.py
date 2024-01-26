from bing_image_downloader import downloader
import random, os, re, shutil
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
quit = False

def menu():
    slideshow_mode_selection()

def clean_filename(filename):
    return re.sub(r"[\\/*?:<>|]", '', filename)

def slideshow_mode_selection():
    with open('paths.txt', 'w'): pass
    print("Aircraft Recognition Program")
    match input("Competition, Casual, Learn, Custom or Test mode?\n").lower():
        case "casual": slideshow_length = 20; slideshow_time = 10; instant_reveal = True; intermission_time = 5; variance = 2; txt_file = "Competition.txt"; text_size = 50; extension = " aircraft"; timer = True
        case "test": slideshow_length = 3; slideshow_time = 4; instant_reveal = True; intermission_time = 2; variance = 2; txt_file = "Competition.txt"; text_size = 50; extension = " aircraft"; timer = True
        case "learn": slideshow_length = 10; slideshow_time = 999; instant_reveal = True; intermission_time = 0; variance = 2; txt_file = "Competition.txt"; text_size = 50; extension = " aircraft"; timer = False
        case _:
            slideshow_length = int(input("Amount of slides? -1 slides will run through all aircraft in the list\n"))
            slideshow_time = int(input("Seconds per slide?\n"))
            if input("Reveal answers immediately yes/no\n").lower() == "yes": instant_reveal = True
            else: instant_reveal = False
            intermission_time = int(input("Seconds of intermission?\n"))
            variance = int(input("How many images per aircraft? (More images means more randomness but slower download speed)\n"))
            text_size = int(input("Text size?\n"))
            txt_file = input("Which list of aircraft do you want to draw from?\n") + ".txt"
            extension = clean_filename(" " + input("Search modifier? e.g real aircraft, top view\n")).rstrip()
            if input("Timer yes/no\n").lower() == "yes": timer = True
            else: timer = False

    selected_aircraft = aircraft_selector(txt_file,slideshow_length)
    image_downloader(selected_aircraft,extension,variance)
    run_slideshow(slideshow_time,text_size,timer,instant_reveal,selected_aircraft,intermission_time,extension,variance)
    show_list_of_aircraft(selected_aircraft,text_size)

def aircraft_selector(txt_file,slideshow_length):
    with open(txt_file, 'r') as file:
        aircraft_list = file.read().splitlines()

    if slideshow_length <= len(aircraft_list) and slideshow_length > 0:
        selected_aircraft = random.sample(aircraft_list, slideshow_length)
        return selected_aircraft
    elif slideshow_length == -1:
        return aircraft_list
    else: print("INVALID SLIDESHOW LENGTH")

def image_downloader(selected_aircraft,extension,variance):
    for aircraft in selected_aircraft:
        query = aircraft + extension
        downloaded_files = downloader.download(query, limit=variance, output_dir='C:/aircraft_recognition_program/images/', adult_filter_off=False, force_replace=True, timeout=60, filter="photo", verbose=True)
        if downloaded_files:
            downloaded_file_path = downloaded_files[0]
            new_file_path = os.path.join('C:/aircraft_recognition_program/images/')
            image = Image.open(downloaded_file_path)
            if image.format != 'JPEG':
                image = image.convert('RGB')
                image.save(new_file_path)
                print("converted to jpeg and Saved to new path")
                os.remove(downloaded_file_path)
            else:
                shutil.move(downloaded_file_path, new_file_path)
                print("Saved to new path")

            print(f"Renamed {downloaded_file_path} to {new_file_path}")
        
def show_image(remaining_time,timer,instant_reveal,text_size,cleaned_filename,image_path,slideshow_time,intermission,intermission_time):
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
        if timer and not intermission:
            window_width = root.winfo_width()
            timer_label.place(x=window_width - timer_label.winfo_width() - 30, y=20)
        elif timer and intermission:
            timer_label.place(x=w - timer_label.winfo_width() - 30, y=20)
        elif hasattr(timer_label, 'place'):
            timer_label.place_forget()
    
    def place_aircraft_name():
        if instant_reveal and intermission and intermission_time > 0:
            aircraft_label.place(x=w/2, y=h/2, anchor="center")
        elif instant_reveal and not intermission and intermission_time == 0:
            aircraft_label.place(x=w/2, y=35, anchor="center")
        elif hasattr(aircraft_label, 'place'):
            aircraft_label.place_forget()
    
    timer_label = ttk.Label(root, text=str(remaining_time), font=('Arial', text_size), foreground='orange')
    place_timer_label()
    
    aircraft_label = ttk.Label(root, text=cleaned_filename, font=('Arial', text_size), foreground='white', background='black')
    place_aircraft_name()
    
    def update_timer():
        nonlocal remaining_time  # Use nonlocal to modify the outer variable
        remaining_time -= 1
        timer_label.config(text=str(remaining_time))
        if remaining_time > 0:
            root.after(1000, update_timer)

    update_timer()
    
    def on_image_resize(event):
        place_timer_label()  
        place_aircraft_name()  
    root.bind('<Configure>', on_image_resize)
    
    def close_window():
        root.destroy()
    
    if intermission:
        root.configure(bg='black')
        root.after(remaining_time*1000, close_window)
    else:
        root.after(slideshow_time*1000, close_window)

    
    root.mainloop()
              
def run_slideshow(slideshow_time, text_size, timer, instant_reveal, selected_aircraft, intermission_time, extension, variance):
    for aircraft in selected_aircraft:
        remaining_time = slideshow_time
        cleaned_filename = clean_filename(aircraft)
        image_path = os.path.join('C:/aircraft_recognition_program/images/' + aircraft + extension + '/Image_' + str(random.randint(1, variance)) + '.jpg')
        with open("paths.txt", "a") as f:
            f.write(image_path + "\n")
        
        if os.path.exists(image_path):
            show_image(remaining_time, timer, instant_reveal, text_size, cleaned_filename, image_path, slideshow_time, False, intermission_time)
            
            if intermission_time > 0:
                show_image(intermission_time, timer, instant_reveal, text_size, cleaned_filename, image_path, slideshow_time, True, intermission_time)
        else:
            print(f"Image not found: {cleaned_filename}")

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

while quit == False: menu()