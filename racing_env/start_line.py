import pygame
import numpy as np


def find_start_line(image_path, target_rgb=(255, 0, 0), tolerance=10):
    surface = pygame.image.load(image_path).convert()
    arr = pygame.surfarray.array3d(surface)  # shape: (width, height, 3)
    r, g, b = target_rgb
    mask = (
        (np.abs(arr[:, :, 0].astype(int) - r) < tolerance) &
        (np.abs(arr[:, :, 1].astype(int) - g) < tolerance) &
        (np.abs(arr[:, :, 2].astype(int) - b) < tolerance)
    )
    coords = np.argwhere(mask)  # (N, 2) each row is (x, y)
    if len(coords) == 0:
        print("WARNING: No start line found in image!")
        return None
    cx = float(np.mean(coords[:, 0]))
    cy = float(np.mean(coords[:, 1]))
    return pygame.Vector2(cx, cy)
