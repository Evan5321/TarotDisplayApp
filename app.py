import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import os


class TarotCardDisplayApp:

    Cards = []
    #Cards列表是一个嵌套列表，其结构为[[[卡片对象]，卡片状态（0为空白，1为已添加），卡片的x位置，卡片的y位置，卡片的正位逆位（-1为未添加，0为正位，1为逆位），卡片的图片路径（-1未添加）],[...],[...]]
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
        
        # 设置Cards_name的数量
        for i in range(0,78):
            self.Cards_name.append("")
            self.Cards_name[i] = str(i+1)

        #print(self.window_width,self.window_height,self.window_width - 50,self.window_height - 30)
        self.add_card_button = self.canvas.create_oval(self.window_width - 85, self.window_height - 175,self.window_width- 30,self.window_height- 115, fill="white", outline="black",width=3)
        self.add_card_text = self.canvas.create_text(self.window_width - 57, self.window_height - 145, text="+", font=("Arial", 38))
        self.canvas.tag_bind(self.add_card_button,"<Button-1>", lambda event: self.create_card(x,y,[0,0],-1))
        self.canvas.tag_bind(self.add_card_text,"<Button-1>", lambda event: self.create_card(x,y,[0,0],-1))
        self.create_card(x,y ,[0,0],-1)

    def create_card(self,x,y,status,index_num):#status为0创建空白卡片，1为创建图片 第二个参数为0是正位，1为逆位
        if status[0] == 0:
            hit_rect = self.canvas.create_rectangle(x, y, x + 150, y + 200, fill="white", stipple="gray50", state="normal")
            # Create the visible outline rectangle
            rect = self.canvas.create_rectangle(x, y, x + 150, y + 200, fill="", outline="black", width=5)
            self.Cards.append([[rect,hit_rect],0,x,y,-1,-1])
            # Create the text_num over the the card
            text_num = len(self.Cards)
            text_num = self.canvas.create_text(x + 75, y - 20, text=text_num, font=("Arial", 24))
            # Store the text_num in the corresponding element of the Cards list
            control_index = len(self.Cards) - 1
            self.Cards[control_index][0].append(text_num)
            # Bind events to the card
            for r in (hit_rect, rect):
                #self.canvas.tag_bind(r,"<ButtonPress-1>", self.card_on_press)
                self.canvas.tag_bind(r,"<B1-Motion>", self.card_on_drag)
                self.canvas.tag_bind(r,"<ButtonPress-3>", self.card_right_click)
        elif status[0] == 1:
            # 计算图片的路径
            image_path = "Waite Deck/" + str(self.popup_selected_index + 1) + ".jpg"
            # Load the image
            image = Image.open(image_path)
            image = image.resize((150, 200))
            
            # 使用字典存储每个图片的引用，防止被垃圾回收
            #if not hasattr(self, 'photo_references'):
            #    self.photo_references = {}
            #使用唯一的键存对象
            #self.popup_references[self.popup_selected_index] = image
            photo = ImageTk.PhotoImage(image)
            # Replace the rectangle with the image
            self.canvas.delete(self.Cards[index_num][0][0])
            self.canvas.delete(self.Cards[index_num][0][1])
            if status[1] == 0:
                self.Cards[index_num][0][0] = self.canvas.create_image(x, y, image=photo, anchor=tk.NW)
                self.Cards[index_num][4] = 0 # 正位
            elif status[1] == 1:
                #将图片翻转90度
                image = image.rotate(180)
                photo = ImageTk.PhotoImage(image)
                self.Cards[index_num][0][0] = self.canvas.create_image(x, y, image=photo, anchor=tk.NW)
                self.Cards[index_num][4] = 1 # 逆位

            self.Cards[index_num][0][1] = photo
            # Update card status
            self.Cards[index_num][1] = 1
            
            self.Cards[index_num][5] = image_path
            # Update card position
            self.Cards[index_num][2] = x
            self.Cards[index_num][3] = y
            # Update card order
            self.update_card_order()
            print(self.Cards[index_num])
            # Bind drag and right-click events to the new card
            num = 0
            for r in self.Cards[index_num][0]:
                if num != 1:
                    self.canvas.tag_bind(r,"<B1-Motion>", self.card_on_drag)
                    self.canvas.tag_bind(r,"<ButtonPress-3>", self.card_right_click)
                    num = num+1
                elif num == 1:
                    break

    def card_on_drag(self, event):
        # Get the clicked item
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        
        # Find which card was clicked by searching through Cards list
        for i, card in enumerate(self.Cards):
            if clicked_item in card[0]:
                # Get current card position
                card_coords = self.canvas.coords(card[0][0])
                
                # Calculate movement based on card type (rectangle or image)
                if self.Cards[i][1] == 0:  # Rectangle
                    # For rectangles, coords returns [x1, y1, x2, y2]
                    current_x = card_coords[0]
                    current_y = card_coords[1]
                    # Calculate the movement delta to center
                    dx = event.x - (current_x + 75)  # 75 is half width of card
                    dy = event.y - (current_y + 100)  # 100 is half height of card
                else:  # Image
                    # For images, coords returns [x, y]
                    current_x = card_coords[0]
                    current_y = card_coords[1]
                    # Calculate the movement delta to center
                    dx = event.x - (current_x + 75)  # 75 is half width of card
                    dy = event.y - (current_y + 100)  # 100 is half height of card
                
                # Move all elements of the card
                for item in card[0]:
                    self.canvas.move(item, dx, dy)
                
                # Update the card's position in Cards list
                self.Cards[i][2] = event.x - 75  # Adjust stored position to top-left corner
                self.Cards[i][3] = event.y - 100
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

       # Detect if the card is already added
        card_exists = False
        for i in range(len(self.Cards)):
            if self.Cards[i][1] == 1 and self.Cards[i][5] == "Waite Deck/" + str(self.popup_selected_index + 1) + ".jpg":
                # Popup a message box
                messagebox.showinfo("Error", "This card has already been added.", icon=messagebox.ERROR)
                self.popup_selected_index = None
                card_exists = True
                break

        # If no duplicate card is found, proceed to add the card
        if not card_exists:
            self.popup.destroy()
            self.popup = None
            if check_var.get() == 1:
                self.create_card(self.Cards[index_num][2], self.Cards[index_num][3], [1, 1], index_num)
            else:
                self.create_card(self.Cards[index_num][2], self.Cards[index_num][3], [1, 0], index_num)
    
    def delete_card(self, index):
        # Remove the card from the canvas
        for item in self.Cards[index][0]:
            self.canvas.delete(item)

        # Remove the card from the Cards list
        del self.Cards[index]
        
        # Update the card order after deletion
        self.update_card_order()

    def update_card_order(self):
        # Update the text number above each card to reflect new order
        for i, card in enumerate(self.Cards):
            # Get the text object (stored as the third element in card[0])
            text_num = card[0][2]
            
            # Update the text to the new index + 1
            self.canvas.itemconfig(text_num, text=str(i + 1))


if __name__ == "__main__":
    root = tk.Tk()
    app = TarotCardDisplayApp(root)
    root.mainloop()