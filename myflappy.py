# from tkinter import *
import tkinter as tk

root=tk.Tk()
root.title("Flappy Bird")
width, height=600,400
root.geometry(f"{width}x{height}")

background_image=tk.PhotoImage(file="background3.png")

canvas=tk.Canvas(root,width=width,height=height)
canvas.pack(fill="both", expand=True)

canvas.create_image(0, 0, image=background_image, anchor="nw")

# bird_image=tk.PhotoImage(file="bird3.png")
# bird_x, bird_y = 50, 250
# bird = canvas.create_image(bird_x, bird_y, image=bird_image, anchor="nw")

bird_size = 30
bird_x = 50
bird_y = height // 2
bird_speed_y = 0
gravity = 1
jump_strength = -12

# Create bird
bird = canvas.create_rectangle(bird_x, bird_y, bird_x + bird_size, bird_y + bird_size, fill="yellow")

root.mainloop()