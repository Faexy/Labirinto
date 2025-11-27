
import tkinter as tk
from tkinter import messagebox
from collections import deque
from typing import List, Tuple, Dict, Optional

class MazeEditorGUI:

    COLORS = {
        "wall": "#1E3A5F",   
        "path": "#FFFFFF",      
        "start": "#4CAF50",   
        "end": "#F44336",  
        "frontier": "#AED6F1", 
        "visited": "#D6EAF8",   
        "final_path": "#FFD700", 
    }

    def __init__(self,
                 cols: int = 30,
                 rows: int = 20,
                 cell_size: int = 25,
                 tempo_ms: int = 25):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.tempo_ms = tempo_ms

        self.labirinto: List[List[str]] = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]

        self.grid_cells: List[List[int]] = [[None]*self.cols for _ in range(self.rows)]

        self.inicio_pos: Optional[Tuple[int,int]] = None
        self.fim_pos: Optional[Tuple[int,int]] = None

        self.fila: Optional[deque] = None
        self.visitados: Optional[set] = None
        self.predecessores: Optional[Dict[Tuple[int,int], Tuple[int,int]]] = None
        self.job_after = None

        self.last_edited_cell: Optional[Tuple[int,int]] = None

        self.root = tk.Tk()
        self.root.title("Solucionador de Labirintos - Editor / Simulação (BFS)")

        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size

        self.canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        self.tool_var = tk.StringVar(value="wall")  
        self.tool_buttons = []  

        self._create_tool_radiobuttons()
        self._create_control_buttons()

        self._draw_initial_grid()

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

    def _create_tool_radiobuttons(self):
        row = 1
        col = 0
        rb_wall = tk.Radiobutton(self.root, text="Parede (#)", variable=self.tool_var, value="wall")
        rb_wall.grid(row=row, column=col, sticky="w", padx=6)
        self.tool_buttons.append(rb_wall)

        rb_path = tk.Radiobutton(self.root, text="Caminho ( )", variable=self.tool_var, value="path")
        rb_path.grid(row=row, column=1, sticky="w", padx=6)
        self.tool_buttons.append(rb_path)

        rb_start = tk.Radiobutton(self.root, text="Início (S)", variable=self.tool_var, value="start")
        rb_start.grid(row=row, column=2, sticky="w", padx=6)
        self.tool_buttons.append(rb_start)

        rb_end = tk.Radiobutton(self.root, text="Fim (E)", variable=self.tool_var, value="end")
        rb_end.grid(row=row, column=3, sticky="w", padx=6)
        self.tool_buttons.append(rb_end)

    def _create_control_buttons(self):
        self.btn_start = tk.Button(self.root, text="Iniciar Busca (BFS)", command=self.iniciar_busca)
        self.btn_start.grid(row=2, column=0, pady=8, padx=6, sticky="we")

        self.btn_reset = tk.Button(self.root, text="Resetar Busca", command=self.resetar_busca)
        self.btn_reset.grid(row=2, column=1, pady=8, padx=6, sticky="we")

        self.btn_clear = tk.Button(self.root, text="Limpar Labirinto", command=self.limpar_labirinto)
        self.btn_clear.grid(row=2, column=2, pady=8, padx=6, sticky="we")

        self.btn_quit = tk.Button(self.root, text="Sair", command=self.root.destroy)
        self.btn_quit.grid(row=2, column=3, pady=8, padx=6, sticky="we")

    def _draw_initial_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill=self.COLORS["path"],
                                                    outline="#CCCCCC")
                self.grid_cells[r][c] = rect

    def _cell_coords_from_event(self, event) -> Optional[Tuple[int,int]]:
        x, y = event.x, event.y
        if x < 0 or y < 0:
            return None
        c = x // self.cell_size
        r = y // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return (r, c)
        return None

    def _paint_cell(self, r: int, c: int, color: str):
        rect_id = self.grid_cells[r][c]
        if rect_id is not None:
            self.canvas.itemconfig(rect_id, fill=color)

    def _set_model_cell(self, r:int, c:int, value: str):
        self.labirinto[r][c] = value

    def on_canvas_click(self, event):
        coords = self._cell_coords_from_event(event)
        if not coords:
            return
        self.last_edited_cell = None
        self.editar_celula(coords[0], coords[1], tool=self.tool_var.get())

    def on_canvas_drag(self, event):
        coords = self._cell_coords_from_event(event)
        if not coords:
            return
        if coords == self.last_edited_cell:
            return
        self.last_edited_cell = coords
        self.editar_celula(coords[0], coords[1], tool=self.tool_var.get())

    def on_canvas_release(self, event):
        self.last_edited_cell = None

    def editar_celula(self, r:int, c:int, tool:str):

        current = self.labirinto[r][c]
        if tool == "wall":
            self._set_model_cell(r, c, '#')
            self._paint_cell(r, c, self.COLORS["wall"])
            if self.inicio_pos == (r,c):
                self.inicio_pos = None
            if self.fim_pos == (r,c):
                self.fim_pos = None
        elif tool == "path":
            self._set_model_cell(r, c, ' ')
            self._paint_cell(r, c, self.COLORS["path"])
            if self.inicio_pos == (r,c):
                self.inicio_pos = None
            if self.fim_pos == (r,c):
                self.fim_pos = None
        elif tool == "start":
            if self.inicio_pos and self.inicio_pos != (r,c):
                pr, pc = self.inicio_pos
                self._set_model_cell(pr, pc, ' ')
                self._paint_cell(pr, pc, self.COLORS["path"])
            self._set_model_cell(r, c, 'S')
            self._paint_cell(r, c, self.COLORS["start"])
            self.inicio_pos = (r, c)
            if self.fim_pos == (r,c):
                self.fim_pos = None
        elif tool == "end":
            if self.fim_pos and self.fim_pos != (r,c):
                pr, pc = self.fim_pos
                self._set_model_cell(pr, pc, ' ')
                self._paint_cell(pr, pc, self.COLORS["path"])
            self._set_model_cell(r, c, 'E')
            self._paint_cell(r, c, self.COLORS["end"])
            self.fim_pos = (r, c)
            if self.inicio_pos == (r,c):
                self.inicio_pos = None

    def iniciar_busca(self):
        if not self.inicio_pos or not self.fim_pos:
            messagebox.showinfo("Aviso", "Defina a posição de Início (S) e Fim (E) antes de iniciar a busca.")
            return

        self._set_controls_state("disabled")

        self.fila = deque()
        self.visitados = set()
        self.predecessores = dict()

        sr, sc = self.inicio_pos
        self.fila.append((sr, sc))
        self.visitados.add((sr, sc))
        self._cells_touched_by_search = set()
        self._cells_touched_by_search.add((sr, sc))

        self._paint_cell(sr, sc, self.COLORS["start"])
        er, ec = self.fim_pos
        self._paint_cell(er, ec, self.COLORS["end"])

        self.job_after = self.root.after(self.tempo_ms, self.processar_passo_bfs)

    def processar_passo_bfs(self):
        if not (self.fila and self.visitados is not None and self.predecessores is not None):
            return 

        if not self.fila:
            messagebox.showinfo("Resultado", "Caminho não encontrado.")
            self._finalizar_busca()
            return

        r, c = self.fila.popleft()

        if (r,c) != self.inicio_pos and (r,c) != self.fim_pos:
            self._paint_cell(r, c, self.COLORS["visited"])

        if (r, c) == self.fim_pos:
            self.reconstruir_caminho()
            self._finalizar_busca()
            return

        for dr, dc in [(-1,0), (0,1), (1,0), (0,-1)]:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                continue
            if (nr, nc) in self.visitados:
                continue
            cell_value = self.labirinto[nr][nc]
            if cell_value == '#':
                continue

            self.predecessores[(nr, nc)] = (r, c)
            self.visitados.add((nr, nc))
            self._cells_touched_by_search.add((nr, nc))

            if (nr, nc) != self.fim_pos and (nr, nc) != self.inicio_pos:
                self._paint_cell(nr, nc, self.COLORS["frontier"])

            self.fila.append((nr, nc))

        self.job_after = self.root.after(self.tempo_ms, self.processar_passo_bfs)

    def reconstruir_caminho(self):

        if not self.predecessores or not self.fim_pos or not self.inicio_pos:
            return

        node = self.fim_pos
        path = []
        while node != self.inicio_pos:
            path.append(node)
            node = self.predecessores.get(node)
            if node is None:
                break

        for (r,c) in path:
            if (r,c) != self.fim_pos and (r,c) != self.inicio_pos:
                self._paint_cell(r, c, self.COLORS["final_path"])

        messagebox.showinfo("Resultado", "Caminho encontrado e destacado.")

    def _finalizar_busca(self):
        self._set_controls_state("normal")
        self.job_after = None
        self.fila = None
        self.visitados = None
        self.predecessores = None

    def resetar_busca(self):
        if self.job_after is not None:
            try:
                self.root.after_cancel(self.job_after)
            except Exception:
                pass
            self.job_after = None

        touched = getattr(self, "_cells_touched_by_search", None)
        if touched:
            for (r,c) in list(touched):
                if self.labirinto[r][c] == '#':
                    self._paint_cell(r, c, self.COLORS["wall"])
                elif self.labirinto[r][c] == 'S':
                    self._paint_cell(r, c, self.COLORS["start"])
                elif self.labirinto[r][c] == 'E':
                    self._paint_cell(r, c, self.COLORS["end"])
                else:
                    self._paint_cell(r, c, self.COLORS["path"])
            self._cells_touched_by_search.clear()

        for r in range(self.rows):
            for c in range(self.cols):
                if self.labirinto[r][c] == '#':
                    self._paint_cell(r, c, self.COLORS["wall"])
                elif self.labirinto[r][c] == 'S':
                    self._paint_cell(r, c, self.COLORS["start"])
                elif self.labirinto[r][c] == 'E':
                    self._paint_cell(r, c, self.COLORS["end"])
                else:
                    self._paint_cell(r, c, self.COLORS["path"])

        self._set_controls_state("normal")

        self.fila = None
        self.visitados = None
        self.predecessores = None

    def limpar_labirinto(self):
        if self.job_after is not None:
            try:
                self.root.after_cancel(self.job_after)
            except Exception:
                pass
            self.job_after = None

        self.labirinto = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.inicio_pos = None
        self.fim_pos = None

        for r in range(self.rows):
            for c in range(self.cols):
                self._paint_cell(r, c, self.COLORS["path"])

        self.fila = None
        self.visitados = None
        self.predecessores = None
        self._cells_touched_by_search = set()
        self._set_controls_state("normal")

    def _set_controls_state(self, state: str):
        for rb in self.tool_buttons:
            try:
                rb.configure(state=state)
            except Exception:
                pass
        for btn in [self.btn_start, self.btn_reset, self.btn_clear, self.btn_quit]:
            try:
                btn.configure(state=state if btn != self.btn_quit else "normal")  
            except Exception:
                pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MazeEditorGUI(cols=30, rows=20, cell_size=28, tempo_ms=25)
    app.run()
