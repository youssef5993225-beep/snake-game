import json
import os
import random
import pygame

# تهيئة بايثون ومكتبة الصوت والخطوط
pygame.init()

# إعدادات الشاشة
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - عمر الحاج")

# الألوان
BLACK = (15, 15, 15)
WHITE = (255, 255, 255)
GREEN = (46, 204, 113)
DARK_GREEN = (39, 174, 96)
RED = (231, 76, 60)
GOLD = (241, 196, 15)
GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

# إعدادات الشبكة والدودة
BLOCK_SIZE = 20
FPS = 10  # سرعة اللعبة

font_title = pygame.font.SysFont("arial", 40, bold=True)
font_main = pygame.font.SysFont("arial", 24)
font_small = pygame.font.SysFont("arial", 18)

# ملف حفظ أعلى سكور (Data)
DATA_FILE = "snake_data.json"


def load_high_score():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r") as f:
        data = json.load(f)
        return data.get("high_score", 0)
    except:
      return 0
  return 0


def save_high_score(score):
  high_score = load_high_score()
  if score > high_score:
    with open(DATA_FILE, "w") as f:
      json.dump({"high_score": score}, f)


def draw_text(text, font, color, surface, x, y, center=True):
  text_obj = font.render(text, True, color)
  text_rect = text_obj.get_rect()
  if center:
    text_rect.center = (x, y)
  else:
    text_rect.topleft = (x, y)
  surface.blit(text_obj, text_rect)


def game_loop():
  clock = pygame.time.Clock()

  # إحداثيات الدودة (بداية في المنتصف)
  snake = [[100, 100], [80, 100], [60, 100]]
  dx, dy = BLOCK_SIZE, 0  # الحركة الافتراضية لليمين

  # التفاحة العادية
  food = [
      random.randrange(0, WIDTH, BLOCK_SIZE),
      random.randrange(40, HEIGHT, BLOCK_SIZE),
  ]

  # التفاحة المميزة (بـ 3 نقاط)
  special_food = None
  normal_food_eaten_count = 0

  score = 0
  high_score = load_high_score()

  running = True
  paused = False
  game_over = False

  while running:
    WIN.fill(BLACK)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        return "QUIT"

      if event.type == pygame.KEYDOWN:
        # الإيقاف والاستئناف بالمسافة (Space)
        if event.key == pygame.K_SPACE:
          if game_over:
            return "RESTART"
          else:
            paused = not paused

        # التحكم (الأسهم أو W, A, S, D)
        if not paused and not game_over:
          if (
              event.key == pygame.K_UP or event.key == pygame.K_w
          ) and dy == 0:
            dx, dy = 0, -BLOCK_SIZE
          elif (
              event.key == pygame.K_DOWN or event.key == pygame.K_s
          ) and dy == 0:
            dx, dy = 0, BLOCK_SIZE
          elif (
              event.key == pygame.K_LEFT or event.key == pygame.K_a
          ) and dx == 0:
            dx, dy = -BLOCK_SIZE, 0
          elif (
              event.key == pygame.K_RIGHT or event.key == pygame.K_d
          ) and dx == 0:
            dx, dy = BLOCK_SIZE, 0

    if not paused and not game_over:
      # حساب موقع الرأس الجديد
      new_x = snake[0][0] + dx
      new_y = snake[0][1] + dy

      # --- ميزة الانتقال عبر الجدران (Wrap Around) ---
      # لو خبط في الشمال يطلع من اليمين والعكس
      if new_x < 0:
        new_x = WIDTH - BLOCK_SIZE
      elif new_x >= WIDTH:
        new_x = 0

      # لو خبط في فوق (تحت شريط السكور) يطلع من تحت والعكس
      if new_y < 40:
        new_y = HEIGHT - BLOCK_SIZE
      elif new_y >= HEIGHT:
        new_y = 40

      head = [new_x, new_y]

      # الخسارة دلوقتي بتحصل بس لو الدودة أكلت نفسها
      if head in snake:
        game_over = True
        save_high_score(score)

      snake.insert(0, head)

      # أكل التفاحة العادية
      if head == food:
        score += 1
        normal_food_eaten_count += 1
        food = [
            random.randrange(0, WIDTH, BLOCK_SIZE),
            random.randrange(40, HEIGHT, BLOCK_SIZE),
        ]

        # كل 3 تفاحات عادية، تظهر التفاحة المميزة
        if normal_food_eaten_count % 3 == 0 and special_food is None:
          special_food = [
              random.randrange(0, WIDTH, BLOCK_SIZE),
              random.randrange(40, HEIGHT, BLOCK_SIZE),
          ]
      # أكل التفاحة المميزة
      elif special_food and head == special_food:
        score += 3
        special_food = None
      else:
        snake.pop()

    # --- رسم العناصر على الشاشة ---
    # شريط المعلومات العلوي
    pygame.draw.rect(WIN, GRAY, (0, 0, WIDTH, 40))
    draw_text(
        f"Score: {score}",
        font_main,
        WHITE,
        WIN,
        20,
        20,
        center=False,
    )
    draw_text(
        f"High Score: {high_score}",
        font_main,
        GOLD,
        WIN,
        WIDTH - 150,
        20,
        center=False,
    )

    # رسم التفاحة العادية (حمراء)
    pygame.draw.rect(
        WIN, RED, (food[0], food[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2)
    )

    # رسم التفاحة المميزة (ذهبية بـ 3 نقاط لو ظهرت)
    if special_food:
      pygame.draw.rect(
          WIN,
          GOLD,
          (special_food[0], special_food[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2),
      )

    # رسم الدودة
    for i, block in enumerate(snake):
      color = DARK_GREEN if i == 0 else GREEN
      pygame.draw.rect(
          WIN, color, (block[0], block[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2)
      )

    # شاشة الإيقاف المؤقت (Paused)
    if paused:
      draw_text(
          "PAUSED - Press SPACE to Continue",
          font_main,
          WHITE,
          WIN,
          WIDTH // 2,
          HEIGHT // 2,
      )

    # شاشة خسارة اللعبة (Game Over)
    if game_over:
      draw_text(
          "GAME OVER",
          font_title,
          RED,
          WIN,
          WIDTH // 2,
          HEIGHT // 2 - 30,
      )
      draw_text(
          "Press SPACE to Play Again",
          font_main,
          WHITE,
          WIN,
          WIDTH // 2,
          HEIGHT // 2 + 20,
      )

    pygame.display.flip()
    clock.tick(FPS)


def start_screen():
  high_score = load_high_score()
  while True:
    WIN.fill(BLACK)
    draw_text(
        "SNAKE GAME",
        font_title,
        GREEN,
        WIN,
        WIDTH // 2,
        HEIGHT // 2 - 80,
    )
    draw_text(
        f"High Score: {high_score}",
        font_main,
        GOLD,
        WIN,
        WIDTH // 2,
        HEIGHT // 2 - 20,
    )
    draw_text(
        "TO START PRESS SPACE",
        font_main,
        WHITE,
        WIN,
        WIDTH // 2,
        HEIGHT // 2 + 40,
    )
    draw_text(
        "Controls: Arrow Keys or W, A, S, D",
        font_small,
        LIGHT_GRAY,
        WIN,
        WIDTH // 2,
        HEIGHT // 2 + 90,
    )
    draw_text(
        "Pause: SPACE | Special Food every 3 apples (+3 pts)",
        font_small,
        LIGHT_GRAY,
        WIN,
        WIDTH // 2,
        HEIGHT // 2 + 120,
    )

    pygame.display.flip()

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        return False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
          return True


# تشغيل اللعبة الأساسي
if __name__ == "__main__":
  while True:
    if not start_screen():
      break
    result = game_loop()
    if result == "QUIT":
      break

  pygame.quit()
