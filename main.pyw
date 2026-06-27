import os
import urllib.request
import tkinter as tk
import threading                       # Handling the tray loop concurrently
import pystray                         # System tray window icon driver
from PIL import Image                  # Required by pystray for the icon asset
from dotenv import load_dotenv
from weather_engine import WeatherEngine

class WeatherWidget:
    def __init__(self, root, api_key, initial_city="Sankt Augustin"):
        self.root = root
        self.engine = WeatherEngine(api_key)
        
        # State tracking variables
        self.current_lat = None
        self.current_lon = None
        self.display_label = initial_city
        self.is_settings_open = False
        self.cached_icon = None 
        
        # Window attribute configurations
        self.root.title("Weather Widget")
        self.root.overrideredirect(True) # Frameless window
        self.root.geometry("280x140+1200+100") # Spacious sizing to prevent clipping
        self.root.config(bg="#1e1e2e")

        # Core View Layout Frame
        self.main_frame = tk.Frame(root, bg="#1e1e2e")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Navigation layer top bar
        self.top_bar = tk.Frame(self.main_frame, bg="#1e1e2e", height=25)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)

        # Settings button '⚙' placed elegantly on the LEFT side
        self.settings_btn = tk.Button(
            self.top_bar, 
            text=" ⚙", 
            font=("Segoe UI", 11), 
            fg="#a6adc8", 
            bg="#1e1e2e", 
            bd=0, 
            activebackground="#1e1e2e", 
            activeforeground="#f5e0dc",
            cursor="hand2"
        )
        self.settings_btn.pack(side=tk.LEFT, padx=5, pady=2)
        self.settings_btn.config(command=self.toggle_settings_drawer)

        # Close button '✕' placed prominently on the RIGHT side
        self.close_btn = tk.Button(
            self.top_bar, 
            text=" ✕ ", 
            font=("Segoe UI", 10, "bold"), 
            fg="#f38ba8", 
            bg="#1e1e2e", 
            bd=0, 
            activebackground="#f38ba8", 
            activeforeground="#1e1e2e",
            cursor="hand2",
            padx=5
        )
        self.close_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # SYSTEM TRAY CHANGE: Withdraw (hide) the window instead of destroying it
        self.close_btn.config(command=self.root.withdraw)
        
        # Close button hover animations
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.config(bg="#313244"))
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.config(bg="#1e1e2e"))

        # Text Layout Container
        self.text_frame = tk.Frame(self.main_frame, bg="#1e1e2e")
        self.text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))

        self.city_label = tk.Label(self.text_frame, text="Loading...", font=("Segoe UI", 11, "bold"), fg="#cdd6f4", bg="#1e1e2e", anchor="w")
        self.city_label.pack(fill=tk.X, pady=(2, 0)) 
        
        self.temp_label = tk.Label(self.text_frame, text="--°C", font=("Segoe UI", 28, "bold"), fg="#f5e0dc", bg="#1e1e2e", anchor="w")
        self.temp_label.pack(fill=tk.X)
        
        self.desc_label = tk.Label(self.text_frame, text="", font=("Segoe UI", 10, "italic"), fg="#a6adc8", bg="#1e1e2e", anchor="w")
        self.desc_label.pack(fill=tk.X, pady=(0, 5))

        # Graphical status icon layout container
        self.icon_label = tk.Label(self.main_frame, bg="#1e1e2e")
        self.icon_label.pack(side=tk.RIGHT, padx=(0, 20), pady=(0, 10))

        # Hidden settings configuration drawer
        self.drawer_frame = tk.Frame(root, bg="#313244", height=50)
        
        self.city_entry = tk.Entry(self.drawer_frame, font=("Segoe UI", 9), bg="#45475a", fg="#cdd6f4", bd=1, relief=tk.FLAT)
        self.city_entry.pack(side=tk.LEFT, padx=(15, 5), pady=10, fill=tk.X, expand=True)
        self.city_entry.insert(0, initial_city)
        
        self.city_entry.bind("<Return>", lambda e: self.change_location())

        self.apply_btn = tk.Button(self.drawer_frame, text="Apply", font=("Segoe UI", 9, "bold"), fg="#1e1e2e", bg="#a6e3a1",
                                   bd=0, padx=10, command=self.change_location)
        self.apply_btn.pack(side=tk.RIGHT, padx=(5, 15), pady=10)

        # Dynamic Window Drag Handling listeners
        self.main_frame.bind("<Button-1>", self.start_drag)
        self.main_frame.bind("<B1-Motion>", self.drag)
        self.top_bar.bind("<Button-1>", self.start_drag)
        self.top_bar.bind("<B1-Motion>", self.drag)
        self.text_frame.bind("<Button-1>", self.start_drag)
        self.text_frame.bind("<B1-Motion>", self.drag)
        self.city_label.bind("<Button-1>", self.start_drag)
        self.city_label.bind("<B1-Motion>", self.drag)
        self.temp_label.bind("<Button-1>", self.start_drag)
        self.temp_label.bind("<B1-Motion>", self.drag)
        self.desc_label.bind("<Button-1>", self.start_drag)
        self.desc_label.bind("<B1-Motion>", self.drag)
        self.icon_label.bind("<Button-1>", self.start_drag)
        self.icon_label.bind("<B1-Motion>", self.drag)
        
        # System Tray/Right-click backup close option
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Exit Widget", command=self.root.destroy)
        self.main_frame.bind("<Button-3>", self.show_menu)

        # Initialize bootstrap location sequence
        self.bootstrap_location(initial_city)

    def bootstrap_location(self, city_name):
        coords = self.engine.get_coords_by_name(city_name)
        if coords:
            self.current_lat, self.current_lon, self.display_label = coords
            self.update_weather_loop()
        else:
            self.city_label.config(text="Location Error")

    def toggle_settings_drawer(self):
        if not self.is_settings_open:
            curr_geom = self.root.geometry().split("+")
            self.root.geometry(f"280x190+{curr_geom[1]}+{curr_geom[2]}")
            self.drawer_frame.pack(fill=tk.X, side=tk.BOTTOM)
            self.is_settings_open = True
        else:
            self.drawer_frame.pack_forget()
            curr_geom = self.root.geometry().split("+")
            self.root.geometry(f"280x140+{curr_geom[1]}+{curr_geom[2]}")
            self.is_settings_open = False

    def change_location(self):
        target_city = self.city_entry.get().strip()
        if target_city:
            coords = self.engine.get_coords_by_name(target_city)
            if coords:
                self.current_lat, self.current_lon, self.display_label = coords
                self.refresh_weather_display()
                self.toggle_settings_drawer() 
            else:
                self.city_label.config(text="City Not Found")

    def fetch_weather_icon(self, icon_id):
        icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
        try:
            with urllib.request.urlopen(icon_url) as response:
                img_data = response.read()
            return tk.PhotoImage(data=img_data)
        except Exception as e:
            print(f"Failed to fetch weather status icon: {e}")
            return None

    def refresh_weather_display(self):
        if self.current_lat and self.current_lon:
            data = self.engine.get_weather(self.current_lat, self.current_lon)
            if data:
                self.city_label.config(text=self.display_label)
                self.temp_label.config(text=f"{data['temp']}°C")
                self.desc_label.config(text=data['description'])
                
                new_icon = self.fetch_weather_icon(data["icon_id"])
                if new_icon:
                    self.cached_icon = new_icon  
                    self.icon_label.config(image=self.cached_icon)

    def update_weather_loop(self):
        self.refresh_weather_display()
        self.root.after(600000, self.update_weather_loop)

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)


# --- SYSTEM TRAY BACKGROUND DRIVER FUNCTION ---
def run_system_tray(widget_root):
    """Controls the permanent background icon in the Windows notification area."""
    def show_widget(icon, item):
        widget_root.deiconify()  # Brings the hidden window back onto the desktop
        widget_root.lift()       # Brings the window to the front
    def exit_completely(icon, item):
        icon.stop()              # Stops the tray loop
        widget_root.quit()       # Securely terminates the Tkinter loop together
        widget_root.destroy()    # Hard-destroys all frames/windows to terminate the python process safely

    # Fallback: Creates a small solid green square if you don't have a local 'weather_icon.png' file
    try:
        tray_image = Image.open("images/weather-icon.png")
    except Exception:
        tray_image = Image.new("RGB", (16, 16), "#a6e3a1")

    tray_menu = pystray.Menu(
        pystray.MenuItem("Show Widget", show_widget, default=True),
        pystray.MenuItem("Exit Completely", exit_completely)
    )
    
    icon = pystray.Icon("WeatherWidget", tray_image, "Weather Widget", tray_menu)
    icon.onclick = show_widget
    icon.run()


if __name__ == "__main__":
    load_dotenv()
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    
    if not API_KEY:
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Security Missing Check", "Critical Error: 'OPENWEATHER_API_KEY' not found.")
        exit(1)
        
    root = tk.Tk()
    widget = WeatherWidget(root, API_KEY, "Sankt Augustin")
    
    # Spawn the background task tray listener on a separate standalone thread
    tray_thread = threading.Thread(target=run_system_tray, args=(root,), daemon=True)
    tray_thread.start()
    
    root.mainloop()