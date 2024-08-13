import functools
import os
import sys
import time
from threading import *
from tkinter import *
import pyotp
from alphatrade import AlphaTrade

import OPTION

root = Tk()
root.title("AKRS technologies")
root.state('zoomed')

import NSE

print("LAUNCHED")

head_frame=Frame(root,height=10,background="light sea green")
head_frame.pack(fill="x")


head_text = Label(head_frame,text="TRADING SOFTWARE",background="light sea green",foreground="white",pady=15,font=("comic",15)).pack()
l=Label(root,text="Instrument type ",fg="black",font=("comic",12),pady=10,padx=10)
l.pack(anchor=NW)
l2=Label(root,text="Token number ",fg="black",font=("comic",12),pady=12,padx=10)
l2.pack(anchor=NW)
l=Label(root,text="Amount",fg="black",font=("comic",12),pady=10,padx=10)
l.pack(anchor=NW)
l2=Label(root,text="Round value  ",fg="black",font=("comic",12),pady=13,padx=10)
l2.pack(anchor=NW)



menu= StringVar()
menu.set("NFO")

#Create a dropdown Menu
drop_inst= OptionMenu(root,menu,"NSE", "NFO")
drop_inst.place(x=140,y=65,height=30,width=200)

token=Entry(root)
token.place(x=140,y=110,height=25,width=200)

price=Entry(root)
price.place(x=140,y=155,height=25,width=200)

round=Entry(root)
round.place(x=140,y=200,height=25,width=200)



tok=0
pri=0
rou=0
net=0
def click_start(inst,token,price,round):

    if(inst == "NSE"):
        NSE.token = int(token)
        NSE.base=int(round)
        NSE.money_per_line = int(price)
        thread = Thread(target=NSE.soft_call)
        thread.start()

    elif(inst == "NFO"):
        OPTION.token = int(token)
        OPTION.base = int(round)
        OPTION.money_per_line = int(price)
        thread = Thread(target=OPTION.soft_call)
        thread.start()



b = Button(root,text="START",foreground="white",background="green",command=lambda : click_start(menu.get(),token.get(),price.get(),round.get()))
b.place(height=30,width=160,x=10,y=245)
c = Button(root,text="STOP",foreground="white",background="red",command=lambda :NSE.exit()).place(height=30,width=160,x=180,y=245)


root.mainloop()
