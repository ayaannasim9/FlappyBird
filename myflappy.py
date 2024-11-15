# from tkinter import *
import tkinter as tk

root=tk.Tk()
root.title("Flappy Bird")
WIDTH, HEIGHT=600,400
root.geometry(f"{WIDTH}x{HEIGHT}")

background_image=tk.PhotoImage(file="background3.png")

canvas=tk.Canvas(root,width=WIDTH,height=HEIGHT)
canvas.pack(fill="both", expand=True)

canvas.create_image(0, 0, image=background_image, anchor="nw")

bird_size = 30
bird_x = 50
bird_y = HEIGHT // 2
bird_speed_y = 0
gravity = 1
jump_strength = -13
game_over=False

# Create bird
bird = canvas.create_rectangle(bird_x, bird_y, bird_x + bird_size, bird_y + bird_size, fill="yellow")

def jump(event):
    global bird_speed_y
    bird_speed_y=jump_strength
    # root.after(40,move)

def move():
    global bird_y, bird_speed_y, score, game_over

    # Apply gravity to the bird
    bird_speed_y += gravity
    bird_y += bird_speed_y
    canvas.coords(bird, bird_x, bird_y, bird_x + bird_size, bird_y + bird_size)
    if game_over==True:
        canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Over", font=('Arial', 24), fill="red")
    else:
        root.after(40,move)




root.bind("<space>", jump)
move()
root.mainloop()