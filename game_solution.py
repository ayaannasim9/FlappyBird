#importing required packages
import tkinter as tk
import random
from PIL import Image, ImageTk
import os
import json

root = tk.Tk()
root.title("Flappy Bird")

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

#variables to check if the user is in a game session
game_over = False
in_game=False
is_paused = False

# Load the bird image
bird_image = Image.open("bird3.png").resize((50,50), Image.LANCZOS)
bird_image_tk=ImageTk.PhotoImage(bird_image)

#bird dimensions adjusted for collision mechanics
bird_width = bird_image_tk.width()-19.3
bird_height = bird_image_tk.height()-19.3

# Pipe settings
pipe_width = 70
pipe_speed = 18
pipes = []
delay=1750
one_time_delay=None

# Load pipe image
pipe_image = Image.open("pipe3.png").resize((70, HEIGHT), Image.LANCZOS) # Open pipe3.png image
pipe_image_tk = ImageTk.PhotoImage(pipe_image)  # Convert to Tkinter PhotoImage format

# Score count
score = 0

# Cheat codes
bypass_collision = False
pipe_gap_mode = False

# Boss key
boss_image = Image.open("spreadsheet.png").resize((WIDTH,HEIGHT), Image.LANCZOS)
boss_image_final=ImageTk.PhotoImage(boss_image)
boss_image_displayed = False

#Leaderboard file
LEADERBOARD_FILE="leaderboard.txt"
SAVE_FOLDER = "saves"
os.makedirs(SAVE_FOLDER, exist_ok=True)

#IDs to stop calling functions when required
move_id=None
spawn_id=None

def clear_screen():
    """Clear all elements from the canvas."""
    canvas.delete("all")

#main menu and function to invoke start of game
def main_menu():
    """Displays main menu"""
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

    load_button = tk.Button(root, text="Load Game", font=("Arial", 20), command=load_game)
    canvas.create_window(WIDTH // 2, HEIGHT // 2 - 120, window=load_button)

def play_game():
    """Starts the game"""
    global in_game
    clear_screen()
    global background_image,bird,score_text
    canvas.create_image(0, 0, image=background_image, anchor="nw")
    score_text = canvas.create_text(WIDTH - 60, 30, text=f"Score: {score}", font=('Arial', 20), fill="white", tags="game")
    bird = canvas.create_image(bird_x, bird_y, image=bird_image_tk, anchor="center", tags="game")
    in_game=True
    spawn_pipe()
    move()

#remap keys and show keys
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
            old_key = key_bindings[action]
            key_bindings[action] = event.keysym
            
            root.unbind(f"<{old_key}>")
            # Apply new bindings
            rebind_keys()
            # Refresh the customization screen
            customize_controls()
            root.unbind("<Key>")

        # Bind key press to get the new key
        root.bind("<Key>", on_key_press)

def rebind_keys():
    global key_bindings
    """Rebind keys based on the key_bindings dictionary."""
    if not game_over:
    # Unbind all current keys
        for action, key in key_bindings.items():
            root.unbind(f"<{key}>")

        root.bind(f"<{key_bindings['jump']}>", jump)
        root.bind(f"<{key_bindings['pause']}>", toggle_pause)
        root.bind(f"<{key_bindings['collision_toggle']}>", no_collision)
        root.bind(f"<{key_bindings['pipe_gap_toggle']}>", pipe_on)
        root.bind(f"<{key_bindings['score_booster']}>", score_booster)
        root.bind(f"<{key_bindings['boss_key']}>", boss_key)

def show_controls():
    """Display the controls screen."""
    clear_screen()
    canvas.create_text(WIDTH // 2, HEIGHT // 6, text="Controls", font=("Arial", 40), fill="white", tags="controls")
    # Display updated key bindings
    controls_info = [
        f"Jump: {key_bindings['jump']}",
        f"Pause/Resume: {key_bindings['pause']}",
        f"Toggle Collision Bypass: {key_bindings['collision_toggle']}",
        f"Toggle Pipe Gap Mode: {key_bindings['pipe_gap_toggle']}",
        f"Score Booster: {key_bindings['score_booster']}",
        f"Boss Key: {key_bindings['boss_key']}"
    ]

    for i, line in enumerate(controls_info):
        canvas.create_text(WIDTH // 2, HEIGHT // 3 + i * 30, text=line, font=("Arial", 20), fill="white", tags="controls")

    # Back to main menu button
    back_button = tk.Button(root, text="Back", font=("Arial", 20), command=main_menu)
    canvas.create_window(WIDTH // 2, HEIGHT - 100, window=back_button)

#display and sort leaderboard
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

#boss key
def boss_key(event):
    """Displays a spreadsheet image"""
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

#jump
def jump(event):
    """Triggers the bird to jump"""
    global bird_speed_y, jump_strength
    if not game_over and in_game: #preventing jump when not in a game session
        bird_speed_y = jump_strength

#pause
def toggle_pause(event):
    """Pauses/Resumes the game"""
    global is_paused
    if game_over==False and in_game:
        is_paused = not is_paused
        if is_paused:
            canvas.create_text(WIDTH // 2, HEIGHT // 2, text="Game Paused", font=('Arial', 20), fill="white", tags="pause")
            save_button = tk.Button(root, text="Save Game", font=("Arial", 20), command=save_game)
            canvas.create_window(WIDTH // 2, HEIGHT // 2 + 50, window=save_button, tags="save_button")
        else:
            canvas.delete("pause")
            canvas.delete("save_button")

#save and load game
def save_game():
    """Save the current game state."""
    if game_over:
        return
     
    def confirm_save():
        """Save the data to the specified file."""
        filename = save_entry.get().strip()
        if not filename:
            filename = "savefile"
        filepath = os.path.join(SAVE_FOLDER, f"{filename}.json")

        if not os.path.exists(SAVE_FOLDER):
            os.makedirs(SAVE_FOLDER)

        save_data = {
            "bird_y": bird_y,
            "bird_speed_y": bird_speed_y,
            "score": score,
            "pipes": [
                {"top": canvas.coords(top), "bottom": canvas.coords(bottom)}
                for top, bottom in pipes
            ],
            "is_paused": is_paused,
            "pipe_speed": pipe_speed,
            "bypass_collision": bypass_collision,
            "pipe_gap_mode": pipe_gap_mode
        }

        with open(filepath, "w") as f:
            json.dump(save_data, f)
        canvas.delete("save_prompt")
        canvas.delete("save_button")
        canvas.delete("save_entry")

    # Prompt for save file name
    canvas.create_text(WIDTH // 2, HEIGHT // 2 - 100, text="Enter Save File Name:", font=("Arial", 20), fill="white", tags="save_prompt")
    save_entry = tk.Entry(root, font=("Arial", 20))
    canvas.create_window(WIDTH // 2, HEIGHT // 2 - 50, window=save_entry, tags="save_entry")
    save_button = tk.Button(root, text="Save", font=("Arial", 20), command=confirm_save)
    canvas.create_window(WIDTH // 2, HEIGHT // 2, window=save_button, tags="save_button")

def load_game():
    """Display the load game menu."""
    clear_screen()
    canvas.create_text(WIDTH // 2, HEIGHT // 6, text="Load Game", font=("Arial", 40), fill="white", tags="load_menu")
    
    # List saved files
    save_files = [f for f in os.listdir(SAVE_FOLDER) if f.endswith(".json")]
    if not save_files:
        canvas.create_text(WIDTH // 2, HEIGHT // 2, text="No saved files found!", font=("Arial", 20), fill="white", tags="load_menu")
        back_button = tk.Button(root, text="Back", font=("Arial", 20), command=main_menu)
        canvas.create_window(WIDTH // 2, HEIGHT - 100, window=back_button)
        return

    def load_selected(file):
        filepath = os.path.join(SAVE_FOLDER, file)
        with open(filepath, "r") as f:
            save_data = json.load(f)

        global bird_y, bird_speed_y, score, pipes, is_paused, pipe_speed, bypass_collision,pipe_gap_mode,in_game,one_time_delay
        bird_y = save_data["bird_y"]
        bird_speed_y = save_data["bird_speed_y"]
        score = save_data["score"]
        is_paused = save_data["is_paused"]
        pipe_speed = save_data["pipe_speed"]
        bypass_collision=save_data["bypass_collision"]
        pipe_gap_mode=save_data["pipe_gap_mode"]
        
        # Restore pipes
        for top_pipe, bottom_pipe in pipes:
            canvas.delete(top_pipe)
            canvas.delete(bottom_pipe)
        pipes.clear()
        clear_screen()
        global background_image,bird,score_text
        canvas.create_image(0, 0, image=background_image, anchor="nw")
        score_text = canvas.create_text(WIDTH - 60, 30, text=f"Score: {score}", font=('Arial', 20), fill="white", tags="game")
        bird = canvas.create_image(bird_x, bird_y, image=bird_image_tk, anchor="center", tags="game")
        for pipe in save_data["pipes"]:
            top_coords = pipe["top"]
            bottom_coords = pipe["bottom"]
            top_pipe = canvas.create_image(top_coords[0], top_coords[1], image=pipe_image_tk, anchor="s", tags="game")
            bottom_pipe = canvas.create_image(bottom_coords[0], bottom_coords[1], image=pipe_image_tk, anchor="n", tags="game")
            pipes.append((top_pipe, bottom_pipe))
        in_game=True
        one_time_delay=root.after(2750,spawn_pipe)
        move()

    for i, file in enumerate(save_files):
        button = tk.Button(root, text=file, font=("Arial", 16), command=lambda f=file: load_selected(f))
        canvas.create_window(WIDTH // 2, HEIGHT // 3 + i * 50, window=button, tags="load_menu")

    # Back to menu button
    back_button = tk.Button(root, text="Back", font=("Arial", 20), command=main_menu)
    canvas.create_window(WIDTH // 2, HEIGHT - 100, window=back_button)

#cheat codes
def no_collision(event):
    """Toggles no collision mode on"""
    global bypass_collision, game_over
    if not game_over and in_game:
        bypass_collision = not bypass_collision

def pipe_on(event):
    """Toggles pipe gap mode on(increases the pipe gap by a lot)"""
    global pipe_gap_mode, game_over
    if not game_over and in_game:
        pipe_gap_mode = not pipe_gap_mode

def score_booster(event):
    """boosts the score by 5 during game"""
    global score, game_over
    if not game_over and in_game:
        score += 5
        canvas.itemconfig(score_text, text=f"Score: {score}")

#difficulty adjustment and main game
def difficulty():
    """Adjusts difficulty, as the player's score increases"""
    global pipe_speed, score, delay
    if score<=5:
        pipe_speed=18
    elif score <=10:
        pipe_speed=22
        delay=1500
    elif score<=15:
        pipe_speed=25
        delay=1350
    else:
        pipe_speed=30
        delay=1200

def spawn_pipe():
    """Spawn pipes after a certain amount of delay"""
    global is_paused, pipe_gap_mode, spawn_id, pipes, delay, one_time_delay
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
    if not game_over:
        spawn_id = root.after(delay, spawn_pipe)
        if one_time_delay is not None:
            root.after_cancel(one_time_delay)
    else:
        if spawn_id is not None:
            root.after_cancel(spawn_id)
    # spawn_id=root.after(delay, spawn_pipe)
    if game_over:
        root.after_cancel(spawn_id)

def move():
    """Main function, which applies gravity to the bird, and makes the pipes move, and checks if collision has happened"""
    global bird_y, bird_speed_y, score, game_over, is_paused, bypass_collision, pipe_speed, gravity, jump_strength, move_id, pipes
    if score%5==0:
        difficulty()

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
            if not bypass_collision: #skips if bypass collision mode is on
                if ((bird_x2 > top_coords[0] - pipe_width // 2 and bird_x1 < top_coords[0] + pipe_width // 2) and
                        (bird_y1 < top_coords[1] or bird_y2 > bottom_coords[1])):
                    game_over = True

        if game_over:
            handle_game_over()
            return
    move_id=root.after(15, move)

#game over and save score and name
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
    
def save_score(player_name, player_score):
    """Save the player's score to the leaderboard."""
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as f:
            pass  # Create the file if it doesn't exist
    
    with open(LEADERBOARD_FILE, 'a') as f:
        f.write(f"{player_name}: {player_score}\n")
    
    sort_leaderboard()

def save_and_exit(player_name):

    """Saves the player's score and returns to the main menu."""
    global score, game_over, pipes, in_game, pipe_speed
    if not player_name.strip():
        player_name = "Unknown"  # Default name if none provided

    save_score(player_name, score)

    #resetting the game variables
    game_over = False
    score=0
    in_game=False
    pipe_speed=18
    for top_pipe, bottom_pipe in pipes:
        canvas.delete(top_pipe)
        canvas.delete(bottom_pipe)
    pipes.clear()
    main_menu()  # Return to main menu

# Key bindings
root.bind("<space>", jump)
root.bind("p", toggle_pause)
root.bind("c", no_collision)
root.bind("g", pipe_on)
root.bind("b", score_booster)
root.bind("<Escape>", boss_key)

# Start game functions
main_menu()
root.mainloop()
