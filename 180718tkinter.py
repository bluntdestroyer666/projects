import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import json
import pandas as pd
import numpy as np
import requests

from matplotlib import pyplot as plt

LARGE_FONT = ('Verdana', 12)
NORM_FONT = ('Verdana', 10)
SMALL_FONT = ('Verdana', 8)

style.use('ggplot')

f = Figure()
a = f.add_subplot(111)

exchange = 'exc1'
DatCounter = 9000
programName = 'btce'

def changeExchange(toWhat, pn):
    global exchange
    global DatCounter
    global programName
    
    exchange = toWhat
    programName = pn
    DatCounter = 9000

def popupmsg(msg):
    popup = tk.Tk()
    
    def leavemini():
        popup.destroy()
    
    popup.wm_title('butts')
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10)
    B1 = ttk.Button(popup, text='Okay', command=leavemini)
    B1.pack()
    popup.mainloop()

def animate(i):
    
    ### This code replaces shit from the original tutorial ###
    
    dataLink = "https://api.bitfinex.com/v1/trades/btcusd?limit_trades=999"
    data = requests.request('Get', dataLink).text
    data = pd.read_json(data)
    data = pd.DataFrame(data)

    # added .copy() to buys & sells (to avoid view with copy error)
    
    buys = data[data['type'] == 'buy'].copy()
    buys['datestamp'] = np.array(buys['timestamp']).astype('datetime64[s]')
    buyDates = (buys['datestamp']).tolist()

    sells = data[data['type'] == 'sell'].copy()
    sells['datestamp'] = np.array(sells['timestamp']).astype('datetime64[s]')
    sellDates = (sells['datestamp']).tolist()
    
    a.clear()
    a.plot_date(buyDates, buys['price'], '#00A3E0', label='buys')
    a.plot_date(sellDates, sells['price'], '#183A54', label='sells')
    
    a.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=2, borderaxespad=0)
    
    title = 'Bitfinex BTCUSD\nLast: ' + str(data['price'][:1].values[0])
    a.set_title(title)
    
    
    
class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):
    
        tk.Tk.__init__(self, *args, **kwargs)
        
        #tk.Tk.iconbitmap(self, default='clienticon.ico')
        tk.Tk.wm_title(self, 'Booty Booty Booty Booty Rockin Everywhere')
        
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Save settings', command = lambda: popupmsg('not supported just yet'))
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=quit)
        menubar.add_cascade(label='File', menu=filemenu)
        
        exchangeChoice = tk.Menu(menubar, tearoff=1)
        exchangeChoice.add_command(label='exc1', 
                                   command=lambda: changeExchange('exc1', 'exc1'))
        exchangeChoice.add_command(label='exc2', 
                                   command=lambda: changeExchange('exc2', 'exc2'))
        exchangeChoice.add_command(label='exc3', 
                                   command=lambda: changeExchange('exc3', 'exc3'))
        exchangeChoice.add_command(label='exc4', 
                                   command=lambda: changeExchange('exc4', 'exc4'))
        
        menubar.add_cascade(label='Exchange', menu=exchangeChoice)
        
        
        
        tk.Tk.config(self, menu=menubar)

        self.frames = {}
        
        for F in (StartPage, PageOne, BTCe_Page):
            
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column = 0, sticky = 'nsew')

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()
        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text='ALPHA Bitcoin App. Do not be a dumbass.', font = LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self, text='Agree', 
                            command=lambda: controller.show_frame(BTCe_Page))
        button1.pack()
        
        button2 = ttk.Button(self, text='Disagree', 
                            command=quit)
        
        button2.pack()
        
class PageOne(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text='Page One', font = LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self, text='Back to Start', 
                            command=lambda: controller.show_frame(StartPage))
        
        button1.pack()
        
class BTCe_Page(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text='Graph', font = LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self, text='Back to Start', 
                            command=lambda: controller.show_frame(StartPage))
        
        button1.pack()
        
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        
        #toolbar = NavigationToolbar2TkAgg(canvas, self)
        #toolbar.update()
        canvas._tkcanvas.pack()
        
		
app = SeaofBTCapp()
app.geometry('1280x720')
ani = animation.FuncAnimation(f, animate, interval=1000)
app.mainloop()

