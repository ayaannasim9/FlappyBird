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
root.mainloop()