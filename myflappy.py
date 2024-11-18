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
jump_strength = -9.8
game_over=False

#score count
score=0
score_text = canvas.create_text(WIDTH - 50, 30, text=f"Score: {score}", font=('Arial', 16), fill="white")

# Pipe settings
pipe_width = 70
# pipe_gap = 88
pipe_speed = 5
pipes = []

#game settings
is_paused=False

#cheat code
bypass_collision=False
pipe_gap_mode=False
slow_motion_toggle=False


# Create bird
bird = canvas.create_rectangle(bird_x, bird_y, bird_x + bird_size, bird_y + bird_size, fill="yellow")

def jump(event):
    global bird_speed_y
    bird_speed_y=jump_strength
    # root.after(40,move)

def toggle_pause(event):
    global is_paused
    is_paused=not is_paused

def slow_motion(event):
    global pipe_speed, slow_motion_toggle
    slow_motion_toggle=not slow_motion_toggle

def no_collision(event):
    global bypass_collision
    bypass_collision=not bypass_collision
    # root.after(25,move)

def pipe_on(event):
    global pipe_gap_mode
    pipe_gap_mode=not pipe_gap_mode

def score_booster(event):
    global score
    score+=5
    canvas.itemconfig(score_text, text=f"Score: {score}")

def spawn_pipe():
    global is_paused, pipe_gap_mode
    delay=2000
    if pipe_gap_mode==False:
        pipe_gap=random.randint(86,92)
    else:
        pipe_gap=200
    if is_paused==False:
        if not game_over:
            # Create top and bottom pipes with a gap
            pipe_x = WIDTH
            gap_y = random.randint(100, HEIGHT - 100 - pipe_gap)
            
            top_pipe = canvas.create_rectangle(pipe_x, 0, pipe_x + pipe_width, gap_y, fill="green")
            bottom_pipe = canvas.create_rectangle(pipe_x, gap_y + pipe_gap, pipe_x + pipe_width, HEIGHT, fill="green")
            
            pipes.append((top_pipe, bottom_pipe))
            
    # Spawn pipes every 2000ms
    if slow_motion_toggle==True:
        delay=10000
    root.after(delay, spawn_pipe)

def move():
    global bird_y, bird_speed_y, score, game_over, score_text, is_paused, bypass_collision, pipe_speed, slow_motion_toggle, gravity, jump_strength
    if slow_motion_toggle==False:
        pipe_speed=5
        gravity=1
        jump_strength=-9.8
    else:
        pipe_speed=1
        gravity=0.2 
        jump_strength=-2.2 

    if is_paused==False:
        # Apply gravity to the bird
        bird_speed_y += gravity
        bird_y += bird_speed_y
        canvas.coords(bird, bird_x, bird_y, bird_x + bird_size, bird_y + bird_size)
        
        #checking if bird is at the bottom or top
        bird_coords=canvas.coords(bird)
        if(bird_coords[1]<0 or bird_coords[3]>400):
            game_over=True
        
        #moving the pipe from the right end of the screen to the bird
        for top_pipe, bottom_pipe in pipes:
            canvas.move(top_pipe, -pipe_speed, 0)
            canvas.move(bottom_pipe, -pipe_speed, 0)
            
            top_coords = canvas.coords(top_pipe)
            bottom_coords = canvas.coords(bottom_pipe)
            if top_coords[2] < 0:
                pipes.remove((top_pipe, bottom_pipe))
                canvas.delete(top_pipe)
                canvas.delete(bottom_pipe)
                score += 1  # Increase score for each pipe passed
                canvas.itemconfig(score_text, text=f"Score: {score}")

            # detect collisions
            if bypass_collision==False:
                bird_coords=canvas.coords(bird)
                if((top_coords[0]<bird_coords[2] and top_coords[2]>bird_coords[0]) and (top_coords[3]>bird_coords[1] or bottom_coords[1]<bird_coords[3])):
                    game_over=True

        if game_over==True:
            canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Over", font=('Arial', 24), fill="red")
            return
            # canvas.create_text(10,10, text=f'Score : {score}', font=('Arial', 18))
    root.after(25,move)


root.bind("<space>", jump)
root.bind("p",toggle_pause)
root.bind("c",no_collision)
root.bind("g", pipe_on)
root.bind("s", slow_motion)
root.bind("b", score_booster)
spawn_pipe()
move()
root.mainloop()