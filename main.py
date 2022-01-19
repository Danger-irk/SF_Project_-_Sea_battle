from random import randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы доски!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку."


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, ship_bow, ship_length, ship_direction):
        self.ship_bow = ship_bow
        self.ship_length = ship_length
        self.ship_direction = ship_direction
        self.ship_lives = ship_length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.ship_length):
            ship_dot_x = self.ship_bow.x
            ship_dot_y = self.ship_bow.y

            if self.ship_direction == 0:
                ship_dot_x += i
            elif self.ship_direction == 1:
                ship_dot_y += i

            ship_dots.append(Dot(ship_dot_x, ship_dot_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.hid = hid
        self.count_dead_ships = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busy_dots = []
        self.ships = []

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy_dots:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy_dots.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):

        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for d in ship.dots:
            for dx, dy in near:
                contour_dot = Dot(d.x + dx, d.y + dy)

                if not (self.out(contour_dot)) and contour_dot not in self.busy_dots:
                    if verb:
                        self.field[contour_dot.x][contour_dot.y] = "."
                    self.busy_dots.append(contour_dot)

    def __str__(self):
        res = ""
        res += "  1 2 3 4 5 6"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} " + " ".join(row)

        if self.hid:
            res = res.replace("■", "O")

        return res

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy_dots:
            raise BoardUsedException()

        self.busy_dots.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.ship_lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.ship_lives == 0:
                    self.count_dead_ships += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy_dots = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        player_board = self.random_board()
        com_board = self.random_board()
        com_board.hid = False

        self.ai = AI(com_board, player_board)
        self.user = User(player_board, com_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        ship_lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in ship_lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.user.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count_dead_ships == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.user.board.count_dead_ships == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()