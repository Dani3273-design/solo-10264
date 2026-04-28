import pygame
import threading
import time
import os

class TicTacToeGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.WIDTH = 600
        self.HEIGHT = 700
        self.CELL_SIZE = 200
        self.BOARD_TOP = 50
        self.BOARD_SIZE = 600
        
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (200, 200, 200)
        self.DARK_GRAY = (150, 150, 150)
        self.GREEN = (0, 200, 0)
        self.BLUE = (50, 150, 255)
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("井字棋游戏")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        self._init_sounds()
        self._init_fonts()
        self._init_game_state()
        
    def _init_sounds(self):
        self.sound_available = True
        try:
            sample_rate = 44100
            duration = 0.1
            
            self.move_sound = self._generate_sound(440, duration)
            self.win_sound = self._generate_sound(880, 0.3)
            self.lose_sound = self._generate_sound(220, 0.5)
            self.draw_sound = self._generate_sound(550, 0.2)
            
        except Exception as e:
            print(f"音效初始化失败: {e}")
            self.sound_available = False
    
    def _generate_sound(self, frequency, duration):
        sample_rate = 44100
        n_samples = int(round(duration * sample_rate))
        import math
        import array
        
        buf = array.array('h', [0] * n_samples)
        max_sample = 2**15 - 1
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            buf[i] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
        
        sound = pygame.mixer.Sound(buffer=buf)
        sound.set_volume(0.3)
        return sound
    
    def _play_sound(self, sound_type):
        if not self.sound_available:
            return
        
        try:
            if sound_type == "move":
                self.move_sound.play()
            elif sound_type == "win":
                self.win_sound.play()
            elif sound_type == "lose":
                self.lose_sound.play()
            elif sound_type == "draw":
                self.draw_sound.play()
        except:
            pass
    
    def _init_fonts(self):
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/SimHei.ttf",
        ]
        
        self.title_font = None
        self.normal_font = None
        self.timer_font = None
        self.button_font = None
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    self.title_font = pygame.font.Font(font_path, 48)
                    self.normal_font = pygame.font.Font(font_path, 36)
                    self.timer_font = pygame.font.Font(font_path, 48)
                    self.button_font = pygame.font.Font(font_path, 32)
                    print(f"成功加载字体: {font_path}")
                    break
                except:
                    continue
        
        if self.title_font is None:
            print("使用默认字体，中文可能显示异常")
            self.title_font = pygame.font.SysFont(None, 48)
            self.normal_font = pygame.font.SysFont(None, 36)
            self.timer_font = pygame.font.SysFont(None, 48)
            self.button_font = pygame.font.SysFont(None, 32)
    
    def _init_game_state(self):
        self.board = [[None, None, None], [None, None, None], [None, None, None]]
        self.current_player = "O"
        self.game_state = "start"
        self.winner = None
        self.win_pattern = None
        self.timer = 10.0
        self.last_time = time.time()
        self.win_check_lock = threading.Lock()
        self.win_thread = None
    
    def _check_win_pattern(self, board, player):
        patterns = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]
        
        for pattern in patterns:
            if all(board[row][col] == player for row, col in pattern):
                return pattern
        return None
    
    def _check_board_full(self, board):
        return all(board[row][col] is not None for row in range(3) for col in range(3))
    
    def _win_check_worker(self, board, player):
        time.sleep(0.01)
        
        with self.win_check_lock:
            if self.game_state != "playing":
                return
            
            win_pattern = self._check_win_pattern(board, player)
            
            if win_pattern:
                self.winner = player
                self.win_pattern = win_pattern
                self.game_state = "game_over"
                self._play_sound("win")
            elif self._check_board_full(board):
                self.winner = "draw"
                self.game_state = "game_over"
                self._play_sound("draw")
    
    def _start_win_check(self, player):
        board_copy = [row.copy() for row in self.board]
        
        if self.win_thread and self.win_thread.is_alive():
            self.win_thread.join(timeout=1.0)
        
        self.win_thread = threading.Thread(
            target=self._win_check_worker,
            args=(board_copy, player),
            daemon=True
        )
        self.win_thread.start()
    
    def _get_cell_pos(self, mouse_pos):
        x, y = mouse_pos
        if y < self.BOARD_TOP or y > self.BOARD_TOP + self.BOARD_SIZE:
            return None
        
        col = x // self.CELL_SIZE
        row = (y - self.BOARD_TOP) // self.CELL_SIZE
        
        if 0 <= row < 3 and 0 <= col < 3:
            return row, col
        return None
    
    def _make_move(self, row, col):
        if self.board[row][col] is not None:
            return
        
        self.board[row][col] = self.current_player
        self._play_sound("move")
        
        self._start_win_check(self.current_player)
        
        if self.game_state == "playing":
            self.current_player = "X" if self.current_player == "O" else "O"
            self.timer = 10.0
            self.last_time = time.time()
    
    def _forfeit(self):
        self.winner = "X" if self.current_player == "O" else "O"
        self.game_state = "game_over"
        self._play_sound("lose")
    
    def _timeout(self):
        self.winner = "X" if self.current_player == "O" else "O"
        self.game_state = "game_over"
        self._play_sound("lose")
    
    def _draw_board(self):
        self.screen.fill(self.WHITE)
        
        for i in range(1, 3):
            pygame.draw.line(self.screen, self.BLACK, 
                           (i * self.CELL_SIZE, self.BOARD_TOP), 
                           (i * self.CELL_SIZE, self.BOARD_TOP + self.BOARD_SIZE), 4)
            pygame.draw.line(self.screen, self.BLACK,
                           (0, self.BOARD_TOP + i * self.CELL_SIZE),
                           (self.WIDTH, self.BOARD_TOP + i * self.CELL_SIZE), 4)
        
        for row in range(3):
            for col in range(3):
                x = col * self.CELL_SIZE + self.CELL_SIZE // 2
                y = self.BOARD_TOP + row * self.CELL_SIZE + self.CELL_SIZE // 2
                
                if self.board[row][col] == "O":
                    pygame.draw.circle(self.screen, self.RED, (x, y), 70, 6)
                elif self.board[row][col] == "X":
                    offset = 50
                    pygame.draw.line(self.screen, self.BLACK,
                                   (x - offset, y - offset),
                                   (x + offset, y + offset), 6)
                    pygame.draw.line(self.screen, self.BLACK,
                                   (x + offset, y - offset),
                                   (x - offset, y + offset), 6)
        
        if self.win_pattern and self.winner != "draw":
            start = self.win_pattern[0]
            end = self.win_pattern[2]
            start_x = start[1] * self.CELL_SIZE + self.CELL_SIZE // 2
            start_y = self.BOARD_TOP + start[0] * self.CELL_SIZE + self.CELL_SIZE // 2
            end_x = end[1] * self.CELL_SIZE + self.CELL_SIZE // 2
            end_y = self.BOARD_TOP + end[0] * self.CELL_SIZE + self.CELL_SIZE // 2
            pygame.draw.line(self.screen, self.GREEN, (start_x, start_y), (end_x, end_y), 10)
    
    def _draw_timer(self):
        current_time = time.time()
        elapsed = current_time - self.last_time
        self.timer = max(0, self.timer - elapsed)
        self.last_time = current_time
        
        if self.timer <= 0 and self.game_state == "playing":
            self._timeout()
        
        timer_text = f"{self.timer:.1f}秒"
        if self.timer <= 3:
            color = self.RED
        else:
            color = self.BLACK
        
        text = self.normal_font.render(timer_text, True, color)
        text_rect = text.get_rect(midright=(self.WIDTH - 10, 25))
        self.screen.blit(text, text_rect)
        
        player_text = f"{'红圈(O)' if self.current_player == 'O' else '黑叉(X)'}的回合"
        p_text = self.normal_font.render(player_text, True, self.RED if self.current_player == "O" else self.BLACK)
        p_rect = p_text.get_rect(midleft=(10, 25))
        self.screen.blit(p_text, p_rect)
    
    def _draw_button(self, text, x, y, width, height, color, hover_color, action=None, text_color=None):
        if text_color is None:
            text_color = self.BLACK
        
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        if x < mouse[0] < x + width and y < mouse[1] < y + height:
            pygame.draw.rect(self.screen, hover_color, (x, y, width, height))
            if click[0] == 1 and action:
                time.sleep(0.1)
                action()
        else:
            pygame.draw.rect(self.screen, color, (x, y, width, height))
        
        pygame.draw.rect(self.screen, self.BLACK, (x, y, width, height), 2)
        
        text_surf = self.button_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surf, text_rect)
    
    def _draw_start_screen(self):
        self.screen.fill(self.WHITE)
        
        title = self.title_font.render("井字棋游戏", True, self.BLACK)
        title_rect = title.get_rect(center=(self.WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        info1 = self.normal_font.render("红圈(O)先手，黑叉(X)后手", True, self.DARK_GRAY)
        info1_rect = info1.get_rect(center=(self.WIDTH // 2, 250))
        self.screen.blit(info1, info1_rect)
        
        info2 = self.normal_font.render("每步限时10秒，超时判负", True, self.DARK_GRAY)
        info2_rect = info2.get_rect(center=(self.WIDTH // 2, 300))
        self.screen.blit(info2, info2_rect)
        
        self._draw_button("开始游戏", 200, 400, 200, 60, self.GREEN, (0, 255, 0), self._start_game)
    
    def _start_game(self):
        self._init_game_state()
        self.game_state = "playing"
        self.last_time = time.time()
    
    def _draw_game_over_screen(self):
        self._draw_board()
        
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(242)
        overlay.fill(self.WHITE)
        self.screen.blit(overlay, (0, 0))
        
        if self.winner == "draw":
            result_text = "平局"
            color = self.DARK_GRAY
        else:
            result_text = f"{'红圈(O)' if self.winner == 'O' else '黑叉(X)'}获胜"
            color = self.RED if self.winner == "O" else self.BLACK
        
        title = self.title_font.render("游戏结束", True, self.BLACK)
        title_rect = title.get_rect(center=(self.WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        result = self.title_font.render(result_text, True, color)
        result_rect = result.get_rect(center=(self.WIDTH // 2, 250))
        self.screen.blit(result, result_rect)
        
        self._draw_button("重新开始", 200, 350, 200, 60, self.GREEN, (0, 255, 0), self._start_game)
        self._draw_button("返回主菜单", 200, 430, 200, 60, self.GRAY, self.DARK_GRAY, self._back_to_start)
    
    def _back_to_start(self):
        self._init_game_state()
        self.game_state = "start"
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "playing":
                    cell_pos = self._get_cell_pos(event.pos)
                    if cell_pos:
                        row, col = cell_pos
                        self._make_move(row, col)
            
            if self.game_state == "start":
                self._draw_start_screen()
            elif self.game_state == "playing":
                self._draw_board()
                self._draw_timer()
                self._draw_button("认输", 480, 660, 100, 35, self.RED, (200, 0, 0), self._forfeit, self.WHITE)
            elif self.game_state == "game_over":
                self._draw_game_over_screen()
            
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        if self.win_thread and self.win_thread.is_alive():
            self.win_thread.join(timeout=1.0)
        
        pygame.quit()
