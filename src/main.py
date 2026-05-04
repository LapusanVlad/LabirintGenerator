import tkinter as tk  # importă biblioteca pentru interfață grafică
import random

CELL_SIZE = 20  # dimensiunea fiecărei celule din labirint (pixeli)
DELAY = 40  # delay între pași pentru animație (milisecunde)

# GENERATOR LABIRINT
def generate_maze(width, height):
    maze = [[1]*width for _ in range(height)]  # creează matrice plină de pereți

    def carve(x, y):  # funcție recursivă pentru "săpat" drumuri
        directions = [(2,0), (-2,0), (0,2), (0,-2)]  # direcții de deplasare (2 pași pentru a lăsa pereți între celule)
        random.shuffle(directions)  # amestecă direcțiile pentru aleatoriu

        for dx, dy in directions:  # parcurge direcțiile
            nx, ny = x + dx, y + dy  # calculează noua poziție

            # verifică dacă noua poziție este în interiorul labirintului
            if 0 < nx < width-1 and 0 < ny < height-1:
                if maze[ny][nx] == 1:  # dacă este încă perete
                    maze[ny][nx] = 0  # face celula liberă
                    maze[y + dy//2][x + dx//2] = 0  # sparge peretele dintre celule
                    carve(nx, ny)  # continuă recursiv

    maze[1][1] = 0  # setează punctul de start ca liber
    carve(1,1)  # începe generarea
    return maze  # returnează labirintul generat

# OBIECTIV RANDOM
from collections import deque  # structură de tip coadă pentru BFS

def far_enough_end(maze, start, min_dist=40):
    height = len(maze)  # număr de rânduri
    width = len(maze[0])  # număr de coloane

    queue = deque([(start, 0)])  # coadă pentru BFS: (poziție, distanță)
    visited = set([start])  # set de noduri vizitate
    candidates = []  # poziții valide pentru obiectiv

    while queue:
        (x, y), dist = queue.popleft()  # extrage din coadă

        if dist >= min_dist:  # dacă este suficient de departe de start
            candidates.append((x, y))  # adaugă la candidați

        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:  # vecini (4 direcții)
            nx, ny = x + dx, y + dy  # calculează poziția vecină

            # verifică dacă este în interior
            if 0 <= nx < width and 0 <= ny < height:
                # verifică dacă este drum liber și nevizitat
                if maze[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))  # marchează ca vizitat
                    queue.append(((nx, ny), dist+1))  # adaugă în coadă

    # alege aleator un punct valid sau fallback la start
    return random.choice(candidates) if candidates else start

# DESENARE
def draw_maze(canvas, maze, visited=set(), path=set(), start=None, end=None):
    canvas.delete("all")  # șterge tot de pe canvas

    for y, row in enumerate(maze):  # parcurge fiecare rând
        for x, val in enumerate(row):  # parcurge fiecare coloană
            color = "black" if val == 1 else "white"  # pereți negri, drum alb

            if (x, y) in visited:  # dacă a fost vizitat
                color = "lightblue"
            if (x, y) in path:  # dacă este pe traseul curent
                color = "blue"
            if (x, y) == start:  # start
                color = "green"
            if (x, y) == end:  # final
                color = "red"

            # desenează pătratul
            canvas.create_rectangle(
                x*CELL_SIZE, y*CELL_SIZE,
                (x+1)*CELL_SIZE, (y+1)*CELL_SIZE,
                fill=color, outline="gray"
            )

# DFS ANIMAT
def animate_dfs(canvas, maze, start, end, on_finish):
    rows, cols = len(maze), len(maze[0])  # dimensiuni

    stack = []  # stivă pentru DFS: (x, y, direcții, index curent, direcție precedentă)
    visited = set([start])  # noduri vizitate
    path = [start]  # traseul curent

    def get_directions(prev_dir=None):
        dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # direcții posibile

        random.shuffle(dirs)  # randomizează

        # dacă există direcție anterioară, încearcă să continue pe ea
        if prev_dir and random.random() < 0.7:
            dirs.remove(prev_dir)  # scoate direcția din listă
            dirs.insert(0, prev_dir)  # o pune prima

        return dirs  # returnează lista

    # inițializează stiva cu punctul de start
    stack.append((start[0], start[1], get_directions(None), 0, None))

    running = {"active": True}  # flag pentru animație

    def step():
        if not running["active"]:  # dacă s-a oprit
            return

        if not stack:  # dacă nu mai sunt noduri
            running["active"] = False
            on_finish()
            return

        x, y, dirs, i, prev_dir = stack[-1]  # ia ultimul element din stivă

        draw_maze(canvas, maze, visited, path, start, end)  # redesenează

        if (x, y) == end:  # dacă a ajuns la final
            running["active"] = False
            on_finish()
            return

        if i >= 4:  # dacă a încercat toate direcțiile
            stack.pop()  # elimină nodul
            if path:
                path.pop()  # scoate din traseu (backtracking)
        else:
            dx, dy = dirs[i]  # ia direcția curentă
            stack[-1] = (x, y, dirs, i + 1, prev_dir)  # crește indexul

            nx, ny = x + dx, y + dy  # calculează vecinul

            # verifică dacă e valid
            if 0 <= nx < cols and 0 <= ny < rows:
                if maze[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))  # marchează vizitat
                    path.append((nx, ny))  # adaugă în traseu
                    # adaugă noul nod în stivă
                    stack.append((nx, ny, get_directions((dx, dy)), 0, (dx, dy)))

        if running["active"]:
            canvas.after(DELAY, step)  # programează următorul pas

    step()  # pornește animația

# Aplicatia
def main():
    width, height = 31, 31  # dimensiunea labirintului

    root = tk.Tk()  # creează fereastra
    root.title("Labirint DFS")  # titlu

    canvas = tk.Canvas(root, width=width*CELL_SIZE, height=height*CELL_SIZE)  # canvas
    canvas.pack()  # afișează

    solving = {"active": False}  # flag pentru blocarea butonului

    def new_maze():
        if solving["active"]:  # dacă deja rulează
            return

        solving["active"] = True  # marchează că rulează
        btn.config(state="disabled")  # dezactivează butonul

        maze = generate_maze(width, height)  # generează labirint
        start = (1,1)  # punct start
        end = far_enough_end(maze, start)  # punct final

        draw_maze(canvas, maze, start=start, end=end)  # desenează inițial

        def finished():
            solving["active"] = False  # permite din nou generare
            btn.config(state="normal")  # reactivează butonul

        # pornește solverul după un mic delay
        root.after(300, lambda: animate_dfs(canvas, maze, start, end, finished))

    btn = tk.Button(root, text="Labirint Nou", command=new_maze)  # buton
    btn.pack(pady=10)  # afișează butonul
    new_maze()  # generează primul labirint
    root.mainloop()  # pornește aplicația


if __name__ == "__main__":
    main()
