import tkinter as tk


class TarotCardDisplayApp:

    Cards = []
    windows_width = 0
    windows_height = 0

    def __init__(self, root):
        self.root = root
        self.root.title("塔罗牌展示软件")
        self.root.resizable(True, True)

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size to match screen size
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # 创建菜单栏
        self.menubar = tk.Menu(self.root)

        # 创建 Files 菜单
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Files", menu=self.file_menu)

        # 创建 Tools 菜单
        self.tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=self.tools_menu)

        # 创建 Settings 菜单
        self.settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Settings", menu=self.settings_menu)

        # 将菜单栏添加到窗口
        self.root.config(menu=self.menubar)

        # 创建画布
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 获取窗口的宽度和高度
        self.window_width = screen_width
        self.window_height = screen_height

        # 计算矩形的位置
        x = (self.window_width - 100) // 2
        y = (self.window_height - 50) // 2
        
        self.create_rectangle(x,y)

    
    def create_rectangle(self,x,y):
        # Create a filled rectangle for hit detection
        hit_rect = self.canvas.create_rectangle(x, y, x + 150, y + 200, fill="white", stipple="gray50", state="normal")
        # Create the visible outline rectangle
        rect = self.canvas.create_rectangle(x, y, x + 150, y + 200, fill="", outline="black", width=5)
        # Store both rectangles as a tuple
        self.Cards.append((hit_rect, rect))
        # Create index number above the rectangle
        index_num = len(self.Cards)
        text = self.canvas.create_text(x + 75, y - 2, text=str(index_num), anchor="s", font=("Arial", 24))
        # Store text with rectangles to enable movement
        self.Cards[-1] = (self.Cards[-1][0], self.Cards[-1][1], text)
        # Bind events to both rectangles
        for r in (hit_rect, rect):
            self.canvas.tag_bind(r, "<ButtonPress-1>", self.on_press)
            self.canvas.tag_bind(r, "<B1-Motion>", self.on_drag)
    
    def on_press(self, event):
        # Store the initial coordinates
        self.start_x = event.x
        self.start_y = event.y
        # Find which rectangle was clicked
        clicked = self.canvas.find_closest(event.x, event.y)[0]
        # Find the associated rectangle group
        for hit_rect, rect, text in self.Cards:
            if clicked in (hit_rect, rect):
                self.current_group = (hit_rect, rect, text)
                break

    def on_drag(self, event):
        # Calculate the movement delta
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        # Move both rectangles and the text
        if hasattr(self, 'current_group'):
            for item in self.current_group:
                self.canvas.move(item, dx, dy)
        # Update the starting position for next movement
        self.start_x = event.x
        self.start_y = event.y


if __name__ == "__main__":
    root = tk.Tk()
    app = TarotCardDisplayApp(root)
    root.mainloop()