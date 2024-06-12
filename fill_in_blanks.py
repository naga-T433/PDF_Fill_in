import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
from pdf2image import convert_from_path
from pdfminer.layout import LAParams, LTTextContainer, LTTextLineHorizontal
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

class ImageViewer:
    def __init__(self, master, pdf_path, page_number):
        self.master = master
        self.master.title("Image Viewer")

        # Canvasのサイズを設定
        page_width, page_height = get_page_dimensions(pdf_path, page_number)
        self.canvas_width = int(page_width)
        self.canvas_height = int(page_height)

        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(anchor=tk.W)

        # PDFから指定ページの画像を取得し、リサイズ
        specific_page_image = get_specific_page_image(pdf_path, page_number, self.canvas_width, self.canvas_height)
        specific_page_image_pil = specific_page_image.convert('RGB')
        specific_page_image_tk = ImageTk.PhotoImage(specific_page_image_pil)

        self.img = specific_page_image_tk
        self.display_image()

        self.canvas.bind("<Button-1>", self.on_click)

        self.label = None
        if self.label is not None:
            self.label.destroy()


    def display_image(self):
        # Canvasの中心に画像を表示するための座標計算
        x = (self.canvas_width - self.img.width()) / 2
        y = (self.canvas_height - self.img.height()) / 2
        self.canvas.create_image(x, y, image=self.img, anchor=tk.NW)

    def on_click(self, event):
        x, y = event.x, event.y
        page_numbers = {page_number-1}  # 処理したいページ番号のセット
        result = main(page_numbers)
        answer=searchPDF(x, y, result)
        if self.label is not None:
            self.label.destroy()
        self.label = tk.Label(self.master, text=f'{answer}',font=("",30))
        self.label.pack(anchor=tk.S)

    def clear_label(self):
        if self.label is not None:
            self.label.destroy()
            self.label = None

def get_page_dimensions(pdf_path, page_number):
    manager = PDFResourceManager()
    layout_params = LAParams()

    with open(pdf_path, 'rb') as f:
        interpreter = PDFPageInterpreter(manager, PDFPageAggregator(manager, laparams=layout_params))
        page_count = 0
        
        for page in PDFPage.get_pages(f):
            page_count += 1
            if page_count == page_number:
                device = PDFPageAggregator(manager, laparams=layout_params)
                interpreter = PDFPageInterpreter(manager, device)
                interpreter.process_page(page)
                layout = device.get_result()
                
                # ページの座標情報を取得
                x0, y0, x1, y1 = layout.bbox
                
                # ページの幅と高さを計算
                page_width = x1 - x0
                page_height = y1 - y0
                
    return page_width, page_height

def get_specific_page_image(pdf_path, page_number, canvas_width, canvas_height):
    images = convert_from_path(pdf_path)
    specific_page_image = images[page_number - 1]

    # Canvasのサイズに合わせてリサイズ
    specific_page_image_pil = specific_page_image.convert('RGB')
    original_width, original_height = specific_page_image_pil.size

    if original_width > canvas_width or original_height > canvas_height:
        aspect_ratio = original_width / original_height
        if canvas_width / aspect_ratio < canvas_height:
            resized_width = canvas_width
            resized_height = int(canvas_width / aspect_ratio)
        else:
            resized_width = int(canvas_height * aspect_ratio)
            resized_height = canvas_height
        specific_page_image_pil = specific_page_image_pil.resize((resized_width, resized_height), Image.ANTIALIAS)

    return specific_page_image_pil

def main(page_numbers):
    manager = PDFResourceManager()
    coordinates = []

    with open(PDF_path, 'rb') as input_file:  # PDFファイルのパスを適宜変更
        with PDFPageAggregator(manager, laparams=LAParams()) as device:
            interpreter = PDFPageInterpreter(manager, device)
            for page in PDFPage.get_pages(input_file, pagenos=page_numbers):
                interpreter.process_page(page)
                layout = device.get_result()
                page_height = layout.bbox[3]

                for element in layout:
                    if isinstance(element, LTTextContainer):
                        for text_line in element:
                            if isinstance(text_line, LTTextLineHorizontal):
                                y0 = page_height - text_line.y1
                                y1 = page_height - text_line.y0
                                coordinates.append([text_line.get_text().strip(), text_line.x0, text_line.x1, y0, y1])
    return coordinates

def searchPDF(in_x, in_y, coordinates):
    result = "見つかりませんでした"
    for i in range(len(coordinates)):
        if coordinates[i][1] <= in_x <= coordinates[i][2]:
            if coordinates[i][3] <= in_y <= coordinates[i][4]:
                result = coordinates[i][0]
    return result

def nextButton():
    global page_number, image_viewer
    page_number += 1
    image_viewer.clear_label() 
    image_viewer.canvas.destroy()
    image_viewer = ImageViewer(root, PDF_path, page_number)

def backButton():
    global page_number, image_viewer
    page_number -= 1
    image_viewer.clear_label() 
    image_viewer.canvas.destroy()
    image_viewer = ImageViewer(root, PDF_path, page_number)


print("ファイル名を入力してください(拡張子はない状態にしてください)")
input_PDF=input()
PDF_path = Path(f'{input_PDF}.pdf')
page_width, page_height=get_page_dimensions(PDF_path, 1)
window_w=int(page_width)+100
window_h=int(page_height)+100

root = tk.Tk()
root.geometry(f"{window_w}x{window_h}")
page_number = 1

image_viewer = ImageViewer(root, PDF_path, page_number)
button = tk.Button(root, text=">",command=nextButton).place(x=window_w-50,y=30)

button = tk.Button(root, text="<",command=backButton).place(x=window_w-90,y=30)

label = tk.Label(root, text='Page変更').place(x=window_w-80,y=0)



root.mainloop()













