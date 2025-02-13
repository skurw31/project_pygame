import pygame
import math
from map import maps
from collections import deque

# Загрузка изображений игрока
player_img = []

for i in range(1, 5):
    player_img.append(pygame.transform.scale(pygame.image.load(f"./{i}.png"), (38, 38)))
# Начальные координаты игрока
player_x = 453
player_y = 670


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0  # Стоимость пути от начальной точки до текущей
        self.h = 0  # Эвристическая оценка стоимости до цели
        self.f = 0  # Общая стоимость: f = g + h

    def __eq__(self, other):
        return self.position == other.position


def astar(level, start, end):
    # Открытый и закрытый список
    open_list = [start]
    closed_list = []
    came_from = {}

    # Словари для хранения стоимости пути
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while open_list:
        # Выбираем узел с минимальной f_score
        current = min(open_list, key=lambda x: f_score.get(x, float("inf")))

        # Если достигли конца, восстанавливаем путь
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        open_list.remove(current)
        closed_list.append(current)

        for neighbor in neighbors(current):
            if neighbor in closed_list or not is_valid_move(level, neighbor):
                continue

            tentative_g_score = (
                g_score[current] + 1
            )  # Стоимость пути от start до соседней клетки

            if neighbor not in open_list:
                open_list.append(neighbor)
            elif tentative_g_score >= g_score.get(neighbor, float("inf")):
                continue

            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, end)

    return []  # Если путь не найден


def heuristic(a, b):
    # Эвристическая функция (Манхэттенское расстояние)
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(node):
    # Возвращаем соседей по 4 направлениям (вверх, вниз, влево, вправо)
    x, y = node
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def is_valid_move(level, pos):
    # Проверяем, что клетка находится в пределах карты и не является стеной
    x, y = pos
    if 0 <= x < len(level) and 0 <= y < len(level[0]):
        return level[x][y] == 0  # 0 — свободная клетка
    return False


# Класс для работы с картой
class Ghost(pygame.sprite.Sprite):
    def __init__(self, x_coard, y_coard, target, speed, img, direct, dead, box, id):
        super().__init__()
        self.x_pos = x_coard
        self.y_pos = y_coard
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.image = img
        self.rect = self.image.get_rect(topleft=(self.x_pos, self.y_pos))
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.path = []


    def update(self, player):
        if not self.path:
            self.find_path(player)

        if self.path:
            next_pos = self.path[0]
            if self.x_pos < next_pos[0] * 30:
                self.x_pos += self.speed
            elif self.x_pos > next_pos[0] * 30:
                self.x_pos -= self.speed
            if self.y_pos < next_pos[1] * 30:
                self.y_pos += self.speed
            elif self.y_pos > next_pos[1] * 30:
                self.y_pos -= self.speed

            if self.x_pos == next_pos[0] * 30 and self.y_pos == next_pos[1] * 30:
                self.path.pop(0)

        self.rect.topleft = (self.x_pos, self.y_pos)


    def find_path(self, player):
        start = (self.y_pos // 30, self.x_pos // 30)
        end = (player.player_y // 30, player.player_x // 30)
        self.path = astar(player.level, start, end)

    def draw(self):
        if (not powerup and not self.dead) or (
            eaten_ghost[self.id] and powerup and not self.dead
        ):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect




class Map:
    def __init__(self, level, color):
        self.level = level
        self.color = color
        self.PI = math.pi

    def draw_map(self, screen):
        num1 = (
            HEIGHT - 50
        ) // 32  # 32, потому что 32 различных вертик. предметов ( -50 для отступа)
        num2 = WIDTH // 30
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                if self.level[i][j] == 1:
                    pygame.draw.circle(
                        screen,
                        "#fffafa",
                        (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)),
                        4,
                    )  # Обычная еда
                if self.level[i][j] == 2:
                    pygame.draw.circle(
                        screen,
                        "#fffafa",
                        (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)),
                        8,
                    )  # Большая еда
                if self.level[i][j] == 3:
                    pygame.draw.line(
                        screen,
                        self.color,
                        (j * num2 + (0.5 * num2), i * num1),
                        (j * num2 + (0.5 * num2), i * num1 + num1),
                        2,
                    )  # Толщина 2
                if self.level[i][j] == 4:
                    pygame.draw.line(
                        screen,
                        self.color,
                        (j * num2, i * num1 + (0.5 * num1)),
                        (j * num2 + num2, i * num1 + (0.5 * num1)),
                        2,
                    )  # Толщина 2
                if self.level[i][j] == 5:
                    pygame.draw.arc(
                        screen,
                        self.color,
                        [
                            (j * num2 - (num2 * 0.4)),
                            (i * num1 + (0.5 * num1)),
                            num2,
                            num1,
                        ],
                        0,
                        self.PI / 2,
                        2,
                    )  # Толщина 2
                if self.level[i][j] == 6:
                    pygame.draw.arc(
                        screen,
                        self.color,
                        [
                            (j * num2 + (num2 * 0.5)),
                            (i * num1 + (0.5 * num1)),
                            num2,
                            num1,
                        ],
                        self.PI / 2,
                        self.PI,
                        2,
                    )  # Толщина 2
                if self.level[i][j] == 7:
                    pygame.draw.arc(
                        screen,
                        self.color,
                        [
                            (j * num2 + (num2 * 0.5)),
                            (i * num1 - (0.4 * num1)),
                            num2,
                            num1,
                        ],
                        self.PI,
                        3 * self.PI / 2,
                        2,
                    )  # Толщина 2
                if self.level[i][j] == 8:
                    pygame.draw.arc(
                        screen,
                        self.color,
                        [
                            (j * num2 - (num2 * 0.4)),
                            (i * num1 - (0.4 * num1)),
                            num2,
                            num1,
                        ],
                        3 * self.PI / 2,
                        2 * self.PI,
                        2,
                    )  # Толщина 2
                if self.level[i][j] == 9:
                    pygame.draw.line(
                        screen,
                        "#fffafa",
                        (j * num2, i * num1 + (0.5 * num1)),
                        (j * num2 + num2, i * num1 + (0.5 * num1)),
                        2,
                    )  # Толщина 2


# Класс для игрока
class Player:
    def __init__(self, level, color, player_x, player_y, player_img):
        self.direction = None  # Направление игрока (изначально None — без движения)
        self.counter = 0  # Счетчик для анимации
        self.player_x = player_x  # Позиция игрока по X
        self.player_y = player_y  # Позиция игрока по Y
        self.player_img = player_img  # Список изображений игрока
        self.speed = 2  # Скорость игрока
        self.level = level  # Карта уровня

    def draw_player(self, screen):
        # Если направление не задано, отображаем первое изображение (без движения)
        if self.direction is None:
            screen.blit(self.player_img[0], (self.player_x, self.player_y))
        # Направо (0)
        elif self.direction == 0:
            screen.blit(
                self.player_img[self.counter // 6], (self.player_x, self.player_y)
            )
        # Налево (1)
        elif self.direction == 1:
            screen.blit(
                pygame.transform.flip(self.player_img[self.counter // 6], True, False),
                (self.player_x, self.player_y),
            )
        # Вверх (2)
        elif self.direction == 2:
            screen.blit(
                pygame.transform.rotate(self.player_img[self.counter // 6], 90),
                (self.player_x, self.player_y),
            )
        # Вниз (3)
        elif self.direction == 3:
            screen.blit(
                pygame.transform.rotate(self.player_img[self.counter // 6], 270),
                (self.player_x, self.player_y),
            )

    def update(self):
        # Если направление задано, обновляем позицию игрока
        if self.direction is not None:
            # Проверяем, можно ли двигаться в выбранном направлении
            if self.can_move(self.direction):
                if self.direction == 0:
                    self.player_x += self.speed
                elif self.direction == 1:
                    self.player_x -= self.speed
                elif self.direction == 2:
                    self.player_y -= self.speed
                elif self.direction == 3:
                    self.player_y += self.speed

            # Проверка на выход за границы карты слева и справа
            if self.player_x < 0:
                self.player_x = WIDTH  # Переносим игрока на правую сторону
            elif self.player_x > WIDTH:
                self.player_x = 0  # Переносим игрока на левую сторону

            # Анимация игрока
            self.counter += 1
            if self.counter > 19:
                self.counter = 0

            # Проверка на сбор еды
            self.check_collision(self.level)
        # Удаляем стены с цифрой 9 при начале движения
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                if self.level[i][j] == 9:
                    self.level[i][j] = 0  # Убираем стену

            # Анимация игрока
            self.counter += 1
            if self.counter > 19:
                self.counter = 0

            # Проверка на сбор еды
            self.check_collision(self.level)
        # Удаляем стены с цифрой 9 при начале движения
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                if self.level[i][j] == 9:
                    self.level[i][j] = 0  # Убираем стену

    def can_move(self, direction):
        num1 = (HEIGHT - 50) // len(self.level)  # Размер по вертикали
        num2 = WIDTH // len(self.level[0])  # Размер по горизонтали

        # Определяем будущее положение игрока
        next_x, next_y = self.player_x, self.player_y
        if direction == 0:  # Вправо
            next_x += self.speed
        elif direction == 1:  # Влево
            next_x -= self.speed
        elif direction == 2:  # Вверх
            next_y -= self.speed
        elif direction == 3:  # Вниз
            next_y += self.speed

        # Определяем, в каких клетках будет игрок
        grid_x = next_x // num2
        grid_y = next_y // num1

        # Проверяем границы карты
        if (
            grid_y < 0
            or grid_y >= len(self.level)
            or grid_x < 0
            or grid_x >= len(self.level[0])
        ):
            return False  # Не двигаемся, если вышли за границы карты

        # Проверяем столкновение со стенами
        if self.level[grid_y][grid_x] in [3, 4, 5, 6, 7, 8, 9]:
            return False  # Движение невозможно

        return True  # Движение возможно

    def check_collision(self, level):
        num1 = (HEIGHT - 50) // 32
        num2 = WIDTH // 30
        i = int(self.player_y // num1)
        j = int(self.player_x // num2)
        if level[i][j] == 1 or level[i][j] == 2:
            level[i][j] = 0  # Убираем еду с карты


# class Ghost(pygame.sprite.Sprite):
#     def __init__(self, x_coard, y_coard, target, speed, img, direct, dead, box, id):
#         super().__init__()
#         self.x_pos = x_coard
#         self.y_pos = y_coard
#         self.target = target
#         self.speed = speed
#         self.image = img
#         self.rect = self.image.get_rect(topleft=(self.x_pos, self.y_pos))
#         self.direction = direct
#         self.dead = dead
#         self.in_box = box
#         self.id = id
#         self.path = []

#     def update(self, player):
#         # Если пути нет, ищем новый
#         if not self.path:
#             self.find_path(player)

#         # Если путь есть, следуем по нему
#         if self.path:
#             next_pos = self.path[0]  # Смотрим на следующую точку пути
#             if self.x_pos < next_pos[0] * 30:
#                 self.x_pos += self.speed
#             elif self.x_pos > next_pos[0] * 30:
#                 self.x_pos -= self.speed
#             if self.y_pos < next_pos[1] * 30:
#                 self.y_pos += self.speed
#             elif self.y_pos > next_pos[1] * 30:
#                 self.y_pos -= self.speed

#             # Если достигли цели, убираем её из пути
#             if self.x_pos == next_pos[0] * 30 and self.y_pos == next_pos[1] * 30:
#                 self.path.pop(0)

#         self.rect.topleft = (self.x_pos, self.y_pos)

#     def find_path(self, player):
#         # Преобразуем координаты в клетки
#         start = (self.y_pos // 30, self.x_pos // 30)
#         end = (player.player_y // 30, player.player_x // 30)
#         self.path = astar(player.level, start, end)

#     def draw(self, screen):
#         screen.blit(self.image, self.rect.topleft)

#     def move_towards_player(self, player_x, player_y, level):
#         path = self.bfs((self.y_pos, self.x_pos), (player_y, player_x), level)

#         if path:
#             next_y, next_x = path[0]  # Следующая клетка в пути
#             num1 = (HEIGHT - 50) // len(level)
#             num2 = WIDTH // len(level[0])

#             self.x_pos = next_x * num2
#             self.y_pos = next_y * num1

#     def can_move(self, x, y, level):
#         num1 = (HEIGHT - 50) // len(level)
#         num2 = WIDTH // len(level[0])

#         grid_x = x // num2
#         grid_y = y // num1

#         if grid_y < 0 or grid_y >= len(level) or grid_x < 0 or grid_x >= len(level[0]):
#             return False

#         if level[grid_y][grid_x] in [3, 4, 5, 6, 7, 8, 9]:
#             return False

#         return True

#     def update(self, player):
#         self.move_towards_player(player.player_x, player.player_y, player.level)
#         self.rect.topleft = (self.x_pos, self.y_pos)

#     def bfs(self, start, target, level):
#         num1 = (HEIGHT - 50) // len(level)  # Размер клетки по Y
#         num2 = WIDTH // len(level[0])  # Размер клетки по X

#         start_cell = (start[1] // num1, start[0] // num2)
#         target_cell = (target[1] // num1, target[0] // num2)

#         queue = deque([(start_cell, [])])  # Очередь: ((y, x), [путь])
#         visited = set()

#         directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Вправо, влево, вниз, вверх

#         while queue:
#             (y, x), path = queue.popleft()

#             if (y, x) in visited:
#                 continue
#             visited.add((y, x))

#             if (y, x) == target_cell:
#                 return path  # Нашли кратчайший путь

#             for dy, dx in directions:
#                 new_y, new_x = y + dy, x + dx
#                 if 0 <= new_y < len(level) and 0 <= new_x < len(
#                     level[0]
#                 ):  # В пределах карты
#                     if level[new_y][new_x] not in [3, 4, 5, 6, 7, 8, 9]:  # Не стенаf
#                         queue.append(((new_y, new_x), path + [(new_y, new_x)]))

#         return []  # Если пути нет




for i in range(1, 5):
    blinky_img = pygame.transform.scale(pygame.image.load(f"./red.png"), (45, 45))
    pinky_img = pygame.transform.scale(pygame.image.load(f"./pink.png"), (45, 45))
    inky_img = pygame.transform.scale(pygame.image.load(f"./blue.png"), (45, 45))
    clyde_img = pygame.transform.scale(pygame.image.load(f"./orange.png"), (45, 45))
    spooked_img = pygame.transform.scale(pygame.image.load(f"./powerup.png"), (45, 45))
    dead_img = pygame.transform.scale(pygame.image.load(f"./dead.png"), (45, 45))

blinky_x = 56
blinky_y = 58
blinky_direction = 0
inky_x = 440
inky_y = 438
inky_direction = 2
pinky_x = 440
pinky_y = 388
pinky_direction = 2
clyde_x = 440
clyde_y = 438
clyde_direction = 2
targets = [
    (player_x, player_y),
    (player_x, player_y),
    (player_x, player_y),
    (player_x, player_y),
]

blinky_dead = False
inky_dead = False
pinky_dead = False
clyde_dead = False

blinky_box = False
inky_box = False
pinky_box = False
clyde_box = False

ghost_speed = 2

powerup = False
eaten_ghost = [False, False, False, False]


# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 900, 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
FPS = 60
level = maps
color = "#0000ff"  # blue

# Создаем объект карты
game_map = Map(level, color)

# Создаем объект игрока
player = Player(level, color, player_x, player_y, player_img)
# Создаем группу спрайтов
ghosts = pygame.sprite.Group()

# Создаем объекты призраков и добавляем их в группу
blinky = Ghost(
    blinky_x,
    blinky_y,
    targets[0],
    ghost_speed,
    blinky_img,
    blinky_direction,
    blinky_dead,
    blinky_box,
    0,
)
inky = Ghost(
    inky_x,
    inky_y,
    targets[1],
    ghost_speed,
    inky_img,
    inky_direction,
    inky_dead,
    inky_box,
    1,
)
pinky = Ghost(
    pinky_x,
    pinky_y,
    targets[2],
    ghost_speed,
    pinky_img,
    pinky_direction,
    pinky_dead,
    pinky_box,
    2,
)
clyde = Ghost(
    clyde_x,
    clyde_y,
    targets[3],
    ghost_speed,
    clyde_img,
    clyde_direction,
    clyde_dead,
    clyde_box,
    3,
)

ghosts.add(blinky, inky, pinky, clyde)
# Основной цикл
run = True
while run:
    timer.tick(FPS)
    screen.fill("#000000")  # Очищаем экран

    # Отрисовка карты
    game_map.draw_map(screen)

    # Отрисовка и обновление игрока
    player.draw_player(screen)
    player.update()

    # Обновляем и отрисовываем призраков
    for ghost in ghosts:
        ghost.update(player)  # Обновляем позиции призраков
    ghosts.draw(screen)  # Отрисовываем призраков

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                player.direction = 0  # Движение вправо
            if event.key == pygame.K_LEFT:
                player.direction = 1  # Движение влево
            if event.key == pygame.K_UP:
                player.direction = 2  # Движение вверх
            if event.key == pygame.K_DOWN:
                player.direction = 3  # Движение вниз

    pygame.display.flip()

pygame.quit()
