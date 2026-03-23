import pygame
import json

pygame.init()
pygame.display.set_mode((1, 1))  # dummy window so convert() works

surface = pygame.image.load("assets/waypoint_layer.png").convert()

waypoints = []
for y in range(surface.get_height()):
    for x in range(surface.get_width()):
        if surface.get_at((x, y))[:3] == (255, 255, 255):
            waypoints.append([x, y])

with open("track.json", "w") as f:
    json.dump({"waypoints": waypoints, "track_width": 8}, f, indent=2)

print(f"Extracted {len(waypoints)} waypoints -> track.json")
pygame.quit()
