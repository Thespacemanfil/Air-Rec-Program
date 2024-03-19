import glob, os, shutil, random, time, msvcrt, requests
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
    print("\n\n\n\n\nProgram shutting down. Reason:",reason)
    time.sleep(5)
    os._exit(0)

def menu():
    path = os.path.dirname(os.path.realpath(__file__))
    if os.path.exists(path) and os.path.isdir(path): os.remove(path)

    settings = {
        "path": f"{path}/images",
        "txt_file": get_txt("default.txt"),
        "slideshow_length": 30,
        "slideshow_time": 10,
        "instant_reveal": False,
        "intermission_time": 0,
        "variance": 2,
        "text_size": 50,
        "extension": " airplane",
        "timer": True,
    }

    print("---Aircraft Recognition Program---")
    while not mode_choices(settings): pass
    slideshow(**settings)

def mode_choices(settings):
    match input("competition, casual, learn or custom mode?\n").lower():
        case "competition":
            return True
        case "casual":
            settings.update({
                "slideshow_length": 20,
                "intermission_time": 5,
                "extension": " aircraft",
            })
            return True
        case "learn":
            settings.update({
                "slideshow_length": -1,
                "slideshow_time": -1,
                "instant_reveal": True,
                "timer": False,
                "txt_file": get_txt(None),
                "extension": " aircraft",
            })
            return True
        case "test":
            settings.update({
            "slideshow_length": 3,
            "slideshow_time": 2,
            "instant_reveal": True,
            "intermission_time": 2,
            })
            return True
        case "custom":
            settings.update({
                "txt_file": get_txt(None),
                "slideshow_length": get_int("Slide count (-1 will use entire list):\n"),
                "slideshow_time": get_int("Slide length (seconds, -1 for unlimited):\n"),
                "instant_reveal": get_yn("Reveal answers immediately y/n"),
                "intermission_time": get_int("intermission length (seconds):\n"),
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

def slideshow(path,slideshow_length,slideshow_time,instant_reveal,intermission_time,variance,txt_file,text_size,extension,timer):
    selected_aircraft = aircraft_selector(txt_file,slideshow_length)
    selected_aircraft, selected_paths = image_downloader(selected_aircraft,extension,path,variance)
    print("\n---------------------------------------------------------------------------------\nPress any key to continue")
    msvcrt.getch()
    run_slideshow(slideshow_time, selected_paths, text_size, timer, instant_reveal, selected_aircraft, intermission_time)
    show_list_of_aircraft(selected_aircraft,text_size,selected_paths)
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

def image_downloader(selected_aircraft, extension, path, variance):
    selected_paths = []
    for aircraft in selected_aircraft:
        query = aircraft + extension
        output_path = os.path.join(path, query)

        downloader.download(query, limit=variance, output_dir=path, adult_filter_off=False, force_replace=False, timeout=10, filter="photo", verbose=False)
        
        if len(glob.glob(f'{output_path}/*')) == 0 or not os.path.exists(output_path):
            print(f"Failed to download image for {query}")
            selected_aircraft.remove(aircraft)
        else:
            images = [f for f in os.listdir(output_path) if os.path.splitext(f)[1] in (".png", ".jpg", ".jpeg")] # list the image files in the folder   
            selected_paths.append(os.path.join(output_path, random.choice(images)))
    
    print(f"selected aircraft:{selected_aircraft}\nselected paths:{selected_paths}")
    return selected_aircraft, selected_paths
        
class display_image:
    def __init__(self, remaining_time, timer, instant_reveal, text_size, filename, image_path, intermission, intermission_time, slide_num):
        self.root = tk.Tk()
        self.root.title("Aircraft Image")
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}")
        self.root.attributes("-topmost", True)

        def close_window():
            self.root.destroy()

        if intermission:
            self.root.configure(bg='black')
        else:
            img = Image.open(image_path)
            resize_image = img.resize((w, h))
            photo = ImageTk.PhotoImage(resize_image)
            label = ttk.Label(self.root, image=photo)
            label.pack(fill=tk.BOTH, expand=tk.YES)

        timer_label = ttk.Label(self.root, text=str(remaining_time), font=('Arial', text_size), foreground='orange')
        aircraft_label = ttk.Label(self.root, text=filename, font=('Arial', text_size), foreground='white', background='black')
        slide_label = ttk.Label(self.root, text=slide_num, font=('Arial', text_size), foreground='black', background='white')

        def place_labels():
            self.root.update()  # Update the window to get the correct dimensions

        if intermission:
            if timer and intermission_time > 0:
                timer_label.place(x=w - 100, y=20)
            else:
                timer_label.place_forget()

            if instant_reveal:
                aircraft_label.place(x=w/2, y=h/2, anchor="center")
            else:
                aircraft_label.place_forget()

        else:
            if timer and remaining_time > 0:
                timer_label.place(x=w - 100, y=20)
            else:
                timer_label.place_forget()

            if instant_reveal and intermission_time == 0:
                aircraft_label.place(x=w/2, y=35, anchor="center")
            else:
                aircraft_label.place_forget()
        
        slide_label.place(x=w/20, y=35, anchor="nw")

        def update_timer():
            nonlocal remaining_time
            remaining_time -= 1
            timer_label.config(text=str(remaining_time))
            self.root.after(1000, update_timer)

        place_labels()

        if remaining_time != -1:
            self.root.after((remaining_time*1000), close_window)
            update_timer()

        self.root.mainloop()
        
def run_slideshow(slideshow_time, selected_paths, text_size, timer, instant_reveal, selected_aircraft, intermission_time):
    i = 0
    for aircraft in selected_aircraft:
        image_path = selected_paths[i]
        slide_num = i + 1
        i = slide_num
        
        show_image = display_image(slideshow_time, timer, instant_reveal, text_size, aircraft, image_path, False, intermission_time,slide_num)
        if intermission_time > 0: show_image = display_image(intermission_time, timer, instant_reveal, text_size, aircraft, image_path, True, intermission_time,"")

def open_image(image_path, aircraft_name):
    try:
        root = tk.Toplevel()
        root.title(f"{aircraft_name} - Image Viewer")
        image = Image.open(image_path)
        new_width = int(root.winfo_screenwidth() * 0.70)
        new_height = int(root.winfo_screenheight() * 0.70)
        image = image.resize((new_width, new_height), Image.LANCZOS)
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
    root.title("List of Selected Aircraft")
    listbox = tk.Listbox(root, font=('Arial', text_size), selectbackground='lightblue', selectforeground='black')
    listbox.pack(fill=tk.BOTH, expand=tk.YES)
    
    for i, aircraft in enumerate(selected_aircraft, start=1): listbox.insert(tk.END, f"{i}. {aircraft}")  #index and full aircraft name for the answer list
    
    listbox.bind('<Double-1>', on_aircraft_click)  # Bind double click event to callback
    root.mainloop()

error()
menu()