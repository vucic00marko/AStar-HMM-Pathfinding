import tkinter as tk
import numpy as np
import threading
from queue import Queue

def create_grid(root, rows, columns):
    grid = []
    for i in range(rows):
        row = []
        for j in range(columns):
            if i == rows // 2 and j == columns // 2:
                entry = tk.Entry(root, width=16, bg='yellow')
            else:
                entry = tk.Entry(root, width=16, bg='white')
            entry.grid(row=i, column=j)
            row.append(entry)
        grid.append(row)
    return grid

def get_input_values(grid):
    values = []
    for row in grid:
        row_values = []
        for entry in row:
            value = entry.get()
            try:
                value = float(value)
            except ValueError:
                value = 0.0
            row_values.append(value)
        values.append(row_values)
    return np.array(values)

def tk_window_input(title: str) -> np.ndarray:
    input_queue = Queue()

    def create_window():
        root = tk.Tk()
        root.title(title)
        rows, columns = 3, 3
        root.geometry(f"{100*columns}x{20*rows + 20}")
        grid = create_grid(root, rows, columns)

        def process_and_close():
            input_values = get_input_values(grid)
            input_queue.put(input_values)
            root.quit()
            root.destroy()

        submit_button = tk.Button(root, text="Submit", command=process_and_close)
        submit_button.grid(row=rows, columnspan=columns)

        root.mainloop()

    input_thread = threading.Thread(target=create_window)
    input_thread.start()
    input_thread.join()

    return input_queue.get()
