import pygame
from random import randint  
WIDTH, HEIGHT = 700, 1000

GREEN = (0, 200, 0) # RGB colour
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')
running = True 
clock = pygame.time.Clock()

TUBE_VELOCITY = 4.46
TUBE_WIDTH = 88
TUBE_GAP = 250

tube1_x = 900
tube2_x = 1250
tube3_x = 1600

tube1_height = randint(167, 584)
tube2_height = randint(167, 584)
tube3_height = randint(167, 584)  

BIRD_X = 88
bird_y = 667
BIRD_WIDTH = 55
BIRD_HEIGHT = 52

bird_drop_velocity = 0
GRAVITY = 0.6

score = 0
font = pygame.font.SysFont('sans', 33)

tube1_pass = False
tube2_pass = False
tube3_pass = False

pausing = False

backgroud_image = pygame.image.load("sprites/background.png")
backgroud_image = pygame.transform.scale(backgroud_image, (WIDTH, HEIGHT))

base_image = pygame.image.load("sprites/base.png")
base_image = pygame.transform.scale(base_image, (700, 83))
bird_image = pygame.image.load("sprites/bird.png")
bird_image = pygame.transform.scale(bird_image, (BIRD_WIDTH, BIRD_HEIGHT))

PIPE_HEIGHT = 667
pipe_image = pygame.image.load("sprites/pipe-green.png").convert_alpha()
pipe_image = pygame.transform.scale(pipe_image, (TUBE_WIDTH, PIPE_HEIGHT))
pipe_image_top = pygame.transform.flip(pipe_image, False, True)

messgage_main = pygame.image.load("sprites/message.png")
messgage_main = pygame.transform.scale(messgage_main, (420, 500))

gameover_txt = pygame.image.load("sprites/gameover.png")
gameover_txt = pygame.transform.scale(gameover_txt, (350, 100))
show_message = True

# sound effect
point_sound = pygame.mixer.Sound("audio/point.ogg")
point_sound = pygame.mixer.Sound(buffer=point_sound.get_raw()[22048:])
wing_sound = pygame.mixer.Sound("audio/wing.ogg")
swoosh_sound = pygame.mixer.Sound("audio/swoosh.ogg")
die_sound = pygame.mixer.Sound("audio/die.ogg")
hit_sound = pygame.mixer.Sound("audio/hit.ogg")
SOUND_VOLUME = 0.3 # 0.0 -> 1.0
all_sounds = [point_sound, wing_sound, swoosh_sound, die_sound, hit_sound]
for sound in all_sounds:
       sound.set_volume(SOUND_VOLUME)

# speaker button
sound_on = True
speaker_rect = pygame.Rect(15, 15, 56, 56)
speaker_on_image = pygame.image.load("sprites/speaker_on.png").convert_alpha()
speaker_on_image = pygame.transform.smoothscale(speaker_on_image, speaker_rect.size)
speaker_off_image = pygame.image.load("sprites/speaker_off.png").convert_alpha()
speaker_off_image = pygame.transform.smoothscale(speaker_off_image, speaker_rect.size)

def toggle_sound():
       global sound_on
       sound_on = not sound_on
       volume = SOUND_VOLUME if sound_on else 0
       for sound in all_sounds:
              sound.set_volume(volume)

DIGIT_WIDTH, DIGIT_HEIGHT = 42, 60
digit_images = []
for i in range(10):
       digit = pygame.image.load("sprites/" + str(i) + ".png").convert_alpha()
       digit_images.append(pygame.transform.scale(digit, (DIGIT_WIDTH, DIGIT_HEIGHT)))

while running:
       clock.tick(60) # fps
       screen.fill(GREEN) # theme
       screen.blit(backgroud_image, (0, 0))

       # draw main 
              # draw main
       if show_message:
              swoosh_sound.play()     
              screen.blit(messgage_main, (140, 167))
              screen.blit(speaker_on_image if sound_on else speaker_off_image, speaker_rect)
              pygame.display.flip()
              for event in pygame.event.get():
                     if event.type == pygame.QUIT:
                            running = False
                     left_click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                     if left_click and speaker_rect.collidepoint(event.pos):
                            toggle_sound()
                     elif event.type == pygame.MOUSEBUTTONDOWN:
                            show_message = False
                            bird_drop_velocity = -11.33
              continue
   
       # draw tube
       tube1_rect = screen.blit(pipe_image_top, (tube1_x, tube1_height - PIPE_HEIGHT))
       tube2_rect = screen.blit(pipe_image_top, (tube2_x, tube2_height - PIPE_HEIGHT))
       tube3_rect = screen.blit(pipe_image_top, (tube3_x, tube3_height - PIPE_HEIGHT))

       # draw tube inverse
       tube1_rect_inv = screen.blit(pipe_image, (tube1_x, tube1_height + TUBE_GAP))
       tube2_rect_inv = screen.blit(pipe_image, (tube2_x, tube2_height + TUBE_GAP))
       tube3_rect_inv = screen.blit(pipe_image, (tube3_x, tube3_height + TUBE_GAP))

       
       # move tube to the left
       tube1_x = tube1_x - TUBE_VELOCITY
       tube2_x = tube2_x - TUBE_VELOCITY
       tube3_x = tube3_x - TUBE_VELOCITY

       # draw bird
       bird_rect = screen.blit(bird_image, (BIRD_X, bird_y))

       # draw sand
       sand_rect = screen.blit(base_image, (0, 917))
       # bird falls
       bird_y += bird_drop_velocity
       bird_drop_velocity += GRAVITY

       # generate new tube
       if tube1_x < -TUBE_WIDTH:
              tube1_x = 963
              tube1_height =  randint(167, 584)
              tube1_pass = False
       if tube2_x < -TUBE_WIDTH:
              tube2_x = 963
              tube2_height = randint(167, 584)
              tube2_pass = False
       if tube3_x < -TUBE_WIDTH:
              tube3_x = 963
              tube3_height = randint(167, 584)
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
                     pausing = True
                     TUBE_VELOCITY = 0
                     bird_drop_velocity = 0

                     
                     screen.blit(gameover_txt, (175, 200))
                    

                 

       for event in pygame.event.get(): #click   
              if event.type == pygame.QUIT: # quit
                     running = False
              left_click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
              space_key = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
              if left_click and speaker_rect.collidepoint(event.pos):
                     toggle_sound()
              elif left_click or space_key:
                     #reset
                     if pausing:
                        bird_y = 667
                        TUBE_VELOCITY = 4.46
                        tube1_x = 900
                        tube2_x = 1250
                        tube3_x = 1600
                        score = 0
                        pausing = False
                     
                     bird_drop_velocity = 0
                     bird_drop_velocity -= 11.33
                     # sound wing
                     wing_sound.play()
       pygame.display.flip()

pygame.quit()