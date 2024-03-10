import tkinter as tk
from tkinter import filedialog, messagebox,ttk
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
        self.sub_frames = {} 
        self.next_row = 0

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
            # 一度に表示する内容をクリアします。
            for widget in self.frame.winfo_children():
                widget.destroy()
            # level 引数に 0 を渡します。
            self.list_directory_contents(self.directory, self.frame, 0)

    def list_directory_contents(self, path, parent_widget, level=0):
        items = os.listdir(path)
        row = 0  # グリッド内の行の位置を追跡
        for item in sorted(items, key=lambda x: (os.path.isfile(os.path.join(path, x)), x.lower())):
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            
            if is_dir:
                # ディレクトリの場合、ラベルを作成し、クリックイベントをバインド
                dir_label = ttk.Label(parent_widget, text='[+] ' + item, style='TLabel', cursor="hand2")
                dir_label.grid(row=row, column=0, sticky='w', padx=20*level)
                dir_label.bind('<Button-1>', lambda e, p=item_path, pw=parent_widget: self.on_directory_click(e, p, pw, level))
            else:
                # ファイルの場合、ファイル名と隣にテキストボックスを表示
                file_label = ttk.Label(parent_widget, text='    ' * level + item, style='TLabel')
                file_label.grid(row=row, column=0, sticky='w', padx=20*level)
                file_entry = ttk.Entry(parent_widget, width=30, background=self.entry_bg, foreground=self.entry_fg)
                file_entry.grid(row=row, column=1, sticky='w')
                self.file_vars.append((item_path, file_entry))  # パスとエントリーウィジェットを保存
            row += 1

    def on_directory_click(self, event, path, parent_widget, level):
        text = event.widget.cget("text")
        if text.startswith("[+]"):  # If the directory is being expanded
            event.widget.config(text=text.replace("[+]", "[-]", 1))
            if path not in self.sub_frames:  # If the subframe for this directory doesn't exist
                sub_frame = ttk.Frame(parent_widget, style='TFrame')
                sub_frame.grid(row=event.widget.grid_info()['row'] + 1, column=0, sticky='w', columnspan=2)
                self.list_directory_contents(path, sub_frame, level+1)
                self.sub_frames[path] = sub_frame  # Store the subframe in the dictionary
            else:
                # If it does exist, just make it visible
                self.sub_frames[path].grid()
        else:  # If the directory is being collapsed
            event.widget.config(text=text.replace("[-]", "[+]", 1))
            if path in self.sub_frames:
                # Make the subframe invisible instead of destroying it
                self.sub_frames[path].grid_remove()

        # Rearrange all following widgets in the grid to avoid overlapping
        self.rearrange_widgets(parent_widget, event.widget.grid_info()['row'] + 1)

    def set_all_checkboxes(self, value):
        for var, _, _ in self.file_vars:
            var.set(value)

    def rename_files(self):
        # ファイル名の変更を記録する辞書
        rename_dict = {}

        for item_path, entry in self.file_vars:
            try:
                new_name = entry.get()
            except tk.TclError:
                continue
            if new_name and new_name != os.path.basename(item_path):  # 新しい名前があり、元の名前と異なる場合のみ
                dir_name = os.path.dirname(item_path)
                new_path = os.path.join(dir_name, new_name)
                os.rename(item_path, new_path)
                rename_dict[os.path.basename(item_path)] = new_name

        # ファイル内のテキストを更新
        if rename_dict:
            self.update_file_contents(self.directory, rename_dict)

        messagebox.showinfo("完了", "選択したファイルの置き換えが完了しました。")
        self.refresh_directory_contents()

    def update_file_contents(self, dir_path, rename_dict):
        for root, _, files in os.walk(dir_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r+', encoding='utf-8') as file:
                    content = file.read()
                    updated_content = content
                    for old_name, new_name in rename_dict.items():
                        # ファイル名の更新
                        updated_content = updated_content.replace(old_name, new_name)
                        # C/C++の二重インクルード防止のマクロも更新
                        macro_old = old_name.replace('.', '_').upper()
                        macro_new = new_name.replace('.', '_').upper()
                        updated_content = updated_content.replace(macro_old, macro_new)
                    if content != updated_content:
                        file.seek(0)
                        file.write(updated_content)
                        file.truncate()

    def refresh_directory_contents(self):
        # 現在選択されているディレクトリの内容を再表示
        for widget in self.frame.winfo_children():
            widget.destroy()  # 既存のウィジェットをクリア
        self.list_directory_contents(self.directory, self.frame, 0)

def main():
    root = tk.Tk()
    app = RenameApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
