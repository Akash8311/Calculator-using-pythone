import tkinter as tk

root = tk.Tk()
root.title("My App")
root.geometry("300x200")

tk.Label(root, text="Hello Akash").pack()

root.mainloop()

# Function to handle button clicks
def click(event):
    text = event.widget.cget("text")
    
    if text == "=":
        try:
            result = eval(screen.get())
            screen.set(result)
        except:
            screen.set("Error")
    
    elif text == "C":
        screen.set("")
    
    else:
        screen.set(screen.get() + text)

# Main window
root = tk.Tk()
root.title("Calculator")
root.geometry("300x400")

# Display screen
screen = tk.StringVar()
entry = tk.Entry(root, textvar=screen, font="Arial 20", bd=5, relief="sunken", justify="right")
entry.pack(fill="both", ipadx=8, pady=10)

# Button layout
buttons = [
    ["7","8","9","/"],
    ["4","5","6","*"],
    ["1","2","3","-"],
    ["0",".","=","+"],
    ["C"]
]

# Create buttons
for row in buttons:
    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")
    
    for btn_text in row:
        btn = tk.Button(frame, text=btn_text, font="Arial 15", bd=3)
        btn.pack(side="left", expand=True, fill="both")
        btn.bind("<Button-1>", click)

# Run app
root.mainloop()