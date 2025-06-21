import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import os
from FileFunction import FileFunction
from tkinter import filedialog
# -*- coding: utf-8 -*-


class TarotCardDisplayApp:

    FileFunction = FileFunction()
    Cards = []
    #Cards列表是一个嵌套列表，其结构为[[[卡片对象]，卡片状态（0为空白，1为已添加），卡片的x位置，卡片的y位置，卡片的正位逆位（-1为未添加，0为正位，1为逆位），卡片的图片路径（-1未添加）],[...],[...]]    
    Cards_name = ["1","2","3"]
    windows_width = 0
    windows_height = 0
    add_card_button = 0
    add_card_text = 0
    popup = None
    is_open_file = False
    opened_file_path = ""
    popup_selected_index = -100
    
    # 添加画布缩放相关变量
    scale_factor = 1.0  # 初始缩放比例为1.0
    min_scale = 0.1     # 最小缩放比例
    max_scale = 5.0     # 最大缩放比例
    scale_step = 0.1    # 每次缩放的步长
    canvas_x_offset = 0  # 画布X偏移量
    canvas_y_offset = 0  # 画布Y偏移量
    scale_text = None    # 显示缩放比例的文本
    
    # 卡片基础尺寸
    base_card_width = 150
    base_card_height = 200

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
        #添加新建文件选项
        #self.file_menu.add_command(label="New", command=self.FileFunction.New)
        #添加打开文件选项
        self.file_menu.add_command(label="Open", command=self.read_file)
        #添加保存文件选项
        self.file_menu.add_command(label="Save", command=self.save_file)
        #添加保存文件为选项
        #self.file_menu.add_command(label="Save As", command=self.FileFunction.SaveAs)

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
        
        # 绑定鼠标滚轮事件用于缩放
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        # 绑定鼠标中键拖动事件用于平移画布
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan_canvas)

        # 获取窗口的宽度和高度
        self.window_width = screen_width
        self.window_height = screen_height

        # 计算矩形的位置 - 现在是相对于画布中心
        self.center_x = self.window_width // 2
        self.center_y = self.window_height // 2
        
        # 设置Cards_name的数量
        for i in range(0,78):
            self.Cards_name.append("")
            self.Cards_name[i] = str(i+1)

        # 创建添加卡片按钮
        self.add_card_button = self.canvas.create_oval(
            self.window_width - 85, self.window_height - 175,
            self.window_width - 30, self.window_height - 115, 
            fill="white", outline="black", width=3, tags="control")
        self.add_card_text = self.canvas.create_text(
            self.window_width - 57, self.window_height - 145, 
            text="+", font=("Arial", 38), tags="control")
        
        # 创建缩放控制按钮
        self.zoom_in_button = self.canvas.create_oval(
            self.window_width - 85, self.window_height - 85,
            self.window_width - 30, self.window_height - 30, 
            fill="white", outline="black", width=3, tags="control")
        self.zoom_in_text = self.canvas.create_text(
            self.window_width - 57, self.window_height - 57, 
            text="+", font=("Arial", 24), tags="control")
            
        self.zoom_out_button = self.canvas.create_oval(
            self.window_width - 155, self.window_height - 85,
            self.window_width - 100, self.window_height - 30, 
            fill="white", outline="black", width=3, tags="control")
        self.zoom_out_text = self.canvas.create_text(
            self.window_width - 127, self.window_height - 57, 
            text="-", font=("Arial", 24), tags="control")
            
        # 创建显示缩放比例的文本
        self.scale_text = self.canvas.create_text(
            self.window_width - 200, self.window_height - 100, 
            text="100%", font=("Arial", 12), tags="control")
        
        # 绑定按钮事件
        self.canvas.tag_bind(self.add_card_button, "<Button-1>", self.add_card_at_center)
        self.canvas.tag_bind(self.add_card_text, "<Button-1>", self.add_card_at_center)
        self.canvas.tag_bind(self.zoom_in_button, "<Button-1>", lambda e: self.zoom(self.scale_step))
        self.canvas.tag_bind(self.zoom_in_text, "<Button-1>", lambda e: self.zoom(self.scale_step))
        self.canvas.tag_bind(self.zoom_out_button, "<Button-1>", lambda e: self.zoom(-self.scale_step))
        self.canvas.tag_bind(self.zoom_out_text, "<Button-1>", lambda e: self.zoom(-self.scale_step))
        
        # 创建第一张卡片在中心
        self.add_card_at_center(None)
    
    def add_card_at_center(self, event):
        """在画布中心添加新卡片"""
        # 计算画布中心位置
        canvas_center_x = self.center_x + self.canvas_x_offset
        canvas_center_y = self.center_y + self.canvas_y_offset
        
        # 计算卡片左上角位置（考虑缩放后的卡片尺寸）
        card_width = self.base_card_width * self.scale_factor
        card_height = self.base_card_height * self.scale_factor
        x = canvas_center_x - (card_width / 2)
        y = canvas_center_y - (card_height / 2)
        
        # 创建卡片
        self.create_card(x, y, [0, 0], -1)
    
    def start_pan(self, event):
        """开始平移画布"""
        self.canvas.scan_mark(event.x, event.y)
        
    def pan_canvas(self, event):
        """平移画布"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        # 更新画布偏移量
        self.canvas_x_offset += (event.x - self.canvas.scan_mark()[0])
        self.canvas_y_offset += (event.y - self.canvas.scan_mark()[1])
        self.canvas.scan_mark(event.x, event.y)
    
    def on_mouse_wheel(self, event):
        """鼠标滚轮事件处理"""
        # 获取滚轮方向 (Windows)
        delta = event.delta
        
        # 根据滚轮方向缩放
        if delta > 0:
            self.zoom(self.scale_step, event.x, event.y)
        else:
            self.zoom(-self.scale_step, event.x, event.y)
    
    def zoom(self, delta, x=None, y=None):
        """缩放画布"""
        new_scale = self.scale_factor + delta
        if new_scale < self.min_scale or new_scale > self.max_scale:
            return
        if x is None:
            x = self.window_width / 2
        if y is None:
            y = self.window_height / 2
        scale_change = new_scale / self.scale_factor
        self.scale_factor = new_scale
        # 记录所有卡片的原始信息
        card_infos = []
        for card in self.Cards:
            card_infos.append({
                'status': card[1],
                'x': card[2],
                'y': card[3],
                'orientation': card[4],
                'image_path': card[5]
            })
        # 删除所有卡片
        for card in self.Cards:
            for item in card[0]:
                if isinstance(item, int):
                    self.canvas.delete(item)
        self.Cards = []
        # 重新创建所有卡片（全部append，不用index）
        for info in card_infos:
            rel_x = info['x'] - x
            rel_y = info['y'] - y
            new_x = x + rel_x * scale_change
            new_y = y + rel_y * scale_change
            if info['status'] == 0:
                self.create_card(new_x, new_y, [0, 0], -1)
            else:
                # 计算图片编号
                if info['image_path'] and isinstance(info['image_path'], str):
                    try:
                        card_num = int(os.path.splitext(os.path.basename(info['image_path']))[0])
                    except:
                        card_num = 1
                else:
                    card_num = 1
                self.popup_selected_index = card_num - 1
                self.create_card(new_x, new_y, [1, info['orientation']], -1)
        self.canvas.itemconfig(self.scale_text, text=f"{int(self.scale_factor * 100)}%")

    def read_file(self):
        # Popup a file choose dialog
        self.opened_file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if self.opened_file_path:
            temp_Cards = self.FileFunction.read_whole_array(self.opened_file_path)
            self.is_open_file = True
            print("temp_va",temp_Cards)
            # Clear all the cards
            for i in range(len(self.Cards)):
                for j in range(len(self.Cards[i][0])):
                    self.canvas.delete(self.Cards[i][0][j])
            
            self.Cards = []  # Clear card list
            for i in range(len(temp_Cards)):
                # Extract image path components
                url = temp_Cards[i][4]
                filename = url.split('/')[-1]  # Get '3.jpg' from 'WaiteDeck/3.jpg'
                card_number = filename.split('.')[0]  # Get '3' from '3.jpg'
                self.popup_selected_index = int(card_number) - 1  # Convert to 0-based index
                
                # Get stored position and orientation
                x_pos = float(temp_Cards[i][1])
                y_pos = float(temp_Cards[i][2])
                orientation = int(temp_Cards[i][3])  # 0=upright, 1=reversed
                
                # 1. Create a blank card first (status [0,0])
                self.create_card(x_pos, y_pos, [0, 0], -1)
                
                # 2. Update the newly created card with image data (status [1, orientation])
                # The new card will be the last one in the Cards list
                card_index = len(self.Cards) - 1
                self.create_card(x_pos, y_pos, [1, orientation], card_index)

            messagebox.showinfo("Info", "File opened successfully.", icon=messagebox.INFO)

    def save_file(self):
        # Detect if is open file
        if self.is_open_file:
            self.FileFunction.save_whole_array(self.Cards, self.opened_file_path)
        else:
            # Popup a file choose dialog
            self.opened_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if self.opened_file_path:
                self.FileFunction.save_whole_array(self.Cards, self.opened_file_path)
                self.is_open_file = True
                messagebox.showinfo("Info", "File saved successfully.", icon=messagebox.INFO)
            else:
                messagebox.showinfo("Info", "File not saved.", icon=messagebox.INFO)
                self.is_open_file = False
                return

    def create_card(self, x, y, status, index_num, update=False):
        """创建或更新卡片
        status是一个列表第一个参数为0创建空白卡片，1为创建图片 第二个参数为0是正位，1为逆位
        update为True时表示更新现有卡片而不是创建新卡片
        """
        print("create_card", x, y, status, index_num)
        
        # 计算当前缩放下的卡片尺寸
        card_width = self.base_card_width * self.scale_factor
        card_height = self.base_card_height * self.scale_factor
        font_size = int(24 * self.scale_factor)  # 缩放字体大小
        
        if status[0] == 0:  # 创建空白卡片
            hit_rect = self.canvas.create_rectangle(
                x, y, x + card_width, y + card_height, 
                fill="white", stipple="gray50", state="normal", tags="card")
                
            # Create the visible outline rectangle
            rect = self.canvas.create_rectangle(
                x, y, x + card_width, y + card_height, 
                fill="", outline="black", width=max(1, int(5 * self.scale_factor)), tags="card")
                
            if not update:  # 如果是新建卡片而不是更新
                self.Cards.append([[rect, hit_rect], 0, x, y, -1, -1])
                # Create the text_num over the the card
                text_num = len(self.Cards)
                text_obj = self.canvas.create_text(
                    x + (card_width / 2), y - (20 * self.scale_factor), 
                    text=text_num, font=("Arial", font_size), tags="card")
                # Store the text_num in the corresponding element of the Cards list
                control_index = len(self.Cards) - 1
                self.Cards[control_index][0].append(text_obj)
            else:  # 更新现有卡片
                self.Cards[index_num][0] = [rect, hit_rect]
                # 更新卡片编号文本
                text_obj = self.canvas.create_text(
                    x + (card_width / 2), y - (20 * self.scale_factor), 
                    text=index_num + 1, font=("Arial", font_size), tags="card")
                self.Cards[index_num][0].append(text_obj)
                # 更新卡片位置
                self.Cards[index_num][2] = x
                self.Cards[index_num][3] = y
                
            # Bind events to the card
            for r in (hit_rect, rect):
                self.canvas.tag_bind(r, "<B1-Motion>", self.card_on_drag)
                self.canvas.tag_bind(r, "<ButtonPress-3>", self.card_right_click)
                
        elif status[0] == 1:  # 创建图片卡片
            # 计算图片的路径
            image_path = "WaiteDeck/" + str(self.popup_selected_index + 1) + ".jpg"
            # Load the image
            image = Image.open(image_path)
            image = image.resize((int(card_width), int(card_height)))
            
            # 创建图片对象
            photo = ImageTk.PhotoImage(image)
            
            # 如果是更新现有卡片，先删除旧的图形
            if not update and index_num >= 0:
                try:
                    self.canvas.delete(self.Cards[index_num][0][0])
                    self.canvas.delete(self.Cards[index_num][0][1])
                except:
                    pass
                    
            # 根据正逆位创建图片
            if status[1] == 0:  # 正位
                img_obj = self.canvas.create_image(x, y, image=photo, anchor=tk.NW, tags="card")
                if index_num >= 0:
                    self.Cards[index_num][4] = 0  # 正位
            elif status[1] == 1:  # 逆位
                # 将图片旋转180度
                image = image.rotate(180)
                photo = ImageTk.PhotoImage(image)
                img_obj = self.canvas.create_image(x, y, image=photo, anchor=tk.NW, tags="card")
                if index_num >= 0:
                    self.Cards[index_num][4] = 1  # 逆位

            # 创建或初始化图片引用字典
            if not hasattr(self, 'photo_references'):
                self.photo_references = {}
                
            # 更新或创建卡片数据
            if index_num >= 0:
                # 保存图片引用到字典中，防止被垃圾回收
                self.photo_references[index_num] = photo
                
                self.Cards[index_num][0][0] = img_obj
                self.Cards[index_num][0][1] = img_obj  # 不再直接存储photo对象
                self.Cards[index_num][1] = 1  # 更新卡片状态
                self.Cards[index_num][5] = image_path  # 更新图片路径
                self.Cards[index_num][2] = x  # 更新位置
                self.Cards[index_num][3] = y
                
                # 更新卡片编号文本
                if len(self.Cards[index_num][0]) > 2:
                    self.canvas.delete(self.Cards[index_num][0][2])
                text_obj = self.canvas.create_text(
                    x + (card_width / 2), y - (20 * self.scale_factor), 
                    text=index_num + 1, font=("Arial", font_size), tags="card")
                self.Cards[index_num][0][2] = text_obj
            else:
                # 新建图片卡片
                self.Cards.append([[img_obj, img_obj], 1, x, y, status[1], image_path])
                text_num = len(self.Cards)
                text_obj = self.canvas.create_text(
                    x + (card_width / 2), y - (20 * self.scale_factor), 
                    text=text_num, font=("Arial", font_size), tags="card")
                self.Cards[-1][0].append(text_obj)
                self.photo_references[len(self.Cards)-1] = photo
            self.update_card_order()
            self.canvas.tag_bind(img_obj, "<B1-Motion>", self.card_on_drag)
            self.canvas.tag_bind(img_obj, "<ButtonPress-3>", self.card_right_click)

    def card_on_drag(self, event):
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        for i, card in enumerate(self.Cards):
            if clicked_item in card[0]:
                card_coords = self.canvas.coords(card[0][0])
                card_width = self.base_card_width * self.scale_factor
                card_height = self.base_card_height * self.scale_factor
                dx = event.x - (card_coords[0] + card_width/2)
                dy = event.y - (card_coords[1] + card_height/2)
                # 移动所有图形对象（包括编号文本）
                for item in card[0]:
                    if isinstance(item, int):
                        self.canvas.move(item, dx, dy)
                # 移动编号文本（如果未被包含在card[0]，则补充移动）
                if len(card[0]) > 2:
                    self.canvas.move(card[0][2], dx, dy)
                self.Cards[i][2] = event.x - (card_width/2)
                self.Cards[i][3] = event.y - (card_height/2)
                break

    def card_right_click(self, event):
        # Get the clicked item
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]

        # Find which card was clicked
        for i, card in enumerate(self.Cards):
            if clicked_item in card[0]:
                
                # Create popup menu
                right_click_menu = tk.Menu(self.root, tearoff=0)
                right_click_menu.add_command(label="Edit", command=lambda: self.edit_card(i))
                right_click_menu.add_command(label="Delete", command=lambda: self.delete_card(i))
                
                # Display popup menu at mouse position
                try:
                    right_click_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    right_click_menu.grab_release()
                break

    def edit_card(self, index):
        # Create a new window for editing
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Edit Card")
        self.popup.geometry("200x100")
        self.popup.attributes('-topmost', True)  # Make window always on top
        self.popup_selected_index = index

        # Create a listbox for editing the card name
        listbox = tk.Listbox(self.popup, selectmode=tk.SINGLE,)
        listbox.pack(fill=tk.BOTH, expand=True)
        # Set the listbox can be scollable
        scrollbar = tk.Scrollbar(listbox, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add the current card name to the listbox
        for i in range(0,len(self.Cards_name)):
            listbox.insert(tk.END, self.Cards_name[i])
        
        # Add a button to confirm the selection
        #confirm_button = tk.Button(self.popup, text="Confirm", command=lambda: self.on_listbox_select(None,index))
        #confirm_button.pack(side=tk.BOTTOM, fill=tk.X)
        
        #Add a sigle-check box beneath the listbox
        check_var = tk.IntVar()
        check_button = tk.Checkbutton(self.popup, text="Reverse", variable=check_var)
        check_button.pack(side=tk.BOTTOM, fill=tk.X)

        # Init selected item
        self.popup_selected_index = None

        # Bind the listbox selection event
        listbox.bind('<<ListboxSelect>>', lambda event:self.on_listbox_select(event,index,check_var))
    
    def on_listbox_select(self, event, index_num, check_var):
        # Get the selected item
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            self.popup_selected_index = index

        # Check if the card exists and its orientation
        card_exists = False
        target_path = "WaiteDeck/" + str(self.popup_selected_index + 1) + ".jpg"
        target_orientation = check_var.get()  # 1 for reverse, 0 for upright
        
        for i in range(len(self.Cards)):
            if self.Cards[i][1] == 1 and self.Cards[i][5] == target_path:
                card_exists = True
                # Check if orientation is different
                if self.Cards[i][4] != target_orientation and index_num == i:
                    # Update card with new orientation
                    self.popup.destroy()
                    self.popup = None
                    self.create_card(self.Cards[i][2], self.Cards[i][3], [1, target_orientation], i)
                else:
                    # Same card with same orientation - show error
                    messagebox.showinfo("Error", "This card already exists in the same orientation.", icon=messagebox.ERROR)
                    self.popup_selected_index = None
                break

        # If card doesn't exist, add it
        if not card_exists:
            self.popup.destroy()
            self.popup = None
            self.create_card(self.Cards[index_num][2], self.Cards[index_num][3], [1, target_orientation], index_num)
    
    def delete_card(self, index):
        # Remove the card from the canvas
        for item in self.Cards[index][0]:
            if isinstance(item, int):  # 确保item是画布对象ID
                self.canvas.delete(item)

        # Remove the card from the Cards list
        del self.Cards[index]
        
        # Update the card order after deletion
        self.update_card_order()

    def update_card_order(self):
        # 计算当前缩放下的字体大小
        font_size = int(24 * self.scale_factor)
        
        # Update the text number above each card to reflect new order
        for i, card in enumerate(self.Cards):
            # 计算当前缩放下的卡片尺寸
            card_width = self.base_card_width * self.scale_factor
            
            # Get the text object (stored as the third element in card[0])
            if len(card[0]) > 2:
                text_num = card[0][2]
                
                # Update the text to the new index + 1
                self.canvas.itemconfig(text_num, text=str(i + 1), font=("Arial", font_size))
                
                # 更新文本位置
                x = card[2] + (card_width / 2)
                y = card[3] - (20 * self.scale_factor)
                self.canvas.coords(text_num, x, y)

if __name__ == "__main__":
    root = tk.Tk()
    app = TarotCardDisplayApp(root)
    root.mainloop()