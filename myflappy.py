import tkinter as tk
import random
from PIL import Image, ImageTk
import os

root = tk.Tk()
root.title("Flappy Bird")
# WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
WIDTH, HEIGHT = 1200,800
root.geometry(f"{WIDTH}x{HEIGHT}")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack(fill="both", expand=True)

#keys
key_bindings = {
    "jump": "<space>",
    "pause": "p",
    "collision_toggle": "c",
    "pipe_gap_toggle": "g",
    "score_booster": "b",
    "boss_key": "<Escape>",
}


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
in_game=False

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
#Leaderboard file
LEADERBOARD_FILE="leaderboard.txt"
#some ids
move_id=None
spawn_id=None

def main_menu():
    # Main menu title
    clear_screen()
    canvas.create_image(0, 0, image=background_image, anchor="nw")
    canvas.create_text(WIDTH // 2, HEIGHT // 4, text="Flappy Bird", font=("Arial", 50), fill="white", tags="menu")

    # Play Game button
    play_button = tk.Button(root, text="Play Game", font=("Arial", 20), command=play_game)
    canvas.create_window(WIDTH // 2, HEIGHT // 2 - 50, window=play_button)

    # Leaderboard button
    leaderboard_button = tk.Button(root, text="Leaderboard", font=("Arial", 20), command=display_leaderboard)
    canvas.create_window(WIDTH // 2, HEIGHT // 2 + 20, window=leaderboard_button)

    # Controls button
    controls_button = tk.Button(root, text="Controls", font=("Arial", 20), command=show_controls)
    canvas.create_window(WIDTH // 2, HEIGHT // 2 + 90, window=controls_button)

    customize_button = tk.Button(root, text="Customize Controls", font=("Arial", 20), command=customize_controls)
    canvas.create_window(WIDTH // 2, HEIGHT // 2 + 160, window=customize_button)

def play_game():
    global in_game
    clear_screen()
    global background_image,bird,score_text
    canvas.create_image(0, 0, image=background_image, anchor="nw")
    score_text = canvas.create_text(WIDTH - 60, 30, text=f"Score: {score}", font=('Arial', 20), fill="white", tags="game")
    bird = canvas.create_image(bird_x, bird_y, image=bird_image_tk, anchor="center", tags="game")
    in_game=True
    spawn_pipe()
    move()
def customize_controls():
    """A screen where users can customize controls."""
    clear_screen()

    canvas.create_text(
        WIDTH // 2, HEIGHT // 6,
        text="Customize Controls",
        font=("Arial", 30), fill="white", tags="controls"
    )

    canvas.create_text(
        WIDTH // 2, HEIGHT // 4,
        text="Click an action below, then press a key to rebind.",
        font=("Arial", 20), fill="white", tags="controls"
    )

    # Display buttons for each action
    for i, (action, current_key) in enumerate(key_bindings.items()):
        button = tk.Button(
            root,
            text=f"{action.capitalize()} (Current: {current_key})",
            font=("Arial", 16),
            command=lambda act=action: wait_for_keypress(act)
        )
        canvas.create_window(WIDTH // 2, HEIGHT // 3 + i * 50, window=button)

    # Add a "Back to Menu" button
    back_button = tk.Button(root, text="Back", font=("Arial", 20), command=main_menu)
    canvas.create_window(WIDTH // 2, HEIGHT - 100, window=back_button)


def wait_for_keypress(action):
    global key_bindings
    """Wait for a keypress to rebind a specific action."""
    if not game_over:
        
        canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 200,
            text=f"Press a new key for {action.capitalize()}...",
            font=("Arial", 20), fill="yellow", tags="controls"
        )

        def on_key_press(event):
            # Update the binding for the action
            key_bindings[action] = event.keysym
            old_key = key_bindings[action]
            root.unbind(old_key)
            # Apply new bindings
            rebind_keys()
            # Refresh the customization screen
            customize_controls()

        # Bind key press to get the new key
        root.bind("<Key>", on_key_press)
def rebind_keys():
    global key_bindings
    """Rebind keys based on the key_bindings dictionary."""
    if not game_over:
    # Unbind all current keys
        for action, key in key_bindings.items():
            root.unbind(key)

        # Bind keys from the updated dictionary
        root.bind(key_bindings["jump"], jump)
        root.bind(key_bindings["pause"], toggle_pause)
        root.bind(key_bindings["collision_toggle"], no_collision)
        root.bind(key_bindings["pipe_gap_toggle"], pipe_on)
        root.bind(key_bindings["score_booster"], score_booster)
        root.bind(key_bindings["boss_key"], boss_key)

def clear_screen():
    """Clear all elements from the canvas."""
    canvas.delete("all")
    # canvas.itemconfigure("game", state="hidden")
def display_leaderboard():
    """Display the leaderboard on a new canvas."""
    clear_screen()

    canvas.create_text(WIDTH // 2, HEIGHT // 6, text="Leaderboard", font=("Arial", 40), fill="white", tags="leaderboard")

    try:
        with open(LEADERBOARD_FILE, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    # Display the top 10 scores
    for i, line in enumerate(lines[:10]):  # Limit to top 10 scores
        canvas.create_text(WIDTH // 2, HEIGHT // 4 + i * 30, text=line.strip(), font=("Arial", 20), fill="white", tags="leaderboard")

    # Back to main menu button
    back_button = tk.Button(root, text="Back", font=("Arial", 20), command=main_menu)
    canvas.create_window(WIDTH // 2, HEIGHT - 100, window=back_button)
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
def sort_leaderboard():
    global LEADERBOARD_FILE
    """Sort the leaderboard and save it back to the file."""
    with open(LEADERBOARD_FILE, 'r') as f:
        lines = f.readlines()
    # Parse and sort the scores
    scores = []
    for line in lines:
        try:
            name, score = line.strip().split(":")
            scores.append((name, int(score)))
        except ValueError:
            continue  # Skip invalid lines
    
    scores.sort(key=lambda x: x[1], reverse=True)  # Sort by score (descending)

    # Write sorted scores back to the file
    with open(LEADERBOARD_FILE, 'w') as f:
        for name, score in scores:
            f.write(f"{name}: {score}\n")

def jump(event):
    global bird_speed_y, jump_strength
    bird_speed_y = jump_strength

def toggle_pause(event):
    global is_paused
    if game_over==False and in_game:
        is_paused = not is_paused
        if is_paused:
            canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Paused", font=('Arial', 20), fill="white", tags="pause")
        else:
            canvas.delete("pause")

def no_collision(event):
    global bypass_collision, game_over
    if not game_over and in_game:
        bypass_collision = not bypass_collision

def pipe_on(event):
    global pipe_gap_mode, game_over
    if not game_over and in_game:
        pipe_gap_mode = not pipe_gap_mode

def score_booster(event):
    global score, game_over
    if not game_over and in_game:
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
    global is_paused, pipe_gap_mode, spawn_id
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
    if not game_over:
        spawn_id = root.after(delay, spawn_pipe)
    else:
        if spawn_id is not None:
            root.after_cancel(spawn_id)
    # spawn_id=root.after(delay, spawn_pipe)
    if game_over:
        root.after_cancel(spawn_id)
def save_score(player_name, player_score):
    """Save the player's score to the leaderboard."""
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as f:
            pass  # Create the file if it doesn't exist
    
    with open(LEADERBOARD_FILE, 'a') as f:
        f.write(f"{player_name}: {player_score}\n")
    
    sort_leaderboard()
def move():
    # print("in move")
    global bird_y, bird_speed_y, score, game_over, is_paused, bypass_collision, pipe_speed, slow_motion_toggle, gravity, jump_strength, move_id
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
            handle_game_over()
            return
    move_id=root.after(15, move)

def handle_game_over():
    """Handles game-over state and prompts for player name."""
    global score, game_over, move_id, bird_y, bird_speed_y, spawn_id
    #ending the root.after calls, for next game to begin properly
    if move_id is not None:
        root.after_cancel(move_id)
        move_id = None
    
    if spawn_id is not None:
        root.after_cancel(spawn_id)
        spawn_id = None
    
    #resetting game variables
    bird_y = HEIGHT // 2
    bird_speed_y = 0
    
    # Display Game Over message and player's score
    canvas.create_text(WIDTH // 2, HEIGHT // 2 - 50, text="Game Over", font=('Arial', 30), fill="red", tags="game")
    canvas.create_text(WIDTH // 2, HEIGHT // 2, text=f"Your Score: {score}", font=('Arial', 20), fill="white", tags="game")

    root.unbind("<Key>")
    # Create an entry widget for player name
    name_entry = tk.Entry(root, font=("Arial", 20))
    canvas.create_window(WIDTH // 2, HEIGHT // 2 + 50, window=name_entry)

    # Add a save button
    save_button = tk.Button(root, text="Save", font=("Arial", 20),  command=lambda: save_and_exit(name_entry.get()))
    canvas.create_window(WIDTH // 2, HEIGHT // 2 + 100, window=save_button)
    
def save_and_exit(player_name):

    """Saves the player's score and returns to the main menu."""
    global score, game_over, pipes, in_game
    if not player_name.strip():
        player_name = "Unknown"  # Default name if none provided

    save_score(player_name, score)

    #resetting the game variables
    game_over = False
    score=0
    in_game=False
    for top_pipe, bottom_pipe in pipes:
        canvas.delete(top_pipe)
        canvas.delete(bottom_pipe)
    pipes.clear()
    bind_keys()
    main_menu()  # Return to main menu

def bind_keys():
    """Bind all game-related keys."""
    root.bind("<space>", jump)
    root.bind("p", toggle_pause)
    root.bind("c", no_collision)
    root.bind("g", pipe_on)
    root.bind("b", score_booster)
    root.bind("<Escape>", boss_key)


# Key bindings
root.bind("<space>", jump)
root.bind("p", toggle_pause)
root.bind("c", no_collision)
root.bind("g", pipe_on)
root.bind("b", score_booster)
root.bind("<Escape>", boss_key)
main_menu()
# Start game functions
root.mainloop()
