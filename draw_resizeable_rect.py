import customtkinter as ctk


class ResizableRectangle(ctk.CTkCanvas):
    def __init__(self, master, x, y, width, height, **kwargs):
        super().__init__(master, **kwargs)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = self.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height, fill="lightblue"
        )
        self.side_width = 5
        self.resize_side = None
        self.bind("<Motion>", self.selecting_line_to_resize)
        self.bind("<Button-1>", self.resize_click)
        self.bind("<B1-Motion>", self.resize_drag)
        self.bind("<ButtonRelease-1>", self.resize_release)
        self.highlighted_side = None

    def draw_highlighted_side(self):
        if self.highlighted_side:
            if self.highlighted_side == "right":
                self.create_line(
                    self.x + self.width,
                    self.y,
                    self.x + self.width,
                    self.y + self.height,
                    fill="red",
                    width=3,
                    tags="highlight",
                )
            elif self.highlighted_side == "left":
                self.create_line(
                    self.x,
                    self.y,
                    self.x,
                    self.y + self.height,
                    fill="red",
                    width=3,
                    tags="highlight",
                )
            elif self.highlighted_side == "top":
                self.create_line(
                    self.x,
                    self.y,
                    self.x + self.width,
                    self.y,
                    fill="red",
                    width=3,
                    tags="highlight",
                )
            elif self.highlighted_side == "bottom":
                self.create_line(
                    self.x,
                    self.y + self.height,
                    self.x + self.width,
                    self.y + self.height,
                    fill="red",
                    width=3,
                    tags="highlight",
                )
            self.tag_raise("highlight")

    def clear_highlight(self):
        self.delete("highlight")

    def selecting_line_to_resize(self, event):
        x, y = event.x, event.y
        if abs(x - (self.x + self.width)) <= self.side_width:
            self.config(cursor="right_side")
            self.highlighted_side = "right"
        elif abs(x - self.x) <= self.side_width:
            self.config(cursor="left_side")
            self.highlighted_side = "left"
        elif abs(y - self.y) <= self.side_width:
            self.config(cursor="top_side")
            self.highlighted_side = "top"
        elif abs(y - (self.y + self.height)) <= self.side_width:
            self.config(cursor="bottom_side")
            self.highlighted_side = "bottom"
        else:
            self.config(cursor="")
            self.highlighted_side = None
        self.clear_highlight()
        self.draw_highlighted_side()

    def resize_click(self, event):
        x, y = event.x, event.y
        if abs(x - (self.x + self.width)) <= self.side_width:
            self.resize_side = "right"
        elif abs(x - self.x) <= self.side_width:
            self.resize_side = "left"
        elif abs(y - self.y) <= self.side_width:
            self.resize_side = "top"
        elif abs(y - (self.y + self.height)) <= self.side_width:
            self.resize_side = "bottom"

    def resize_drag(self, event):
        if self.resize_side == "right":
            new_width = event.x - self.x
            if new_width > 10:
                self.width = new_width
                self.coords(
                    self.rect, self.x, self.y, self.x + self.width, self.y + self.height
                )
        elif self.resize_side == "left":
            new_x = event.x
            new_width = (self.x + self.width) - new_x
            if new_width > 10:
                self.x = new_x
                self.width = new_width
                self.coords(
                    self.rect, self.x, self.y, self.x + self.width, self.y + self.height
                )
        elif self.resize_side == "top":
            new_y = event.y
            new_height = (self.y + self.height) - new_y
            if new_height > 10:
                self.y = new_y
                self.height = new_height
                self.coords(
                    self.rect, self.x, self.y, self.x + self.width, self.y + self.height
                )
        elif self.resize_side == "bottom":
            new_height = event.y - self.y
            if new_height > 10:
                self.height = new_height
                self.coords(
                    self.rect, self.x, self.y, self.x + self.width, self.y + self.height
                )
        self.clear_highlight()
        self.draw_highlighted_side()

    def resize_release(self, event):
        self.resize_side = None


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Resizable Rectangle (All Sides)")
        self.canvas = ResizableRectangle(self, 100, 100, 200, 150, bg="white")
        self.canvas.pack(padx=20, pady=20, fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
