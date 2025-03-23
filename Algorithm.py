import heapq
import time
from collections import deque
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

def hamming_distance(board):
    distance = 0
    for i in range(4):
        for j in range(4):
            if board[i][j] != target_board[i][j] and board[i][j] != 0:
                distance += 1
    return distance

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

            if current_node.move:
                all_moves.append(current_node.move)

            if tuple_board(current_node.board) == tuple_board(target_board): # sprawdzamy czy dany stan jest tym oczekiwanym
                path=[]                            # szukamy sciezki jaka nas doprowadzila do tego stanu
                while current_node.parent is not None:
                    path.append(current_node.move)
                    current_node = current_node.parent

                end_time = time.time()
                sum_time = end_time - start_time
                return {
                    "sciezka": all_moves[::-1],
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



def dfs (init_board, target_board, move_order, depth_limit = 36):

    start_time = time.time() # licznik czasu

    stack = [] # uzywamy stosu do zapisu plansz (LIFO)
    visited = set()
    all_moves = []

    empty_pos = find_empty(init_board)

    starting_point = Node(init_board, empty_pos)  # przechowywanie aktualnego stanu planszy

    stack.append(starting_point)
    visited.add(tuple_board(init_board))  # dodajemy do visited by wiedziec czy juz ten stan sprawdzalismy

    states_counter = 0
    max_depth = 0

    while stack:
        current_node = stack.pop()
        states_counter += 1

        if current_node.move:
            all_moves.append(current_node.move)

        if tuple_board(current_node.board) == tuple_board(target_board):
            path = []

            while current_node.parent is not None:
                path.append(current_node.move)
                current_node = current_node.parent
            end_time = time.time()
            sum_time = end_time - start_time
            return {
                    "sciezka": all_moves[::-1],
                    "dlugosc_sciezka": len(path),
                    "lso": len(visited),
                    "lsp": states_counter,
                    "max_d": max_depth,
                    "t": sum_time
                }
        if current_node.depth < depth_limit: # nie przekaraczamy limitu glebokosci
            for move , new_board in next_move(current_node.board, current_node.empty_pos, move_order):
                board_tuple = tuple_board(new_board)
                if board_tuple not in visited: # sprawdzamy czy plansza byla juz "odziedzona"
                    visited.add(board_tuple)
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
            sum_time = end_time - start_time
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
        file.write(f"{computation_time:.8f}\n")


def main():


    print("podaj nazwe pliku")
    file_name = input()

    w, k, board = read_file(file_name)
    empty_pos = find_empty(board)

    # Wyświetlenie wyników
    print(f"Wymiary planszy: {w} x {k}")
    print("Macierz układanki:")
    for row in board:
        print(row)  # Każdy wiersz w nowej linii

    print(f"Pozycja pustego pola: {empty_pos}")

    bfs_result = bfs(board, target_board, ['U', 'D', 'L', 'R'])
    dfs_result = dfs(board, target_board, ['U', 'D', 'L', 'R'])


    astar_result = astar(board, hamming_distance , ['U', 'D', 'L', 'R'])


    bfssol_filename = "bfs_UDLR_sol.txt"
    bfsstats_filename = "bfs_UDLR_stats.txt"

    if bfs_result:
        with open(bfssol_filename, 'w') as f:
            f.write(f"{bfs_result['dlugosc_sciezka']}\n")
            f.write("".join(bfs_result['sciezka']) + "\n")

        write_stats(bfsstats_filename, bfs_result['dlugosc_sciezka'], bfs_result['lso'], bfs_result['lsp'],
                    bfs_result['max_d'], bfs_result['t'])
    else:
        with open(bfssol_filename, 'w') as f:
            f.write("-1\n")

        with open(bfsstats_filename, 'w') as f:
            f.write("-1\n")

    print("\nAlgorytm DFS")

    if dfs_result:
        print("Znaleziono rozwiązanie!")
        print(f"Sekwencja ruchów: {' '.join(dfs_result['sciezka'])}")
        print(f"Długość rozwiązania: {dfs_result['dlugosc_sciezka']}")
        print(f"Liczba stanow odwiedzonych: {dfs_result['lso']}")
        print(f"Liczba stanow przetworzonych: {dfs_result['lsp']}")
        print(f"Maksymalna glebokosc: {dfs_result['max_d']}")
        print(f"Czas operacji: {dfs_result['t']:.10f} sekund")
    else:
        print("Nie znaleziono rozwiązania.")

    print("\nAlgorytm ASTAR")

    if astar_result:
        print("Znaleziono rozwiązanie!")
        print(f"Sekwencja ruchów: {' '.join(astar_result['sciezka'])}")
        print(f"Długość rozwiązania: {astar_result['dlugosc_sciezka']}")
        print(f"Liczba stanow odwiedzonych: {astar_result['lso']}")
        print(f"Liczba stanow przetworzonych: {astar_result['lsp']}")
        print(f"Maksymalna glebokosc: {astar_result['max_d']}")
        print(f"Czas operacji: {astar_result['t']:.10f} sekund")
    else:
        print("Nie znaleziono rozwiązania.")

if __name__ == "__main__":
    main()