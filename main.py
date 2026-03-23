import pygame
import config
import racing_env.car as car
from utils import get_human_action
import json

pygame.init()
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("rl-driver")
clock = pygame.time.Clock()

track_img = pygame.image.load("assets/waypoint_layer.png").convert()
track_img = pygame.transform.scale(track_img, (config.WIDTH, config.HEIGHT))

with open("track.json") as f:
    track_data = json.load(f)

waypoints = [pygame.Vector2(p) for p in track_data["waypoints"]]
track_width = track_data["track_width"]

# scale waypoints from 160x90 to 1280x720
scale_x = config.WIDTH / 160
scale_y = config.HEIGHT / 90
waypoints = [pygame.Vector2(wp.x * scale_x, wp.y * scale_y) for wp in waypoints]
track_width_scaled = track_width * scale_x

def is_on_track(pos):
    return any(pos.distance_to(wp) < track_width_scaled for wp in waypoints)

track_img = pygame.image.load("assets/bg.png").convert()

car = car.Car(100, 100)

running = True
while running:
    dt = clock.get_time() / 1000
    #dt = 1/60  # for training

    clock.tick(config.FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill(config.BLACK)

    keys = get_human_action(pygame.key.get_pressed())

    car.update(dt, keys)
    if not is_on_track(car.position):
        car.position -= car.velocity * dt
        car.velocity *= 0

    screen.blit(track_img, (0, 0))



    car.draw(screen)



    # push buffer to screen
    pygame.display.flip()       
pygame.quit()

