import tkinter as tk
import random
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Flappy Bird")
# WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
WIDTH, HEIGHT = 1200,800
root.geometry(f"{WIDTH}x{HEIGHT}")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack(fill="both", expand=True)

# Open and resize the background image
original_bg = Image.open("background3.png").resize((WIDTH, HEIGHT), Image.LANCZOS)
background_image = ImageTk.PhotoImage(original_bg)
canvas.create_image(0, 0, image=background_image, anchor="nw")

# Bird settings
bird_size = 50 # Size for collision purposes
bird_x = 80
bird_y = HEIGHT // 2
bird_speed_y = 0
gravity = 2
jump_strength = -19.0
game_over = False

# Load the bird image
bird_image = Image.open("bird3.png").resize((50,50), Image.LANCZOS)
bird_image_tk=ImageTk.PhotoImage(bird_image)
# bird = canvas.create_image(bird_x, bird_y, image=bird_image_tk, anchor="center", tags="game")
bird_width = bird_image_tk.width()-19.3
bird_height = bird_image_tk.height()-19.3

# Pipe settings
pipe_width = 70
pipe_speed = 18
pipes = []
# Load pipe image (pipe3.png)
pipe_image = Image.open("pipe3.png").resize((70, HEIGHT), Image.LANCZOS) # Open pipe3.png image
pipe_image_tk = ImageTk.PhotoImage(pipe_image)  # Convert to Tkinter PhotoImage format

# Score count
score = 0

# Game settings
is_paused = False

# Cheat code
bypass_collision = False
pipe_gap_mode = False
slow_motion_toggle = False
# Boss key
boss_image = Image.open("spreadsheet.png").resize((WIDTH,HEIGHT), Image.LANCZOS)
boss_image_final=ImageTk.PhotoImage(boss_image)
boss_image_displayed = False


def main_menu():
    # Main menu title
    clear_screen()
    canvas.create_image(0, 0, image=background_image, anchor="nw")
    canvas.create_text(WIDTH // 2, HEIGHT // 4, text="Flappy Bird", font=("Arial", 50), fill="white", tags="menu")

    # Play Game button
    play_button = tk.Button(root, text="Play Game", font=("Arial", 20), command=play_game)
    canvas.create_window(WIDTH // 2, HEIGHT // 2 - 50, window=play_button)

        # Leaderboard button
        # leaderboard_button = tk.Button(root, text="Leaderboard", font=("Arial", 20), command=show_leaderboard)
        # canvas.create_window(WIDTH // 2, HEIGHT // 2 + 20, window=leaderboard_button)

    # Controls button
    controls_button = tk.Button(root, text="Controls", font=("Arial", 20), command=show_controls)
    canvas.create_window(WIDTH // 2, HEIGHT // 2 + 90, window=controls_button)

def play_game():
    clear_screen()
    global background_image,bird,score_text
    canvas.create_image(0, 0, image=background_image, anchor="nw")
    score_text = canvas.create_text(WIDTH - 60, 30, text=f"Score: {score}", font=('Arial', 20), fill="white", tags="game")
    bird = canvas.create_image(bird_x, bird_y, image=bird_image_tk, anchor="center", tags="game")
    spawn_pipe()
    move()

def clear_screen():
    """Clear all elements from the canvas."""
    canvas.delete("all")
    # canvas.itemconfigure("game", state="hidden")

def show_controls():
    """Display the controls screen."""
    clear_screen()
    canvas.create_text(WIDTH // 2, HEIGHT // 6, text="Controls", font=("Arial", 40), fill="white", tags="controls")
    controls_info = [
        "Space: Jump",
        "P: Pause/Resume",
        "C: Toggle Collision Bypass",
        "G: Toggle Pipe Gap Mode",
        "B: Score Booster",
        "A: Boss Key"
    ]
    for i, line in enumerate(controls_info):
        canvas.create_text(WIDTH // 2, HEIGHT // 3 + i * 30, text=line, font=("Arial", 20), fill="white", tags="controls")

    # Back to main menu button
    back_button = tk.Button(root, text="Back", font=("Arial", 20), command=main_menu)
    canvas.create_window(WIDTH // 2, HEIGHT - 100, window=back_button)
def boss_key(event):
    global boss_image_displayed, is_paused
    is_paused=not is_paused
    if not boss_image_displayed:
        # Hide all game elements
        canvas.itemconfigure("game", state="hidden")
        # Display boss image
        canvas.create_image(0, 0, anchor="nw", image=boss_image_final, tags="boss")
    else:
        # Remove boss image
        canvas.delete("boss")
        # Show all game elements
        canvas.itemconfigure("game", state="normal")
    
    boss_image_displayed = not boss_image_displayed

def jump(event):
    global bird_speed_y, jump_strength
    bird_speed_y = jump_strength

def toggle_pause(event):
    global is_paused
    if game_over==False:
        is_paused = not is_paused
        if is_paused:
            canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Paused", font=('Arial', 20), fill="white", tags="pause")
        else:
            canvas.delete("pause")

def no_collision(event):
    global bypass_collision
    bypass_collision = not bypass_collision

def pipe_on(event):
    global pipe_gap_mode
    pipe_gap_mode = not pipe_gap_mode

def score_booster(event):
    global score, game_over
    if not game_over:
        score += 5
        canvas.itemconfig(score_text, text=f"Score: {score}")
def difficulty():
    # print("adjusting difficulty")
    global pipe_speed, score
    if score<=5:
        pipe_speed=pipe_speed
        # print(pipe_speed)
    elif score <=10:
        pipe_speed=23.5
        # print(pipe_speed)
    elif score<=15:
        pipe_speed=28
        # print(pipe_speed)
    else:
        pipe_speed=33
        # print(pipe_speed)

def spawn_pipe():
    # print("in spaw_pipe")
    global is_paused, pipe_gap_mode
    delay = 1750
    if not pipe_gap_mode:
        pipe_gap = random.randint(30, 38)
    else:
        pipe_gap = 200
    if not is_paused:
        if not game_over:
            # Create top and bottom pipes using the pipe image
            pipe_x = WIDTH
            gap_y = random.randint(100, HEIGHT - 100 - pipe_gap)

            if pipe_image_tk:  # Only use pipe image if it's properly loaded
                top_pipe = canvas.create_image(pipe_x, gap_y - (pipe_width // 2), image=pipe_image_tk, anchor="s", tags="game")
                bottom_pipe = canvas.create_image(pipe_x, gap_y + pipe_gap + (pipe_width // 2), image=pipe_image_tk, anchor="n", tags="game")
                pipes.append((top_pipe, bottom_pipe))

    # Spawn pipes every 4000ms (or adjust as needed)
    root.after(delay, spawn_pipe)

def move():
    # print("in move")
    global bird_y, bird_speed_y, score, game_over, is_paused, bypass_collision, pipe_speed, slow_motion_toggle, gravity, jump_strength
    if score%5==0:
        # print("inside this thing in move")
        difficulty()
    # print(pipe_speed)
    if not is_paused:
        # Apply gravity to the bird
        bird_speed_y += gravity
        bird_y += bird_speed_y
        canvas.coords(bird, bird_x, bird_y)

        # Calculate bird's bounding box for collision
        bird_coords = canvas.coords(bird)  # Returns [center_x, center_y]
        bird_x1 = bird_coords[0] - bird_width // 2
        bird_y1 = bird_coords[1] - bird_height // 2
        bird_x2 = bird_coords[0] + bird_width // 2
        bird_y2 = bird_coords[1] + bird_height // 2

        # Check if the bird hits the top or bottom
        if bird_y1 < 0 or bird_y2 > HEIGHT:
            game_over = True

        # Move pipes and check collisions
        for top_pipe, bottom_pipe in pipes:
            canvas.move(top_pipe, -pipe_speed, 0)
            canvas.move(bottom_pipe, -pipe_speed, 0)

            # Get pipe coordinates
            top_coords = canvas.coords(top_pipe)
            bottom_coords = canvas.coords(bottom_pipe)

            # Check if pipes are out of bounds
            if top_coords[0] < 0:
                pipes.remove((top_pipe, bottom_pipe))
                canvas.delete(top_pipe)
                canvas.delete(bottom_pipe)
                score += 1  # Increase score for each pipe passed
                canvas.itemconfig(score_text, text=f"Score: {score}")

            # Detect collisions
            if not bypass_collision:
                if ((bird_x2 > top_coords[0] - pipe_width // 2 and bird_x1 < top_coords[0] + pipe_width // 2) and
                        (bird_y1 < top_coords[1] or bird_y2 > bottom_coords[1])):
                    game_over = True

        if game_over:
            canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Over", font=('Arial', 30), fill="red", tags="game")
            return
    root.after(15, move)

# Key bindings
root.bind("<space>", jump)
root.bind("p", toggle_pause)
root.bind("c", no_collision)
root.bind("g", pipe_on)
root.bind("b", score_booster)
root.bind("a", boss_key)
main_menu()
# Start game functions
root.mainloop()
