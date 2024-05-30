import glob, os, sys, random, time, msvcrt, requests
from PIL import Image, ImageTk #pillow
import tkinter as tk
from tkinter import ttk
from bing_image_downloader import downloader

def error():
    if glob.glob("*.txt") == []:
        crash("No txt lists found.")
    try: requests.head("http://www.google.com/", timeout=1)
    except requests.ConnectionError: crash("No internet connection")

def crash(reason):
    print("--------------------------------------------\nProgram shutting down. Reason:",reason)
    time.sleep(5)
    os._exit(0)

def menu():
    error()
    path = os.path.dirname(os.path.realpath(__file__))
    settings = {
        "path": f"{path}/images",
        "txt_file": get_txt("default.txt"),
        "slideshow_length": 30,
        "primary_time": 3,
        "answers": False,
        "secondary_time": 7,
        "secondary_black": True,
        "variance": 2,
        "text_size": 50,
        "extension": " airplane",
        "show_slide_num": True,
        "timer": True,
    }

    print("-------Aircraft Recognition Program-------")
    while not mode_choices(settings): pass
    slideshow(**settings)

def mode_choices(settings):
    match input("competition, casual, learn or custom mode?\n").lower():
        case "competition":
            return True
        case "casual":
            settings.update({
                "slideshow_length": 20,
                "secondary_time": 5,
                "extension": " aircraft",
            })
            return True
        case "learn":
            settings.update({
                "slideshow_length": -1,
                "primary_time": -1,
                "answers": True,
                "secondary_time": 0,
                "timer": False,
                "txt_file": get_txt(None),
                "extension": " aircraft",
            })
            return True
        case "test":
            settings.update({
                "slideshow_length": 4,
                "primary_time": 5,
                "answers": True,
                "secondary_time": 5,
                "secondary_black": False,
                "variance": 2,
                "text_size": 50,
                "extension": " airplane",
                "show_slide_num": True,
                "timer": True,
            })
            return True
        case "custom":
            settings.update({
                "txt_file": get_txt(None),
                "slideshow_length": get_int("Slide count (-1 will use entire list):\n"),
                "primary_time": get_int("Slide length (seconds, -1 for unlimited):\n"),
                "answers": get_yn("Reveal answers immediately y/n"),
                "secondary_time": get_int("Secondary time length (seconds), 0 to disable:\n"),
                "secondary_black": get_yn("Secondary is blank?"),
                "extension": (" " + input("Search modifier: e.g top view, in flight, [or leave blank]\n")).rstrip(),
                "timer": get_yn("Countdown timer y/n"),
            })
            return True
        case _:
            return False

def get_txt(file):
    if file is None: file = input("Choose a TXT list: " + str(glob.glob("*.txt")) + "\n")
    while os.path.exists(file) == False:
        print("Failed to find",file)
        file = input("Choose a TXT list: " + str(glob.glob("*.txt")) + "\n")
    return file

def get_yn(text):
    print(text)
    key = msvcrt.getch().lower()
    match key:
        case b"y": print("y"); return True
        case b"n": print("n"); return False
        case _: print("Invalid input"); return get_yn(text)

def get_int(text):
    while True:
        try: return int(input(text))
        except ValueError: print("Invalid input")

def slideshow(path,slideshow_length,primary_time,answers,secondary_time,secondary_black,variance,txt_file,text_size,extension,show_slide_num,timer):
    aircraft_list = aircraft_selector(txt_file,slideshow_length)
    selected_aircraft, primary_paths = image_downloader(aircraft_list,extension,path,variance)
    print("\n---------------------------------------------------------------------------------\nPress any key to continue")
    msvcrt.getch()
    print("")
    present_slideshow(primary_time, primary_paths, text_size, timer, answers, selected_aircraft, secondary_time, secondary_black, show_slide_num)
    show_list_of_aircraft(selected_aircraft,text_size,primary_paths)
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

def image_downloader(aircraft_list, extension, path, variance):
    primary_paths = []
    selected_aircraft = []
    for aircraft in aircraft_list:
        query = aircraft + extension
        output_path = os.path.join(path, query)

        try:
            downloader.download(query, limit=variance, output_dir=path, adult_filter_off=False, force_replace=False, timeout=1, filter="photo", verbose=False)
            images = [f for f in os.listdir(output_path) if os.path.splitext(f)[1] in (".png", ".jpg", ".jpeg")] # list the image files in the folder
            if len(images) > 0:
                primary_paths.append(os.path.join(output_path, random.choice(images)))
                selected_aircraft.append(aircraft)
        except:
            error()
            print(f"Failed to download image for {query}")

    return selected_aircraft, primary_paths

def present_slideshow(primary_time, primary_paths, text_size, timer, answers, selected_aircraft, secondary_time, secondary_black, show_slide_num):
    root = tk.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.attributes("-fullscreen", True)
    root.wm_attributes("-topmost", 1)
    slide_num = 1
    secondary_enabled = False
    if secondary_time > 0: secondary_enabled = True
    primary = True
    label = None
    photo = None
    rootafters = []

    def key_pressed(event):
        for after_id in rootafters:
            root.after_cancel(after_id)
        rootafters.clear()

        if event.keysym == 'Return': next_slide()
        elif event.keysym == 'BackSpace': prev_slide()
        elif event.keysym == 'Escape': sys.exit()
    root.bind("<Key>", key_pressed)

    def next_slide():
        nonlocal slide_num, primary, secondary_enabled
        if secondary_enabled:
            if not primary: slide_num += 1
            primary = not primary
        else: slide_num += 1

        if slide_num > len(primary_paths): root.destroy()
        else: present_slide()

    def prev_slide():
        nonlocal slide_num, primary, secondary_enabled
        if secondary_enabled and primary and slide_num > 1: slide_num -= 1
        primary = True
        present_slide()

    def present_slide():
        nonlocal label, photo
        remaining_time = primary_time if primary else secondary_time

        for widget in root.winfo_children():
            widget.destroy()

        if primary or not secondary_black:
            with Image.open(primary_paths[slide_num - 1]) as img:
                resize_image = img.resize((w, h))
                photo = ImageTk.PhotoImage(resize_image)
                label = ttk.Label(root, image=photo)
                label.image = photo
                label.pack(fill=tk.BOTH, expand=tk.YES)
        else:
            root.configure(bg='black')

        timer_label = ttk.Label(root, text=str(remaining_time), font=('Arial', text_size), foreground='orange')
        aircraft_label = ttk.Label(root, text=selected_aircraft[slide_num - 1], font=('Arial', text_size), foreground='white', background='black')
        slide_label = ttk.Label(root, text=slide_num, font=('Arial', text_size), foreground='black', background='white')

        if show_slide_num: slide_label.place(x=w/20, y=35, anchor="nw")
        if timer: timer_label.place(x=w - 100, y=20)
        if answers:
            if not secondary_enabled: aircraft_label.place(x=w/2, y=35, anchor="center")
            elif not primary:
                if secondary_black: aircraft_label.place(x=w/2, y=h/2, anchor="center")
                else: aircraft_label.place(x=w/2, y=35, anchor="center")

        root.update()

        def update_timer():
            nonlocal remaining_time
            if remaining_time > 0:
                remaining_time -= 1
                timer_label.config(text=str(remaining_time))
                rootafters.append(root.after(1000, update_timer))

        if remaining_time != -1:
            rootafters.append(root.after((remaining_time*1000), next_slide))
            update_timer()

        root.mainloop()

    present_slide()

def open_image(image_path, aircraft_name):
    try:
        root = tk.Toplevel()
        root.title(f"{aircraft_name} - Image Viewer")
        image = Image.open(image_path)
        image = image.resize((int(root.winfo_screenwidth() * 0.70), int(root.winfo_screenheight() * 0.70)), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=photo) # Display the image
        label.image = photo  # Keep a reference to the image to prevent garbage collection
        label.pack()
        aircraft_label = tk.Label(root, text=aircraft_name, font=('Arial', 30)) # Display the aircraft name
        aircraft_label.pack()
        root.mainloop()
    except Exception as e: print(f"Error opening image {image_path} for aircraft {aircraft_name}: {e}")

def show_list_of_aircraft(selected_aircraft, text_size, paths):
    def on_aircraft_click(event):
        index = listbox.nearest(event.y)
        if 0 <= index < len(selected_aircraft):
            selected_aircraft_name = selected_aircraft[index]  # Get the aircraft name
            if index < len(paths):
                pather = paths[index]  # Get the path at the clicked index
                open_image(pather, selected_aircraft_name)
            else:
                print(f"No path found for aircraft {selected_aircraft_name}")

    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    root.title("List of Selected Aircraft")
    listbox = tk.Listbox(root, font=('Arial', int(text_size*0.8)), selectbackground='lightblue', selectforeground='black')
    listbox.pack(fill=tk.BOTH, expand=tk.YES)
    
    for i, aircraft in enumerate(selected_aircraft, start=1): listbox.insert(tk.END, f"{i}. {aircraft}")  #index and full aircraft name for the answer list
    
    listbox.bind('<Double-1>', on_aircraft_click)  # Bind double click event to callback
    root.mainloop()

menu()