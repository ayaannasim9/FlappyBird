import tkinter as tk
import random

root=tk.Tk()
root.title("Flappy Bird")
WIDTH, HEIGHT=600,400
root.geometry(f"{WIDTH}x{HEIGHT}")

background_image=tk.PhotoImage(file="background3.png")

canvas=tk.Canvas(root,width=WIDTH,height=HEIGHT)
canvas.pack(fill="both", expand=True)

canvas.create_image(0, 0, image=background_image, anchor="nw")

#bird settings
bird_size = 30
bird_x = 50
bird_y = HEIGHT // 2
bird_speed_y = 0
gravity = 1
jump_strength = -9.5
game_over=False

#score count
score=0

# Pipe settings
pipe_width = 70
pipe_gap = 90
pipe_speed = 5
pipes = []

# Create bird
bird = canvas.create_rectangle(bird_x, bird_y, bird_x + bird_size, bird_y + bird_size, fill="yellow")

def jump(event):
    global bird_speed_y
    bird_speed_y=jump_strength
    # root.after(40,move)

def spawn_pipe():
    if not game_over:
        # Create top and bottom pipes with a gap
        pipe_x = WIDTH
        gap_y = random.randint(100, HEIGHT - 100 - pipe_gap)
        
        top_pipe = canvas.create_rectangle(pipe_x, 0, pipe_x + pipe_width, gap_y, fill="green")
        bottom_pipe = canvas.create_rectangle(pipe_x, gap_y + pipe_gap, pipe_x + pipe_width, HEIGHT, fill="green")
        
        pipes.append((top_pipe, bottom_pipe))
        
        # Spawn pipes every 2000ms
        root.after(2000, spawn_pipe)

def move():
    global bird_y, bird_speed_y, score, game_over

    # Apply gravity to the bird
    bird_speed_y += gravity
    bird_y += bird_speed_y
    canvas.coords(bird, bird_x, bird_y, bird_x + bird_size, bird_y + bird_size)

    #moving the pipe from the right end of the screen to the bird
    for top_pipe, bottom_pipe in pipes:
        canvas.move(top_pipe, -pipe_speed, 0)
        canvas.move(bottom_pipe, -pipe_speed, 0)
        
        top_coords = canvas.coords(top_pipe)
        bottom_coords = canvas.coords(bottom_pipe)


        
        
        
        #detect collisions
        bird_coords=canvas.coords(bird)
        if((top_coords[0]<bird_coords[2] and top_coords[2]>bird_coords[0]) and (top_coords[3]>bird_coords[1] or bottom_coords[1]<bird_coords[3])):
            game_over=True

    


    if game_over==True:
        canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Over", font=('Arial', 24), fill="red")
    else:
        # canvas.create_text(10,10, text=f'Score : {score}', font=('Arial', 18))
        root.after(25,move)


root.bind("<space>", jump)
spawn_pipe()
move()
root.mainloop()