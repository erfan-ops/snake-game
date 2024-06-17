import pygame
import sys
from ctypes import wintypes
import ctypes
from random import randint
from time import perf_counter
from settings import *


def draw_rect_alpha(surface: pygame.SurfaceType, color: Color, rect: pygame.rect.RectType):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


class Snake:
    def __init__(self) -> None:
        self.length = SNAKE_START_SIZE
        self.body: list[pygame.rect.RectType] = []
        for x in range(0, -SNAKE_START_SIZE, -1):
            self.body.append(pygame.rect.Rect(x*TILE_SIZE + HALF_LINE_WIDTH, HALF_LINE_WIDTH, TILE_SIZE_IN_LINES, TILE_SIZE_IN_LINES))
        
        self.facing = 0
        self.go_func = self.go_right
    
    def render(self, surface: pygame.SurfaceType):
        body_len = len(self.body)
        alpha_ratio = 255 / body_len
        rng = SNAKE_COLORS_LEN_M1 if SNAKE_COLORS_LEN_M1 <= body_len else body_len
        for icol in range(rng):
            next_icol = icol + 1
            r, g, b = SNAKE_COLORS[icol]
            r2, g2, b2 = SNAKE_COLORS[next_icol]
            n_drawing = body_len / rng
            color_ratio = 1 / n_drawing
            start = int(n_drawing*icol)
            for i in range(start, int(n_drawing*next_icol)):
                c1r = color_ratio*(i - start)
                c2r = 1 - c1r
                alpha = alpha_ratio*(body_len-i) if TRANSPARENT_SNAKE_TAIL else 255
                col1 = (r*c2r + r2*c1r,
                        g*c2r + g2*c1r,
                        b*c2r + b2*c1r,
                        alpha)
                draw_rect_alpha(surface, col1, self.body[i])
    
    def go_right(self):
        self.body[0].x += TILE_SIZE
            
    def go_left(self):
        self.body[0].x -= TILE_SIZE
    
    def go_up(self):
        self.body[0].y -= TILE_SIZE
    
    def go_down(self):
        self.body[0].y += TILE_SIZE
    
    def collision(self, other: pygame.rect.RectType) -> bool:
        if self.body[0].colliderect(other):
            self.body.append(self.body[-1].copy())
            return True
        return False
    
    def self_hit(self):
        if self.body[0].left < 0 or self.body[0].right > WIDTH or self.body[0].top < 0 or self.body[0].bottom > HEIGHT:
            return True
        for i in range(len(self.body)):
            for other in self.body[i+1 : ]:
                if self.body[i].colliderect(other):
                    return True
        return False
    
    def go(self, face: list[Literal[0, 1, 2, 3]]) -> None:
        for i in range(len(self.body)-1, 0, -1):
            self.body[i].topleft = self.body[i-1].topleft
        
        if not face and self.facing != 1:
            self.go_func = self.go_right
            self.facing = 0
        elif face == 1 and self.facing:
            self.go_func = self.go_left
            self.facing = 1
        elif face == 2 and self.facing != 3:
            self.go_func = self.go_up
            self.facing = 2
        elif face == 3 and self.facing != 2:
            self.go_func = self.go_down
            self.facing = 3
        
        self.go_func()

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.SurfaceType = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food_rect = pygame.rect.Rect(randint(0, TILES_IN_WIDTH -1)*TILE_SIZE + HALF_LINE_WIDTH,
                                          randint(0, TILES_IN_HEIGHT-1)*TILE_SIZE + HALF_LINE_WIDTH,
                                          TILE_SIZE_IN_LINES,
                                          TILE_SIZE_IN_LINES)
        
        pygame.display.set_icon(pygame.image.load("icon.png").convert_alpha())
        
        lpBuffer = wintypes.LPWSTR()
        AppUserModelID = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID
        AppUserModelID(ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR))
        ctypes.windll.kernel32.LocalFree(lpBuffer)
    
    
    def end(self):
        pygame.quit()
        sys.exit()
    
    
    def render(self):
        self.screen.fill(BG_COLOR)
            
        #-- drawing the grid lines --#
        for vertical in range(1, TILES_IN_WIDTH):
            x = vertical * TILE_SIZE
            pygame.draw.line(self.screen, LINES_COLOR, (x, 0), (x, HEIGHT), LINES_WIDTH)
        
        for horizontal in range(1, TILES_IN_HEIGHT):
            y = horizontal * TILE_SIZE
            pygame.draw.line(self.screen, LINES_COLOR, (0, y), (WIDTH, y), LINES_WIDTH)
        
        #-- renderings stuff --#
        pygame.draw.rect(self.screen, FOOD_COLOR, self.food_rect)
        self.snake.render(self.screen)
    
    def wait(self):
        endf = perf_counter()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.end()
                    elif event.key == pygame.K_r:
                        self.snake = Snake()
                        return
                elif event.type == pygame.QUIT:
                    self.end()
            
            startf = endf
            endf = perf_counter()
            dt = endf - startf
            pygame.display.set_caption(f"fps: {1/dt:.2f}")
            self.clock.tick(15)
    
    def run(self):
        snake_face = 0
        frame_counter = 1
        
        timer: float = 0
        
        endf = perf_counter()
        
        self.render()
        pygame.display.flip()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        snake_face = 0
                    elif event.key == pygame.K_LEFT:
                        snake_face = 1
                    elif event.key == pygame.K_UP:
                        snake_face = 2
                    elif event.key == pygame.K_DOWN:
                        snake_face = 3
                    
                    elif event.key == pygame.K_ESCAPE:
                        self.end()
                
                elif event.type == pygame.QUIT:
                    self.end()
            
            startf = endf
            endf = perf_counter()
            dt = endf - startf
            timer += dt
            pygame.display.set_caption(f"fps: {1/dt:.2f}")
            
            # timer += self.clock.get_time()
            # pygame.display.set_caption(f"fps: {self.clock.get_fps():.2f}")
            
            frame_counter %= FRAME_BREAKER
            if not frame_counter and timer >= SPEED:
                rng = int(timer / SPEED)
                timer %= SPEED
                for _ in range(rng):
                    self.render()
                    if self.snake.collision(self.food_rect):
                        while self.food_rect.topleft in [rect.topleft for rect in self.snake.body]:
                            self.food_rect = pygame.rect.Rect(randint(0, TILES_IN_WIDTH -1)*TILE_SIZE + HALF_LINE_WIDTH,
                                                            randint(0, TILES_IN_HEIGHT-1)*TILE_SIZE + HALF_LINE_WIDTH,
                                                            TILE_SIZE_IN_LINES,
                                                            TILE_SIZE_IN_LINES)
                    
                    self.snake.go(snake_face)
                    
                    if self.snake.self_hit():
                        self.render()
                        pygame.display.flip()
                        if len(self.snake.body) >= TILES_IN_WIDTH * TILES_IN_HEIGHT:
                            print("Victory!!!")
                        self.wait()
                        endf = perf_counter()
            
            frame_counter += 1
        
            pygame.display.flip()
            self.clock.tick(TFPS)



if __name__ == "__main__":
    game = Game()
    game.run()