import pygame, sys, random, math

# Initialize Pygame and its mixer for music
pygame.init()
pygame.mixer.init()

# Screen dimensions and setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Our Love Story Animation")
clock = pygame.time.Clock()

# Global variables for scene control and extra features
current_scene = 0
fade_value = 0  # Alpha value (0 to 255)
fading_in = True
scene_hold_time = 3000  # Milliseconds to hold scene when fully visible
scene_start_time = pygame.time.get_ticks()

# Typewriter effect variables
displayed_text = ""
typewriter_index = 0
typewriter_delay = 50  # Milliseconds delay between each character
last_char_time = pygame.time.get_ticks()

# Zoom effect variable
zoom_offset = 0.0  # Additional scale factor; increases over time when scene is fully visible

# Confetti effect variables (auto-triggered on final scene)
confetti_active = False
confetti_start_time = 0
confetti_duration = 2000  # Duration in ms for confetti
confetti_particles = []

# List of nine scenes with image file paths and text messages
scenes = [
    {"image": "image1.jpeg", "text": "Our Journey Begins\nThe day we met..."},
    {"image": "image3.jpeg", "text": "The First Date\nA magical evening together"},
    {"image": "image4.jpeg", "text": "Moments of Laughter\nEvery smile shared"},
    {"image": "image10.jpg", "text": "Adventures Together\nExploring new horizons"},
    {"image": "image10.jpg", "text": "Shared Secrets\nTrust and understanding"},
    {"image": "image10.jpg", "text": "Dreams & Hopes\nBuilding our future"},
    {"image": "image10.jpg", "text": "Overcoming Challenges\nStronger together"},
    {"image": "image10.jpg", "text": "Cherished Moments\nTime stands still"},
    {"image": "image10.jpg", "text": "Forever Us\nI Love You Always"},
    {"image": "image10.jpg", "text": "Forever Us\nI Love You Always"}
]

# Preload images and scale them to fit the window
loaded_scenes = []
for scene in scenes:
    try:
        img = pygame.image.load(scene["image"]).convert_alpha()
    except Exception as e:
        print(f"Error loading {scene['image']}: {e}")
        sys.exit(1)
    img = pygame.transform.scale(img, (WIDTH, HEIGHT))
    loaded_scenes.append({"image": img, "text": scene["text"]})

# Load background music (ensure the file exists or comment these lines if not needed)
try:
    pygame.mixer.music.load("background.mp3")
    pygame.mixer.music.play(-1)  # Loop indefinitely
except Exception as e:
    print("Music file not found or error loading music:", e)


# Particle class for background floating dots
class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed_y = random.uniform(-0.5, -2)
        self.size = random.randint(2, 5)
        self.alpha = random.randint(50, 255)

    def update(self):
        self.y += self.speed_y
        self.alpha -= 1
        if self.alpha <= 0 or self.y < 0:
            self.reset()
            self.y = HEIGHT + random.randint(0, 50)

    def draw(self, surface):
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, self.alpha), (self.size, self.size), self.size)
        surface.blit(s, (self.x, self.y))


particles = [Particle() for _ in range(50)]


# Confetti particle class
class Confetti:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-50, 0)
        self.speed_y = random.uniform(2, 5)
        self.speed_x = random.uniform(-2, 2)
        self.size = random.randint(3, 7)
        self.color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)])

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))


def draw_progress_bar():
    """Draw a progress bar at the bottom of the screen when the scene is fully visible."""
    if fade_value == 255:
        elapsed = pygame.time.get_ticks() - scene_start_time
        progress = min(elapsed / scene_hold_time, 1.0)
        bar_width = 200
        bar_height = 10
        x = (WIDTH - bar_width) // 2
        y = HEIGHT - 40
        pygame.draw.rect(screen, (255, 255, 255, 100), (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width * progress, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)


def draw_pulsing_overlay():
    """Draw a pulsating 'I Love You' message at the center."""
    pulse = 1 + 0.1 * math.sin(pygame.time.get_ticks() / 300)
    font_size = int(60 * pulse)
    font = pygame.font.SysFont("Arial", font_size, bold=True)
    text_surface = font.render("I Love You", True, (255, 20, 147))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)


def draw_confetti():
    """Draw and update confetti particles if active."""
    global confetti_particles
    for c in confetti_particles:
        c.update()
        c.draw(screen)


def reset_scene(new_scene_index):
    """Reset scene-specific variables when switching scenes."""
    global current_scene, fade_value, fading_in, scene_start_time, displayed_text, typewriter_index, last_char_time, zoom_offset, confetti_active
    current_scene = new_scene_index
    fade_value = 0
    fading_in = True
    scene_start_time = pygame.time.get_ticks()
    displayed_text = ""
    typewriter_index = 0
    last_char_time = pygame.time.get_ticks()
    zoom_offset = 0.0
    # Automatically trigger confetti on the final scene (index 8) once fully visible
    if current_scene == len(loaded_scenes) - 1:
        confetti_active = True
        confetti_start_time = pygame.time.get_ticks()


# Main loop (with only QUIT event handling)
running = True
while running:
    dt = clock.tick(60)  # Limit to 60 FPS

    # Process only QUIT events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update background particles
    for p in particles:
        p.update()

    # Fill background
    screen.fill((0, 0, 0))
    for p in particles:
        p.draw(screen)

    # If confetti is active, update and draw it
    if confetti_active:
        draw_confetti()
        if pygame.time.get_ticks() - confetti_start_time > confetti_duration:
            confetti_active = False

    # Get current scene data
    scene = loaded_scenes[current_scene]

    # Auto scene progression logic (fade in and fade out)
    if fading_in:
        fade_value += 5
        if fade_value >= 255:
            fade_value = 255
            # When fully visible, hold the scene then start fade out
            if pygame.time.get_ticks() - scene_start_time > scene_hold_time:
                fading_in = False
        zoom_offset = 0.0  # No zoom while fading in
    else:
        fade_value -= 5
        if fade_value <= 0:
            fade_value = 0
            # Automatically advance to the next scene
            reset_scene((current_scene + 1) % len(loaded_scenes))

    # Increase zoom offset when scene is fully visible
    if fade_value == 255:
        zoom_offset += 0.0005 * dt  # Adjust zoom speed as desired

    # Draw the scene image with fade and zoom effect
    new_width = int(WIDTH * (1 + zoom_offset))
    new_height = int(HEIGHT * (1 + zoom_offset))
    zoomed_img = pygame.transform.scale(scene["image"], (new_width, new_height))
    zoom_rect = zoomed_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    temp_img = zoomed_img.copy()
    temp_img.set_alpha(fade_value)
    screen.blit(temp_img, zoom_rect)

    # Typewriter effect: reveal one character at a time when scene is fully visible
    if fade_value == 255 and typewriter_index < len(scene["text"]):
        if pygame.time.get_ticks() - last_char_time > typewriter_delay:
            displayed_text += scene["text"][typewriter_index]
            typewriter_index += 1
            last_char_time = pygame.time.get_ticks()

    # Render the typewritten text (supports multiple lines)
    font = pygame.font.SysFont("Arial", 32)
    lines = displayed_text.split("\n")
    y_offset = HEIGHT - 100
    for line in lines:
        text_surface = font.render(line, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, y_offset))
        screen.blit(text_surface, text_rect)
        y_offset += 40

    # Draw the progress bar if scene is fully visible
    if fade_value == 255:
        draw_progress_bar()

    # Draw the pulsing "I Love You" overlay
    draw_pulsing_overlay()

    pygame.display.flip()

pygame.quit()
sys.exit()
