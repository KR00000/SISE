import heapq
import time
from collections import deque
import sys
from idlelib.search import find_again

target_board = [
    [1,2,3,4],
    [5,6,7,8],
    [9,10,11,12],
    [13,14,15,0],
                ]

class Node:
    def __init__(self, board, empty_pos, parent = None, move = None, depth = 0, cost = 0):
        self.board = [row[:] for row in board]
        self.empty_pos = empty_pos
        self.parent = parent
        self.move = move
        self.depth = depth
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost


def read_file(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()


    w, k = map(int, lines[0].split())
    board = [list(map(int, line.split())) for line in lines[1:]]

    return w, k, board

def find_empty(board):
    for i, row in enumerate(board):
        for j, val in enumerate(row):
            if val == 0:
                return (i, j)


def next_move(board, empty_pos, moves_order):
        w = len(board)
        k = len(board[0])

        x, y = empty_pos

        moves = {
        'U': (-1,0),
        'D': (1,0),
        'L': (0,-1),
        'R': (0,1)
        }

        possible_moves = []

        for move in moves_order:
            dx, dy = moves[move]
            nx, ny = x+dx, y+dy

            if 0 <= nx < w and 0 <= ny < k: # warunki by nie wyjsc poza plansze
                new_board = [row[:] for row in board]
                temp = new_board[x][y]
                new_board[x][y] = new_board[nx][ny]
                new_board[nx][ny] = temp
                possible_moves.append((move, new_board))

        return possible_moves # zwracamy liste dostepnych ruchow

def tuple_board(board):
    return tuple(tuple(row) for row in board)

# liczy ilosc zle umiejscowionych kafelkow
def hamming_distance(board):
    distance = 0
    for i in range(4):
        for j in range(4):
            if board[i][j] != target_board[i][j] and board[i][j] != 0:
                distance += 1
    return distance

# liczy odlegloc od celu
def manhattan_distance(board):
    distance = 0
    for i in range(4):
        for j in range(4):
            if board[i][j] != 0:
                target_row, target_col = divmod(board[i][j] - 1, 4)
                distance += abs(i - target_row) + abs(j - target_col)
    return distance


def bfs(init_board, target_board, moves_order):

        start_time = time.time()

        queue = deque()  # kolejka (FIFO)
        visited = set()

        all_moves = []

        empty_pos = find_empty(init_board)

        starting_point = Node(init_board, empty_pos) # przechowywanie aktualnego stanu planszy

        queue.append(starting_point)
        visited.add(tuple_board(init_board)) # dodajemy do visited by wiedziec czy juz ten stan sprawdzalismy

        states_counter = 0
        max_depth = 0

        while queue:
            current_node = queue.popleft() # pobieramy pierwszy stan z listy
            visited.add(tuple_board(current_node.board))
            states_counter += 1

            if current_node.move: # zapisujemy ruch jesli otrzymalismy nowy stan
                all_moves.append(current_node.move)

            if tuple_board(current_node.board) == tuple_board(target_board): # sprawdzamy czy dany stan jest tym oczekiwanym
                path=[]                            # szukamy sciezki jaka nas doprowadzila do tego stanu
                while current_node.parent is not None:
                    path.append(current_node.move)
                    current_node = current_node.parent

                end_time = time.time()
                sum_time = (end_time - start_time) * 1000
                return {
                    "sciezka": path[::-1],
                    "dlugosc_sciezka": len(path),
                    "lso": len(visited),
                    "lsp": states_counter,
                    "max_d": max_depth,
                    "t": sum_time
                }

            for move , new_board in next_move(current_node.board, current_node.empty_pos, moves_order):
                board_tuple = tuple_board(new_board)
                if board_tuple not in visited:
                    visited.add(board_tuple)
                    new_node = Node(new_board, find_empty(new_board), current_node, move, current_node.depth + 1)
                    queue.append(new_node)
                    max_depth = max(max_depth, new_node.depth)

        return None



def dfs(init_board, target_board, move_order, depth_limit=22):
    start_time = time.time()  # licznik czasu

    stack = []  # stos (LIFO)
    visited = set()
    all_moves = []

    empty_pos = find_empty(init_board)
    starting_point = Node(init_board, empty_pos)  # przechowywanie aktualnego stanu planszy

    stack.append(starting_point)
    visited.add(tuple_board(init_board))  # dodajemy do visited by wiedziec czy juz ten stan sprawdzalismy

    states_counter = 0
    max_depth = 0

    while stack:
        current_node = stack.pop()  # pobieramy ostatni stan
        states_counter += 1

        if current_node.move:
            all_moves.append(current_node.move)

        if tuple_board(current_node.board) == tuple_board(target_board):
            # Jesli znaleziono rozwiazanie, budujemy sciezke
            path = []
            while current_node.parent is not None:
                path.append(current_node.move)
                current_node = current_node.parent

            end_time = time.time()
            sum_time = (end_time - start_time) * 1000
            return {
                "sciezka": path[::-1],
                "dlugosc_sciezka": len(path),
                "lso": len(visited),
                "lsp": states_counter,
                "max_d": max_depth,
                "t": sum_time
            }

        # Sprawdzamy czy limit glebokosci nie zostal przekroczony
        if current_node.depth < depth_limit:
            for move, new_board in next_move(current_node.board, current_node.empty_pos, move_order):
                board_tuple = tuple_board(new_board)
                if board_tuple not in visited:
                    visited.add(board_tuple)  # dodajemy do visited
                    new_node = Node(new_board, find_empty(new_board), current_node, move, current_node.depth + 1)
                    stack.append(new_node)
                    max_depth = max(max_depth, new_node.depth)


    return None

def astar(init_board, heuristic, move_order):
    start_time = time.time()
    visited = set()
    heap = []  # Kolejka priorytetowa

    empty_pos = find_empty(init_board)
    start_node = Node(init_board, empty_pos, cost=heuristic(init_board))

    heapq.heappush(heap, start_node)

    states_counter = 0
    max_depth = 0

    while heap:
        current_node = heapq.heappop(heap)
        states_counter += 1

        if tuple_board(current_node.board) == tuple_board(target_board):
            path = []
            while current_node.parent is not None:
                path.append(current_node.move)
                current_node = current_node.parent
            end_time = time.time()
            sum_time = (end_time - start_time) * 1000
            return {
                "sciezka": path[::-1],
                "dlugosc_sciezka": len(path),
                "lso": len(visited),
                "lsp": states_counter,
                "max_d": max_depth,
                "t": sum_time
            }

        visited.add(tuple_board(current_node.board))

        for move, new_board in next_move(current_node.board, current_node.empty_pos, move_order):
            new_empty_pos = find_empty(new_board)
            new_node = Node(new_board, new_empty_pos, current_node, move,
                            current_node.depth + 1,
                            current_node.depth + 1 + heuristic(new_board))

            if tuple_board(new_board) not in visited:
                visited.add(tuple_board(new_board))
                heapq.heappush(heap, new_node)
                max_depth = max(max_depth, new_node.depth)

    return None


def write_solution(filename, node):
    with open(filename, 'w') as file:
        if node is None:
            file.write('None')
        else:
            moves = []
            while node.parent is not None:
                moves.append(node.move)
                node = node.parent
            moves.reverse()
            file.write(f"{len(moves)}\n")
            file.write("".join(moves)+"\n")

def write_stats(filename, solution_length, visited_states, processed_states, max_depth, computation_time):
    with open(filename, 'w') as file:
        file.write(f"{solution_length}\n")
        file.write(f"{visited_states}\n")
        file.write(f"{processed_states}\n")
        file.write(f"{max_depth}\n")
        file.write(f"{computation_time:.3f}\n")


def main():
    if len(sys.argv) != 6:
        print("Usage: python fifteen_puzzle.py <strategy> <parameter> <input_file> <solution_file> <stats_file>")
        sys.exit(1)

    strategy = sys.argv[1]
    parameter = sys.argv[2]
    input_file = sys.argv[3]
    solution_file = sys.argv[4]
    stats_file = sys.argv[5]

    w, k, board = read_file(input_file)

    if strategy == 'bfs':
        move_order = list(parameter)
        result = bfs(board, target_board, move_order)
    elif strategy == 'dfs':
        move_order = list(parameter)
        result = dfs(board, target_board, move_order)
    elif strategy == 'astr':
        if parameter == 'hamm':
            heuristic = hamming_distance
        elif parameter == 'manh':
            heuristic = manhattan_distance
        else:
            print("Invalid heuristic")
            sys.exit(1)
        result = astar(board, heuristic, ['U', 'D', 'L', 'R'])
    else:
        print("Invalid strategy")
        sys.exit(1)

    if result:
        solution_length = result['dlugosc_sciezka']
        with open(solution_file, 'w') as f:
            f.write(f"{solution_length}\n")
            f.write("".join(result['sciezka']) + "\n")
        write_stats(stats_file, solution_length, result['lso'], result['lsp'], result['max_d'], result['t'])
    else:
        with open(solution_file, 'w') as f:
            f.write("-1\n")
        with open(stats_file, 'w') as f:
            f.write("-1\n")


if __name__ == "__main__":
    main()
