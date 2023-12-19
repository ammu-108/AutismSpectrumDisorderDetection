from tkinter import *
from tkinter import filedialog
from PIL import ImageTk,Image
from tensorflow import keras
import random
import test2
import threading




        
class create_gui:
    def __init__(self,window):
        
        self.window = window
        self.window.geometry("1400x1200")
        self.window.title("Autism Spectrum Disorder Detection")
        self.window.resizable(True,True)

        self.icon = PhotoImage(file = 'icon.png')
        self.window.iconphoto(True, self.icon)

        self.img = ImageTk.PhotoImage(Image.open("images.jpg").resize((1300,700),Image.ANTIALIAS))
        self.panel = Label(image = self.img)
        self.panel.pack(side = "bottom", fill = "both",expand = "yes")
        
        self.img2 = ImageTk.PhotoImage(Image.open("upload.png").resize((150,150),Image.ANTIALIAS))
        self.btn = Button(self.window,text='Upload Image',image=self.img2,command = self.detection)
        self.btn.place(x=250,y=400)
        
        """self.txt = "Detection Of Autism Spectrum Disorder"
        self.count=0
        self.text=''
        self.color=['#ff9999','#e6ccff']
        self.heading = Label(self.window,text=self.txt,font=("Comic SansMS",30,'bold'),bg="#00001a",fg="black", bd=5,relief=RIDGE)
        self.heading.place(x=100,y=80,width=750)"""
        
        threading.Thread(target=self.slider).start()

        threading.Thread(target=self.heading_color).start()
        
        
       

    def slider(self):
        if self.count>=len(self.txt):
            self.count = -1
            self.text = ''
            self.heading.config(text=self.text)
            
        else:
            self.text = self.text+self.txt[self.count]
            self.heading.config(text=self.text)
            
        self.count+=1
        self.heading.after(200,self.slider)

        
            
    def heading_color(self):
        fg = random.choice(self.color)
        self.heading.config(fg=fg)
        self.heading.after(50,self.heading_color)
            
    def openfilename(self):
        filename = filedialog.askopenfilename(title ='Select an Image')
        return filename
    def open_img(self,heading):
    
        x = self.openfilename()
        
        img = Image.open(x)
        
        img = img.resize((150, 150), Image.ANTIALIAS)
    
        img = ImageTk.PhotoImage(img)
        panel = Label(self.window, image = img)
        panel.image = img
    
        panel.place(x=350,y=370)
        heading.place(x=140,y=550,width=600)
    
        return x
    
    
        
    def detection(self):
        
        heading = Label(self.window,text='Processing...',font=("Comic SansMS",20,'bold'),bg="white",fg="black", bd=5,relief=FLAT)
       
        
        result = threading.Thread(target = test2.detect,args = (self.open_img(heading),heading,)).start()
              
        
  
window = Tk()

create_gui(window)

window.mainloop()
    








