import tkinter as tk


class TarotCardDisplayApp:

    Cards = []
    Cards_content = []
    Cards_name = ["1","2","3"]
    windows_width = 0
    windows_height = 0
    add_card_button = 0
    add_card_text = 0
    popup = None
    popup_selected_index = -100

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
        
        print(self.window_width,self.window_height,self.window_width - 50,self.window_height - 30)
        self.add_card_button = self.canvas.create_oval(self.window_width - 85, self.window_height - 175,self.window_width- 30,self.window_height- 115, fill="white", outline="black",width=3)
        self.add_card_text = self.canvas.create_text(self.window_width - 57, self.window_height - 145, text="+", font=("Arial", 38))
        self.canvas.tag_bind(self.add_card_button, "<Button-1>", lambda event: self.create_rectangle(x,y))
        self.canvas.tag_bind(self.add_card_text, "<Button-1>", lambda event: self.create_rectangle(x,y))
        self.create_rectangle(x,y)


    
    def create_rectangle(self,x,y):
        # Create a filled rectangle for hit detection
        hit_rect = self.canvas.create_rectangle(x, y, x + 150, y + 200, fill="white", stipple="gray50", state="normal")
        # Create the visible outline rectangle
        rect = self.canvas.create_rectangle(x, y, x + 150, y + 200, fill="", outline="black", width=5)
        # Store both rectangles as a tuple
        self.Cards.append((hit_rect, rect))
        self.Cards_content.append(0)
        # Create index number above the rectangle
        index_num = len(self.Cards)
        text = self.canvas.create_text(x + 75, y - 2, text=str(index_num), anchor="s", font=("Arial", 24))
        # Store text with rectangles to enable movement
        self.Cards[-1] = (self.Cards[-1][0], self.Cards[-1][1], text)
        # Bind events to both rectangles
        for r in (hit_rect, rect):
            self.canvas.tag_bind(r, "<ButtonPress-1>", self.card_on_press)
            self.canvas.tag_bind(r, "<B1-Motion>", self.card_on_drag)
            self.canvas.tag_bind(r, "<ButtonPress-3>", self.card_right_click)  # Add right-click binding
    
    def card_on_press(self, event):
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

    def card_on_drag(self, event):
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

    def card_right_click(self, event):
        # Find which rectangle was right-clicked
        clicked = self.canvas.find_closest(event.x, event.y)[0]
        print(event.x,event.y)
        # Find the index of clicked rectangle in self.Cards array
        clicked_index = -1
        for i, (hit_rect, rect, text) in enumerate(self.Cards):
            if clicked in (hit_rect, rect):
                clicked_index = i
                break
        # Find the associated rectangle group
        for hit_rect, rect, text in self.Cards:
            if clicked in (hit_rect, rect):
                # Create right-click menu
                if self.Cards_content[clicked_index] == 0:
                    cardset = "Add"
                else:
                    cardset = "Edit"
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label=cardset,command=lambda: self.card_to_image(hit_rect, rect, text, event))
                menu.add_command(label="Delete", command=lambda: self.delete_card(hit_rect, rect, text))
                menu.add_command(label="Cancel")
                
                # Display the menu at cursor position
                menu.post(event.x_root, event.y_root)
                
    def card_to_image(self, hit_rect,rect, text,event):
        # Find which rectangle was clicked
        clicked = self.canvas.find_closest(event.x, event.y)[0]
        # Create a popup window
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Popup Window")
        self.popup.geometry("300x600")
        # Create a listbox within the popup window
        listbox = tk.Listbox(self.popup)
        listbox.pack(fill=tk.BOTH, expand=True)
        #set the listbox can be scrolled
        scrollbar = tk.Scrollbar(self.popup, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

        # Add items to the listbox
        for i in range(0,len(self.Cards_name)):
            listbox.insert(tk.END, self.Cards_name[i])

        # 初始化 selected_index 属性
        self.popup_selected_index = None
        
        # 绑定选择事件
        listbox.bind("<<ListboxSelect>>", lambda event: self.handle_listbox_select(event, hit_rect, rect, text,clicked))

        
    def handle_listbox_select(self, event,hit_rect, rect, text,clicked):
        # 获取选择的索引并保存
        self.popup_selected_index = self.on_listbox_select(event, hit_rect, rect, text,clicked)
    
    def on_listbox_select(self, event, hit_rect, rect, text, clicked):
        # Return the number of the selected item
        self.popup_selected_index = event.widget.curselection()[0]
        selected_item = event.widget.get(self.popup_selected_index)
        # Close the popup window
        self.popup.destroy()
        self.delete_card(hit_rect, rect, text)
        print("bbbb",self.popup_selected_index)

    def display_image(self,hit_rect, rect, text,clicked):
        # Find which rectangle was clicked
        clicked = self.canvas.find_closest(event.x, event.y)[0]
        # Find the position of the clicked rectangle
        rect_coords = self.canvas.coords(clicked)
        # Find the index of clicked rectangle in self.Cards array
        clicked_index = -1
        for i, (hit_rect, rect, text) in enumerate(self.Cards):
            if clicked in (hit_rect, rect):
                clicked_index = i
                break
        x = rect_coords[0]
        y = rect_coords[1]
        # Create a image by local file
        # handle the image path
        if self.popup_selected_index == None:
            image_path = "1.png"
        else:
            image_path = str(self.popup_selected_index) + ".png"
        print(image_path)
        photo = tk.PhotoImage(file="1.png")
        image = self.canvas.create_image(x, y, anchor=tk.NW, image=photo)
    def delete_card(self, hit_rect, rect, text):
        # Remove the rectangle group from the canvas
        self.canvas.delete(hit_rect, rect, text)


if __name__ == "__main__":
    root = tk.Tk()
    app = TarotCardDisplayApp(root)
    root.mainloop()