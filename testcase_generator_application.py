import openai
from openai import OpenAIError
import tkinter as tk
from tkinter import TclError, scrolledtext
import pandas as pd
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import fixed_values
from table_generator import TableGenerator
from dotenv import load_dotenv
import os

logo = '''Testcase Generator'''

# OpenAI API key setup
openai.api_key = os.environ['OPENAI_KEY']

content = {
    1: 'You are an experienced Quality Analyst, you will be asked some doubts, related to Quality testing.',  # doubt
    2: "You are an experienced quality analyst. You will be provided functionality later, you have to generate as many as test cases. Each test case should include the following fields: Test case description, Prerequisites, Step number, Step description, Expected results, and Validations. Write them in number list and step number in 'a,b,c,d....'. Strictly use the given field names and don't used bold, italic texts",  # testcase
    3: 'You are an experienced Quality Analyst, you will be asked to generate selenium with java code for the user story provided.',  # automation code: java
    4: 'You are an experienced Quality Analyst, you will be asked to generate selenium with python code for the user story provided.',  # automation code: python
    5: 'You are a helpful assistant.'  # other
}

msg = []

def setMsg(content):
    global msg
    msg = [
        {
            "role": "system",
            "content": content,
        },
    ]

# Initialize Tkinter root window with ThemedTk
window = ttk.Window(themename='darkly')
window.title("TestCase Generator")
window.attributes('-fullscreen', False)  # Open in full screen

# Title:
title_label = ttk.Label(master=window, text=logo, font='Calibri 16 bold')
title_label.pack()

# Frame to hold entry field and send button
bottom_frame = ttk.Frame(master=window, padding="5 5 5 5")
bottom_frame.pack(padx=30, pady=30, fill=tk.X)

# Entry widget for user input
entry_field = ttk.Entry(master=bottom_frame, width=100, font=('Calibri', 14))
entry_field.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)

# Dropdown menu for options
options = ["Doubt", "Testcases", "Automation Code: Java", "Automation Code: Python", "Other"]
option_var = tk.StringVar(window)
option_var.set(options[0])
option_menu = ttk.Combobox(master=bottom_frame, textvariable=option_var, values=options, font=("Calibri", 14), state="readonly")
option_menu.pack(side=tk.LEFT, padx=(0, 10))

# Load and resize the send icon image using Pillow
send_icon_image = Image.open("C:\\Users\\n523197\\Documents\\Blubolt_idea\\TestCase_Generator_VS_Code\\send_icon.png")
send_icon_image = send_icon_image.resize((30, 30))  # Resize image to 30x30 pixels
send_icon = ImageTk.PhotoImage(send_icon_image)

# Text area to display conversation
text_area_frame = ttk.Frame(master=window, padding="5 5 5 5")
text_area_frame.pack(padx=20, pady=20, expand=True, fill=tk.BOTH)

text_area = scrolledtext.ScrolledText(master=text_area_frame, wrap=tk.NONE, font=("Calibri", 12), height = 15)
text_area.pack(padx=20, pady=20, expand=True, fill=tk.BOTH)
text_area.xview_moveto(0)  # Initialize horizontal scrollbar

# Prevent user from editing text but allow copying
def ignore_event(event):
    return "break"

text_area.bind("<Key>", ignore_event)
text_area.bind("<Control-c>", ignore_event)
text_area.bind("<Control-v>", ignore_event)  # Ignore paste
text_area.bind("<Button-3>", ignore_event)   # Ignore right-click menu

# Treeview to display conversation
tree_frame = ttk.Frame(master=window, padding="5 5 5 5")
tree_frame.pack(padx=5, pady=5, expand=True, fill=tk.BOTH)

# Define columns
columns = (
    "Test Case ID", "Test Case Description", "Pre-requisite Condition", "Step Number",
    "Steps Description", "Expected Result", "Actual Result", "Validations", "Status", "Comments"
)

# Create Treeview
style = ttk.Style()
style.configure("Treeview", rowheight=50, background="#333333", foreground="white", fieldbackground="#333333")
style.map('Treeview', background=[('selected', '#5A9')], foreground=[('selected', 'white')])

tree = ttk.Treeview(master=tree_frame, columns=columns, show='headings', style="Treeview", height=15, padding='5 5 5 5')

# Define headings
for col in columns:
    tree.heading(col, text=col)

# Adjust the column width
for col in columns:
    tree.column(col, width=200)

# Add striped row tags for gridline effect
tree.tag_configure('odd', background='#3A3A3A')
tree.tag_configure('even', background='#2A2A2A')
tree.xview_moveto(0)
tree.yview_moveto(0)

# Initially hide the Treeview
tree.pack_forget()

# Custom tooltip class
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

    def show_tip(self):
        try:
            x, y, _, _ = self.widget.bbox("insert")
        except TclError:
            # Fallback to a default position if bbox("insert") is not supported
            x, y = self.widget.winfo_rootx(), self.widget.winfo_rooty()
            x += self.widget.winfo_width() // 2
            y += self.widget.winfo_height() // 2
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)


    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

# Function to show tooltip with full content
def show_tooltip(event):
    row_id = tree.identify_row(event.y)
    col_id = tree.identify_column(event.x)
    
    if row_id and col_id:
        cell_value = tree.item(row_id)["values"][int(col_id[1:]) - 1]
        tooltip = ToolTip(tree, text=cell_value)
        tooltip.show_tip()

# Bind the Treeview to show tooltips
tree.bind("<Motion>", show_tooltip)

def send_message():
    user_message = entry_field.get()
    if user_message.lower() == "exit":
        window.quit()
    
    selected_option = options.index(option_var.get()) + 1
    setMsg(content[selected_option])
    
    if user_message:
        text_area.insert(tk.END, f"You: {user_message}\n")
        text_area.insert(tk.END, f"\n")
        entry_field.delete(0, tk.END)
        
        msg.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=msg,
                temperature=fixed_values.TEMPERATURE,
                max_tokens=fixed_values.MAX_TOKENS,
            )
            reply = response.choices[0].message.content
            if selected_option == 2:
                # Create a TableGenerator instance and generate the Excel file with dynamic filename
                generator = TableGenerator(reply)
                excel_filepath = generator.generate_excel()
                
                # Read the generated Excel file back into Python and display it in a readable format
                df_read = pd.read_excel(excel_filepath)
                
                # Replace 'NaN' with an empty string
                df_read.fillna('', inplace=True)

                # Wrap text in each cell
                # wrapped_data = df_read.applymap(lambda x: textwrap.fill(str(x), width=20))

                # table_str = tabulate.tabulate(wrapped_data, headers='keys', tablefmt='fancy_grid', showindex=False)

                text_area.insert(tk.END, f"ChatGPT: Excel file '{excel_filepath}' generated successfully.")
                text_area.insert(tk.END, f"\n")

                # Insert rows into the treeview
                for i, row in df_read.iterrows():
                    tag = 'even' if i % 2 == 0 else 'odd'
                    tree.insert("", "end", values=tuple(row), tags=(tag,))

                # Show the Treeview when test cases are generated
                tree.pack(expand=True, fill=tk.BOTH, side=ttk.LEFT)

            
            text_area.insert(tk.END, f"ChatGPT: {reply}\n")
            text_area.insert(tk.END, f"\n")
            print(f"ChatGPT: {reply}\n")
            
            msg.append({
                "role": "assistant",
                "content": reply
            })
        except OpenAIError as e:
            text_area.insert("", "end", values=(f"Error: {str(e)}",))
            text_area.insert(tk.END, f"\n")

# Send button with icon and adjusted size
send_button = ttk.Button(bottom_frame, image=send_icon, command=send_message)
send_button.image = send_icon  # Keep a reference to the image to avoid garbage collection
send_button.pack(side=tk.LEFT, ipadx=10, ipady=10)  # Adjust padding for button size

window.bind('<Return>', lambda event=None: send_button.invoke())  # Bind Enter key to send button



# Run the program/application
window.mainloop()
