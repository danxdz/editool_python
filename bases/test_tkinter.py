import tkinter as tk

# --- functions ---

def move_item(event):
    canvas.coords(item, event.x-50, event.y-50, event.x+50, event.y+50)

def change_item(event):
    if canvas.itemcget(item, 'fill') == 'red':
        canvas.itemconfig(item, fill='blue')
    else:        
        canvas.itemconfig(item, fill='red')

# --- main ---

root = tk.Tk()

canvas = tk.Canvas(root, width=500, height=300)
canvas.pack()

item = canvas.create_rectangle(0, 0, 100, 100, fill='red')

canvas.bind("<Button-1>", change_item)
canvas.bind("<Motion>", move_item)

root.mainloop()
