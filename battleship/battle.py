class BoardOutException(Exception):
    """Исключение, которое возникает, когда точка выходит за границы игрового поля."""
    pass


class UsedPointException(Exception):
    """Исключение, возникающее при попытке выстрела в уже использованное место."""
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x + i * self.direction
            cur_y = self.bow.y + i * (1 - self.direction)
            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots


class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.field = [['O'] * size for _ in range(size)]
        self.ships = []
        self.hid = hid
        self.live_ships = len(self.ships)

    def add_ship(self, ship):
        for dot in ship.dots:
            if not (0 <= dot.x < self.size and 0 <= dot.y < self.size) or self.field[dot.x][dot.y] != 'O':
                raise BoardOutException()

        for dot in ship.dots:
            self.field[dot.x][dot.y] = '■'

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=True):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for ship_dot in ship.dots:
            for dx, dy in near:
                cur_x = ship_dot.x + dx
                cur_y = ship_dot.y + dy

                if (0 <= cur_x < self.size and
                        0 <= cur_y < self.size and
                        self.field[cur_x][cur_y] == 'O'):

                    if verb:
                        self.field[cur_x][cur_y] = '.'
                    else:
                        self.field[cur_x][cur_y] = '-'

    def show(self):
        print('-' * (self.size * 2 + 1))
        for row in self.field:
            print('|', end=' ')
            for cell in row:
                if cell == '■' and self.hid:
                    print('O', end=' ')
                else:
                    print(cell, end=' ')
            print('|')
        print('-' * (self.size * 2 + 1))

    def out(self, dot):
        return not (0 <= dot.x < self.size and 0 <= dot.y < self.size)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()

        if self.field[dot.x][dot.y] in ('X', '.'):
            raise UsedPointException()

        if self.field[dot.x][dot.y] == '■':
            self.field[dot.x][dot.y] = 'X'
            for ship in self.ships:
                if dot in ship.dots:
                    ship.lives -= 1
                    if ship.lives == 0:
                        self.live_ships -= 1
                        self.contour(ship, verb=False)
                        break
            return True
        elif self.field[dot.x][dot.y] == 'O':
            self.field[dot.x][dot.y] = '.'
        return False


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        # Реализуется в дочерних классах
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                break
            except (BoardOutException, UsedPointException) as e:
                print("Ошибка:", e)

        return repeat


import random


class AI(Player):
    def ask(self):
        dot = Dot(random.randint(0, self.enemy_board.size - 1), random.randint(0, self.enemy_board.size - 1))
        print(f"Компьютер стреляет в {dot}")
        return dot


class User(Player):
    def ask(self):
        while True:
            coord = input("Ваш ход: ").split()
            if len(coord) != 2:
                print("Неверный формат ввода. Попробуйте снова.")
                continue

            x, y = coord
            if not x.isdigit() or not y.isdigit():
                print("Координаты должны быть целыми числами. Попробуйте снова.")
                continue

            x, y = int(x), int(y)
            if not (0 <= x < self.enemy_board.size and 0 <= y < self.enemy_board.size):
                print("Вы ввели координаты вне поля. Попробуйте снова.")
                continue

            return Dot(x, y)


class Game:
    def __init__(self, user, ai):
        self.user = user
        self.ai = ai
        self.user_board = user.board
        self.ai_board = ai.board

    def greet(self):
        print("Добро пожаловать в Морской бой!")
        print("Формат ввода координат: X Y")
        print("Пример: 1 3")

    def loop(self):
        while True:
            print("\nВаше поле:")
            self.user_board.show()
            print("\nПоле противника:")
            # self.ai_board.show(hid=True)

            if self.user.move():
                print("Вы потопили корабль! Повторите выстрел.")
            if self.ai_board.live_ships == 0:
                print("Поздравляем! Вы выиграли!")
                break

            if self.ai.move():
                print("Компьютер потопил ваш корабль! Его ход продолжается.")
            if self.user_board.live_ships == 0:
                print("К сожалению, вы проиграли.")
                break

    def start(self):
        self.greet()
        self.loop()


def main():
    user_board = Board(hid=False)
    ai_board = Board(hid=True)
    user = User(user_board, ai_board)
    ai = AI(ai_board, user_board)
    game = Game(user, ai)
    game.start()


if __name__ == "__main__":
    main()
