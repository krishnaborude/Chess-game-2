import pygame
import sys
import random
import time
import math
 
# Initialize Pygame
pygame.init()
 
# Constants
WINDOW_SIZE = 680
BOARD_SIZE = 8
SQUARE_SIZE = (WINDOW_SIZE - 100) // BOARD_SIZE  # Reduced square size to make room for player names
BOARD_OFFSET_Y = 50  # Space for player names at top and bottom
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
HIGHLIGHT = (255, 255, 0, 128)
VALID_MOVE = (0, 255, 0, 128)
FPS = 60
 
# Colors for the board
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
 
# Add these colors to the constants section at the top
SELECTED_PIECE = (255, 255, 0, 180)  # Brighter yellow for selected piece
VALID_MOVE_HIGHLIGHT = (124, 252, 0, 160)  # Bright green for valid moves
LAST_MOVE = (135, 206, 250, 160)  # Light blue for showing last move
CHECKED_KING = (255, 0, 0, 180)  # Red highlight for checked king
AI_MOVE_HIGHLIGHT = (255, 165, 0, 160)  # Orange highlight for AI moves
AI_MOVE_START = (255, 140, 0, 180)  # Darker orange for AI move start
AI_MOVE_END = (255, 165, 0, 180)  # Lighter orange for AI move end
 
# Menu colors
MENU_BG = (30, 30, 40)  # Dark background
MENU_TITLE_COLOR = (220, 220, 230)  # Light text for titles
MENU_TEXT_COLOR = (200, 200, 210)  # Light text for content
MENU_BUTTON_BG = (45, 45, 55)  # Dark button background
MENU_BUTTON_HOVER = (55, 55, 65)  # Lighter on hover
MENU_BUTTON_SELECTED = (65, 65, 75)  # Even lighter when selected
MENU_BORDER_COLOR = (75, 75, 85)  # Gray borders
MENU_ACCENT_COLOR = (100, 149, 237)  # Cornflower blue accent
MENU_MARGIN = 40
MENU_PADDING = 20  # Padding between elements

# AI settings
AI_SPEEDS = {
    'easy': {'move': 500, 'thinking': 500},
    'medium': {'move': 300, 'thinking': 1000},
    'hard': {'move': 200, 'thinking': 1500}
}

AI_DEPTH = {
    'easy': 2,
    'medium': 3,
    'hard': 4
}
 
# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Chess Game")
 
# Chess piece Unicode characters
PIECES = {
    'white': {
        'king': '♔',
        'queen': '♕',
        'rook': '♖',
        'bishop': '♗',
        'knight': '♘',
        'pawn': '♙'
    },
    'black': {
        'king': '♚',
        'queen': '♛',
        'rook': '♜',
        'bishop': '♝',
        'knight': '♞',
        'pawn': '♟'
    }
}
 
# Piece values for evaluation
PIECE_VALUES = {
    'pawn': 100,
    'knight': 320,
    'bishop': 330,
    'rook': 500,
    'queen': 900,
    'king': 20000
}
 
# Add these constants for skill measurement
SKILL_METRICS = {
    'piece_value': {
        'pawn': 1,
        'knight': 3,
        'bishop': 3,
        'rook': 5,
        'queen': 9,
        'king': 0
    },
    'position_bonus': {
        'center_control': 2,  # Bonus for controlling center squares
        'pawn_structure': 1,  # Bonus for good pawn structure
        'piece_development': 1.5,  # Bonus for developing pieces early
        'king_safety': 2  # Bonus for king safety
    }
}

class TextInput:
    def __init__(self, x, y, width, height, default_text, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = default_text
        self.default_text = default_text
        self.label = label
        self.active = False
        self.font = pygame.font.SysFont('Arial', 32)
        self.label_font = pygame.font.SysFont('Arial', 24)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # milliseconds

    def draw(self, surface):
        # Draw label above the input field
        label_surface = self.label_font.render(self.label, True, MENU_TEXT_COLOR)
        label_rect = label_surface.get_rect(bottomleft=(self.rect.left, self.rect.top - 5))
        surface.blit(label_surface, label_rect)

        # Draw input background
        bg_color = MENU_BUTTON_HOVER if self.active else MENU_BUTTON_BG
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, MENU_ACCENT_COLOR if self.active else MENU_BORDER_COLOR, self.rect, 2, border_radius=5)

        # Draw text
        text_color = MENU_TEXT_COLOR if self.text != self.default_text else (128, 128, 128)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)

        # Draw cursor if active
        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2
            if cursor_x < self.rect.right - 10:  # Ensure cursor stays within bounds
                pygame.draw.line(surface, MENU_TEXT_COLOR,
                               (cursor_x, self.rect.centery - 15),
                               (cursor_x, self.rect.centery + 15), 2)

        # Update cursor blink
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                if self.text == self.default_text:
                    self.text = ""
            else:
                self.active = False
                if self.text == "":
                    self.text = self.default_text

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Only add character if there's room in the input field
                if self.font.size(self.text + event.unicode)[0] < self.rect.width - 20:
                    self.text += event.unicode
 
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.selected = False
        self.hover = False
        self.animation_offset = 0
        self.animation_speed = 0.2
        self.target_offset = 0
        self.glow_alpha = 0
        self.glow_direction = 1
 
    def draw(self, surface):
        # Draw shadow effect
        shadow_offset = 4
        shadow_rect = self.rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        pygame.draw.rect(surface, (20, 20, 30), shadow_rect, border_radius=12)
        
        # Create animated rect
        animated_rect = self.rect.copy()
        animated_rect.y += self.animation_offset
        
        # Update glow effect
        if self.hover:
            self.glow_alpha = min(60, self.glow_alpha + 4)
        else:
            self.glow_alpha = max(0, self.glow_alpha - 4)
        
        # Draw glow effect if hovering
        if self.glow_alpha > 0:
            glow_surface = pygame.Surface((animated_rect.width + 20, animated_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*MENU_ACCENT_COLOR[:3], self.glow_alpha), 
                           (10, 10, animated_rect.width, animated_rect.height), 
                           border_radius=12)
            surface.blit(glow_surface, (animated_rect.x - 10, animated_rect.y - 10))
        
        # Draw button background with hover/selected effect
        if self.hover:
            bg_color = MENU_BUTTON_HOVER
            border_color = MENU_ACCENT_COLOR
        elif self.selected:
            bg_color = MENU_BUTTON_SELECTED
            border_color = MENU_ACCENT_COLOR
        else:
            bg_color = MENU_BUTTON_BG
            border_color = MENU_BORDER_COLOR
        
        # Draw main button with rounded corners
        pygame.draw.rect(surface, bg_color, animated_rect, border_radius=12)
        pygame.draw.rect(surface, border_color, animated_rect, 2, border_radius=12)
        
        # Draw text with enhanced visibility
        font = pygame.font.SysFont('Arial', 36, bold=True)
        
        # Draw multiple text shadows for better depth
        shadow_offsets = [(2, 2), (1, 1)]
        for offset_x, offset_y in shadow_offsets:
            shadow_text = font.render(self.text, True, (20, 20, 30))
            shadow_rect = shadow_text.get_rect(center=(animated_rect.centerx + offset_x, 
                                                     animated_rect.centery + offset_y))
            surface.blit(shadow_text, shadow_rect)
        
        # Draw main text with better contrast
        text_surface = font.render(self.text, True, MENU_TITLE_COLOR)
        text_rect = text_surface.get_rect(center=animated_rect.center)
        surface.blit(text_surface, text_rect)
 
class PromotionButton:
    def __init__(self, x, y, width, height, piece_type, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.piece_type = piece_type
        self.color = color
        self.hover = False

    def draw(self, screen):
        # Draw button background with shadow and hover effect
        shadow_offset = 3
        shadow_rect = self.rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        pygame.draw.rect(screen, (20, 20, 30), shadow_rect, border_radius=12)  # Shadow
        
        # Button background
        bg_color = (65, 65, 75) if self.hover else (55, 55, 65)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=12)
        
        # Button border
        border_color = (100, 149, 237) if self.hover else (75, 75, 85)  # Blue border on hover
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=12)
        
        # Draw piece with larger size and better positioning
        font_size = int(self.rect.height * 0.7)  # Piece takes up 70% of button height
        font = pygame.font.SysFont('segoeuisymbol', font_size)
        text = font.render(PIECES[self.color][self.piece_type], True, WHITE if self.color == 'white' else BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

class PlayerStats:
    def __init__(self, color):
        self.color = color
        self.pieces_captured = []
        self.moves_made = 0
        self.center_control_moves = 0
        self.pieces_developed = set()
        self.check_moves = 0
        self.pawn_structure_score = 0
        self.king_safety_score = 0
        
    def update_stats(self, board, move_from, move_to, captured_piece=None):
        self.moves_made += 1
        
        # Track captured pieces
        if captured_piece:
            self.pieces_captured.append(captured_piece)
        
        # Check for center control (squares e4, e5, d4, d5)
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if move_to in center_squares:
            self.center_control_moves += 1
        
        # Track piece development
        piece = board[move_to[0]][move_to[1]]
        if piece and piece[1] != 'pawn' and piece[1] != 'king':
            self.pieces_developed.add((piece[1], move_from))
        
        # Update pawn structure score
        self.update_pawn_structure(board)
        
        # Update king safety score
        self.update_king_safety(board)
    
    def update_pawn_structure(self, board):
        self.pawn_structure_score = 0
        for col in range(BOARD_SIZE):
            pawn_count = 0
            for row in range(BOARD_SIZE):
                piece = board[row][col]
                if piece and piece[0] == self.color and piece[1] == 'pawn':
                    pawn_count += 1
            # Penalize doubled pawns, reward connected pawns
            if pawn_count > 1:
                self.pawn_structure_score -= 1
            elif pawn_count == 1:
                self.pawn_structure_score += 1
    
    def update_king_safety(self, board):
        # Find king position
        king_pos = None
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                if piece and piece[0] == self.color and piece[1] == 'king':
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if king_pos:
            # Check pawns in front of king
            self.king_safety_score = 0
            row, col = king_pos
            pawn_shield = 0
            for r in range(max(0, row-1), min(BOARD_SIZE, row+2)):
                for c in range(max(0, col-1), min(BOARD_SIZE, col+2)):
                    piece = board[r][c]
                    if piece and piece[0] == self.color and piece[1] == 'pawn':
                        pawn_shield += 1
            self.king_safety_score = pawn_shield * 0.5

    def calculate_skill_rating(self):
        # Base score starts at 1000
        score = 1000
        
        # Add points for captured pieces
        for piece in self.pieces_captured:
            score += SKILL_METRICS['piece_value'][piece[1]] * 10
        
        # Add points for center control
        score += self.center_control_moves * SKILL_METRICS['position_bonus']['center_control'] * 15
        
        # Add points for piece development
        score += len(self.pieces_developed) * SKILL_METRICS['position_bonus']['piece_development'] * 20
        
        # Add points for pawn structure
        score += self.pawn_structure_score * SKILL_METRICS['position_bonus']['pawn_structure'] * 10
        
        # Add points for king safety
        score += self.king_safety_score * SKILL_METRICS['position_bonus']['king_safety'] * 15
        
        # Add bonus for checkmate
        if self.check_moves > 0:
            score += self.check_moves * 25
        
        return int(score)

class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 1
        self.particles = []
        self.alive = True
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        self.create_particles()
    
    def create_particles(self):
        num_particles = 30
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(2, 6)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'dx': dx,
                'dy': dy,
                'alpha': 255
            })
    
    def update(self):
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['dy'] += 0.1  # Gravity
            particle['alpha'] = max(0, particle['alpha'] - 3)
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p['alpha'] > 0]
        if not self.particles:
            self.alive = False
    
    def draw(self, screen):
        for particle in self.particles:
            surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, particle['alpha']), (2, 2), 2)
            screen.blit(surface, (particle['x'] - 2, particle['y'] - 2))

def get_player_name(title):
    clock = pygame.time.Clock()
    
    # Draw subtitle
    font_subtitle = pygame.font.SysFont('Arial', 36, bold=True)
    subtitle = font_subtitle.render("Enter Player Name", True, MENU_TEXT_COLOR)
    subtitle_rect = subtitle.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE//2 - 80))
    screen.blit(subtitle, subtitle_rect)
    
    # Create text input
    input_width = 400
    input_height = 60
    input_field = TextInput(
        WINDOW_SIZE//2 - input_width//2,
        WINDOW_SIZE//2 - input_height//2,
        input_width,
        input_height,
        "",
        "Enter Player Name"  # Changed default text
    )
    
    # Create back and next buttons
    button_width = 300
    button_height = 60
    next_button = Button(WINDOW_SIZE//2 - button_width//2, WINDOW_SIZE//2 + 100, button_width, button_height, "Next", MENU_BUTTON_BG)
    back_button = Button(20, 20, 120, 50, "Back", MENU_BUTTON_BG)
    
    while True:
        screen.fill(MENU_BG)
        
        # Draw background pattern
        for i in range(MENU_MARGIN, WINDOW_SIZE - MENU_MARGIN, 40):
            pygame.draw.line(screen, (35, 35, 45), (i, MENU_MARGIN), (i, WINDOW_SIZE - MENU_MARGIN))
            pygame.draw.line(screen, (35, 35, 45), (MENU_MARGIN, i), (WINDOW_SIZE - MENU_MARGIN, i))
        
        # Draw title with shadow effect
        font_title = pygame.font.SysFont('Arial', 72, bold=True)
        
        # Multiple shadow layers for depth
        for offset in range(4, 0, -1):
            shadow = font_title.render("Chess Game", True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(WINDOW_SIZE // 2 + offset, 120 + offset))
            screen.blit(shadow, shadow_rect)
        
        # Main title
        title = font_title.render("Chess Game", True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_SIZE // 2, 120))
        screen.blit(title, title_rect)
        
        # Draw subtitle
        font_subtitle = pygame.font.SysFont('Arial', 36, bold=True)
        subtitle = font_subtitle.render("Enter Player Name", True, MENU_TEXT_COLOR)  # Fixed subtitle text
        subtitle_rect = subtitle.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE//2 - 80))
        screen.blit(subtitle, subtitle_rect)
        
        # Draw input field and buttons
        input_field.draw(screen)
        back_button.draw(screen)
        if input_field.text and input_field.text != input_field.default_text:
            next_button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle text input
            input_field.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if back_button.rect.collidepoint(mouse_pos):
                    return None
                elif next_button.rect.collidepoint(mouse_pos) and input_field.text and input_field.text != input_field.default_text:
                    next_button.selected = True
                    pygame.display.flip()
                    pygame.time.wait(200)
                    return input_field.text
            
            # Handle hover effects
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                back_button.hover = back_button.rect.collidepoint(mouse_pos)
                if input_field.text and input_field.text != input_field.default_text:
                    next_button.hover = next_button.rect.collidepoint(mouse_pos)
        
        clock.tick(FPS)

def get_ai_difficulty():
    clock = pygame.time.Clock()
   
    # Create buttons
    button_width = 300
    button_height = 60
    button_spacing = 40
    center_y = WINDOW_SIZE // 2
    
    # Draw subtitle
    font_subtitle = pygame.font.SysFont('Arial', 36, bold=True)
    subtitle = font_subtitle.render("Select Difficulty", True, MENU_TEXT_COLOR)
    subtitle_rect = subtitle.get_rect(center=(WINDOW_SIZE // 2, 200))  # Fixed position
    screen.blit(subtitle, subtitle_rect)
    
    # Create difficulty buttons
    difficulty_start_y = 250  # Fixed starting position
    difficulty_buttons = [
        Button(WINDOW_SIZE//2 - button_width//2, difficulty_start_y, button_width, button_height, "Easy", MENU_BUTTON_BG),
        Button(WINDOW_SIZE//2 - button_width//2, difficulty_start_y + button_height + button_spacing, button_width, button_height, "Medium", MENU_BUTTON_BG),
        Button(WINDOW_SIZE//2 - button_width//2, difficulty_start_y + 2 * (button_height + button_spacing), button_width, button_height, "Hard", MENU_BUTTON_BG)
    ]
    
    # Create back button
    back_button = Button(20, 20, 120, 50, "Back", MENU_BUTTON_BG)
    
    # Create start button
    start_button = Button(WINDOW_SIZE//2 - button_width//2, difficulty_start_y + 3 * (button_height + button_spacing), button_width, button_height, "Start Game", MENU_BUTTON_BG)
    
    # Initialize button states
    buttons = difficulty_buttons + [start_button]
    for button in buttons:
        button.animation_offset = 50  # Start with offset
        button.target_offset = 0      # Target position
    
    selected_difficulty = None
   
    while True:
        # Handle animations
        for button in buttons:
            if button.animation_offset > 0:
                button.animation_offset = max(0, button.animation_offset - 3)  # Smooth animation
        
        screen.fill(MENU_BG)
        
        # Draw background pattern
        for i in range(MENU_MARGIN, WINDOW_SIZE - MENU_MARGIN, 40):
            pygame.draw.line(screen, (35, 35, 45), (i, MENU_MARGIN), (i, WINDOW_SIZE - MENU_MARGIN))
            pygame.draw.line(screen, (35, 35, 45), (MENU_MARGIN, i), (WINDOW_SIZE - MENU_MARGIN, i))
        
        # Draw title with shadow effect
        font_title = pygame.font.SysFont('Arial', 72, bold=True)
        
        # Multiple shadow layers for depth
        for offset in range(4, 0, -1):
            shadow = font_title.render("Chess Game", True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(WINDOW_SIZE // 2 + offset, 120 + offset))
            screen.blit(shadow, shadow_rect)
        
        # Main title
        title = font_title.render("Chess Game", True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_SIZE // 2, 120))
        screen.blit(title, title_rect)
       
        # Draw buttons
        back_button.draw(screen)
        for button in difficulty_buttons:
            button.draw(screen)
       
        if selected_difficulty:
            start_button.draw(screen)
       
        pygame.display.flip()
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
               
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
               
                if back_button.rect.collidepoint(mouse_pos):
                    return None
                
                for i, button in enumerate(difficulty_buttons):
                    if button.rect.collidepoint(mouse_pos):
                        selected_difficulty = ["easy", "medium", "hard"][i]
                        for b in difficulty_buttons:
                            b.selected = False
                        button.selected = True
                
                if selected_difficulty and start_button.rect.collidepoint(mouse_pos):
                    start_button.selected = True
                    pygame.display.flip()
                    pygame.time.wait(200)
                    return selected_difficulty
            
            # Handle hover effects
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                back_button.hover = back_button.rect.collidepoint(mouse_pos)
                for button in difficulty_buttons:
                    button.hover = button.rect.collidepoint(mouse_pos)
                if selected_difficulty:
                    start_button.hover = start_button.rect.collidepoint(mouse_pos)
        
        clock.tick(FPS)

def menu_loop():
    clock = pygame.time.Clock()
    
    while True:
        # Get game mode selection
        game_mode = game_mode_selection_loop()
        if game_mode is None:
            continue
            
        # Get side selection
        is_white = side_selection_loop()
        if is_white is None:
            continue
            
        # Get player names and difficulty based on game mode
        if game_mode == "PvP":
            player1_name = get_player_name("Player 1")
            if player1_name is None:
                continue
            player2_name = get_player_name("Player 2")
            if player2_name is None:
                continue
            return game_mode, None, player1_name, player2_name, is_white
        else:  # AI mode
            player_name = get_player_name("Player")
            if player_name is None:
                continue
            ai_speed = get_ai_difficulty()
            if ai_speed is None:
                continue
            return game_mode, ai_speed, player_name, "AI", is_white

def game_mode_selection_loop():
    clock = pygame.time.Clock()
    
    # Create buttons
    button_width = 300
    button_height = 60
    button_spacing = 40
    center_y = WINDOW_SIZE // 2
    
    # Create mode selection buttons
    pvp_button = Button(WINDOW_SIZE//2 - button_width//2, center_y - 100, button_width, button_height, "Play with Friend", MENU_BUTTON_BG)
    ai_button = Button(WINDOW_SIZE//2 - button_width//2, center_y - 20, button_width, button_height, "Play with AI", MENU_BUTTON_BG)
    
    # Initialize button states
    buttons = [pvp_button, ai_button]
    for button in buttons:
        button.animation_offset = 50  # Start with offset
        button.target_offset = 0      # Target position
    
    while True:
        # Handle animations
        for button in buttons:
            if button.animation_offset > 0:
                button.animation_offset = max(0, button.animation_offset - 3)  # Smooth animation
        
        # Draw background
        screen.fill(MENU_BG)
        
        # Draw background pattern
        for i in range(MENU_MARGIN, WINDOW_SIZE - MENU_MARGIN, 40):
            pygame.draw.line(screen, (35, 35, 45), (i, MENU_MARGIN), (i, WINDOW_SIZE - MENU_MARGIN))
            pygame.draw.line(screen, (35, 35, 45), (MENU_MARGIN, i), (WINDOW_SIZE - MENU_MARGIN, i))
        
        # Draw title with shadow effect
        font_title = pygame.font.SysFont('Arial', 72, bold=True)
        
        # Multiple shadow layers for depth
        for offset in range(4, 0, -1):
            shadow = font_title.render("Chess Game", True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(WINDOW_SIZE // 2 + offset, 120 + offset))
            screen.blit(shadow, shadow_rect)
        
        # Main title
        title = font_title.render("Chess Game", True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(center=(WINDOW_SIZE // 2, 120))
        screen.blit(title, title_rect)
        
        # Draw buttons
        for button in buttons:
            button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if pvp_button.rect.collidepoint(mouse_pos):
                    pvp_button.selected = True
                    pygame.display.flip()
                    pygame.time.wait(200)
                    return "PvP"
                elif ai_button.rect.collidepoint(mouse_pos):
                    ai_button.selected = True
                    pygame.display.flip()
                    pygame.time.wait(200)
                    return "AI"
            
            # Handle hover effects
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                for button in buttons:
                    button.hover = button.rect.collidepoint(mouse_pos)
        
        clock.tick(FPS)
 
# Game logic functions
def get_raw_moves(board, start_pos, piece):
    """Get moves without considering check (to avoid recursion)"""
    valid_moves = []
    row, col = start_pos
    piece_type = piece[1]
    piece_color = piece[0]
    
    # Determine pawn direction based on color and board orientation
    if is_white:  # White at bottom
        direction = -1 if piece_color == 'white' else 1
        start_row = 6 if piece_color == 'white' else 1
    else:  # Black at bottom
        direction = -1 if piece_color == 'black' else 1
        start_row = 6 if piece_color == 'black' else 1
 
    if piece_type == 'pawn':
        # Forward move
        new_row = row + direction
        if 0 <= new_row < BOARD_SIZE:
            if not board[new_row][col]:
                valid_moves.append((new_row, col))
                # Initial two-square move
                if row == start_row:
                    new_row = row + 2 * direction
                    if 0 <= new_row < BOARD_SIZE and not board[new_row][col]:
                        valid_moves.append((new_row, col))
       
        # Diagonal captures
        for dcol in [-1, 1]:
            new_col = col + dcol
            new_row = row + direction
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                target = board[new_row][new_col]
                if target and target[0] != piece_color:
                    valid_moves.append((new_row, new_col))
 
    elif piece_type in ['rook', 'bishop', 'queen']:
        directions = []
        if piece_type in ['rook', 'queen']:
            directions.extend([(0, 1), (0, -1), (1, 0), (-1, 0)])
        if piece_type in ['bishop', 'queen']:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
        
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            while 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                target = board[new_row][new_col]
                if not target:
                    valid_moves.append((new_row, new_col))
                else:
                    if target[0] != piece_color:
                        valid_moves.append((new_row, new_col))
                    break
                new_row += drow
                new_col += dcol
 
    elif piece_type == 'knight':
        moves = [
            (row + 2, col + 1), (row + 2, col - 1),
            (row - 2, col + 1), (row - 2, col - 1),
            (row + 1, col + 2), (row + 1, col - 2),
            (row - 1, col + 2), (row - 1, col - 2)
        ]
        for new_row, new_col in moves:
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                target = board[new_row][new_col]
                if not target or target[0] != piece_color:
                    valid_moves.append((new_row, new_col))
 
    elif piece_type == 'king':
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                target = board[new_row][new_col]
                if not target or target[0] != piece_color:
                    valid_moves.append((new_row, new_col))
    
    return valid_moves
 
def get_valid_moves(board, start_pos, piece):
    valid_moves = []
    raw_moves = get_raw_moves(board, start_pos, piece)
   
    # Test each move to ensure it doesn't leave or put the king in check
    for move in raw_moves:
        temp_board = [row[:] for row in board]
        temp_board[move[0]][move[1]] = piece
        temp_board[start_pos[0]][start_pos[1]] = ''
       
        if not is_in_check(temp_board, piece[0]):
            valid_moves.append(move)
 
    return valid_moves
 
def evaluate_board(board):
    score = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece:
                value = PIECE_VALUES[piece[1]]
                if piece[0] == 'white':
                    score += value
                else:
                    score -= value
    return score
 
# Add performance monitoring
def show_fps(screen, clock):
    font = pygame.font.SysFont('Arial', 20)
    fps = str(int(clock.get_fps()))
    fps_text = font.render(f'FPS: {fps}', True, BLACK)
    screen.blit(fps_text, (10, 10))
 
# Optimize minimax with move ordering and better pruning
def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0:
        return evaluate_board(board), None

    # Pre-calculate all valid moves and sort them by potential value
    moves = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece and piece[0] == ('white' if maximizing_player else 'black'):
                valid_moves = get_valid_moves(board, (row, col), piece)
                for move in valid_moves:
                    temp_board = [row[:] for row in board]
                    temp_board[move[0]][move[1]] = piece
                    temp_board[row][col] = ''
                    score = evaluate_board(temp_board)
                    moves.append((score, (row, col), move))

    # Sort moves by score
    moves.sort(reverse=maximizing_player)

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for _, start, end in moves:
            piece = board[start[0]][start[1]]
            temp_board = [row[:] for row in board]
            temp_board[end[0]][end[1]] = piece
            temp_board[start[0]][start[1]] = ''
            eval, _ = minimax(temp_board, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = (start, end)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for _, start, end in moves:
            piece = board[start[0]][start[1]]
            temp_board = [row[:] for row in board]
            temp_board[end[0]][end[1]] = piece
            temp_board[start[0]][start[1]] = ''
            eval, _ = minimax(temp_board, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = (start, end)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move
 
def make_ai_move(board):
    _, best_move = minimax(board, 3, float('-inf'), float('inf'), False)
    if best_move:
        start_pos, end_pos = best_move
        piece = board[start_pos[0]][start_pos[1]]
        board[end_pos[0]][end_pos[1]] = piece
        board[start_pos[0]][start_pos[1]] = ''
        return True
    return False
 
def make_easy_ai_move(board):
    """Make a simple move for easy AI mode with some randomness"""
    possible_moves = []
    # Collect all possible moves for black pieces
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece and piece[0] == 'black':
                valid_moves = get_valid_moves(board, (row, col), piece)
                for move in valid_moves:
                    possible_moves.append(((row, col), move))
    
    if possible_moves:
        # Randomly select a move from the possible moves
        start_pos, end_pos = random.choice(possible_moves)
        piece = board[start_pos[0]][start_pos[1]]
        board[end_pos[0]][end_pos[1]] = piece
        board[start_pos[0]][start_pos[1]] = ''
        return True, (start_pos, end_pos)
    return False, None
 
def create_board(white_at_bottom=True):
    board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    if white_at_bottom:
        # Set up pawns
        for i in range(BOARD_SIZE):
            board[6][i] = ('white', 'pawn')  # White pawns on row 6 (second from bottom)
            board[1][i] = ('black', 'pawn')  # Black pawns on row 1 (second from top)
        
        # Set up other pieces
        pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for i in range(BOARD_SIZE):
            board[7][i] = ('white', pieces[i])  # White pieces on bottom row
            board[0][i] = ('black', pieces[i])  # Black pieces on top row
    else:
        # Set up pawns for black at bottom
        for i in range(BOARD_SIZE):
            board[6][i] = ('black', 'pawn')  # Black pawns on row 6 (second from bottom)
            board[1][i] = ('white', 'pawn')  # White pawns on row 1 (second from top)
        
        # Set up other pieces for black at bottom
        pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for i in range(BOARD_SIZE):
            board[7][i] = ('black', pieces[i])  # Black pieces on bottom row
            board[0][i] = ('white', pieces[i])  # White pieces on top row
    
    return board
 
def draw_board(screen, selected_piece=None, valid_moves=None, last_move=None):
    # First draw the base board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE * SQUARE_SIZE) // 2, 
                                          row * SQUARE_SIZE + BOARD_OFFSET_Y, 
                                          SQUARE_SIZE, SQUARE_SIZE))
    
    # Draw last move highlight
    if last_move:
        start, end = last_move
        for pos in [start, end]:
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(128)
            s.fill(LAST_MOVE)
            screen.blit(s, (pos[1] * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE * SQUARE_SIZE) // 2,
                          pos[0] * SQUARE_SIZE + BOARD_OFFSET_Y))
    
    # Draw valid moves with better visibility
    if valid_moves:
        for row, col in valid_moves:
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(160)
            s.fill(VALID_MOVE_HIGHLIGHT)
            screen.blit(s, (col * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE * SQUARE_SIZE) // 2,
                          row * SQUARE_SIZE + BOARD_OFFSET_Y))
            # Draw a border around valid move squares
            pygame.draw.rect(screen, BLACK, (col * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE * SQUARE_SIZE) // 2,
                                          row * SQUARE_SIZE + BOARD_OFFSET_Y,
                                          SQUARE_SIZE, SQUARE_SIZE), 2)
    
    # Draw selected piece highlight
    if selected_piece:
        row, col = selected_piece
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(180)
        s.fill(SELECTED_PIECE)
        screen.blit(s, (col * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE * SQUARE_SIZE) // 2,
                       row * SQUARE_SIZE + BOARD_OFFSET_Y))
        pygame.draw.rect(screen, BLACK, (col * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE * SQUARE_SIZE) // 2,
                                       row * SQUARE_SIZE + BOARD_OFFSET_Y,
                                       SQUARE_SIZE, SQUARE_SIZE), 3)
    
    # Draw pieces with increased size and ensure they're centered
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece:
                color = WHITE if piece[0] == 'white' else BLACK
                # Increase font size to 80% of square size
                font = pygame.font.SysFont('segoeuisymbol', int(SQUARE_SIZE * 0.8))
                text = font.render(PIECES[piece[0]][piece[1]], True, color)
                # Center the piece in the square
                text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2 + (WINDOW_SIZE - BOARD_SIZE * SQUARE_SIZE) // 2,
                                                row * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_Y))
                screen.blit(text, text_rect)
                
                # Highlight king in check
                if piece[1] == 'king' and is_in_check(board, piece[0]):
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                    s.set_alpha(180)
                    s.fill(CHECKED_KING)
                    screen.blit(s, (col * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE * SQUARE_SIZE) // 2,
                                  row * SQUARE_SIZE + BOARD_OFFSET_Y))
                    pygame.draw.rect(screen, (255, 0, 0), (col * SQUARE_SIZE + (WINDOW_SIZE - BOARD_SIZE * SQUARE_SIZE) // 2,
                                                         row * SQUARE_SIZE + BOARD_OFFSET_Y,
                                                         SQUARE_SIZE, SQUARE_SIZE), 3)
 
def get_board_position(pos):
    x, y = pos
    # Adjust coordinates to account for board offset
    x = x - (WINDOW_SIZE - BOARD_SIZE * SQUARE_SIZE) // 2
    y = y - BOARD_OFFSET_Y
    
    # Check if the click is within the board boundaries
    if x < 0 or x >= BOARD_SIZE * SQUARE_SIZE or y < 0 or y >= BOARD_SIZE * SQUARE_SIZE:
        return None
        
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    
    # Ensure the position is within the board
    if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
        return None
        
    return row, col
 
def is_valid_move(start, end, piece):
    valid_moves = get_valid_moves(board, start, piece)
    return end in valid_moves
 
def is_in_check(board, color):
    # Find king position
    king_pos = None
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece and piece[0] == color and piece[1] == 'king':
                king_pos = (row, col)
                break
        if king_pos:
            break
   
    # Check if any opponent piece can attack the king
    opponent = 'black' if color == 'white' else 'white'
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece and piece[0] == opponent:
                moves = get_raw_moves(board, (row, col), piece)  # Use raw moves to avoid recursion
                if king_pos in moves:
                    return True
    return False
 
def is_checkmate(board, color):
    if not is_in_check(board, color):
        return False
   
    # Try all possible moves for all pieces
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece and piece[0] == color:
                valid_moves = get_valid_moves(board, (row, col), piece)
                for move in valid_moves:
                    # Try the move
                    temp_board = [row[:] for row in board]
                    temp_board[move[0]][move[1]] = piece
                    temp_board[row][col] = ''
                   
                    # If this move gets us out of check, it's not checkmate
                    if not is_in_check(temp_board, color):
                        return False
    return True
 
def is_stalemate(board, color):
    if is_in_check(board, color):
        return False
   
    # Check if any piece has valid moves
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece and piece[0] == color:
                valid_moves = get_valid_moves(board, (row, col), piece)
                if valid_moves:
                    return False
    return True
 
def draw_game_status(screen, current_player, is_check, is_mate):
    # Fill the top and bottom areas with a dark background
    pygame.draw.rect(screen, MENU_BG, (0, 0, WINDOW_SIZE, BOARD_OFFSET_Y))
    pygame.draw.rect(screen, MENU_BG, (0, WINDOW_SIZE - BOARD_OFFSET_Y, WINDOW_SIZE, BOARD_OFFSET_Y))
    
    # Draw player names with better visibility
    font = pygame.font.SysFont('Arial', 32, bold=True)
    
    # Draw white player name at top
    white_text = font.render(player1_name, True, MENU_TEXT_COLOR)
    white_rect = white_text.get_rect(center=(WINDOW_SIZE // 2, BOARD_OFFSET_Y // 2))
    # Add background for white player name
    bg_rect = white_rect.copy()
    bg_rect.inflate_ip(20, 10)
    pygame.draw.rect(screen, MENU_BUTTON_BG, bg_rect, border_radius=5)
    pygame.draw.rect(screen, MENU_BORDER_COLOR, bg_rect, 2, border_radius=5)
    screen.blit(white_text, white_rect)
    
    # Draw black player name at bottom
    black_text = font.render(player2_name, True, MENU_TEXT_COLOR)
    black_rect = black_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE - BOARD_OFFSET_Y // 2))
    # Add background for black player name
    bg_rect = black_rect.copy()
    bg_rect.inflate_ip(20, 10)
    pygame.draw.rect(screen, MENU_BUTTON_BG, bg_rect, border_radius=5)
    pygame.draw.rect(screen, MENU_BORDER_COLOR, bg_rect, 2, border_radius=5)
    screen.blit(black_text, black_rect)
    
    # Draw game status (check/checkmate) only if necessary
    if is_mate or is_check:
        status_text = ""
        text_color = MENU_TEXT_COLOR
        
        if is_mate:
            winner = "Black" if current_player == 'white' else "White"
            status_text = f"Checkmate! {winner} wins!"
        elif is_check:
            status_text = f"{current_player.capitalize()} is in CHECK!"
            text_color = RED
        
        if status_text:
            text_surface = font.render(status_text, True, text_color)
            text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
            # Draw background for text with padding
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(40, 20)
            pygame.draw.rect(screen, MENU_BUTTON_BG, bg_rect, border_radius=5)
            if is_check:
                pygame.draw.rect(screen, RED, bg_rect, 2, border_radius=5)
            else:
                pygame.draw.rect(screen, MENU_BORDER_COLOR, bg_rect, 2, border_radius=5)
            screen.blit(text_surface, text_rect)
 
def handle_pawn_promotion(board, pos, color):
    row, col = pos
    # Check if pawn has reached the opposite end based on board orientation
    if is_white:  # White pieces at bottom
        promotion_row = 0 if color == 'white' else 7
    else:  # Black pieces at bottom
        promotion_row = 7 if color == 'white' else 0
        
    if row == promotion_row:
        promoted_piece = show_promotion_menu(screen, pos, color)
        if promoted_piece:
            board[row][col] = (color, promoted_piece)
            return True
    return False

def show_promotion_menu(screen, pos, color):
    # Create semi-transparent overlay
    overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    
    # Create promotion menu background
    menu_width = 280
    menu_height = 280
    button_size = 80
    padding = 20
    
    # Position the menu in the center of the board
    menu_x = (WINDOW_SIZE - menu_width) // 2
    menu_y = (WINDOW_SIZE - menu_height) // 2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    
    # Draw menu background with rounded corners and shadow effect
    shadow_offset = 4
    shadow_rect = menu_rect.copy()
    shadow_rect.x += shadow_offset
    shadow_rect.y += shadow_offset
    pygame.draw.rect(screen, (20, 20, 30), shadow_rect, border_radius=15)  # Shadow
    pygame.draw.rect(screen, (45, 45, 55), menu_rect, border_radius=15)  # Main background
    pygame.draw.rect(screen, (75, 75, 85), menu_rect, 2, border_radius=15)  # Border
    
    # Draw title with better styling
    font = pygame.font.SysFont('Arial', 36, bold=True)
    title = font.render("Promote Pawn", True, MENU_TEXT_COLOR)
    title_rect = title.get_rect(center=(WINDOW_SIZE // 2, menu_y + 40))
    screen.blit(title, title_rect)
    
    # Calculate button positions in 2x2 grid with more space
    grid_width = 2 * button_size + padding
    grid_height = 2 * button_size + padding
    start_x = menu_x + (menu_width - grid_width) // 2
    start_y = menu_y + 80  # More space below title
    
    pieces = ['queen', 'rook', 'bishop', 'knight']
    buttons = []
    
    # Create buttons in 2x2 grid
    for i, piece in enumerate(pieces):
        row = i // 2
        col = i % 2
        x = start_x + col * (button_size + padding)
        y = start_y + row * (button_size + padding)
        buttons.append(PromotionButton(x, y, button_size, button_size, piece, color))
    
    # Event loop for promotion selection
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                for button in buttons:
                    button.hover = button.rect.collidepoint(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.rect.collidepoint(event.pos):
                        return button.piece_type
        
        # Draw buttons
        for button in buttons:
            button.draw(screen)
        
        pygame.display.flip()

def draw_side_selection():
    screen.fill(MENU_BG)
    
    # Draw subtle grid pattern in background
    for i in range(0, WINDOW_SIZE, 40):
        pygame.draw.line(screen, (35, 35, 45), (i, 0), (i, WINDOW_SIZE), 1)
        pygame.draw.line(screen, (35, 35, 45), (0, i), (WINDOW_SIZE, i), 1)
    
    # Draw main title with enhanced shadow effect
    font_title = pygame.font.SysFont('Arial', 72, bold=True)
    title_y = 100
    
    # Draw multiple shadow layers for better depth
    shadow_offsets = [(4, 4), (3, 3), (2, 2)]
    for offset_x, offset_y in shadow_offsets:
        shadow = font_title.render("Chess Game", True, (20, 20, 30))
        shadow_rect = shadow.get_rect(center=(WINDOW_SIZE // 2 + offset_x, title_y + offset_y))
        screen.blit(shadow, shadow_rect)
    
    # Draw main title with glow
    title = font_title.render("Chess Game", True, MENU_TITLE_COLOR)
    title_rect = title.get_rect(center=(WINDOW_SIZE // 2, title_y))
    screen.blit(title, title_rect)
    
    # Draw subtitle with enhanced styling
    font_subtitle = pygame.font.SysFont('Arial', 42, bold=True)
    subtitle_y = title_y + 100
    
    # Draw subtitle shadow
    subtitle_shadow = font_subtitle.render("Select Your Position", True, (20, 20, 30))
    subtitle_shadow_rect = subtitle_shadow.get_rect(center=(WINDOW_SIZE // 2 + 2, subtitle_y + 2))
    screen.blit(subtitle_shadow, subtitle_shadow_rect)
    
    # Draw main subtitle
    subtitle = font_subtitle.render("Select Your Position", True, MENU_TITLE_COLOR)
    subtitle_rect = subtitle.get_rect(center=(WINDOW_SIZE // 2, subtitle_y))
    screen.blit(subtitle, subtitle_rect)
    
    # Create buttons with proper spacing
    button_width = 400
    button_height = 80
    button_spacing = 30
    first_button_y = subtitle_y + 80
    
    # Create side selection buttons with improved text
    white_button = Button(
        WINDOW_SIZE//2 - button_width//2,
        first_button_y,
        button_width,
        button_height,
        "Play as White (Bottom)",
        MENU_BUTTON_BG
    )
    
    black_button = Button(
        WINDOW_SIZE//2 - button_width//2,
        first_button_y + button_height + button_spacing,
        button_width,
        button_height,
        "Play as Black (Bottom)",
        MENU_BUTTON_BG
    )
    
    # Create back button
    back_button = Button(20, 20, 120, 50, "Back", MENU_BUTTON_BG)
    
    # Draw helpful hint text with better styling
    font_hint = pygame.font.SysFont('Arial', 28)
    hint_text = "Choose your preferred starting position"
    hint_surface = font_hint.render(hint_text, True, MENU_TEXT_COLOR)
    hint_rect = hint_surface.get_rect(center=(WINDOW_SIZE // 2, first_button_y + 2 * button_height + button_spacing + 40))
    screen.blit(hint_surface, hint_rect)
    
    # Draw all buttons
    back_button.draw(screen)
    white_button.draw(screen)
    black_button.draw(screen)
    
    return white_button, black_button, back_button

def side_selection_loop():
    clock = pygame.time.Clock()
    
    # Create buttons
    white_button, black_button, back_button = draw_side_selection()
    
    # Initialize button states
    buttons = [white_button, black_button]
    for button in buttons:
        button.animation_offset = 50  # Start with offset
        button.target_offset = 0      # Target position
    
    while True:
        # Handle animations
        for button in buttons:
            if button.animation_offset > 0:
                button.animation_offset = max(0, button.animation_offset - 3)  # Smooth animation
        
        # Redraw everything
        screen.fill(MENU_BG)
        white_button, black_button, back_button = draw_side_selection()
        
        # Draw buttons with current animation state
        for button in buttons:
            button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if back_button.rect.collidepoint(mouse_pos):
                    return None
                elif white_button.rect.collidepoint(mouse_pos):
                    white_button.selected = True
                    pygame.display.flip()
                    pygame.time.wait(200)
                    return True
                elif black_button.rect.collidepoint(mouse_pos):
                    black_button.selected = True
                    pygame.display.flip()
                    pygame.time.wait(200)
                    return False
            
            # Handle hover effects
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                for button in [white_button, black_button, back_button]:
                    button.hover = button.rect.collidepoint(mouse_pos)
        
        clock.tick(FPS)

def show_skill_rating(screen, winner_stats, loser_stats=None):
    # Create semi-transparent overlay with a subtle gradient
    overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
    for i in range(WINDOW_SIZE):
        alpha = max(140, min(200, 180 + math.sin(i * 0.01) * 20))
        pygame.draw.line(overlay, (0, 0, 0, alpha), (0, i), (WINDOW_SIZE, i))
    screen.blit(overlay, (0, 0))
    
    # Create result panel with increased size
    panel_width = 500
    panel_height = 600  # Adjusted height
    panel_x = (WINDOW_SIZE - panel_width) // 2
    panel_y = (WINDOW_SIZE - panel_height) // 2
    
    # Draw panel background with enhanced shadow and gradient
    for i in range(4, 0, -1):
        shadow_rect = pygame.Rect(panel_x + i*2, panel_y + i*2, panel_width, panel_height)
        pygame.draw.rect(screen, (10, 10, 15, 50), shadow_rect, border_radius=20)
    
    # Main panel with gradient
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    gradient_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    for i in range(panel_height):
        alpha = 255 - int(i * 0.2)
        pygame.draw.line(gradient_surface, (*MENU_BUTTON_BG[:3], alpha), 
                        (0, i), (panel_width, i))
    
    # Apply rounded corners to gradient
    pygame.draw.rect(gradient_surface, (0, 0, 0, 0), gradient_surface.get_rect(), border_radius=20)
    screen.blit(gradient_surface, panel_rect)
    pygame.draw.rect(screen, MENU_BORDER_COLOR, panel_rect, 3, border_radius=20)
    
    # Initialize celebration effects
    fireworks = []
    celebration_start = pygame.time.get_ticks()
    winner_name = player1_name if winner_stats.color == 'white' else player2_name
    
    # Enhanced fonts with adjusted sizes
    title_font = pygame.font.SysFont('Arial', 64, bold=True)
    stats_font = pygame.font.SysFont('Arial', 36, bold=True)
    stats_value_font = pygame.font.SysFont('Arial', 36)
    icon_font = pygame.font.SysFont('Arial', 48, bold=True)  # Larger font for icons
    
    # Prepare stats text with labels and values separated
    stats_labels = [
        "Skill Rating",
        "Pieces Captured",
        "Center Control",
        "Pieces Developed",
        "Pawn Structure",
        "King Safety"
    ]
    
    stats_values = [
        str(winner_stats.calculate_skill_rating()),
        str(len(winner_stats.pieces_captured)),
        str(winner_stats.center_control_moves),
        str(len(winner_stats.pieces_developed)),
        str(winner_stats.pawn_structure_score),
        f"{winner_stats.king_safety_score:.1f}"
    ]
    
    # Create buttons with icons in a horizontal row
    button_size = 70  # Square buttons for icons
    button_spacing = 30
    total_buttons_width = 3 * button_size + 2 * button_spacing
    first_button_x = WINDOW_SIZE//2 - total_buttons_width//2
    buttons_y = panel_y + panel_height - button_size - 40  # 40px padding from bottom
    
    # Button icons and text
    button_configs = [
        {"icon": "↻", "text": "Play Again", "action": "restart"},  # Better reload/restart icon
        {"icon": "⌂", "text": "Main Menu", "action": "menu"},      # Home icon
        {"icon": "✖", "text": "Quit", "action": "quit"}           # Better cross/quit icon
    ]
    
    buttons = []
    for i, config in enumerate(button_configs):
        x = first_button_x + i * (button_size + button_spacing)
        button = Button(x, buttons_y, button_size, button_size, config["icon"], MENU_BUTTON_BG)
        buttons.append((button, config))
    
    # Main celebration and interaction loop
    while True:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - celebration_start
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button, config in buttons:
                    if button.rect.collidepoint(event.pos):
                        if config["action"] == "quit":
                            pygame.quit()
                            sys.exit()
                        return config["action"]
            
            if event.type == pygame.MOUSEMOTION:
                for button, _ in buttons:
                    button.hover = button.rect.collidepoint(event.pos)
        
        # Redraw panel background
        screen.blit(overlay, (0, 0))
        screen.blit(gradient_surface, panel_rect)
        pygame.draw.rect(screen, MENU_BORDER_COLOR, panel_rect, 3, border_radius=20)
        
        # Create new fireworks
        if random.random() < 0.1:
            x = random.randint(0, WINDOW_SIZE)
            y = random.randint(0, WINDOW_SIZE // 2)
            fireworks.append(Firework(x, y))
        
        # Update and draw fireworks
        for fw in fireworks[:]:
            fw.update()
            if not fw.alive:
                fireworks.remove(fw)
            else:
                fw.draw(screen)
        
        # Draw victory text with enhanced animation
        scale = 1 + 0.08 * math.sin(elapsed * 0.004)
        title_text = f"{winner_name} Wins!"
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect()
        scaled_surface = pygame.transform.scale(
            title_surface,
            (int(title_rect.width * scale), int(title_rect.height * scale))
        )
        scaled_rect = scaled_surface.get_rect(center=(WINDOW_SIZE // 2, panel_y + 80))
        
        # Add glow effect to title
        glow_surface = pygame.Surface((scaled_rect.width + 20, scaled_rect.height + 20), pygame.SRCALPHA)
        glow_alpha = int(128 + 64 * math.sin(elapsed * 0.004))
        pygame.draw.rect(glow_surface, (255, 255, 255, glow_alpha), glow_surface.get_rect(), border_radius=10)
        screen.blit(glow_surface, glow_surface.get_rect(center=scaled_rect.center))
        screen.blit(scaled_surface, scaled_rect)
        
        # Draw stats with enhanced layout and proper spacing
        stats_start_y = panel_y + 160  # Start stats lower to avoid title
        y_offset = stats_start_y
        for label, value in zip(stats_labels, stats_values):
            # Draw label with right alignment
            label_surface = stats_font.render(label + ":", True, (200, 200, 200))
            label_rect = label_surface.get_rect(right=WINDOW_SIZE//2 - 20, y=y_offset)
            screen.blit(label_surface, label_rect)
            
            # Draw value with left alignment and golden color
            value_surface = stats_value_font.render(value, True, (255, 215, 0))
            value_rect = value_surface.get_rect(left=WINDOW_SIZE//2 + 20, y=y_offset)
            screen.blit(value_surface, value_rect)
            
            y_offset += 55  # Increased spacing between stats
        
        # Draw buttons with icons and hover effects
        for button, config in buttons:
            button.draw(screen)
            if button.hover:
                # Draw tooltip with button text
                tooltip_font = pygame.font.SysFont('Arial', 20)
                tooltip = tooltip_font.render(config["text"], True, (255, 255, 255))
                tooltip_rect = tooltip.get_rect(centerx=button.rect.centerx, 
                                             bottom=button.rect.top - 5)
                screen.blit(tooltip, tooltip_rect)
        
        pygame.display.flip()
        clock.tick(60)
 
# Initialize the game
game_mode, ai_speed, player1_name, player2_name, is_white = menu_loop()

# Create board with selected orientation
board = create_board(is_white)  # Pass the orientation to create_board
selected_piece = None
current_player = 'white'
valid_moves = None
ai_thinking = False
 
# Set AI speed based on selection
if game_mode == "AI":
    AI_MOVE_DELAY = AI_SPEEDS[ai_speed]['move']
    AI_THINKING_DELAY = AI_SPEEDS[ai_speed]['thinking']

# Add last_move tracking to store the last move made
last_move = None

# Initialize player stats at the start of the game
white_stats = PlayerStats('white')
black_stats = PlayerStats('black')

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:  # Restart game
                board = create_board()
                selected_piece = None
                current_player = 'white'
                valid_moves = None
                ai_thinking = False
                last_move = None
        elif event.type == pygame.MOUSEBUTTONDOWN and not ai_thinking:
            pos = get_board_position(event.pos)
            if pos is None:  # Click was outside the board
                selected_piece = None
                valid_moves = None
                continue
                
            if event.button == 1:  # Left click
                if selected_piece is None:
                    piece = board[pos[0]][pos[1]]
                    if piece and piece[0] == current_player:
                        selected_piece = pos
                        valid_moves = get_valid_moves(board, pos, piece)
                else:
                    piece = board[selected_piece[0]][selected_piece[1]]
                    # Check if clicking on the same piece
                    if pos == selected_piece:
                        selected_piece = None
                        valid_moves = None
                    # Check if clicking on a valid move
                    elif is_valid_move(selected_piece, pos, piece):
                        # Store captured piece before making the move
                        captured_piece = board[pos[0]][pos[1]]
                        
                        # Make the move
                        board[pos[0]][pos[1]] = piece
                        board[selected_piece[0]][selected_piece[1]] = ''
                        
                        # Update stats
                        if current_player == 'white':
                            white_stats.update_stats(board, selected_piece, pos, captured_piece)
                        else:
                            black_stats.update_stats(board, selected_piece, pos, captured_piece)
                        
                        # Store last move
                        last_move = (selected_piece, pos)
                        
                        # Handle pawn promotion
                        if piece[1] == 'pawn':
                            if handle_pawn_promotion(board, pos, piece[0]):
                                draw_board(screen, None, None, last_move)
                                pygame.display.flip()
                        
                        # Switch player
                        current_player = 'black' if current_player == 'white' else 'white'
                        selected_piece = None
                        valid_moves = None
                    # Click on different piece of same color
                    elif board[pos[0]][pos[1]] and board[pos[0]][pos[1]][0] == current_player:
                        selected_piece = pos
                        valid_moves = get_valid_moves(board, pos, board[pos[0]][pos[1]])
            elif event.button == 3:  # Right click to deselect
                selected_piece = None
                valid_moves = None
   
    # Check game state
    in_check = is_in_check(board, current_player)
    in_checkmate = is_checkmate(board, current_player)
    in_stalemate = is_stalemate(board, current_player)
   
    # If game is over, show message and wait for restart
    if in_checkmate or in_stalemate:
        draw_board(screen, selected_piece, valid_moves, last_move)
        if in_checkmate:
            winner_stats = white_stats if current_player == 'black' else black_stats
            loser_stats = black_stats if current_player == 'black' else white_stats
            result = show_skill_rating(screen, winner_stats, loser_stats)
            if result == "restart":
                # Reset the game
                board = create_board(is_white)
                selected_piece = None
                current_player = 'white'
                valid_moves = None
                ai_thinking = False
                last_move = None
                white_stats = PlayerStats('white')
                black_stats = PlayerStats('black')
            elif result == "menu":
                # Return to main menu
                game_mode, ai_speed, player1_name, player2_name, is_white = menu_loop()
                board = create_board(is_white)
                selected_piece = None
                current_player = 'white'
                valid_moves = None
                ai_thinking = False
                last_move = None
                white_stats = PlayerStats('white')
                black_stats = PlayerStats('black')
            if result == "restart" or result == "menu":
                continue
        else:
            status_text = "Stalemate! Game is a draw!"
           
        font = pygame.font.SysFont('Arial', 48)
        text_surface = font.render(status_text, True, BLACK)
        text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
        screen.blit(text_surface, text_rect)
       
        restart_text = font.render("Press R to restart", True, BLACK)
        restart_rect = restart_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 50))
        screen.blit(restart_text, restart_rect)
    else:
        # If playing against AI and it's AI's turn
        if game_mode == "AI" and current_player == 'black' and not ai_thinking:
            ai_thinking = True
            
            if ai_speed == "easy":
                # Use simple random moves for easy mode
                success, move = make_easy_ai_move(board)
                if success:
                    start_pos, end_pos = move
                    # Update AI stats
                    black_stats.update_stats(board, start_pos, end_pos, board[end_pos[0]][end_pos[1]])
                    last_move = (start_pos, end_pos)
            
            # Switch back to player's turn
            current_player = 'white'
            ai_thinking = False
   
    # Draw the game state
        draw_board(screen, selected_piece, valid_moves, last_move)
        draw_game_status(screen, current_player, in_check, in_checkmate)
   
    show_fps(screen, clock)
    pygame.display.flip()
    clock.tick(FPS)
 
pygame.quit()
sys.exit()