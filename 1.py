import pygame
from random import randint  
WIDTH, HEIGHT = 400, 600
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

TUBE_VELOCITY = 3
TUBE_WIDTH = 50
TUBE_GAP = 150

tube1_x = 600
tube2_x = 800
tube3_x = 1000

tube1_height = randint(100, 400)
tube2_height = randint(100, 400)
tube3_height = randint(100, 400)  

BIRD_X = 50
bird_y = 400
BIRD_WIDTH = 35
BIRD_HEIGHT = 35

bird_drop_velocity = 0
GRAVITY = 0.5

score = 0
font = pygame.font.SysFont('sans', 20)

tube1_pass = False
tube2_pass = False
tube3_pass = False

pausing = False

backgroud_image = pygame.image.load("background.png")
backgroud_image = pygame.transform.scale(backgroud_image, (WIDTH, HEIGHT))
bird_image = pygame.image.load("bird.png")
bird_image = pygame.transform.scale(bird_image, (BIRD_WIDTH, BIRD_HEIGHT))
while running:
       clock.tick(60) # fps
       screen.fill(GREEN) # theme
       screen.blit(backgroud_image, (0, 0))

       # draw tube
       tube1_rect = pygame.draw.rect(screen, BLUE, (tube1_x, 0, TUBE_WIDTH, tube1_height))
       tube2_rect = pygame.draw.rect(screen, BLUE, (tube2_x, 0, TUBE_WIDTH, tube2_height))
       tube3_rect = pygame.draw.rect(screen, BLUE, (tube3_x, 0, TUBE_WIDTH, tube3_height))

       # draw tube inverse
       tube1_rect_inv = pygame.draw.rect(screen, BLUE, (tube1_x, tube1_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube1_height - TUBE_GAP))
       tube2_rect_inv = pygame.draw.rect(screen, BLUE, (tube2_x, tube2_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube2_height - TUBE_GAP))
       tube3_rect_inv = pygame.draw.rect(screen, BLUE, (tube3_x, tube3_height + TUBE_GAP, TUBE_WIDTH, HEIGHT - tube3_height - TUBE_GAP))
       
       # move tube to the left
       tube1_x = tube1_x - TUBE_VELOCITY
       tube2_x = tube2_x - TUBE_VELOCITY
       tube3_x = tube3_x - TUBE_VELOCITY

       # draw bird
       bird_rect = screen.blit(bird_image, (BIRD_X, bird_y))

       # draw sand
       sand_rect = pygame.draw.rect(screen, YELLOW, (0, 570, 400, 30))
       # bird falls
       bird_y += bird_drop_velocity
       bird_drop_velocity += GRAVITY

       # generate new tube
       if tube1_x < -TUBE_WIDTH:
              tube1_x = 550
              tube1_height =  randint(100, 400)
              tube1_pass = False
       if tube2_x < -TUBE_WIDTH:
              tube2_x = 550
              tube2_height = randint(100, 400)
              tube2_pass = False
       if tube3_x < -TUBE_WIDTH:
              tube3_x = 550
              tube3_height = randint(100, 400)
              tube3_pass = False

       score_txt = font.render("Score: " + str(score), True, BLACK)
       screen.blit(score_txt, (5, 5))
       # update score

       if tube1_x + TUBE_WIDTH <= BIRD_X and tube1_pass == False:
              score += 1
              tube1_pass = True
       if tube2_x + TUBE_WIDTH <= BIRD_X and tube2_pass == False:
              score += 1
              tube2_pass = True
       if tube3_x + TUBE_WIDTH <= BIRD_X and tube3_pass == False:
              score += 1 
              tube3_pass = True

       # check collision
       for tube in [tube1_rect, tube2_rect, tube3_rect,
           tube1_rect_inv, tube2_rect_inv, tube3_rect_inv, sand_rect]:
                if bird_rect.colliderect(tube):
                     pausing = True
                     TUBE_VELOCITY = 0
                     bird_drop_velocity = 0

                     game_over_txt = font.render("GAME OVER, score: " + str(score), True, BLACK)
                     screen.blit(game_over_txt, (200, 300))

                     press_space_txt = font.render("Press Space to Continue", True, BLACK)
                     screen.blit(press_space_txt, (200, 400))

       for event in pygame.event.get(): #click   
              if event.type == pygame.QUIT: # quit
                     running = False
              if event.type == pygame.KEYDOWN:
                     if event.key == pygame.K_SPACE: 
                            #reset
                            if pausing:
                               bird_y = 400
                               TUBE_VELOCITY = 3
                               tube1_x = 600
                               tube2_x = 800
                               tube3_x = 1000
                               score = 0
                               pausing = False

                            bird_drop_velocity = 0
                            bird_drop_velocity -= 8
       pygame.display.flip()

pygame.quit()