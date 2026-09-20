import pygame
import random
import pygame.font

pygame.init()
pygame.mixer.init() # initialize the mixer module for sound

# pixel size screen
screen_width = 500
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height)) # make a screen

# clock
clock = pygame.time.Clock() # create a clock object to manage the frame rate
fps = 60 # frames per second
time = 0 # time in seconds
time_text = pygame.font.SysFont(None, 40)

# score
score = 0
score_text = pygame.font.SysFont(None, 40)

# title screen
game_state = "title" # "title" or "playing"
title_font = pygame.font.SysFont(None, 100)
button_font = pygame.font.SysFont(None, 60)
title_surface = title_font.render("The D Skies", True, (255, 255, 255))
title_shadow = title_font.render("The D Skies", True, (0, 50, 150))
title_rect = title_surface.get_rect(center=(screen_width // 2, 260))
start_button = pygame.Rect(0, 0, 220, 80) # x, y, width, height
start_button.center = (screen_width // 2, 460)
start_surface = button_font.render("Start", True, (255, 255, 255))
button_color = (0, 170, 60) # RGB color
button_hover_color = (0, 210, 80) # brighter when the mouse is over it

# player
player = pygame.image.load("assets/base_donut.png") # load the image
player_max_height = 300
player_hitbox = player.get_rect(topleft=(260, 510)) # create a hitbox for the player
height = 0

double_jump_time = 0
double_jump_cooldown = 1000 # milliseconds
double_jump_available = True
double_jump_icon = pygame.Rect(25, 100, 50, 50) # x, y, width, height
double_jump_icon_color = (0, 255, 0) # RGB color

hp = 3
hp_text = pygame.font.SysFont(None, 40)
heart_img = pygame.image.load("assets/heart.png") # load the heart image

# Clouds
cloud_color = (255, 255, 255) # RGB color
cloud_width = 125
cloud_height = 25
max_clouds = 3 # how many clouds to keep on screen (more clouds = easier to land)

cloud_img = pygame.image.load("assets/cloud.png") # load the cloud image
thunder_img = pygame.image.load("assets/thunder_cloud.png") # load the thunder cloud image
mist_img = pygame.image.load("assets/mist_cloud.png") # load the mist cloud image
bounce_img = pygame.image.load("assets/bounce_cloud.png") # load the bounce cloud image

rocket_img = pygame.image.load("assets/rocket.png") # load the rocket cloud image

cloud_images = {
    "normal": cloud_img,
    "thunder": thunder_img,
    "mist": mist_img,
    "trampoline": bounce_img,  # swap in a different image when you have one
}

clouds = [] # filled in by reset_game()
rockets = [] # filled in by reset_game()

# Screen Speed
Vel_Y = 0
Jump_velocity = 20
Gravity = 0.5
Max_fall_speed = 12 # terminal velocity, gives you more time to steer onto a cloud

jump_sound = pygame.mixer.Sound("assets/jump.wav") # load the sound


def reset_game():
    # put everything back to its starting state for a new run
    global score, hp, time, Vel_Y, double_jump_time, double_jump_available, double_jump_icon_color
    score = 0
    hp = 3
    time = 0
    Vel_Y = 0
    double_jump_time = 0
    double_jump_available = True
    double_jump_icon_color = (0, 255, 0) # RGB color
    player_hitbox.topleft = (260, 510)
    clouds[:] = [
        {"type": "normal", "rect": pygame.Rect(250, 700, 125, 25)},
        {"type": "normal", "rect": pygame.Rect(250, 500, 125, 25)},
        {"type": "normal", "rect": pygame.Rect(250, 300, 125, 25)},
        {"type": "normal", "rect": pygame.Rect(250, 100, 125, 25)},
    ]
    rockets[:] = [(rocket_img, pygame.Rect(100, 400, 50, 100)), (rocket_img, pygame.Rect(300, 200, 50, 100))]


is_game_running = True
while is_game_running:
    clock.tick(fps) # limit the frame rate to 60 FPS

    # Title Screen
    if game_state == "title":
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # clicking the x in the corner
                is_game_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # left click
                if start_button.collidepoint(event.pos):
                    reset_game() # fresh score, hp, player, clouds, and rockets
                    game_state = "playing"

        mouse_over_button = start_button.collidepoint(pygame.mouse.get_pos())
        screen.fill((10, 100, 255)) # same sky blue as the game
        screen.blit(title_shadow, title_rect.move(4, 4)) # drop shadow
        screen.blit(title_surface, title_rect)
        pygame.draw.rect(screen, button_hover_color if mouse_over_button else button_color, start_button)
        pygame.draw.rect(screen, (255, 255, 255), start_button, 4) # white outline
        screen.blit(start_surface, start_surface.get_rect(center=start_button.center))
        pygame.display.flip()
        continue # skip the game code below until the player presses Start

    tick_time = pygame.time.get_ticks()
    time += clock.get_time() / 1000 # update the time in seconds
    time_surface = time_text.render(f"Time: {time:.1f}", True, (255, 255, 255))

    # Quit Game Events
    for event in pygame.event.get(): # anything in the window is an event
        if event.type == pygame.QUIT: # clicking the x in the corner
            is_game_running = False
    if player_hitbox.y > screen_height: # if the rectangle is off the screen
        game_state = "title" # back to the title screen
        continue
    if hp <= 0: # if the player has no health
        game_state = "title" # back to the title screen
        continue

    if tick_time - double_jump_time > double_jump_cooldown: 
        double_jump_available = True
        double_jump_icon_color = (0, 255, 0) # RGB color


    # Player Movement
    pressed_keys = pygame.key.get_pressed() # get the state of all keys
    speed = 5 # speed of the rectangle
    if pressed_keys[pygame.K_LSHIFT]:
        speed = 10
    if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]: 
        if player_hitbox.x - speed > 0: # check if the rectangle is not going off the screen
            player_hitbox.x -= speed # move the rectangle up
    if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]: 
        if player_hitbox.x + speed < screen_width: # check if the rectangle is not going off the screen
            player_hitbox.x += speed # move the rectangle down
    if pressed_keys[pygame.K_SPACE]:
        if double_jump_available: 
            Vel_Y = Jump_velocity # set the velocity to the jump velocity
            double_jump_time = tick_time
            double_jump_available = False
            double_jump_icon_color = (255, 0, 0) # RGB color
            jump_sound.play()

    print(Vel_Y)
    if Vel_Y <= 0:
        player_hitbox.y -= Vel_Y # move the rectangle down
    elif Vel_Y > 0:
        if player_hitbox.y > player_max_height:
            player_hitbox.y -= Vel_Y # move the rectangle up

    screen.fill((10, 100, 255)) # background, covers everything behind the screen

    if len(clouds) < max_clouds:
        cloud_x = random.randint(0, screen_width - cloud_width)
        clouds.append({"type": "normal", "rect": pygame.Rect(cloud_x, 0, cloud_width, cloud_height)})
    if len(rockets) < 1:
        rocket_x = random.randint(0 - 50, screen_width - 50)
        rockets.append((rocket_img, pygame.Rect(rocket_x, 0, 50, 100)))
    

    for cloud in clouds[:]:  # loop over a copy so removing is safe
        rect = cloud["rect"]

        # only normal clouds react, and only once
        if cloud["type"] == "normal" and player_hitbox.colliderect(rect):
            lotto = random.randint(1, 40)
            if lotto == 1:
                hp -= 1
                cloud["type"] = "thunder"
            elif lotto == 2:
                cloud["type"] = "mist"
            elif lotto <= 6:
                cloud["type"] = "trampoline"
                Vel_Y = Jump_velocity * 2
                jump_sound.play()
                score += 1
            else:
                Vel_Y = Jump_velocity
                score += 1
                jump_sound.play()
                clouds.remove(cloud)
                continue  # skip drawing this one, but keep the loop going

        if Vel_Y > 0:
            rect.y += Vel_Y
            if rect.y > screen_height:
                clouds.remove(cloud)
                continue

        screen.blit(cloud_images[cloud["type"]], rect)

    for rocket_img, rocket_rect in rockets[:]:  # loop over a copy so removing is safe
        if player_hitbox.colliderect(rocket_rect):
            lotto = random.randint(1, 4)
            if lotto == 1:
                hp += 1
            elif lotto == 2:
                jump_sound.play()
                Vel_Y = Jump_velocity * 2
            elif lotto == 3:
                hp -= 1
            # lotto == 4: harmless bump, nothing happens
            rockets.remove((rocket_img, rocket_rect))
            continue  # skip drawing this one, but keep the loop going

        if Vel_Y > 0:
            rocket_rect.y += Vel_Y
            if rocket_rect.y > screen_height:
                rockets.remove((rocket_img, rocket_rect))
                continue

        rocket_rect.x += 10
        if rocket_rect.x > screen_width:
            rockets.remove((rocket_img, rocket_rect))
            continue

        screen.blit(rocket_img, rocket_rect)

    if hp == 3:
        screen.blit(heart_img, (screen_width - 325, 25))
        screen.blit(heart_img, (screen_width - 225, 25))
        screen.blit(heart_img, (screen_width - 125, 25))
    elif hp == 2:
        screen.blit(heart_img, (screen_width - 225, 25))
        screen.blit(heart_img, (screen_width - 125, 25))
    elif hp == 1:
        screen.blit(heart_img, (screen_width - 125, 25))
    
    screen.blit(player, player_hitbox)  # draw the player
    screen.blit(time_surface, (25, 25))
    screen.blit(score_text.render(f"Score: {score}", True, (255, 255, 255)), (25, 60))
    pygame.draw.rect(screen, double_jump_icon_color, double_jump_icon) # draw the double jump icon
    pygame.display.flip() # update the display, pygame uses double buffering, so this flips the buffers
    Vel_Y = max(Vel_Y - Gravity, -Max_fall_speed) # gravity pulls down, but falling speed is capped

    # if cloud list gets too long, remove the oldest clouds
    if len(clouds) > max_clouds + 1:
        clouds.pop(0)
    if len(rockets) > 2:
        rockets.pop(0)

pygame.quit() # quit pygame