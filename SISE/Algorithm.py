import time
from collections import deque
from tkinter.ttk import Treeview

target_board = [
    [1,2,3,4],
    [5,6,7,8],
    [9,10,11,12],
    [13,14,15,0],
                ]

class Node:
    def __init__(self, board, empty_pos, parent = None, move = None, depth = 0):
        self.board = [row[:] for row in board]
        self.empty_pos = empty_pos
        self.parent = parent
        self.move = move
        self.depth = depth


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


def checker(board):
    temp_board=[]
    for row in board:
        for val in row:
            if val != 0:
                temp_board.append(val)


    counter = 0

    for i in range(len(temp_board)-1):
           if temp_board[i] > temp_board[i+1]:
                counter += 1

    x, y = find_empty(board)

    true_x = len(board) - x

    if ((counter + true_x)%2) == 0:
        return True
    else:
        return False

def next_move(board, empty_pos, move):
        w = len(board)
        k = len(board[0])

        x, y = empty_pos

        moves = {
        'U': (-1,0),
        'D': (1,0),
        'L': (0,-1),
        'R': (0,1)
        }

        dx, dy = moves[move]
        nx, ny = x+dx, y+dy

        if 0 <= nx < w and 0 <= ny < k: # warunki by nie wyjsc poza plansze
            new_board = [row[:] for row in board]
            temp = new_board[x][y]
            new_board[x][y] = new_board[nx][ny]
            new_board[nx][ny] = temp
            return new_board, (nx, ny)
        return None

def tuple_board(board):
    return tuple(tuple(row) for row in board)


def bfs(init_board, target_board):

        start_time = time.time()

        queue = deque()  # kolejka (FIFO)
        visited = set()

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

            if tuple_board(current_node.board) == tuple_board(target_board): # sprawdzamy czy dany stan jest tym oczekiwanym
                path=[]                            # szukamy sciezki jaka nas doprowadzila do tego stanu
                while current_node.parent != None:

                    end_time = time.time()
                    sum_time = end_time - start_time

                    path.append(current_node.move)
                    current_node = current_node.parent
                return {
                    "sciezka": path[::-1],
                    "dlugosc_sciezka": len(path),
                    "lso": len(visited),
                    "lsp": states_counter,
                    "max_d": max_depth,
                    "t": sum_time
                }

            for move in ['U', 'D', 'L', 'R']:
                result = next_move(current_node.board, current_node.empty_pos, move)
                if result:
                    new_board, new_empty_pos = result
                    board_tuple = tuple_board(new_board)

                    if board_tuple not in visited:
                        visited.add(board_tuple)
                        new_node = Node(new_board, new_empty_pos, current_node, move, current_node.depth + 1)
                        queue.append(new_node)

        return None



def dfs (init_board, target_board, depth_limit = 36):

    start_time = time.time() # licznik czasu

    stack = [] # uzywamy stosu do zapisu plansz (LIFO)
    visited = set()

    empty_pos = find_empty(init_board)

    starting_point = Node(init_board, empty_pos)  # przechowywanie aktualnego stanu planszy

    stack.append(starting_point)
    visited.add(tuple_board(init_board))  # dodajemy do visited by wiedziec czy juz ten stan sprawdzalismy

    states_counter = 0
    max_depth = 0

    while stack:
        current_node = stack.pop()
        states_counter += 1
        if tuple_board(current_node.board) == tuple_board(target_board):
            end_time = time.time()
            sum_time = end_time - start_time

            path=[]

            while current_node.parent != None:
                path.append(current_node.move)
                current_node = current_node.parent
            return {
                    "sciezka": path[::-1],
                    "dlugosc_sciezka": len(path),
                    "lso": len(visited),
                    "lsp": states_counter,
                    "max_d": max_depth,
                    "t": sum_time
                }
        if current_node.depth < depth_limit: # nie przekaraczamy limitu glebokosci
            for move in ['U', 'D', 'L', 'R']:
                result = next_move(current_node.board, current_node.empty_pos, move)
                if result:
                    new_board, new_empty_pos = result
                    board_tuple = tuple_board(new_board)

                    if board_tuple not in visited: # sprawdzamy czy plansza byla juz "odziedzona"
                        visited.add(board_tuple)
                        new_node = Node(new_board, new_empty_pos, current_node, move, current_node.depth + 1)
                        stack.append(new_node)
                        max_depth = max(max_depth, new_node.depth)
    return None




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

    testdef = checker(board)
    bfs_result = bfs(board, target_board)
    #dfs_result = dfs(board, target_board)

    print(testdef)

    if bfs_result:
        print("Znaleziono rozwiązanie!")
        print(f"Sekwencja ruchów: {' '.join(bfs_result['sciezka'])}")
        print(f"Długość rozwiązania: {bfs_result['dlugosc_sciezka']}")
        print(f"Liczba stanow odwiedzonych: {bfs_result['lso']}")
        print(f"Liczba stanow przetworzonych: {bfs_result['lsp']}")
        print(f"Maksymalna glebokosc: {bfs_result['max_d']}")
        print(f"Czas operacji: {bfs_result['t']:.6f} sekund")
    else:
        print("Nie znaleziono rozwiązania.")

    print("\nAlgorytm DFS")

    #if dfs_result:
    #    print("Znaleziono rozwiązanie!")
    #    print(f"Sekwencja ruchów: {' '.join(dfs_result['sciezka'])}")
    #    print(f"Długość rozwiązania: {dfs_result['dlugosc_sciezka']}")
    #    print(f"Liczba stanow odwiedzonych: {dfs_result['lso']}")
    #    print(f"Liczba stanow przetworzonych: {dfs_result['lsp']}")
    #    print(f"Maksymalna glebokosc: {dfs_result['max_d']}")
    #    print(f"Czas operacji: {dfs_result['t']:.6f} sekund")
    #else:
    #    print("Nie znaleziono rozwiązania.")

if __name__ == "__main__":
    main()