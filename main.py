import asyncio
import base64
import sys
import time
import pygame
from random import randint

# pygbag runs the game in the browser, where sys.platform is "emscripten".
WEB = sys.platform == "emscripten"
if WEB:
       import platform # pygbag's version, gives access to the browser

WIDTH = 700
MIN_HEIGHT, MAX_HEIGHT = 1000, 1700 # from a wide screen to a very tall phone
if WEB:
       # Match the shape of the player's screen, so the game fills phones of any size.
       # Wider screens (tablets, computers) get the 1000 px layout with bars at the sides.
       screen_shape = float(platform.window.innerHeight) / float(platform.window.innerWidth)
       HEIGHT = int(min(max(WIDTH * screen_shape, MIN_HEIGHT), MAX_HEIGHT))
else:
       HEIGHT = 1522 # same shape as an iPhone 16 Pro screen (402 x 874 points)
BASE_HEIGHT = 83
GROUND_Y = HEIGHT - BASE_HEIGHT # where the ground starts
# The game was first made 1000 px tall, with the ground at 917. Everything placed for that
# size moves down by SHIFT, so it sits in the middle of the taller screen.
SHIFT = (GROUND_Y - 917) // 2

GREEN = (0, 200, 0) # RGB colour
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

pygame.init()
if WEB:
       screen = pygame.display.set_mode((WIDTH, HEIGHT)) # the browser scales it to fit the page
       window = screen
else:
       # A 1522 px tall window does not fit most computer screens. The game is drawn on
       # "screen" at full size, then shown smaller in a window that fits.
       window_height = int(pygame.display.get_desktop_sizes()[0][1] * 0.85)
       window = pygame.display.set_mode((window_height * WIDTH // HEIGHT, window_height))
       screen = pygame.Surface((WIDTH, HEIGHT)).convert()

def show_frame():
       if window is not screen:
              pygame.transform.smoothscale(screen, window.get_size(), window)
       pygame.display.flip()

# Mouse positions are in window pixels; this turns them into game pixels.
def to_game_pos(pos):
       return (pos[0] * WIDTH // window.get_width(), pos[1] * HEIGHT // window.get_height())
pygame.display.set_caption('FlappyPie')
running = True 
clock = pygame.time.Clock()
MAX_STEP = 3 # the bird never jumps further than 3 frames, even after the page pauses

TUBE_VELOCITY = 4.46
TUBE_WIDTH = 88
TUBE_GAP = 250

tube1_x = 900
tube2_x = 1250
tube3_x = 1600

# Top of each gap between pipes. The range is as wide as before, so the game is just as hard.
GAP_TOP_MIN = 167 + SHIFT
GAP_TOP_MAX = 584 + SHIFT
tube1_height = randint(GAP_TOP_MIN, GAP_TOP_MAX)
tube2_height = randint(GAP_TOP_MIN, GAP_TOP_MAX)
tube3_height = randint(GAP_TOP_MIN, GAP_TOP_MAX)  

BIRD_X = 88
BIRD_START_Y = 667 + SHIFT
bird_y = BIRD_START_Y
BIRD_WIDTH = 55
BIRD_HEIGHT = 39 

bird_drop_velocity = 0
GRAVITY = 0.6

score = 0

# Load the saved high score. The file does not exist the first time the game runs.
HIGH_SCORE_FILE = "highscore.txt"

# Files do not survive a page reload in the browser, so the web version uses localStorage.
def load_high_score():
       try:
              if WEB:
                     return int(platform.window.localStorage.getItem(HIGH_SCORE_FILE))
              with open(HIGH_SCORE_FILE) as file:
                     return int(file.read())
       except (FileNotFoundError, ValueError, TypeError):
              return 0

def save_high_score(value):
       if WEB:
              platform.window.localStorage.setItem(HIGH_SCORE_FILE, str(value))
       else:
              with open(HIGH_SCORE_FILE, "w") as file:
                     file.write(str(value))

high_score = load_high_score()

tube1_pass = False
tube2_pass = False
tube3_pass = False

pausing = False

# convert() / convert_alpha() match the image to the screen format, which makes drawing much faster.
# Scale the background to the screen height without stretching it, so it ends up wider than the screen.
backgroud_image = pygame.image.load("sprites/background.png").convert()
BACKGROUND_WIDTH = backgroud_image.get_width() * HEIGHT // backgroud_image.get_height()
backgroud_image = pygame.transform.scale(backgroud_image, (BACKGROUND_WIDTH, HEIGHT))
background_night_image = pygame.image.load("sprites/background-night.png").convert()
background_night_image = pygame.transform.scale(background_night_image, (BACKGROUND_WIDTH, HEIGHT))
BACKGROUND_SPEED = 1 # slower than the pipes, so the background looks far away
background_x = 0

base_image = pygame.image.load("sprites/base.png").convert()
base_image = pygame.transform.scale(base_image, (WIDTH, BASE_HEIGHT))

# Yellow bird animation: load 3 images into a list, then pick one to draw each frame.
BIRD_ANIMATION_SPEED = 6 # change image every 6 game frames (60 FPS -> 10 images per second)
MAIN_BIRD_RECT = pygame.Rect(310, 477 + SHIFT, 80, 56) # larger bird shown on the main screen

# bird_skins holds one animation (a list of images) per colour.
# bird_skins_large is the same thing, scaled for the main screen.
BIRD_COLORS = ["yellow", "red", "blue"]
bird_skins = []
bird_skins_large = []
for color in BIRD_COLORS:
       bird_images = []
       bird_images_large = []
       for wing_position in ["upflap", "midflap", "downflap"]:
              bird_image = pygame.image.load("sprites/" + color + "bird-" + wing_position + ".png").convert_alpha()
              bird_images.append(pygame.transform.scale(bird_image, (BIRD_WIDTH, BIRD_HEIGHT)))
              bird_images_large.append(pygame.transform.scale(bird_image, MAIN_BIRD_RECT.size))
       # Add midflap again so the order is up -> mid -> down -> mid, keeping the wing motion smooth when it loops.
       bird_images.append(bird_images[1])
       bird_images_large.append(bird_images_large[1])
       bird_skins.append(bird_images)
       bird_skins_large.append(bird_images_large)
bird_frame_count = 0 # counts elapsed frames, used to work out which image to draw
current_bird = 0 # index in BIRD_COLORS of the bird the player picked

# arrow buttons to change the bird on the main screen
arrow_left_rect = pygame.Rect(240, 477 + SHIFT, 48, 56)
arrow_right_rect = pygame.Rect(412, 477 + SHIFT, 48, 56)
arrow_left_image = pygame.image.load("sprites/button/arrow_left.png").convert_alpha()
arrow_right_image = pygame.image.load("sprites/button/arrow_right.png").convert_alpha()

# The pipes must be long enough to reach the top of the screen and the ground from any gap.
# Stretching the whole image would make the pipe's opening too tall, so the image is drawn at
# its usual size and its last row (plain pipe body) is repeated to make it longer.
PIPE_IMAGE_HEIGHT = 667
PIPE_HEIGHT = GROUND_Y
def load_pipe(path):
       image = pygame.image.load(path).convert_alpha()
       image = pygame.transform.scale(image, (TUBE_WIDTH, PIPE_IMAGE_HEIGHT))
       pipe = pygame.Surface((TUBE_WIDTH, PIPE_HEIGHT), pygame.SRCALPHA)
       pipe.blit(image, (0, 0))
       body_row = image.subsurface((0, PIPE_IMAGE_HEIGHT - 1, TUBE_WIDTH, 1))
       pipe.blit(pygame.transform.scale(body_row, (TUBE_WIDTH, PIPE_HEIGHT - PIPE_IMAGE_HEIGHT)), (0, PIPE_IMAGE_HEIGHT))
       return pipe

pipe_image = load_pipe("sprites/pipe-green.png")
pipe_image_top = pygame.transform.flip(pipe_image, False, True)
pipe_red_image = load_pipe("sprites/pipe-red.png")
pipe_red_image_top = pygame.transform.flip(pipe_red_image, False, True)

messgage_main = pygame.image.load("sprites/message-nobird.png").convert_alpha() # message.png without the grey bird
messgage_main = pygame.transform.scale(messgage_main, (420, 500))

gameover_txt = pygame.image.load("sprites/gameover.png").convert_alpha()
gameover_txt = pygame.transform.scale(gameover_txt, (350, 100))
scoreboard_image = pygame.image.load("sprites/scoreboard.png").convert_alpha()

# Black layer drawn over the game at game over. Alpha: 0 = no change, 255 = fully black.
DARK_OVERLAY_ALPHA = 130
dark_overlay = pygame.Surface((WIDTH, HEIGHT)).convert() # black by default
dark_overlay.set_alpha(DARK_OVERLAY_ALPHA)
show_message = True

# sound effect
point_sound = pygame.mixer.Sound("audio/point.ogg")
point_sound = pygame.mixer.Sound(buffer=point_sound.get_raw()[22048:])
wing_sound = pygame.mixer.Sound("audio/wing.ogg")
swoosh_sound = pygame.mixer.Sound("audio/swoosh.ogg")
die_sound = pygame.mixer.Sound("audio/die.ogg")
hit_sound = pygame.mixer.Sound("audio/hit.ogg")
change_bird_sound = pygame.mixer.Sound("audio/changeBird.ogg")
SOUND_VOLUME = 0.3 # 0.0 -> 1.0
all_sounds = [point_sound, wing_sound, swoosh_sound, die_sound, hit_sound, change_bird_sound]

# In the browser, pygame mixes sound on the same thread as the game, so any busy moment
# makes it crackle. The browser's own audio system plays on a separate thread, so pygame
# only decodes the sounds here and the browser plays them.
WEB_AUDIO_SCRIPT = """
window.gameAudio = {
       ctx: new (window.AudioContext || window.webkitAudioContext)(),
       buffers: [],
       load(base64Text, rate) {
              const bytes = Uint8Array.from(atob(base64Text), (ch) => ch.charCodeAt(0));
              const samples = new Int16Array(bytes.buffer);
              const frames = samples.length / 2;
              const buffer = this.ctx.createBuffer(2, frames, rate);
              for (let channel = 0; channel < 2; channel++) {
                     const data = buffer.getChannelData(channel);
                     for (let i = 0; i < frames; i++) {
                            data[i] = samples[i * 2 + channel] / 32768;
                     }
              }
              this.buffers.push(buffer);
       },
       play(index, volume) {
              const source = this.ctx.createBufferSource();
              const gain = this.ctx.createGain();
              source.buffer = this.buffers[index];
              gain.gain.value = volume;
              source.connect(gain).connect(this.ctx.destination);
              source.start();
       },
};
// Browsers keep audio paused until the player touches the page.
for (const type of ["pointerdown", "touchstart", "keydown"]) {
       document.addEventListener(type, () => window.gameAudio.ctx.resume(), true);
}
"""

class WebSound:
       def __init__(self, sound, index, rate):
              self.index = index
              self.volume = 1.0
              base64_text = base64.b64encode(sound.get_raw()).decode()
              platform.window.eval(f"gameAudio.load('{base64_text}', {rate})")

       def set_volume(self, volume):
              self.volume = volume

       def play(self):
              platform.window.eval(f"gameAudio.play({self.index}, {self.volume})")

if WEB:
       platform.window.eval(WEB_AUDIO_SCRIPT)
       rate = pygame.mixer.get_init()[0]
       all_sounds = [WebSound(sound, index, rate) for index, sound in enumerate(all_sounds)]
       point_sound, wing_sound, swoosh_sound, die_sound, hit_sound, change_bird_sound = all_sounds
       pygame.mixer.quit() # pygame's sound is no longer needed

for sound in all_sounds:
       sound.set_volume(SOUND_VOLUME)

# speaker button
sound_on = True
speaker_rect = pygame.Rect(15, 15, 56, 56)
speaker_on_image = pygame.image.load("sprites/button/speaker_on.png").convert_alpha()
speaker_on_image = pygame.transform.smoothscale(speaker_on_image, speaker_rect.size)
speaker_off_image = pygame.image.load("sprites/button/speaker_off.png").convert_alpha()
speaker_off_image = pygame.transform.smoothscale(speaker_off_image, speaker_rect.size)

# theme button
night_mode = False
theme_rect = pygame.Rect(601, 24, 84, 38)
def load_theme_button(path):
       image = pygame.image.load(path).convert_alpha()
       image = image.subsurface(image.get_bounding_rect(min_alpha=128)) # remove transparent border
       return pygame.transform.smoothscale(image, theme_rect.size)

theme_light_image = load_theme_button("sprites/button/LightMode.png")
theme_dark_image = load_theme_button("sprites/button/DarkMode.png")

def toggle_sound():
       global sound_on
       sound_on = not sound_on
       volume = SOUND_VOLUME if sound_on else 0
       for sound in all_sounds:
              sound.set_volume(volume)

DIGIT_WIDTH, DIGIT_HEIGHT = 42, 60
SMALL_DIGIT_WIDTH, SMALL_DIGIT_HEIGHT = 30, 44
digit_images = []
small_digit_images = [] # smaller digits for the score board
for i in range(10):
       digit = pygame.image.load("sprites/number/" + str(i) + ".png").convert_alpha()
       digit_images.append(pygame.transform.scale(digit, (DIGIT_WIDTH, DIGIT_HEIGHT)))
       small_digit_images.append(pygame.transform.scale(digit, (SMALL_DIGIT_WIDTH, SMALL_DIGIT_HEIGHT)))

# Draw a number so that it ends at right_x, which keeps the digits lined up on the right.
def draw_small_number(number, right_x, y):
       number_str = str(number)
       digit_x = right_x - len(number_str) * SMALL_DIGIT_WIDTH
       for ch in number_str:
              screen.blit(small_digit_images[int(ch)], (digit_x, y))
              digit_x += SMALL_DIGIT_WIDTH

# In the browser the game must run inside an async function, so the page can
# update between frames. "global" lets this function change the variables above.
async def main():
       global running, TUBE_VELOCITY, background_x, bird_frame_count, current_bird
       global night_mode, show_message, pausing, score, high_score
       global bird_y, bird_drop_velocity
       global tube1_x, tube2_x, tube3_x
       global tube1_height, tube2_height, tube3_height
       global tube1_pass, tube2_pass, tube3_pass

       swoosh_sound.play() # play once when the game opens on the main screen
       step = 1 # how many 1/60 s passed since the last frame; always 1 on desktop
       last_frame_time = time.perf_counter()
       while running:
              if WEB:
                     # In the browser, "await asyncio.sleep(0)" already waits for the next screen
                     # refresh and clock.tick() would freeze the page. Screens refresh at different
                     # speeds (60 Hz, 165 Hz...), so everything moves by the time that really passed.
                     now = time.perf_counter()
                     step = min((now - last_frame_time) * 60, MAX_STEP)
                     last_frame_time = now
              else:
                     clock.tick(60) # fps
              screen.fill(GREEN) # theme

              # Scrolling background: draw two copies side by side and move them left.
              # When the first copy is fully off screen, jump back to 0. The second copy
              # is then exactly where the first one starts, so the loop is not visible.
              current_background = background_night_image if night_mode else backgroud_image
              screen.blit(current_background, (background_x, 0))
              screen.blit(current_background, (background_x + BACKGROUND_WIDTH, 0))
              if not pausing: # the background stops at game over
                     background_x -= BACKGROUND_SPEED * step
                     if background_x <= -BACKGROUND_WIDTH:
                            background_x = 0

              # draw main 
                     # draw main
              if show_message:
                     screen.blit(messgage_main, (140, 167 + SHIFT))

                     # The bird stays in place and only flaps. The counter must keep going here,
                     # because the "continue" below skips the counter in the game part of the loop.
                     bird_images_large = bird_skins_large[current_bird]
                     screen.blit(bird_images_large[int(bird_frame_count // BIRD_ANIMATION_SPEED) % len(bird_images_large)], MAIN_BIRD_RECT)
                     bird_frame_count += step
                     screen.blit(arrow_left_image, arrow_left_rect)
                     screen.blit(arrow_right_image, arrow_right_rect)

                     screen.blit(speaker_on_image if sound_on else speaker_off_image, speaker_rect)
                     # The theme button is only drawn and clickable in this block, so it only exists on the main screen.
                     screen.blit(theme_dark_image if night_mode else theme_light_image, theme_rect)
                     show_frame()
                     for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                   running = False
                            left_click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                            space_key = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
                            if left_click and speaker_rect.collidepoint(to_game_pos(event.pos)):
                                   toggle_sound()
                            elif left_click and theme_rect.collidepoint(to_game_pos(event.pos)):
                                   night_mode = not night_mode
                            # % wraps around: left of the first bird is the last one, and right of the last is the first.
                            elif left_click and arrow_left_rect.collidepoint(to_game_pos(event.pos)):
                                   current_bird = (current_bird - 1) % len(BIRD_COLORS)
                                   change_bird_sound.play()
                            elif left_click and arrow_right_rect.collidepoint(to_game_pos(event.pos)):
                                   current_bird = (current_bird + 1) % len(BIRD_COLORS)
                                   change_bird_sound.play()
                            elif event.type == pygame.MOUSEBUTTONDOWN or space_key:
                                   show_message = False
                                   bird_drop_velocity = -11.33
                     await asyncio.sleep(0) # give control back to the browser
                     continue
   
              # Choose pipe images by theme: red pipes at night, green pipes during the day.
              current_pipe = pipe_red_image if night_mode else pipe_image
              current_pipe_top = pipe_red_image_top if night_mode else pipe_image_top

              # draw tube
              tube1_rect = screen.blit(current_pipe_top, (tube1_x, tube1_height - PIPE_HEIGHT))
              tube2_rect = screen.blit(current_pipe_top, (tube2_x, tube2_height - PIPE_HEIGHT))
              tube3_rect = screen.blit(current_pipe_top, (tube3_x, tube3_height - PIPE_HEIGHT))

              # draw tube inverse
              tube1_rect_inv = screen.blit(current_pipe, (tube1_x, tube1_height + TUBE_GAP))
              tube2_rect_inv = screen.blit(current_pipe, (tube2_x, tube2_height + TUBE_GAP))
              tube3_rect_inv = screen.blit(current_pipe, (tube3_x, tube3_height + TUBE_GAP))

       
              # move tube to the left
              tube1_x = tube1_x - TUBE_VELOCITY * step
              tube2_x = tube2_x - TUBE_VELOCITY * step
              tube3_x = tube3_x - TUBE_VELOCITY * step

              # draw bird
              # Divide the frame count by the speed to get the current step, then use % to loop through the image list.
              # Example with speed 6: frames 0-5 -> image 0, frames 6-11 -> image 1, ..., frame 24 goes back to image 0.
              bird_images = bird_skins[current_bird]
              bird_image = bird_images[int(bird_frame_count // BIRD_ANIMATION_SPEED) % len(bird_images)]
              bird_rect = screen.blit(bird_image, (BIRD_X, bird_y))
              if not pausing: # the counter stops at game over, so the bird stops flapping
                     bird_frame_count += step

              # draw sand
              sand_rect = screen.blit(base_image, (0, GROUND_Y))
              # bird falls
              # The second part keeps the jump the same height at any screen speed.
              bird_y += bird_drop_velocity * step + GRAVITY * step * (step - 1) / 2
              bird_drop_velocity += GRAVITY * step

              # generate new tube
              if tube1_x < -TUBE_WIDTH:
                     tube1_x = 963
                     tube1_height =  randint(GAP_TOP_MIN, GAP_TOP_MAX)
                     tube1_pass = False
              if tube2_x < -TUBE_WIDTH:
                     tube2_x = 963
                     tube2_height = randint(GAP_TOP_MIN, GAP_TOP_MAX)
                     tube2_pass = False
              if tube3_x < -TUBE_WIDTH:
                     tube3_x = 963
                     tube3_height = randint(GAP_TOP_MIN, GAP_TOP_MAX)
                     tube3_pass = False

              score_str = str(score)
              digit_x = (WIDTH - len(score_str) * DIGIT_WIDTH) // 2
              for ch in score_str:
                     screen.blit(digit_images[int(ch)], (digit_x, 50))
                     digit_x += DIGIT_WIDTH

              screen.blit(speaker_on_image if sound_on else speaker_off_image, speaker_rect)

              # update score
              if tube1_x + TUBE_WIDTH <= BIRD_X and tube1_pass == False:
                     score += 1
                     tube1_pass = True
                     point_sound.play()
              if tube2_x + TUBE_WIDTH <= BIRD_X and tube2_pass == False:
                     score += 1
                     tube2_pass = True
                     point_sound.play()
              if tube3_x + TUBE_WIDTH <= BIRD_X and tube3_pass == False:
                     score += 1 
                     tube3_pass = True
                     point_sound.play()

              # check collision
              for tube in [tube1_rect, tube2_rect, tube3_rect,
                  tube1_rect_inv, tube2_rect_inv, tube3_rect_inv, sand_rect]:
                       if bird_rect.colliderect(tube):
                            if not pausing:
                                   hit_sound.play()
                                   # Save only on a new record, once per death.
                                   if score > high_score:
                                          high_score = score
                                          save_high_score(high_score)
                            pausing = True
                            TUBE_VELOCITY = 0
                            bird_drop_velocity = 0

                     
                    

                 

              # game over screen
              # Draw the overlay first, so only what is drawn after it stays bright.
              if pausing:
                     screen.blit(dark_overlay, (0, 0))
                     screen.blit(speaker_on_image if sound_on else speaker_off_image, speaker_rect)
                     screen.blit(gameover_txt, (175, 200 + SHIFT))
                     screen.blit(scoreboard_image, (90, 330 + SHIFT))
                     draw_small_number(high_score, 582, 382 + SHIFT)
                     draw_small_number(score, 582, 498 + SHIFT)

              for event in pygame.event.get(): #click
                     if event.type == pygame.QUIT: # quit
                            running = False
                     left_click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                     space_key = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
                     if left_click and speaker_rect.collidepoint(to_game_pos(event.pos)):
                            toggle_sound()
                     elif left_click or space_key:
                            #reset and back to main
                            if pausing:
                               bird_y = BIRD_START_Y
                               TUBE_VELOCITY = 4.46
                               tube1_x = 900
                               tube2_x = 1250
                               tube3_x = 1600
                               tube1_pass = False
                               tube2_pass = False
                               tube3_pass = False
                               score = 0
                               pausing = False
                               bird_drop_velocity = 0
                               show_message = True
                               swoosh_sound.play() # play once when returning to the main screen
                            else:
                               bird_drop_velocity = 0
                               bird_drop_velocity -= 11.33
                               # sound wing
                               wing_sound.play()
              show_frame()
              await asyncio.sleep(0) # give control back to the browser

       pygame.quit()

asyncio.run(main())
