import pygame
import sys
from ctypes import wintypes
import ctypes
from random import randint
from time import perf_counter
from settings import *
import os


def draw_rect_alpha(surface: pygame.SurfaceType, color: Color, rect: pygame.rect.RectType):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


class Rect(pygame.rect.Rect):
    def __init__(self, left: float, top: float, width: float, height: float, face: Literal[0, 1, 2, 3]):
        super().__init__(left, top, width, height)
        self.facing = face


class Snake:
    def __init__(self) -> None:
        self.body: list[Rect] = []
        for x in range(0, -SNAKE_START_SIZE, -1):
            self.body.append(Rect(x*TILE_SIZE + HALF_LINE_WIDTH, HALF_LINE_WIDTH, TILE_SIZE_IN_LINES, TILE_SIZE_IN_LINES, 0))
        
        self.facing = 0
        self.go_func = self.go_right
        
        self.texture_map = [1, 0, 3, 2]
        
        self.head_texture = pygame.transform.scale(pygame.image.load(os.path.join(TEXTURE_PATH, "head.png")).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.body_texture = pygame.transform.scale(pygame.image.load(os.path.join(TEXTURE_PATH, "body.png")).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.tail_texture = pygame.transform.scale(pygame.image.load(os.path.join(TEXTURE_PATH, "tail.png")).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.turn_texture = pygame.transform.scale(pygame.image.load(os.path.join(TEXTURE_PATH, "turn.png")).convert_alpha(), (TILE_SIZE, TILE_SIZE))

        all_textures = [self.head_texture, self.body_texture, self.tail_texture, self.turn_texture]
        for texture in all_textures:
            for y in range(texture.get_height()):
                for x in range(texture.get_width()):
                    r, g, b, a = texture.get_at((x, y))
                    if [r, g, b] == WHITE and a != 0:
                        texture.set_at((x, y), PRIMARY_COL)
                    elif [r, g, b] == BLACK and a != 0:
                        texture.set_at((x, y), SECONDARY_COL)
                    elif [r, g, b] == RED and a != 0:
                        texture.set_at((x, y), TONGUE_COL)
    
    def render(self, surface: pygame.SurfaceType):
        if RENDER_TEXTURES:
            self.render_texture(surface)
            return
        
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
    
    def render_texture(self, surface: pygame.SurfaceType):        
        surface.blit(pygame.transform.rotate(self.head_texture, self.texture_map[self.facing] * 90), self.body[0].topleft)
        for i in range(1, len(self.body)-1):
            other = self.body[i-1]
            rect = self.body[i]
            if rect.facing == other.facing:
                surface.blit(pygame.transform.rotate(self.body_texture, self.texture_map[rect.facing] * 90), rect.topleft)
            else:
                turn_texture = self.turn_texture
                if (rect.facing == 1 and other.facing == 0) or (rect.facing == 2 and other.facing == 3):
                    turn_texture = pygame.transform.rotate(self.turn_texture, 180)
                elif (rect.facing == 3 and other.facing == 0) or (rect.facing == 2 and other.facing == 1):
                    turn_texture = pygame.transform.rotate(self.turn_texture, 90)
                elif (rect.facing == 0 and other.facing == 3) or (rect.facing == 1 and other.facing == 2):
                    turn_texture = pygame.transform.rotate(self.turn_texture, 270)
                    
                    
                surface.blit(turn_texture, rect.topleft)
            
        surface.blit(pygame.transform.rotate(self.tail_texture, self.texture_map[self.body[-2].facing] * 90), self.body[-1].topleft)
    
    def go_right(self):
        self.body[0].x += TILE_SIZE
        self.body[0].facing = 0
            
    def go_left(self):
        self.body[0].x -= TILE_SIZE
        self.body[0].facing = 2
    
    def go_up(self):
        self.body[0].y -= TILE_SIZE
        self.body[0].facing = 3
    
    def go_down(self):
        self.body[0].y += TILE_SIZE
        self.body[0].facing = 1
    
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
                if self.body[i].topleft == other.topleft:
                    return True
        return False
    
    def is_in_dangerous_block(self, point: tuple[int, int]):
        if point[0] < 0 or point[0] > WIDTH or point[1] < 0 or point[1] > HEIGHT:
            return True
        for rect in self.body:
            if point == rect.topleft:
                return True
        return False
            
    
    def go(self, face: Literal[0, 1, 2, 3]) -> None:
        for i in range(len(self.body)-1, 0, -1):
            self.body[i].topleft = self.body[i-1].topleft
            self.body[i].facing = self.body[i-1].facing
        
        if not face and self.facing != 2:
            self.go_func = self.go_right
            self.facing = 0
        elif face == 2 and self.facing:
            self.go_func = self.go_left
            self.facing = 2
        elif face == 3 and self.facing != 1:
            self.go_func = self.go_up
            self.facing = 3
        elif face == 1 and self.facing != 3:
            self.go_func = self.go_down
            self.facing = 1
        
        self.go_func()

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.SurfaceType = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.font = pygame.font.Font(FONT_PATH, 40)
        self.food_rect = pygame.rect.Rect(randint(0, TILES_IN_WIDTH -1)*TILE_SIZE + HALF_LINE_WIDTH,
                                          randint(0, TILES_IN_HEIGHT-1)*TILE_SIZE + HALF_LINE_WIDTH,
                                          TILE_SIZE_IN_LINES,
                                          TILE_SIZE_IN_LINES)
        
        pygame.display.set_icon(pygame.image.load(ICON_PATH).convert_alpha())
        
        lpBuffer = wintypes.LPWSTR()
        AppUserModelID = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID
        AppUserModelID(ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR))
        ctypes.windll.kernel32.LocalFree(lpBuffer)
        
        self.reward = 0
        self.game_over = False
        self.score = 0
        self.snake_face = 0
        self.frame_counter = 1
        
        self.step_timer: float = 0
        # self.game_timer: float = 0
    
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
        score_text = self.font.render(str(self.score), True, (255, 255, 255))
        self.screen.blit(score_text, (30, 20))
    
    def reset(self):
        self.snake = Snake()
        self.snake_face = 0
        # self.game_timer = 0
        self.game_over = False
        self.score = 0
        self.endf = perf_counter()
    
    def wait(self):
        endf = perf_counter()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.end()
                    elif event.key == pygame.K_r:
                        self.reset()
                        return
                elif event.type == pygame.QUIT:
                    self.end()
            
            startf = endf
            endf = perf_counter()
            dt = endf - startf
            pygame.display.set_caption(f"fps: {1/dt:.2f}")
            self.clock.tick(15)
    
    def play_step(self, dt: float, move: Literal[0, 1, 2, 3]):
        # if move == 1:
        #     self.snake_face += 1
        # elif move == 2:
        #     self.snake_face -= 1
        # self.snake_face %= 3
        self.snake_face = move
        
        self.step_timer += dt
        # self.game_timer += dt
        pygame.display.set_caption(f"fps: {1/dt:.2f}")
        
        # timer += self.clock.get_time()
        # pygame.display.set_caption(f"fps: {self.clock.get_fps():.2f}")
        
        self.frame_counter %= FRAME_BREAKER
        if not self.frame_counter and self.step_timer >= SPEED:
            rng = int(self.step_timer / SPEED)
            self.step_timer %= SPEED
            for _ in range(rng):
                self.render()
                if self.snake.collision(self.food_rect):
                    self.game_timer = 0
                    self.score += 1
                    self.reward = 10
                    while self.food_rect.topleft in [rect.topleft for rect in self.snake.body]:
                        self.generate_random_food()
                
                self.snake.go(self.snake_face)
                
                if self.snake.self_hit():
                    self.reward = -10
                    self.game_over = True
                    self.render()
                    pygame.display.flip()
                    self.wait()
        
        self.frame_counter += 1
    
        pygame.display.flip()
        self.clock.tick(TFPS)
        
        return self.reward, self.game_over, self.score
    
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.snake_face = 0
                    #-- for rotating clockwise --#
                    # self.snake_face += 1
                    # self.snake_face %= 4
                elif event.key == pygame.K_LEFT:
                    self.snake_face = 2
                    #-- for rotating counter-clockwise --#
                    # self.snake_face -= 1
                    # self.snake_face %= 4
                elif event.key == pygame.K_UP:
                    self.snake_face = 3
                elif event.key == pygame.K_DOWN:
                    self.snake_face = 1
                
                if event.key == pygame.K_ESCAPE:
                    self.end()
            
            if event.type == pygame.QUIT:
                self.end()
        return self.snake_face
    
    def generate_random_food(self):
        self.food_rect = pygame.rect.Rect(randint(0, TILES_IN_WIDTH -1)*TILE_SIZE + HALF_LINE_WIDTH,
                                          randint(0, TILES_IN_HEIGHT-1)*TILE_SIZE + HALF_LINE_WIDTH,
                                          TILE_SIZE_IN_LINES,
                                          TILE_SIZE_IN_LINES)
    
    def run(self):
        self.endf = perf_counter()
        
        self.render()
        pygame.display.flip()
        
        while True:
            startf = self.endf
            self.endf = perf_counter()
            dt = self.endf - startf
            
            self.play_step(dt, self.check_events())


if __name__ == "__main__":
    game = Game()
    game.run()