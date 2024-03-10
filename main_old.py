import tkinter as tk
from tkinter import filedialog, messagebox, Checkbutton, Entry, Label, Button, Frame ,ttk
import os

class RenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title('ファイル名置き換えツール')
        self.root.geometry('900x600')
        self.bg_color = '#333333'  # 暗い背景色
        self.fg_color = '#ffffff'  # 明るい前景色
        self.entry_bg = '#555555'  # エントリーの背景色
        self.entry_fg = '#ffffff'  # エントリーのテキスト色
        self.button_color = '#555555'  # ボタンの色
        self.button_active_color = '#777777'  # アクティブなボタンの色

        # ttkスタイルの設定
        style = ttk.Style()
        style.configure('TFrame', background=self.bg_color)
        style.configure('TButton', background=self.button_color, foreground=self.fg_color, borderwidth=1)
        style.map('TButton', background=[('active', self.button_active_color)])
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        style.configure('TEntry', background=self.entry_bg, foreground=self.entry_fg, borderwidth=1)
        style.configure('TCheckbutton', background=self.bg_color, foreground=self.fg_color)

        self.setup_ui()

        self.directory = ''
        self.file_vars = []

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)
        top_frame = ttk.Frame(self.root, style='TFrame')
        top_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(top_frame, text='ディレクトリ選択', command=self.select_directory).pack(side='left', padx=10)
        ttk.Button(top_frame, text='全選択', command=lambda: self.set_all_checkboxes(True)).pack(side='left', padx=10)
        ttk.Button(top_frame, text='全解除', command=lambda: self.set_all_checkboxes(False)).pack(side='left', padx=10)

        self.canvas = tk.Canvas(self.root, borderwidth=0, bg=self.bg_color, highlightthickness=0)
        self.frame = ttk.Frame(self.canvas, style='TFrame')
        self.vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))  

        ttk.Button(top_frame, text='選択したファイルを置き換え', command=self.rename_files).pack(pady=20)


    def select_directory(self):
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.list_directory_contents(self.directory)

    def list_directory_contents(self, path, indent=0):
        try:
            # ディレクトリ内のアイテムを取得
            items = os.listdir(path)
        except PermissionError:
            # 権限がないディレクトリへのアクセスに対するエラー処理
            messagebox.showerror("権限エラー", f"ディレクトリ '{path}' にアクセスする権限がありません。")
            return

        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                # ディレクトリの場合は、再帰的に処理しない
                label = ttk.Label(self.frame, text=item, background=self.bg_color, foreground=self.fg_color)
                label.pack(side="top", fill="x", padx=indent)
            else:
                # ファイルの場合は、ファイル名とリネーム用のテキストボックスを表示
                file_frame = ttk.Frame(self.frame, style='TFrame')
                file_frame.pack(side="top", fill="x", padx=indent)

                var = tk.BooleanVar()
                cb = ttk.Checkbutton(file_frame, variable=var, style='TCheckbutton')
                cb.pack(side="left")

                label = ttk.Label(file_frame, text=item, style='TLabel')
                label.pack(side="left", fill="x", expand=True)

                entry = ttk.Entry(file_frame, style='TEntry')
                entry.pack(side="left", fill="x", expand=True)
                self.file_vars.append((var, item_path, entry))



    def set_all_checkboxes(self, value):
        for var, _, _ in self.file_vars:
            var.set(value)

    def rename_files(self):
        for var, old_name, entry in self.file_vars:
            if var.get():
                base_name = entry.get()
                extension = os.path.splitext(old_name)[1]
                new_name = f"{base_name}{extension}"

                old_path = os.path.join(self.directory, old_name)
                new_path = os.path.join(self.directory, new_name)
                os.rename(old_path, new_path)

        messagebox.showinfo("完了", "選択したファイルの置き換えが完了しました。")
        self.list_files()

def main():
    root = tk.Tk()
    app = RenameApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
