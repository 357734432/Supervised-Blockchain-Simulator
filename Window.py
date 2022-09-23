import tkinter as tk
from tkinter import ttk
from Read_excel import readExcel

class Window:
    def mainwindow():
        window = tk.Tk()
        window.title('基于跨链共识机制的以链治链监管系统原型')

        frame = tk.Frame(window)
        frame_left = tk.Frame(frame)
        frame_right = tk.Frame(frame)
        frame_left.pack(side='left')
        frame_right.pack(side='right', fill='both')
        frame.pack()
        tk.Frame(frame_right, width=600).pack(side=tk.TOP)

        excel = readExcel()

        tk.Label(frame_left, text='实验结果', bg='GREY').pack(fill='x')
        listbox = tk.Listbox(frame_left, height=10)
        for i in range(1, len(excel.sheet_names)):
            listbox.insert(i, excel.sheet_names[i])

        listbox.bind('<Double-Button-1>', lambda event: on_click())
        listbox.pack(side=tk.LEFT)

        def on_click():
            for widget in frame_right.winfo_children():
                widget.destroy()
            position = listbox.curselection()[0]
            tree = ttk.Treeview(frame_right, height=10)

            table_num = position+1
            title = excel.read_line(table_num, 1)
            lines = excel.get_lines(table_num)
            tree["columns"] = title
            for i in range(len(title)):
                tree.column(i, width=100)
                tree.heading(i, text=title[i])
            for i in range(1, lines):
                tree.insert("", i, text="line{}".format(i), values=excel.read_line(table_num, i + 1))

            tree.pack()

        window.mainloop()

