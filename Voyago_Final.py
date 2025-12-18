from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar 
import datetime
import csv
import os
import random

# --- Constants & Configuration ---
WINDOW_TITLE = "Voyago – Bus Ticket Booking"
WINDOW_SIZE = "1200x1200"
DATA_FILE = "bookings.csv"

# Color Palette (Redbus-inspired)
COLOR_PRIMARY = "#4A90E2"  # Subtle Blue
COLOR_SECONDARY = "#3e3e52" # Dark Grey
COLOR_BG = "#f0f0f0"       # Light Grey
COLOR_WHITE = "#ffffff"
COLOR_TEXT = "#333333"
COLOR_SEAT_AVAILABLE = "#ffffff"
COLOR_SEAT_SELECTED = "#4A90E2"
COLOR_SEAT_BOOKED = "#d0d0d0" # Light Grey shade, darker than BG but light enough
COLOR_SEAT_BORDER_AVAILABLE = "#28a745" # Green border

CITIES = [
    "Bengaluru", "Chennai", "Hyderabad", "Delhi", 
    "Chandigarh", "Mumbai", "Madurai", "Mangalore"
]

# --- Helper Class: Bus Data Service ---
class BusService:
    """
    Simulates a backend service to fetch bus data.
    """
    def __init__(self):
        self.buses = []
        self._generate_dummy_data()

    def _generate_dummy_data(self):
        """Generates a list of dummy buses for demonstration."""
        bus_types = ["Sleeper", "Semi-sleeper", "AC Volvo", "Non-AC Seater"]
        travels = ["Voyago Travels", "GreenLine", "CityConnect", "RoadKing", "StarBus"]
        
        # Create a pool of buses that can be filtered
        # In a real app, this would be a database query
        for _ in range(50):
            start_city = random.choice(CITIES)
            end_city = random.choice(CITIES)
            while start_city == end_city:
                end_city = random.choice(CITIES)
            
            # Random times
            h = random.randint(0, 23)
            m = random.choice([0, 15, 30, 45])
            dep_time = f"{h:02d}:{m:02d}"
            
            duration_h = random.randint(5, 12)
            arr_h = (h + duration_h) % 24
            arr_time = f"{arr_h:02d}:{m:02d}"
            
            price = random.choice([450, 600, 850, 1200, 1500])
            
            self.buses.append({
                "id": f"BUS{random.randint(1000, 9999)}",
                "name": random.choice(travels),
                "type": random.choice(bus_types),
                "from": start_city,
                "to": end_city,
                "dep_time": dep_time,
                "arr_time": arr_time,
                "duration": f"{duration_h}h 00m",
                "price": price,
                "seats_total": 32,
                "seats_booked": [] # List of booked seat numbers (e.g., "1A", "2B")
            })

    def search_buses(self, from_city, to_city, date_str):
        """
        Returns a list of buses matching the criteria.
        Note: date_str is passed but not strictly used to filter the *existence* 
        of the bus in this dummy generator, but we pretend it is.
        """
        results = []
        for bus in self.buses:
            if bus["from"] == from_city and bus["to"] == to_city:
                # Deep copy to avoid modifying the original template for this session
                # In a real app, we'd fetch specific schedule for the date
                bus_copy = bus.copy()
                # Simulate some random booked seats for this specific date search
                # We'll just generate them on the fly for the UI to render
                booked_count = random.randint(0, 20)
                all_seats = []
                rows = 8
                cols = 4
                col_labels = ['A', 'B', 'C', 'D']
                for r in range(1, rows + 1):
                    for c in col_labels:
                        all_seats.append(f"{r}{c}")
                
                bus_copy["seats_booked"] = random.sample(all_seats, booked_count)
                bus_copy["seats_available"] = bus_copy["seats_total"] - len(bus_copy["seats_booked"])
                results.append(bus_copy)
        
        # Fallback: If no buses found, generate some on the fly for this route
        if not results:
            bus_types = ["Sleeper", "Semi-sleeper", "AC Volvo", "Non-AC Seater"]
            travels = ["Voyago Travels", "GreenLine", "CityConnect", "RoadKing", "StarBus"]
            
            # Generate 3-5 random buses
            for _ in range(random.randint(3, 5)):
                # Random times
                h = random.randint(0, 23)
                m = random.choice([0, 15, 30, 45])
                dep_time = f"{h:02d}:{m:02d}"
                
                duration_h = random.randint(5, 12)
                arr_h = (h + duration_h) % 24
                arr_time = f"{arr_h:02d}:{m:02d}"
                
                price = random.choice([450, 600, 850, 1200, 1500])
                
                new_bus = {
                    "id": f"BUS{random.randint(1000, 9999)}",
                    "name": random.choice(travels),
                    "type": random.choice(bus_types),
                    "from": from_city,   # Force match
                    "to": to_city,       # Force match
                    "dep_time": dep_time,
                    "arr_time": arr_time,
                    "duration": f"{duration_h}h 00m",
                    "price": price,
                    "seats_total": 32,
                    "seats_booked": [] 
                }
                
                # Add seat logic similar to above
                booked_count = random.randint(0, 20)
                all_seats = []
                rows = 8
                cols = 4
                col_labels = ['A', 'B', 'C', 'D']
                for r in range(1, rows + 1):
                    for c in col_labels:
                        all_seats.append(f"{r}{c}")
                
                new_bus["seats_booked"] = random.sample(all_seats, booked_count)
                new_bus["seats_available"] = new_bus["seats_total"] - len(new_bus["seats_booked"])
                
                results.append(new_bus)
                
        return results


# --- Main Application Class ---
class VoyagoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry("900x600") 
        self.minsize(900, 600)
        self.configure(bg=COLOR_BG)
        
        # Configure root grid weights to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Shared State
        self.search_criteria = {}
        self.selected_bus = None
        self.selected_seats = []
        self.total_fare = 0
        self.passenger_details = {} # Store passenger info before payment
        
        # Service
        self.bus_service = BusService()
        
        # Container for frames
        self.container = tk.Frame(self, bg=COLOR_BG)
        self.container.grid(row=0, column=0, sticky="nsew")
        
        # Configure container grid weights
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        # Initialize Screens
        for F in (SearchScreen, ResultsScreen, SeatSelectionScreen, BookingScreen, PaymentScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            # Put all frames in the same cell, they will stack
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("SearchScreen")

    def show_frame(self, page_name):
        """Raises a frame to the top."""
        frame = self.frames[page_name]
        frame.tkraise()
        # Optional: Call a refresh method if the frame has one
        if hasattr(frame, "on_show"):
            frame.on_show()

    def get_page(self, page_name):
        return self.frames[page_name]

    def save_booking(self):
        details = self.passenger_details
        bus = self.selected_bus
        seats = ",".join(self.selected_seats)
        booking_id = f"BKG{random.randint(10000, 99999)}"
        
        row = [
            booking_id,
            bus["from"],
            bus["to"],
            self.search_criteria["date"],
            bus["name"],
            seats,
            details.get("name"),
            details.get("age"),
            details.get("gender"),
            details.get("phone"),
            details.get("email"),
            self.total_fare
        ]
        
        # Write to CSV
        file_exists = os.path.isfile(DATA_FILE)
        try:
            with open(DATA_FILE, mode='a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Booking ID", "From", "To", "Date of Journey", "Bus Name", 
                                     "Seat Numbers", "Passenger Name", "Age", "Gender", "Contact", "Email", "Total Fare"])
                writer.writerow(row)
            
            # Success Message
            msg = (f"Booking Confirmed!\n\nID: {booking_id}\nBus: {bus['name']}\n"
                   f"Seats: {seats}\nTotal Fare: INR {self.total_fare}\n\n"
                   "Thank you for choosing Voyago!")
            messagebox.showinfo("Success", msg)
            
            # Return to Home
            self.show_frame("SearchScreen")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save booking: {e}")

# --- Screen 1: Home/Search ---
class SearchScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)
        self.controller = controller
        
        # Configure this frame to expand
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1) # Content row expands
        
        # Header
        header = tk.Frame(self, bg=COLOR_PRIMARY, height=80)
        header.grid(row=0, column=0, sticky="ew")
        # Removed pack_propagate(False) to allow natural expansion if needed
        
        lbl_title = tk.Label(header, text="Voyago", font=("Helvetica", 24, "bold"), 
                             bg=COLOR_PRIMARY, fg=COLOR_WHITE)
        lbl_title.pack(pady=20)
        
        # Center Container (to hold the search card)
        center_frame = tk.Frame(self, bg=COLOR_BG)
        center_frame.grid(row=1, column=0, sticky="nsew")
        center_frame.columnconfigure(0, weight=1)
        center_frame.rowconfigure(0, weight=1) # Top spacer
        center_frame.rowconfigure(2, weight=1) # Bottom spacer
        
        # Search Card
        search_frame = tk.Frame(center_frame, bg=COLOR_WHITE, bd=2, relief="groove")
        search_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=40)
        
        # Grid Layout for Inputs inside the card
        search_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        # FROM
        tk.Label(search_frame, text="FROM", font=("Arial", 10, "bold"), bg=COLOR_WHITE, fg="gray").grid(row=0, column=0, padx=20, pady=(40, 5), sticky="w")
        self.var_from = tk.StringVar()
        self.dd_from = ttk.Combobox(search_frame, textvariable=self.var_from, values=CITIES, state="readonly", font=("Arial", 12))
        self.dd_from.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # TO
        tk.Label(search_frame, text="TO", font=("Arial", 10, "bold"), bg=COLOR_WHITE, fg="gray").grid(row=0, column=1, padx=20, pady=(40, 5), sticky="w")
        self.var_to = tk.StringVar()
        self.dd_to = ttk.Combobox(search_frame, textvariable=self.var_to, values=CITIES, state="readonly", font=("Arial", 12))
        self.dd_to.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="ew")
        
        # DATE
        tk.Label(search_frame,text="DATE OF JOURNEY",font=("Arial", 10, "bold"),bg=COLOR_WHITE,fg="gray" ).grid(row=0, column=2, padx=45, pady=(40, 5), sticky="w")


        def open_calendar():
        # Create popup window
            cal_win = Toplevel(search_frame)
            cal_win.title("Select Date")

            # Calendar widget
            cal = Calendar(cal_win, selectmode='day', date_pattern="dd-mm-yyyy")
            cal.grid(row=1, column=2, pady=10, padx=10)

            # Function to pick date
            def pick_date():
                self.date_var.set(cal.get_date())   # set selected date
                cal_win.destroy()              # close popup

            Button(cal_win, text="Select", command=pick_date).grid(row=1, column=3 ,pady=(0,20))


        self.date_var = StringVar()

        date_entry = Entry(search_frame, textvariable=self.date_var, font=("Arial", 12), width=20)
        date_entry.grid(row=1, column=2, pady=(0,20), padx=20)


        Button(search_frame, text="Choose Date", command=open_calendar).grid(row=2, column=2, pady=10)


        # RETURN DATE (Optional)
        #tk.Label(search_frame, text="RETURN (Optional)", font=("Arial", 10, "bold"), bg=COLOR_WHITE, fg="gray").grid(row=0, column=3, padx=20, pady=(40, 5), sticky="w")
        #self.ent_return = DateEntry(search_frame, width=12, date_pattern='dd-mm-yyyy')
        #self.ent_return.delete(0, "end") # Allow it to be empty initially
        #self.ent_return.grid(row=1, column=3, padx=20, pady=(0, 20), sticky="ew")
        
        # Search Button
        # Note: On macOS, bg color might not render on standard buttons. 
        # Using standard fg="black" to ensure text is visible if bg is ignored.
        btn_search = tk.Button(search_frame, text="Search Buses", font=("Helvetica", 11, "bold"), 
                               bg="#357ABD", fg="black", # Changed to black for visibility on Mac
                               padx=20, pady=8,
                               relief="flat", command=self.on_search)
        btn_search.grid(row=3, column=1, columnspan=2, pady=40, sticky="ew")

    def on_search(self):
        f = self.var_from.get()
        t = self.var_to.get()
        d = self.date_var.get()
        
        if not f or not t or not d:
            messagebox.showwarning("Input Error", "Please fill in From, To, and Date fields.")
            return
        
        if f == t:
            messagebox.showerror("Input Error", "Source and Destination cannot be the same.")
            return
            
        # Basic date validation (DateEntry guarantees valid date format usually)
        try:
            Calendar.datetime.strptime(d, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Date Error", "Invalid date format. Please use DD-MM-YYYY.")
            return

        # Save criteria and move to next screen
        self.controller.search_criteria = {"from": f, "to": t, "date": d}
        self.controller.show_frame("ResultsScreen")

# --- Screen 2: Search Results ---
class ResultsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)
        self.controller = controller
        
        # Top Bar
        top_bar = tk.Frame(self, bg=COLOR_WHITE, height=60)
        top_bar.pack(fill="x")
        
        btn_back = tk.Button(top_bar, text="< Back", command=lambda: controller.show_frame("SearchScreen"),
                             bg=COLOR_WHITE, relief="flat", font=("Arial", 10))
        btn_back.pack(side="left", padx=10)
        
        self.lbl_route = tk.Label(top_bar, text="", font=("Arial", 14, "bold"), bg=COLOR_WHITE)
        self.lbl_route.pack(side="left", padx=20)
        
        # Results Area (Scrollable)
        self.canvas = tk.Canvas(self, bg=COLOR_BG)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas to resize the window when canvas resizes
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.scrollbar.pack(side="right", fill="y")
        
    def on_canvas_configure(self, event):
        # Resize the inner frame to match the canvas width
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_show(self):
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        criteria = self.controller.search_criteria
        self.lbl_route.config(text=f"{criteria['from']}  →  {criteria['to']}  |  {criteria['date']}")
        
        buses = self.controller.bus_service.search_buses(criteria['from'], criteria['to'], criteria['date'])
        
        if not buses:
            lbl_no_bus = tk.Label(self.scrollable_frame, text="No buses found for this route.", 
                                  font=("Arial", 16), bg=COLOR_BG, fg="gray")
            lbl_no_bus.pack(pady=50)
            return

        for bus in buses:
            self.create_bus_card(bus)

    def create_bus_card(self, bus):
        card = tk.Frame(self.scrollable_frame, bg=COLOR_WHITE, bd=1, relief="solid")
        card.pack(fill="x", pady=10, ipady=10)
        
        # Grid layout for card content
        card.columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Bus Name & Type
        tk.Label(card, text=bus["name"], font=("Arial", 14, "bold"), bg=COLOR_WHITE).grid(row=0, column=0, sticky="w", padx=20)
        tk.Label(card, text=bus["type"], font=("Arial", 10), fg="gray", bg=COLOR_WHITE).grid(row=1, column=0, sticky="w", padx=20)
        
        # Times
        tk.Label(card, text=bus["dep_time"], font=("Arial", 12, "bold"), bg=COLOR_WHITE).grid(row=0, column=1)
        tk.Label(card, text="Departure", font=("Arial", 9), fg="gray", bg=COLOR_WHITE).grid(row=1, column=1)
        
        tk.Label(card, text=bus["duration"], font=("Arial", 10), fg="gray", bg=COLOR_WHITE).grid(row=0, column=2)
        
        tk.Label(card, text=bus["arr_time"], font=("Arial", 12, "bold"), bg=COLOR_WHITE).grid(row=0, column=3)
        tk.Label(card, text="Arrival", font=("Arial", 9), fg="gray", bg=COLOR_WHITE).grid(row=1, column=3)
        
        # Price & Seats
        tk.Label(card, text=f"INR {bus['price']}", font=("Arial", 14, "bold"), fg=COLOR_PRIMARY, bg=COLOR_WHITE).grid(row=0, column=4)
        tk.Label(card, text=f"{bus['seats_available']} Seats Left", font=("Arial", 10), fg="gray", bg=COLOR_WHITE).grid(row=1, column=4)
        
        # View Seats Button
        btn_view = tk.Button(card, text="VIEW SEATS", bg=COLOR_PRIMARY, fg="black", 
                             font=("Arial", 10, "bold"), relief="flat",
                             command=lambda b=bus: self.select_bus(b))
        btn_view.grid(row=0, column=5, rowspan=2, padx=20)

    def select_bus(self, bus):
        self.controller.selected_bus = bus
        self.controller.show_frame("SeatSelectionScreen")

# --- Screen 3: Seat Selection ---
class SeatSelectionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)
        self.controller = controller
        self.seat_buttons = {}
        
        # Top Bar
        top_bar = tk.Frame(self, bg=COLOR_WHITE, height=60)
        top_bar.pack(fill="x")
        btn_back = tk.Button(top_bar, text="< Back to Results", command=lambda: controller.show_frame("ResultsScreen"),
                             bg=COLOR_WHITE, relief="flat", font=("Arial", 10))
        btn_back.pack(side="left", padx=10)
        
        self.lbl_bus_info = tk.Label(top_bar, text="", font=("Arial", 12, "bold"), bg=COLOR_WHITE)
        self.lbl_bus_info.pack(side="left", padx=20)
        
        # Main Content
        content = tk.Frame(self, bg=COLOR_BG)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left: Seat Map
        self.seat_frame = tk.Frame(content, bg=COLOR_WHITE, bd=1, relief="solid")
        self.seat_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(self.seat_frame, text="Select Seats", font=("Arial", 14), bg=COLOR_WHITE).pack(pady=10)
        self.grid_frame = tk.Frame(self.seat_frame, bg=COLOR_WHITE)
        self.grid_frame.pack(pady=20)
        
        # Legend
        legend_frame = tk.Frame(self.seat_frame, bg=COLOR_WHITE)
        legend_frame.pack(side="bottom", pady=20)
        self._create_legend_item(legend_frame, "Available", COLOR_SEAT_AVAILABLE, 0, border_color=COLOR_SEAT_BORDER_AVAILABLE)
        self._create_legend_item(legend_frame, "Selected", COLOR_SEAT_SELECTED, 1)
        self._create_legend_item(legend_frame, "Booked", COLOR_SEAT_BOOKED, 2)
        
        # Right: Summary
        self.summary_frame = tk.Frame(content, bg=COLOR_WHITE, bd=1, relief="solid", width=300)
        self.summary_frame.pack(side="right", fill="y")
        self.summary_frame.pack_propagate(False)
        
        tk.Label(self.summary_frame, text="Booking Summary", font=("Arial", 14, "bold"), bg=COLOR_WHITE).pack(pady=20)
        
        self.lbl_selected_seats = tk.Label(self.summary_frame, text="Seats: None", font=("Arial", 12), bg=COLOR_WHITE)
        self.lbl_selected_seats.pack(pady=5)
        
        self.lbl_total_fare = tk.Label(self.summary_frame, text="Total: INR 0", font=("Arial", 14, "bold"), fg=COLOR_PRIMARY, bg=COLOR_WHITE)
        self.lbl_total_fare.pack(pady=10)
        
        self.btn_proceed = tk.Button(self.summary_frame, text="PROCEED", bg=COLOR_PRIMARY, fg="black",
                                     font=("Arial", 12, "bold"), relief="flat", state="disabled",
                                     command=self.proceed_to_booking)
        self.btn_proceed.pack(side="bottom", fill="x", padx=20, pady=20)

    def _create_legend_item(self, parent, text, color, col, border_color=None):
        f = tk.Frame(parent, bg=COLOR_WHITE)
        f.grid(row=0, column=col, padx=10)
        
        # Use a frame to simulate border if needed for the legend icon
        if border_color:
            icon_frame = tk.Frame(f, bg=border_color, width=20, height=20)
            icon_frame.pack(side="left")
            icon_frame.pack_propagate(False)
            tk.Label(icon_frame, bg=color, width=2).pack(fill="both", padx=1, pady=1)
        else:
            tk.Label(f, bg=color, width=2, relief="solid", bd=1).pack(side="left")
            
        tk.Label(f, text=text, bg=COLOR_WHITE, font=("Arial", 9)).pack(side="left", padx=5)

    def on_show(self):
        # Reset state
        self.controller.selected_seats = []
        self.update_summary()
        
        # Clear grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.seat_buttons = {}
        
        bus = self.controller.selected_bus
        self.lbl_bus_info.config(text=f"{bus['name']} ({bus['type']})")
        
        # Draw Seats (4 cols x 8 rows)
        rows = 8
        cols = 4
        col_labels = ['A', 'B', 'C', 'D']
        
        for r in range(1, rows + 1):
            for c_idx, c_label in enumerate(col_labels):
                seat_num = f"{r}{c_label}"
                is_booked = seat_num in bus["seats_booked"]
                
                # Gap for aisle (between B and C)
                col_pos = c_idx if c_idx < 2 else c_idx + 1
                
                # Button styling
                # For Mac, standard buttons don't support borders well, so we might rely on highlightbackground or generic relief
                # But to get a specific green border, on Mac, using highlightbackground is the trick for 'border' color.
                
                btn = tk.Button(self.grid_frame, text=seat_num, width=4, height=2, font=("Arial", 8),
                                relief="flat")
                
                if is_booked:
                    btn.config(bg=COLOR_SEAT_BOOKED, state="disabled", disabledforeground="white")
                else:
                    # Green border for available
                    btn.config(bg=COLOR_SEAT_AVAILABLE, 
                               highlightbackground=COLOR_SEAT_BORDER_AVAILABLE, 
                               highlightthickness=2,
                               command=lambda s=seat_num: self.toggle_seat(s))
                
                btn.grid(row=r, column=col_pos, padx=5, pady=5)
                self.seat_buttons[seat_num] = btn

    def toggle_seat(self, seat_num):
        if seat_num in self.controller.selected_seats:
            self.controller.selected_seats.remove(seat_num)
            self.seat_buttons[seat_num].config(bg=COLOR_SEAT_AVAILABLE, fg=COLOR_TEXT, highlightbackground=COLOR_SEAT_BORDER_AVAILABLE)
        else:
            self.controller.selected_seats.append(seat_num)
            # Remove border/change border to selected color if desired, or keep it. 
            # Usually selected has its own solid fill.
            self.seat_buttons[seat_num].config(bg=COLOR_SEAT_SELECTED, fg=COLOR_WHITE, highlightbackground=COLOR_SEAT_SELECTED)
        
        self.update_summary()

    def update_summary(self):
        count = len(self.controller.selected_seats)
        if count > 0:
            seats_str = ", ".join(self.controller.selected_seats)
            price = self.controller.selected_bus['price']
            total = count * price
            
            self.lbl_selected_seats.config(text=f"Seats: {seats_str}")
            self.lbl_total_fare.config(text=f"Total: INR {total}")
            self.btn_proceed.config(state="normal", bg=COLOR_PRIMARY)
            
            self.controller.total_fare = total
        else:
            self.lbl_selected_seats.config(text="Seats: None")
            self.lbl_total_fare.config(text="Total: INR 0")
            self.btn_proceed.config(state="disabled", bg="gray")

    def proceed_to_booking(self):
        self.controller.show_frame("BookingScreen")

# --- Screen 4: Passenger Details & Confirmation ---
class BookingScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)
        self.controller = controller
        
        # Top Bar
        top_bar = tk.Frame(self, bg=COLOR_WHITE, height=60)
        top_bar.pack(fill="x")
        btn_back = tk.Button(top_bar, text="< Back to Seats", command=lambda: controller.show_frame("SeatSelectionScreen"),
                             bg=COLOR_WHITE, relief="flat", font=("Arial", 10))
        btn_back.pack(side="left", padx=10)
        tk.Label(top_bar, text="Passenger Details", font=("Arial", 14, "bold"), bg=COLOR_WHITE).pack(side="left", padx=20)
        
        # Form Container
        form_frame = tk.Frame(self, bg=COLOR_WHITE, bd=1, relief="solid")
        form_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=500)
        
        tk.Label(form_frame, text="Enter Contact Details", font=("Arial", 16, "bold"), bg=COLOR_WHITE).pack(pady=20)
        
        # Form Fields
        grid_f = tk.Frame(form_frame, bg=COLOR_WHITE)
        grid_f.pack(pady=10)
        
        # Name
        tk.Label(grid_f, text="Name:", bg=COLOR_WHITE, font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.ent_name = tk.Entry(grid_f, font=("Arial", 11), width=30)
        self.ent_name.grid(row=0, column=1, padx=10, pady=10)
        
        # Age
        tk.Label(grid_f, text="Age:", bg=COLOR_WHITE, font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.ent_age = tk.Entry(grid_f, font=("Arial", 11), width=10)
        self.ent_age.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        # Gender
        tk.Label(grid_f, text="Gender:", bg=COLOR_WHITE, font=("Arial", 11)).grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.var_gender = tk.StringVar()
        self.dd_gender = ttk.Combobox(grid_f, textvariable=self.var_gender, values=["Male", "Female", "Other"], state="readonly", width=10)
        self.dd_gender.grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
        # Email
        tk.Label(grid_f, text="Email:", bg=COLOR_WHITE, font=("Arial", 11)).grid(row=3, column=0, sticky="e", padx=10, pady=10)
        self.ent_email = tk.Entry(grid_f, font=("Arial", 11), width=30)
        self.ent_email.grid(row=3, column=1, padx=10, pady=10)
        
        # Phone
        tk.Label(grid_f, text="Phone:", bg=COLOR_WHITE, font=("Arial", 11)).grid(row=4, column=0, sticky="e", padx=10, pady=10)
        self.ent_phone = tk.Entry(grid_f, font=("Arial", 11), width=30)
        self.ent_phone.grid(row=4, column=1, padx=10, pady=10)
        
        # Footer with Price and Pay Button
        self.footer_frame = tk.Frame(self, bg=COLOR_WHITE, height=80, bd=1, relief="raised")
        self.footer_frame.pack(side="bottom", fill="x")
        self.footer_frame.pack_propagate(False) # Maintain height
        
        # Price Display (Left side of footer)
        price_container = tk.Frame(self.footer_frame, bg=COLOR_WHITE)
        price_container.pack(side="left", padx=20, pady=10)
        
        tk.Label(price_container, text="Amount", font=("Arial", 10), fg="gray", bg=COLOR_WHITE).pack(anchor="w")
        self.lbl_footer_price = tk.Label(price_container, text="INR 0", font=("Arial", 16, "bold"), fg=COLOR_TEXT, bg=COLOR_WHITE)
        self.lbl_footer_price.pack(anchor="w")
        
        # Proceed Button (Right side of footer)
        self.btn_pay = tk.Button(self.footer_frame, text="PROCEED TO PAY", bg=COLOR_PRIMARY, fg="black",
                                 font=("Arial", 12, "bold"), relief="flat", padx=20, pady=10,
                                 command=self.confirm_booking)
        self.btn_pay.pack(side="right", padx=20, pady=15)

    def on_show(self):
        # Clear fields
        self.ent_name.delete(0, tk.END)
        self.ent_age.delete(0, tk.END)
        self.var_gender.set("")
        self.ent_email.delete(0, tk.END)
    def on_show(self):
        # Clear fields
        self.ent_name.delete(0, tk.END)
        self.ent_age.delete(0, tk.END)
        self.var_gender.set("")
        self.ent_email.delete(0, tk.END)
        self.ent_phone.delete(0, tk.END)
        
        # Update Price in Footer
        self.lbl_footer_price.config(text=f"INR {self.controller.total_fare}")

    def confirm_booking(self):
        name = self.ent_name.get().strip()
        age = self.ent_age.get().strip()
        gender = self.var_gender.get()
        email = self.ent_email.get().strip()
        phone = self.ent_phone.get().strip()
        
        # Validation
        if not name or not age or not gender or not email or not phone:
            messagebox.showwarning("Missing Info", "Please fill all fields.")
            return
        
        if not age.isdigit() or int(age) <= 0:
            messagebox.showerror("Invalid Input", "Age must be a positive number.")
            return
            
        if "@" not in email:
            messagebox.showerror("Invalid Input", "Please enter a valid email.")
            return
            
        if not phone.isdigit() or len(phone) != 10:
            messagebox.showerror("Invalid Input", "Phone number must be 10 digits.")
            return
            
        # Move to Payment Screen
        self.controller.passenger_details = {
            "name": name,
            "age": age,
            "gender": gender,
            "email": email,
            "phone": phone
        }
        self.controller.show_frame("PaymentScreen")

# --- Screen 5: Payment Screen ---
class PaymentScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)
        self.controller = controller
        
        # Layout
        self.pack_propagate(False)
        
        # Header
        header = tk.Frame(self, bg=COLOR_WHITE, height=60)
        header.pack(fill="x", pady=(0, 20))
        btn_back = tk.Button(header, text="< Back", command=lambda: controller.show_frame("BookingScreen"),
                             bg=COLOR_WHITE, relief="flat", font=("Arial", 10))
        btn_back.pack(side="left", padx=10)
        tk.Label(header, text="Payment", font=("Arial", 14, "bold"), bg=COLOR_WHITE).pack(side="left", padx=20)
        
        # content
        content_frame = tk.Frame(self, bg=COLOR_BG)
        content_frame.pack(expand=True)
        
        tk.Label(content_frame, text="Total Amount to Pay", font=("Arial", 12), bg=COLOR_BG, fg="gray").pack(pady=5)
        self.lbl_amount = tk.Label(content_frame, text="INR 0", font=("Arial", 24, "bold"), bg=COLOR_BG, fg=COLOR_TEXT)
        self.lbl_amount.pack(pady=(0, 30))
        
        # Pay Button
        self.btn_qr = tk.Button(content_frame, text="Pay through QR Code", bg=COLOR_PRIMARY, fg="black",
                                font=("Arial", 14, "bold"), relief="flat", padx=30, pady=15,
                                command=self.show_qr_popup)
        self.btn_qr.pack()
        
    def on_show(self):
        self.lbl_amount.config(text=f"INR {self.controller.total_fare}")
        
    def show_qr_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Scan to Pay")
        popup.geometry("400x500")
        popup.configure(bg=COLOR_WHITE)
        
        tk.Label(popup, text="Scan QR Code", font=("Arial", 16, "bold"), bg=COLOR_WHITE).pack(pady=20)
        
        # Image
        try:
            # Look for qr_code.png in the same directory as the script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(script_dir, "qr_code.png")
            
            # Using PhotoImage
            self.qr_image = tk.PhotoImage(file=img_path)
            # Resize if necessary? Tkinter PhotoImage zooming/subsampling is limited.
            # Assuming the image is reasonably sized or we display as is. 
            # If large, we might need a library, but let's try displaying as is first.
            img_label = tk.Label(popup, image=self.qr_image, bg=COLOR_WHITE)
            img_label.pack(pady=10)
        except Exception as e:
            tk.Label(popup, text=f"QR Code not found.\n{e}", bg=COLOR_WHITE, fg="red").pack(pady=20)
            
        tk.Label(popup, text=f"Amount: INR {self.controller.total_fare}", font=("Arial", 12), bg=COLOR_WHITE).pack(pady=10)
        
        # Done Button (Simulates successful payment)
        btn_done = tk.Button(popup, text="Payment Done", bg="#28a745", fg="black",
                             font=("Arial", 12, "bold"), relief="flat", padx=20, pady=10,
                             command=lambda: [popup.destroy(), self.controller.save_booking()])
        btn_done.pack(side="bottom", pady=30)

if __name__ == "__main__":
    app = VoyagoApp()
    app.mainloop()
