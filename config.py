WIDTH = 820 // 2
HEIGHT = 1180 // 2
FPS = 60

# Física do Touro
GRAVITY = 0.6
JUMP_FORCE = -14.0
MOVE_SPEED = 7.0

# Nível e Plataformas
LEVEL_HEIGHT = 6000  # Altura total do nível finito
PLATFORM_WIDTH = 90
PLATFORM_HEIGHT = 18
PLATFORM_MIN_GAP = 70
PLATFORM_MAX_GAP = 120

# Mecânica de Energia
MAX_ENERGY = 100.0
INITIAL_DECAY_RATE = 4.0   # Consumo base por segundo
DECAY_ACCELERATION = 0.25  # Aumento na taxa de consumo a cada 10s de jogo
ENERGY_REFILL = 40.0       # Energia recuperada ao pegar o Red Bull

# Power-Up de Voo (Dash de 1s ao pegar o Red Bull)
FLY_DURATION = 0.3         # Duração em segundos
FLY_SPEED = -10.0          # Impulso constante para cima durante o voo

# Cores (RGB)
BG_COLOR = (25, 30, 45)
ENERGY_BAR_COLOR = (220, 20, 60)
ENERGY_BAR_BG = (50, 50, 65)
TOUCH_BTN_COLOR = (255, 255, 255, 60)
