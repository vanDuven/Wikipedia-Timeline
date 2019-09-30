import io
import json
import mmap
import os
import re
import tkinter as tk
import webbrowser
from html import unescape
from random import randrange
from statistics import median, stdev
from tkinter import colorchooser, filedialog, scrolledtext, ttk
from urllib.parse import quote, unquote
from urllib.request import urlopen

from PIL import Image, ImageTk

import finddate
from wikitojson import alone, balance


#class point = date point on timeline
#Variables - (x = dictionary data: (y = year of date, d = day of date m = month of date,
#set = period condition to next date (not used in class point),
#title = title of date(s),
#pos = (list of positions within wiki xml file, position 0 = begin, postion 1 = end,
#if the date is acquired not through the xml file position 0 will be 0.)
#key = full or adjusted string of the key with the date string as value from the infobox dictionary
#every = list with the unadjusted strings of the key(position 0) and date(position 1))
#tot = total days
#spec = (list of the period condition to next date(used in class point),
#position 0 = from previous to current date, postion 1 = from current to next date)
#xcor = (position 0 = difference in days compared to previous date(year -1 to year 1 is ignored), 
#position1 = coordination of the point on the canvas, position2 = stance condition used in the creating the timeline)))
class point:
    ycor = {}     
    connt = {}    
    stindex = {}
    del_list = {}
    mot_point = {}
    chdrag = {'check_yu':0,'check_yd':0,'change_y':False}
    setting = {'draw':1,'timeline':1,'del':0,'destroy':0,'parallel':2}    
    colour_line = {'None': {'col': 'purple', 'dash': 3}, 'to': {'col': 'red', 'dash': None}, 
    'or': {'col':'blue','dash':6},'and':{'col':'turquoise3','dash':6}, 'brace': {'col': 'DarkOrange2', 'dash': None}}     

    def __init__(self, x,ro):        
        self.w = ro
        self.every= x

        keys = (' '.join(x['key'].replace('_',' ').replace('dates','').replace('date','').split())).strip() 

        if keys != '':
            keys = ' |'+keys

        self.title = x['title']
        self.posar = x['pos']                          
        self.spec = x['spec'] 
        self.pic = None           
        xcor1 = x['xcor'][1]        
        self.x = xcor1 * mainwin.length_line['skip']

        if self.posar[1]-self.posar[0] > mainwin.background_set['length_colour']['length']:
            forg = mainwin.background_set['length_colour']['col']          
        else:
            forg = mainwin.background_set['normal_colour']['col']

        self.bit = tk.Label(self.w, text =self.title+keys, fg = 'black',bd = 1,
        relief='solid' ,bg = forg, cursor = "hand2")        
        self.getu = self.bit.winfo_reqwidth() 

        if 'rcor' in x:
            self.y = x['rcor']
            if 'u0' in x:
                self.u0 = self.w.create_line(x['u0']['l1x'],x['u0']['l1y'],x['u0']['l2x'],x['u0']['l2y'],
                dash=x['u0']['dash'],fill=x['u0']['fill'],width=x['u0']['width'])
                point.mot_point[self.u0]=[self,None]

            if 'u1' in x:
                self.u1 = self.w.create_line(x['u1']['l1x'],x['u1']['l1y'],x['u1']['l2x'],x['u1']['l2y'],
                dash=x['u1']['dash'],fill=x['u1']['fill'],width=x['u1']['width']) 

            if 'u2' in x:
                self.u2 = self.w.create_line(x['u2']['l1x'],x['u2']['l1y'],x['u2']['l2x'],x['u2']['l2y'],
                dash=x['u2']['dash'],fill=x['u2']['fill'],width=x['u2']['width'])
                point.mot_point[self.u2]=[self,None]

        else: 
            self.y = 440              
            self.y_time(stand=0) 

        if 'del' not in x:           
            if self.title not in point.connt:                
                point.connt[self.title] = {}                
                point.connt[self.title]['cor'] = [self]         
            else:
                point.connt[self.title]['cor'].append(self)

            self.win = self.w.create_window((self.x,self.y), window=self.bit)
        elif x['del'] == True:
            if self.title in point.del_list:
                point.del_list[self.title].append(self)
            else:
                point.del_list[self.title] = [self]

        self.bit.bind("<Double-Button-1>",lambda nope:self.article())
        self.bit.bind("<Button-2>",lambda nope:self.open_wikipic()) 
        self.bit.bind("<Button-3>",lambda nope: self.line_but(self.title,point.connt,right=1))  
        self.bit.bind("<Button-1>",lambda yc:self.click(yc))      
        self.bit.bind("<B1-Motion>",lambda yc:self.drag(yc))

    def key_change(self):

        def key_config(key):
            keys = (' '.join(key.replace('_',' ').replace('dates','').replace('date','').split())).strip() 
            if keys != '':
                keys = ' |'+keys
                
            return keys

        def change():
            lab1.config(fg = "green")
            fset.after(800,lambda:lab1.config(fg = "black"))
            
            if 'old_key' not in self.every:
                self.every['old_key'] = self.every['key']

            self.every['key'] = l1.get()
            lab1_key.config(text=f"{self.every['key']}")
            new_key = key_config(self.every['key'])
            lab2_key.config(text=f"{new_key}")
            self.bit.config(text =self.title+new_key)
            point.stindex={}
            
            try:
                half = self.getu*(1/2)
                mx = int(self.x - half)
                px = int(self.x + half)
                point.ycor[str(self.y)].remove([mx,px])
                self.getu = self.bit.winfo_reqwidth()

                old = self.y                         
                self.y_time(stand=0)          
                self.w.move(self.win, 0, (self.y-old)* mainwin.zoom['zoomn'])

                line_draw = False
                for c in range(3):
                    try:                        
                        if c == 0:
                            if self.stru0 != None:
                                line_draw = True                                
                                break
                        elif c == 1:
                            if self.stru1 != None:
                                line_draw = True                                
                                break
                        elif c == 2:
                            if self.stru2 != None:
                                line_draw = True                                
                                break
                    except:
                        pass
                
                if line_draw:
                    self.line_but(self.title,point.connt) 

                self.w.config(scrollregion=self.w.bbox("all")) 
            except:
                self.getu = self.bit.winfo_reqwidth()            

        def default():
            if 'old_key' in self.every:
                l1.delete(0,'end')
                l1.insert(0,self.every['old_key'])

        fset = tk.Toplevel(self.w)
        fset.columnconfigure(1, weight=1)
        main_lab = tk.Label(fset,text="Change key\tpress enter to confirm")
        main_lab.grid(row=0,column=0,columnspan=2,sticky="w")
        lab1 = tk.Label(fset,text="Current key: ")
        lab1.grid(row=1,column=0,sticky="w")
        lab1_key = tk.Label(fset,text=f"{self.every['key']}",fg = 'blue')
        lab1_key.grid(row=1,column=1,sticky="w")
        lab2 = tk.Label(fset,text="Displays key as: ")
        lab2.grid(row=2,column=0,sticky="w")
        lab2_key = tk.Label(fset,text=f"{key_config(self.every['key'])}",fg = 'blue')
        lab2_key.grid(row=2,column=1,sticky="w")
        
        tk.ttk.Separator(fset, orient='horizontal').grid(row=3,column=0,columnspan=2,sticky='we')

        l11 = tk.Label(fset,text="New key:")
        l11.grid(row=4,column=0,sticky="w") 
        l1 =tk.Entry(fset,width=35)
        l1.insert(0,self.every['key'])
        l1.bind("<Return>", lambda nope:change())    
        l1.grid(row=4,column=1,sticky="we")
        b1 = tk.Button(fset,text = 'Default',bg='white',relief='solid',command=default)
        b1.grid(row=5,column=0,sticky="w")
    
    def click(self,cor):
        point.chdrag['check_yu'] = 0
        point.chdrag['check_yd'] = 0
    
    def drag(self,cor,ym=40):
        ym1 = ym
        ym = ym * mainwin.zoom['zoomn']  

        if point.chdrag['change_y'] == True:            
            if abs(cor.y) > ym/2:
                if abs(cor.y) > ym-1:
                    point.chdrag['change_y'] = False
                    return
            else:
                point.chdrag['change_y'] = False

        if cor.y > ym+point.chdrag['check_yu']:
            check_y = self.y            
            self.move_ybutton(-ym1)
            point.chdrag['check_yu'] = 0
            point.chdrag['check_yd'] = 0            
            if check_y - self.y < -ym:
                point.chdrag['check_yd'] = check_y - self.y + ym
            else:
                point.chdrag['check_yd'] = 0

            point.chdrag['change_y'] = True
            return

        if cor.y < -ym+point.chdrag['check_yd']:
            check_y = self.y            
            self.move_ybutton(ym1)            
            point.chdrag['check_yu'] = 0            
            point.chdrag['check_yd'] = 0  

            if check_y - self.y > ym:
                point.chdrag['check_yu'] = check_y - self.y -ym
            else:
                point.chdrag['check_yu'] = 0

            point.chdrag['change_y'] = True
            return       

    def line_but(self,link, link_list,col='purple',dash=3,width=1, right=0): 

        def colour_pick(spec):
            spec  = str(spec)
            for cl in point.colour_line:
                if cl in spec:
                    col_line = point.colour_line[cl]['col']
                    dash_line = point.colour_line[cl]['dash']
                    break            
            return [col_line,dash_line]

        def delete_lines(i):
            for c in range(3):                
                try:
                    if c == 0:
                        self.w.delete(li[i].u0)
                        li[i].stru0=None
                        del point.mot_point[li[i].u0]
                    elif c == 1:
                        self.w.delete(li[i].u1)
                        li[i].stru1=None
                        del point.mot_point[li[i].u1]
                    elif c == 2:
                        self.w.delete(li[i].u2)
                        li[i].stru2=None
                        del point.mot_point[li[i].u2]                                  
                except:
                    pass       
        li = sorted(link_list[link]['cor'], key = lambda k: k.x) 

        if point.setting['draw'] == 0 and point.setting['timeline'] ==0 and right==0:
            for i in range(len(li)): 
                delete_lines(i)
            return

        if point.setting['destroy'] == 1 and right==1:
            for i in range(len(link_list[link]['cor'])):
                delete_lines(i)
            if link not in point.del_list:
                point.del_list[link] = [self]
            else:            
                point.del_list[link].append(self)

            link_list[link]['cor'].remove(self)                        
            self.w.delete(self.win)
            li = sorted(link_list[link]['cor'], key = lambda k: k.x)

        if point.setting['destroy'] == 2 and right==1:            
            if link in point.del_list:
                for z in point.del_list[link]:                    
                    link_list[link]['cor'].append(z)                    
                    z.win = self.w.create_window(z.x* mainwin.zoom['zoomn'], z.y* mainwin.zoom['zoomn'], window=z.bit)
                point.del_list[link] = []
                link_list[link]['cor'] = sorted(link_list[link]['cor'], key = lambda k: k.x)
                li = link_list[link]['cor'] 

        if len(li) > 1:
            l = 1
        else:
            l = 0   

        for i in range(len(li)): 
            delete_lines(i)
            if point.setting['del'] == 1:
                continue

            lix1 = li[i].x* mainwin.zoom['zoomn']
            liy1 = li[i].y* mainwin.zoom['zoomn']

            if point.setting['timeline'] == 1:
                if liy1 < 520* mainwin.zoom['zoomn']:
                    point_line = 480* mainwin.zoom['zoomn']
                else:
                    point_line = 580* mainwin.zoom['zoomn']

                li[i].u2 = self.w.create_line(lix1,liy1,lix1, point_line, dash=4, fill = 'black',width=width)
                li[i].stru2 = {'l1x':lix1,'l1y':liy1,'l2x':lix1,'l2y':point_line,'dash':4,'fill':'black','width':width}
                point.mot_point[li[i].u2]=[li[i],None]  

            if l == 1 and i == len(li)-1:
                break

            lix2 = li[i+l].x* mainwin.zoom['zoomn']
            liy2 = li[i+l].y* mainwin.zoom['zoomn']

            if point.setting['draw'] == 0:
                continue   

            if li[i].spec[1] == li[i+l].spec[0]:
                line_atr = colour_pick(li[i].spec[1])
                col_line = line_atr[0]
                dash_line = line_atr[1]                
            elif li[i].spec[0] == li[i+l].spec[1] and li[i].spec[0] != None:
                line_atr = colour_pick(li[i].spec[0])
                col_line = line_atr[0]
                dash_line = line_atr[1]
            else:
                col_line = point.colour_line['None']['col']
                dash_line = point.colour_line['None']['dash']
                last_i = None
                col_i = 1

                if li[i+l].spec[0] != None:
                    for i1 in range(i):                        
                        if li[i+l].spec[0] == li[i1].spec[1]:
                            last_i = i1
                elif li[i+l].spec[1] != None:               
                    for i1 in range(i):            
                        if li[i+l].spec[1] == li[i1].spec[0]:
                            last_i = i1
                            col_i = 0

                if last_i != None:                    
                    lix3 = li[last_i].x * mainwin.zoom['zoomn']
                    liy3 = li[last_i].y * mainwin.zoom['zoomn']
                    line_atr = colour_pick(li[last_i].spec[col_i])
                    li[i].u1 = self.w.create_line(lix3, liy3,lix2, liy2,
                    dash=line_atr[1], fill = line_atr[0],width=width)

                    li[i].stru1 = {'l1x':lix3,'l1y':liy3,'l2x':lix2,'l2y':liy2,
                    'dash':line_atr[1],'fill':line_atr[0],'width':width}
                    point.mot_point[li[i].u1]=[li[i+l],[li[i+l].every['tot'],li[last_i].every['tot']]]

            li[i].u0 = self.w.create_line(lix1, liy1,lix2, liy2, dash=dash_line, fill =col_line,width=width)
            li[i].stru0 = {'l1x':lix1,'l1y':liy1,'l2x':lix2,'l2y':liy2,'dash':dash_line,'fill':col_line,'width':width}
            point.mot_point[li[i].u0]=[li[i],[li[i+l].every['tot'],li[i].every['tot']]]
                       
    def y_time(self, yplus=40,stand=1):
        if yplus == 0:
            return 
               
        half = self.getu*(1/2)
        y2 = 440

        try:
            y2 = self.y
        except:
            pass

        y1 = y2
        change = True
        inchange = False 
        mx = int(self.x - half)
        px = int(self.x + half)
        yx = [mx,px]

        if str(y2) in point.ycor:                    
            while change == True:
                change = False

                if str(y2) not in point.stindex:
                    point.stindex[str(y2)] = 0

                if str(y2) not in point.ycor:
                    point.ycor[str(y2)] = []                
                    continue

                for yx in point.ycor[str(y2)][point.stindex[str(y2)]:]: 
                    if mx >= yx[0] and mx <= yx[1]:
                        y2 -= yplus
                        change = True
                        break
                    elif px >= yx[0] and px <= yx[1]:
                        y2 -= yplus
                        change = True
                        break
                    elif mx <= yx[0] and px >= yx[1]:
                        y2 -= yplus
                        change = True
                        break
                    elif mx <= yx[0] and px <= yx[0]:
                        change = False
                        break  

                if  440 < y2 < 600:
                    if yplus < 0:
                        y2 = 600
                    else:
                        y2 = 440

                    change = True
                if change == True:
                    inchange = True

            if inchange == False:
                if point.ycor[str(y2)] != []:               
                    point.stindex[str(y2)] = max(0,point.ycor[str(y2)].index(yx))

            if stand == 1:               
                point.ycor[str(y1)].remove([mx,px]) 

            point.ycor[str(y2)].append([mx,px])
            if stand == 1:
                point.ycor[str(y2)] = sorted(point.ycor[str(y2)]) 

        else:
            point.ycor[str(y2)] = [[mx,px]]   

        self.y = y2        
        
    def move_ybutton(self,ym):
        point.stindex={}

        if point.setting['parallel'] >= 1: 
            stand = point.setting['parallel']           
            point.setting['parallel'] = 0  

            if stand == 2:
                if self.spec[1] == None and self.spec[0] != None:
                    key = self.spec[0]
                else:
                    key = self.spec[1]

                sort = [self]
                for s in point.connt[self.title]['cor']:
                    if (s.spec[0] == key and key != None) or (s.spec[1] == key and key != None):
                        if self != s:
                            sort.append(s)

            elif stand == 1:
                sort = point.connt[self.title]['cor']

            if ym > 0:
                sort = sorted(sort, key = lambda k: k.y)                
            else:
                sort = sorted(sort, key = lambda k: k.y,reverse=True)

            for x in sort:
                x.move_ybutton(ym)            
            point.setting['parallel'] = stand 
            return

        old = self.y                         
        self.y_time(ym,stand=1)          
        self.w.move(self.win, 0, (self.y-old)* mainwin.zoom['zoomn'])       
        self.line_but(self.title,point.connt) 
        self.w.config(scrollregion=self.w.bbox("all"))

    def open_wikipic(self):              
        if self.pic != None and self.pic.lab1.winfo_exists() ==1:
            return

        typepic = ['jpg','jpeg','png','gif']
        url1 = None
        title = quote(self.title.replace(' ','_'))
        url = "https://en.wikipedia.org/wiki/" + title        
        im1 = urlopen(url).read()
        yy1 = im1.find(b'<meta property="og:image" content="https://upload.wikimedia.org/wikipedia/')   

        if yy1 != -1:
            yy3 = im1.find(b'https:',yy1)
            yy2 = im1.find(b'"/>',yy1)

            if yy2 != -1:
                im2 = im1[yy3:yy2].decode('utf-8')                
                yy4 = im2.find('.svg/')
                yy5 = re.search(r'\/\d+px',im2) 

                if yy4 == -1 and yy5 != None:            
                    url1 = im2[:yy5.start()].replace('thumb/','')
                else:
                    url1 = im2

        else:    
            url2 = "https://en.wikipedia.org/wiki/Special:Export/" + title
            im2 = urlopen(url2).read()

            try:
                im2 = self.redirect_title(im2)[0]
            except:
                pass

            ny1 = im2.find(b'File:')

            if ny1 == -1:                
                ny1 = im2.find(b'Image:')
                if ny1 == -1:
                    ny1 = im2.find(b'image =')
                    if ny1 == -1:
                        ny1 = im2.find(b'Image =')  

            if ny1 != -1: 
                im2 = im2[ny1:].decode('utf-8')
                fis1 = re.finditer(r'([Ff]ile|[Ii]mage)(?:\:|\s\=)(\s|.?)\b(\w+.*?\.(\w\w(\w\w|\w)))',im2)
                im1 = im1.decode('utf-8')                
                for x in fis1:                    
                    if x.groups()[3].lower() in typepic: 
                        name = quote(x.groups()[2].replace(' ','_'))                         
                        fis2 = re.search(r'//(\bupload.wikimedia.org/wikipedia/.*?%s\b)'%name,im1)
                        if fis2 == None:
                            continue
                        url1 = "https://"+(fis2.groups()[0].replace('thumb/',''))
                        break
                del im2

        del im1

        if url1 == None:
            nofindlab = tk.Label(bg =mainwin.background_set['background_colour'], text = "no image found")
            self.w.create_window((self.x*mainwin.zoom['zoomn'],(self.y*mainwin.zoom['zoomn'])-25), window=nofindlab)
            nofindlab.lift()
            self.w.after(1000,lambda:nofindlab.destroy())
        
        elif url1 != None:             
            image_bytes = urlopen(url1).read()
            data_stream = io.BytesIO(image_bytes)               
            orimage = Image.open(data_stream)            
            w, h = orimage.size
            scw = 1
            sch = 1            
            if w > 500:
                scw = 500/w
            if h > 300:
                sch = 300/h 
            sc = min(scw,sch)
            w = int(w*sc)
            h = int(h*sc)
            orimage = orimage.resize((w, h))      
            self.pic = wikipic(self.w,orimage,self.x,self.y,self,url1)
            self.w.config(scrollregion=self.w.bbox("all"))

    def article(self):

        def open_url():
            base = 'https://en.wikipedia.org/wiki/' + quote(self.title.replace(' ','_'))
            webbrowser.open(base) 

        def ask_xml():            
            patt = filedialog.askopenfilename(title = "Select file",filetypes = (("xml files","*.xml"),))
            if patt:
                mainwin.pat = patt
                but1.grid_forget()
                open_xml()

        def open_xml(): 
            titlep = self.title          
            pos1 = self.posar[0]
            pos2 = self.posar[1]            
            read = None
            file_check = os.path.isfile(mainwin.pat) 

            if (pos1 == 0 and pos2 != 0) or file_check == False:                    
                urlcom = "https://en.wikipedia.org/wiki/Special:Export/"+ quote(self.title.replace(' ','_'))
                try:
                    xmlp = urlopen(urlcom)
                    read = xmlp.read()
                    read = self.redirect_title(read,titlep)
                    titlep = read[1].strip()
                    read = read[0]
                except:
                    pos2 = 0

            if read == None and file_check == True:
                with open(mainwin.pat, 'rb',0) as fi:                
                    fi.seek(pos1)                    
                    read = fi.read(pos2-pos1) 

            if read != None:
                fis1 = read.rfind(b'</text>')
                fis2 = read.find(b'<text')
                fis3 = read.find(b'>',fis2+5,fis1)
                if fis1 != -1 and fis2 != -1 and fis3 != -1:
                    read = read[fis2:fis1+7].decode('utf-8','replace')
                    tt.delete(poslast,'end')

                    but2 = tk.Button(newwin,text='Search for dates in text',bg='white',
                    relief='solid',command=lambda:mainwin.ask_textan('nope',read,titlep,newwin,self.posar))
                    but2.grid(row=0,column=2,sticky="w") 

                    try:
                        tt.insert('end', read)
                    except tk.TclError:
                        read = self.tk_unicode(read)
                        tt.insert('end', read)

        newwin = tk.Toplevel(self.w) 
        newwin.columnconfigure(0, weight=1)
        newwin.columnconfigure(3, weight=1)
        newwin.rowconfigure(1, weight=1)                
        but = tk.Button(newwin,text='Open en.wikipedia URL',bg='white',relief='solid',command=open_url)
        but.grid(row=0,column=1,sticky="e")

        tt = scrolledtext.ScrolledText(newwin,width=130, height=50,font=("sans-serif", 11),relief='flat',wrap='word')
        tt.grid(row=1,column=0,columnspan=4,padx=10,sticky="nswe") 
        tt.tag_config('col1', foreground="DeepSkyBlue2")
        tt.tag_config('col2', foreground="sienna3")
        tt.insert('end', '\u2022 Data: ','col1')
        tt.insert('end', self.every)
        tt.insert('end', '\n\u2022 Date text: ','col1')
        tt.insert('end', f"{self.every['every'][0].strip()}", 'col2')
        tt.insert('end', f" = ", 'col1')
        tt.insert('end', f"{self.every['every'][1]}", 'col2')
        tt.insert('end', '\n\n')    
        poslast = tt.index('end')
        file_check = os.path.isfile(mainwin.pat)

        if self.getu != None:  
            but3 = tk.Button(newwin,text='Edit key',bg='white',relief='solid',command=lambda:self.key_change())
            but3.grid(row=0,column=3,sticky="w")

        if file_check == False:
            but1 = tk.Button(newwin,text='Path wiki.xml',bg='white',relief='solid',command=ask_xml)
            but1.grid(row=0,column=0,sticky="e")

        open_xml()
                 
    def redirect_title(self,read,ortitle=None):
        redtitle = ortitle
        redf = b'<redirect title=\"'
        rev = read.find(b'<revision')

        if rev != -1:
            red = read.find(redf,0,rev)        
            if red != -1:                               
                red2 = read.find(b'/>',red)
                if red2 != -1:                                   
                    redtitle = read[red+len(redf):red2-len(b'"/')].decode('utf-8')                                 
                    urlcom = "https://en.wikipedia.org/wiki/Special:Export/"+ quote(redtitle.replace(' ','_'))                
                    try:
                        xmlp = urlopen(urlcom)                                
                        read = xmlp.read()
                    except:
                        pass
                        
        return (read,redtitle)

    def tk_unicode(self,con):
        for x in con:
            if ord(x) > 65535:
                con = con.replace(x,'\uFFFD')
        return con

#Label displayed on a line btween dates or timeline. 
class linepoint:
    cor = []

    def __init__(self,ro,xc,yc,x,years):
        self.every = x
        self.w = ro
        self.x = xc
        self.y = yc 
        keys = (' '.join(x['key'].replace('_',' ').replace('dates','').replace('date','').split())).strip()     

        if keys != '':                           
            keys = ' |'+keys

        if years:
            if years[0] > 0 > years[1]:
                years = years[0] - years[1] - 365
            else:
                years = years[0] - years[1]

            if years != 0:
                if (years//365) == 0:
                    if (years//(365/12)) == 0:
                        stryear = 'days'
                        if years == 1:
                            stryear = 'day'
                        keys = keys + f' |{round(years,2)} ' + stryear 
                    else:
                        stryear = 'months'
                        if years == 1:
                            stryear = 'month'
                        keys = keys + f' |{round(years/(365/12),2)} ' + stryear

                else:
                    stryear = 'years'
                    if years == 1:
                        stryear = 'year'
                    keys = keys + f' |{round(years/365,2)} ' + stryear    

        self.title = x['title']
        self.posar = x['pos']                          
        self.spec = x['spec'] 
        self.pic = None
        self.getu = None

        if self.posar[1]-self.posar[0] > mainwin.background_set['length_colour']['length']:
            forg = 'style2.TButton'          
        else:
            forg = 'style1.TButton'

        self.bit = ttk.Label(self.w, text =self.title+keys,cursor = "hand2",style=forg)
        self.bit.bind("<Double-Button-1>",lambda nope:self.article())
        self.bit.bind("<Button-2>",lambda nope:self.open_wikipic())
        self.bit.bind("<Leave>",lambda nope:self.leave())
        self.win = self.w.create_window((self.x,self.y), window=self.bit)
        self.x = xc / mainwin.zoom['zoomn']
        self.y = yc / mainwin.zoom['zoomn']

    open_wikipic = point.open_wikipic
    article = point.article
    tk_unicode = point.tk_unicode
    redirect_title = point.redirect_title
    
    def leave(self):                                  
        self.w.delete(self.win)
        self.bit.destroy()
        linepoint.cor = []
        mainwin.look = None

class wikipic:
    check_yd = 0
    update_can = True
    every = []

    def __init__(self,ro,orimage,x,y,par,url):
        self.orimage = orimage
        self.url = url                  
        w, h = orimage.size 
        resize = (int(w*min(1,(mainwin.zoom['zoomp']))), int(h*min(1,(mainwin.zoom['zoomp']))))         
        wikiimage = ImageTk.PhotoImage(self.orimage.resize(resize))        
        self.lab1 = tk.Label(ro, image=wikiimage,text =par.title,compound="top",
        borderwidth=0,highlightthickness = 0,bg=mainwin.background_set['background_colour'])
        self.lab1.image = wikiimage
        self.par = par        
        self.ro =ro
        self.x = x
        self.y = y - 300         
        self.win = self.ro.create_window(self.x* mainwin.zoom['zoomn'],
        (self.y* mainwin.zoom['zoomn']), window=self.lab1) 
        self.lab1.lower()
        self.lab1.bind("<Button-1>",lambda yc:self.click(yc)) 
        self.lab1.bind("<Double-Button-1>",lambda nope:self.open_url())     
        self.lab1.bind("<B1-Motion>",lambda yc:self.drag(yc))
        self.lab1.bind("<Button-3>",lambda nope: self.line_but(right=1))
        wikipic.every.append(self)
        self.line_but()

    def open_url(self):        
        webbrowser.open(self.url)  

    def click(self,cor):
        wikipic.check_yd = cor.y

    def drag(self,cor):

        def upd():
            wikipic.update_can = True  

        if wikipic.update_can == True:
            self.ro.move(self.win, 0, cor.y-wikipic.check_yd)  
            self.line_but()
            wikipic.update_can = False
            self.ro.config(scrollregion=self.ro.bbox("all"))            
            self.ro.after(5,lambda:upd())             

    def line_but(self,right=0): 

        def delete_lines():
            try:
                self.ro.delete(self.u2)
                del point.mot_point[self.u2]
            except:
                pass 

        if point.setting['destroy'] == 1 and right==1:
            delete_lines()                                 
            self.ro.delete(self.win)
            wikipic.every.remove(self)
            self.lab1.image = None
            self.lab1.destroy()
            self.par.pic = None  
            return   

        delete_lines()
        if point.setting['del'] == 1:
            return   

        if point.setting['timeline'] == 1:
            lix1 = self.x* mainwin.zoom['zoomn']
            liy1 = self.ro.coords(self.win)[1]            
            if liy1 < 520* mainwin.zoom['zoomn']:
                point_line = 480* mainwin.zoom['zoomn']
            else:
                point_line = 580* mainwin.zoom['zoomn']

            self.u2 = self.ro.create_line(lix1,liy1,lix1, point_line, dash=4, fill = 'black')
            point.mot_point[self.u2]=[self.par,None]
                 
class wbegin(tk.Frame):

    def __init__(self,ro):
        tk.Frame.__init__(self,ro,bd=1,highlightthickness=1,highlightbackground="sienna3",highlightcolor="sienna3")                
        lab1 = tk.Label(self,relief='solid',bd=1,width=28, height=5) 
        lab1.grid(row=0,column=0,rowspan=2,columnspan=2,sticky="nswe")
        lab2 = tk.Label(self,relief='solid',bd=1,height=3)
        lab2.grid(row=2,column=0,columnspan=2,sticky="we")
        lab3 = tk.Label(self,relief='solid',bd=1,height=3) 
        lab3.grid(row=3,column=0,columnspan=2,sticky="we") 
        lab3 = tk.Label(self,relief='solid',bd=1,height=3)
        lab3.grid(row=4,column=0,columnspan=2,sticky="we")  

        but1 = ttk.Button(self, text = 'Run', style='style1.TButton',cursor = "hand2",
        command=ro.mainbut)       
        but1.grid(row=4,column=0,columnspan=2)
        but2 = ttk.Button(self, text = 'add date', style='style1.TButton',cursor = "hand2",
        command=lambda:ro.insertdate(self))
        but2.grid(row=2,column=0)
        but6 = ttk.Button(self, text = 'add wiki url', style='style1.TButton', cursor = "hand2",
        command=lambda:ro.save_wiki(self))  
        but6.grid(row=2,column=1)
        but3 = ttk.Button(self, text = 'add wiki json', style='style1.TButton', cursor = "hand2",
        command=lambda:ro.open_json(self)) 
        but3.grid(row=0,column=0,columnspan=2,pady=5, padx=5)
        but4 = ttk.Button(self, text = 'add json keyword', style='style2.TButton',cursor = "hand2",
        command=lambda:ro.json_keyword())     
        but4.grid(row=1,column=0, pady=5, padx=5)
        but4 = ttk.Button(self, text = 'infobox filter', style='style2.TButton',cursor = "hand2",
        command=lambda:ro.box_keyword())    
        but4.grid(row=1,column=1)
        but5 = ttk.Button(self, text = 'open saved file', style='style2.TButton',cursor = "hand2",
        command=lambda:ro.open_timeline())    
        but5.grid(row=3,column=0)
        but7 = ttk.Button(self, text = 'path enwiki.xml', style='style2.TButton',cursor = "hand2",
        command=lambda:ro.path_wikixml()) 
        but7.grid(row=3,column=1,pady=5, padx=5)

        self.box1 = listbox_frame(self,stand=1,dlist=mainwin.data_insert)
        self.box1.grid(row=5,column=0,columnspan=2,sticky="we")     
        
class settingmain(tk.Frame):

    def __init__(self,setting):
        tk.Frame.__init__(self,setting)
        self.setting = setting  
        self.set1 = setting1(self)
        self.set1.grid(row=0,column=0,sticky="we")
        self.set2 = setting2(self)
        self.set2.grid(row=1,column=0,sticky="we")
        self.set1c = setting1_close(self)
        self.set2c = setting2_close(self)

    def collapse_switch1(self,sw):
        if sw == 1:
            self.set1c.grid_forget()
            self.set1.grid(row=0,column=0,sticky="we")        
        elif sw == 0:        
            self.set1.grid_forget()
            self.set1c.grid(row=0,column=0,sticky="we")

    def collapse_switch2(self,sw):
        if sw == 1:
            self.set2c.grid_forget()
            self.set2.grid(row=1,column=0,sticky="we")        
        elif sw == 0:        
            self.set2.grid_forget()
            self.set2c.grid(row=1,column=0,sticky="we")

class setting1_close(tk.Frame):

    def __init__(self,setting):
        tk.Frame.__init__(self,setting,highlightbackground="blue",highlightcolor="blue", highlightthickness=1)
        collapse = tk.Button(self, text = 'Open', fg = "blue", bd = 0, bg = "#fff", cursor = "hand2")
        collapse.grid(row=0,column=0,sticky="w")
        collapse.bind("<Button-1>", lambda nope:setting.collapse_switch1(1))

class setting1(tk.Frame):

    def __init__(self,setting):        
        tk.Frame.__init__(self,setting,highlightbackground="blue",highlightcolor="blue", highlightthickness=1)
        self.setting = setting            
        self.op_line1= tk.Button(self, text = 'Delete all lines',
        fg = "blue",activeforeground="green4", bd = 0, cursor = "hand2") 
        self.op_line1.grid(row=0,column=0,sticky="w")
        self.op_line1.bind("<Button-1>", lambda nope:setting.setting.delete_all())
        self.op_line1.bind("<Enter>", lambda nope: self.op_line1.configure(fg="green4"))
        self.op_line1.bind("<Leave>", lambda nope: self.op_line1.configure(fg="blue"))
        self.op_line2= tk.Button(self, text = 'Line between dates: On',
        fg = "blue", activeforeground="green4",bd = 0, cursor = "hand2")
        self.op_line2.grid(row=1,column=0,sticky="w")
        self.op_line2.bind("<Button-1>", lambda nope:self.line2_switch())
        self.op_line2.bind("<Enter>", lambda nope: self.op_line2.configure(fg="green4"))
        self.op_line2.bind("<Leave>", lambda nope: self.op_line2.configure(fg="blue"))

        if point.setting['draw'] == 0:
            self.op_line2.config(text="Line between dates: Off")

        self.op_line3= tk.Button(self, text = 'Line to timeline: Off',
        fg = "blue", activeforeground="green4",bd = 0, cursor = "hand2")
        self.op_line3.grid(row=2,column=0,sticky="w")
        self.op_line3.bind("<Button-1>", lambda nope:self.line3_switch())
        self.op_line3.bind("<Enter>", lambda nope: self.op_line3.configure(fg="green4"))
        self.op_line3.bind("<Leave>", lambda nope: self.op_line3.configure(fg="blue"))

        if point.setting['timeline'] == 1:            
            self.op_line3.config(text="Line to timeline: On")

        self.op_line4= tk.Button(self, text = 'Delete line: Off',
        fg = "blue", activeforeground="green4",bd = 0, cursor = "hand2")
        self.op_line4.grid(row=3,column=0,sticky="w")
        self.op_line4.bind("<Button-1>", lambda nope:self.line4_switch())
        self.op_line4.bind("<Enter>", lambda nope: self.op_line4.configure(fg="green4"))
        self.op_line4.bind("<Leave>", lambda nope: self.op_line4.configure(fg="blue"))

        if point.setting['del'] == 1:            
            self.op_line4.config(text="Delete line: On")

        self.op_line5= tk.Button(self, text = 'Delete point: Off',
        fg = "blue", activeforeground="green4",bd = 0, cursor = "hand2")
        self.op_line5.grid(row=4,column=0,sticky="w")
        self.op_line5.bind("<Button-1>", lambda nope:self.line5_switch())
        self.op_line5.bind("<Enter>", lambda nope: self.op_line5.configure(fg="green4"))
        self.op_line5.bind("<Leave>", lambda nope: self.op_line5.configure(fg="blue"))

        if point.setting['destroy'] == 1:            
            self.op_line5.config(text="Delete point: On")
        elif point.setting['destroy'] == 2:            
            self.op_line5.config(text="Recover title points: On")

        self.op_line6= tk.Button(self, text = 'Parallel: Off',
        fg = "blue", activeforeground="green4",bd = 0, cursor = "hand2")
        self.op_line6.grid(row=5,column=0,sticky="w")
        self.op_line6.bind("<Button-1>", lambda nope:self.line6_switch())
        self.op_line6.bind("<Enter>", lambda nope: self.op_line6.configure(fg="green4"))
        self.op_line6.bind("<Leave>", lambda nope: self.op_line6.configure(fg="blue"))

        if point.setting['parallel'] == 1:            
            self.op_line6.config(text="Parallel title: On")
        elif point.setting['parallel'] == 2:
            self.op_line6.config(text="Parallel periods: On")
            
        tk.ttk.Separator(self, orient='horizontal').grid(row=6,column=0, sticky='we') 
        la1 = tk.Label(self)
        la1.grid(row=7,column=0,sticky="we")
        la1.columnconfigure(1, weight=1)        
        tk.Label(la1,text="Go to year:").grid(row=0,column=0,sticky="w")
        self.l1 =tk.Entry(la1,width=8)
        self.l1.bind("<Return>", lambda nope:self.go_to_year())
        self.l1.grid(row=0,column=1,sticky="we")
        la2 = tk.Label(self)
        la2.grid(row=8,column=0,sticky="we")
        la2.columnconfigure(1, weight=1)
        tk.Label(la2,text="Search title:").grid(row=0,column=0,sticky="w")
        self.l2 =tk.Entry(la2,width=8)
        self.term = None
        self.index = 0
        self.l2.bind("<Return>", lambda nope:self.go_to_title())
        self.l2.grid(row=0,column=1,sticky="we")
        tk.ttk.Separator(self, orient='horizontal').grid(row=9,column=0, sticky='we') 
        self.op_line7= tk.Button(self, text = 'Collapse', fg = "blue", bd = 0, bg = "#fff", cursor = "hand2")
        self.op_line7.grid(row=10,column=0,sticky="w")
        self.op_line7.bind("<Button-1>", lambda nope:setting.collapse_switch1(0))
        self.columnconfigure(0, weight=1)          

    def line2_switch(self):         
        if point.setting['draw'] == 1:
            point.setting['draw'] = 0
            self.op_line2.config(text="Line between dates: Off")         
        elif point.setting['draw'] == 0:
            point.setting['draw'] = 1
            self.op_line2.config(text="Line between dates: On")        

    def line3_switch(self):       
        if point.setting['timeline'] == 1:
            point.setting['timeline'] = 0
            self.op_line3.config(text="Line to timeline: Off")         
        elif point.setting['timeline'] == 0:
            point.setting['timeline'] = 1
            self.op_line3.config(text="Line to timeline: On")
            
    def line4_switch(self):       
        if point.setting['del'] == 1:
            point.setting['del'] = 0
            self.op_line4.config(text="Delete line: Off")         
        elif point.setting['del'] == 0:
            point.setting['del'] = 1
            self.op_line4.config(text="Delete line: On")

    def line5_switch(self):       
        if point.setting['destroy'] == 2:
            point.setting['destroy'] = 0
            self.op_line5.config(text="Delete point: Off")         
        elif point.setting['destroy'] == 0:
            point.setting['destroy'] = 1
            self.op_line5.config(text="Delete point: On")
        elif point.setting['destroy'] == 1:
            point.setting['destroy'] = 2
            self.op_line5.config(text="Recover title points: On")

    def line6_switch(self):       
        if point.setting['parallel'] == 2:
            point.setting['parallel'] = 0
            self.op_line6.config(text="Parallel: Off")         
        elif point.setting['parallel'] == 0:
            point.setting['parallel'] = 1
            self.op_line6.config(text="Parallel title: On")
        elif point.setting['parallel'] == 1:
            point.setting['parallel'] = 2
            self.op_line6.config(text="Parallel between periods: On")

    def go_to_year(self):
        day = int(self.l1.get())*365        
        lastx = mainwin.ruall[-1]['xcor'][1]
        avx = None
        for x in mainwin.ruall:
            if x['tot'] >= day:                
                avx = x['xcor'][1]
                fracx = ((avx-(self.setting.setting.ro.winfo_width()/30))/lastx)                
                self.setting.setting.w.xview_moveto(fracx)
                break 
        if avx == None:
            self.setting.setting.w.xview_moveto(1)                 

    def go_to_title(self):   
        term = self.l2.get().lower()

        if self.term == term:
            ind = self.index
        else:
            ind = 0 

        lastx = mainwin.ruall[-1]['xcor'][1]
        avx = None
        for i,x in enumerate(mainwin.ruall[ind:]):
            if term in x['title'].lower():                
                avx = x['xcor'][1]
                fracx = ((avx-(self.setting.setting.ro.winfo_width()/30))/lastx) 
                self.term = term
                self.index = i+ind+1
                self.setting.setting.w.xview_moveto(fracx)
                break

class setting2_close(tk.Frame):

    def __init__(self,setting):
        tk.Frame.__init__(self,setting,highlightbackground="blue",highlightcolor="blue", highlightthickness=1)
        collapse = tk.Button(self, text = 'Open', fg = "blue", bd = 0, bg = "#fff", cursor = "hand2")
        collapse.grid(row=0,column=0,sticky="w")
        collapse.bind("<Button-1>", lambda nope:setting.collapse_switch2(1))

class setting2(tk.Frame):

    def __init__(self,setting):        
        tk.Frame.__init__(self,setting,highlightbackground="blue", highlightcolor="blue",highlightthickness=1)
        self.setting = setting
        tk.Label(self,text="Background:").grid(row=0,column=0,columnspan=2,sticky="w")
        self.l1 = tk.Button(self,text=f"{mainwin.background_set['background_colour']}",
        bd=1,relief='sunken', bg = "#fff", cursor = "hand2",
        command=self.background11)    
        self.l1.grid(row=0,column=1,columnspan=2,sticky="e")

        tk.ttk.Separator(self, orient='horizontal').grid(row=1,column=0,columnspan=3, sticky='we')

        tk.Label(self,text="Line period |colour|dash|").grid(row=2,column=0,columnspan=3, sticky="w") 
        tk.Label(self,text="to:").grid(row=3,column=0,sticky="w")  
        self.l11 = tk.Button(self,text=f"{point.colour_line['to']['col']}",
        bd=1,relief='sunken',bg = "#fff", cursor = "hand2",
        command=lambda:self.linecp(self.l11,point.colour_line['to'])) 
        self.l11.grid(row=3,column=1,sticky="w")
        self.l12 =tk.Entry(self,width=5)
        self.l12.bind("<Return>", lambda nope:self.linecd(self.l12,point.colour_line['to']))
        self.l12.insert(0,str(point.colour_line['to']['dash']))
        self.l12.grid(row=3,column=2,sticky="w")
        tk.Label(self,text="title:").grid(row=4,column=0,sticky="w")
        self.l21 = tk.Button(self,text=f"{point.colour_line['None']['col']}", 
        bd=1,relief='sunken',bg = "#fff", cursor = "hand2",
        command=lambda:self.linecp(self.l21,point.colour_line['None']))
        self.l21.grid(row=4,column=1,sticky="w")
        self.l22 =tk.Entry(self,width=5)
        self.l22.bind("<Return>", lambda nope:self.linecd(self.l22,point.colour_line['None']))
        self.l22.insert(0,str(point.colour_line['None']['dash']))
        self.l22.grid(row=4,column=2,sticky="w")
        tk.Label(self,text="or:").grid(row=5,column=0,sticky="w")
        self.l31 = tk.Button(self,text=f"{point.colour_line['or']['col']}",
        bd=1,relief='sunken',bg = "#fff", cursor = "hand2",
        command=lambda:self.linecp(self.l31,point.colour_line['or'])) 
        self.l31.grid(row=5,column=1,sticky="w")
        self.l32 =tk.Entry(self,width=5)
        self.l32.bind("<Return>", lambda nope:self.linecd(self.l32,point.colour_line['or']))
        self.l32.insert(0,str(point.colour_line['or']['dash']))
        self.l32.grid(row=5,column=2,sticky="w")
        tk.Label(self,text="and:").grid(row=6,column=0,sticky="w")
        self.l41 = tk.Button(self,text=f"{point.colour_line['and']['col']}",
        bd=1,relief='sunken',bg = "#fff", cursor = "hand2",
        command=lambda:self.linecp(self.l41,point.colour_line['and'])) 
        self.l41.grid(row=6,column=1,sticky="w")
        self.l42 =tk.Entry(self,width=5)
        self.l42.bind("<Return>", lambda nope:self.linecd(self.l42,point.colour_line['and']))
        self.l42.insert(0,str(point.colour_line['and']['dash']))
        self.l42.grid(row=6,column=2,sticky="w")
        tk.Label(self,text="format:").grid(row=7,column=0,sticky="w")
        self.l51 = tk.Button(self,text=f"{point.colour_line['brace']['col']}",
        bd=1,relief='sunken',bg = "#fff", cursor = "hand2",
        command=lambda:self.linecp(self.l51,point.colour_line['brace']))
        self.l51.grid(row=7,column=1,sticky="w")
        self.l52 =tk.Entry(self,width=5)
        self.l52.bind("<Return>", lambda nope:self.linecd(self.l52,point.colour_line['brace']))
        self.l52.insert(0,str(point.colour_line['brace']['dash']))
        self.l52.grid(row=7,column=2,sticky="w")

        tk.ttk.Separator(self, orient='horizontal').grid(row=8,column=0,columnspan=3, sticky='we')

        tk.Label(self,text="Right-click: draw line").grid(row=9,column=0,columnspan=3,sticky="w")
        tk.Label(self,text="Left + drag: move and draw").grid(row=10,column=0,columnspan=3,sticky="w")
        tk.Label(self,text="Double left click: open article").grid(row=11,column=0,columnspan=3,sticky="w")
        tk.Label(self,text="Right + scroll: zoom").grid(row=12,column=0,columnspan=3,sticky="w")
        tk.Label(self,text="Middle-click: add wiki image").grid(row=13,column=0,columnspan=3,sticky="w")
        tk.Label(self,text="Hold-Left on line: view point").grid(row=14,column=0,columnspan=3,sticky="w")
        tk.ttk.Separator(self, orient='horizontal').grid(row=15,column=0,columnspan=3, sticky='we')
        tk.Label(self,text="Article filter |colour|length|").grid(row=16,column=0,columnspan=3,sticky="w")       
        tk.Label(self,text="filter:").grid(row=17,column=0,sticky="w") 
        self.l61 = tk.Button(self,text=f"{mainwin.background_set['length_colour']['col']}",
        bd=1,relief='sunken',bg = "#fff", cursor = "hand2",
        command=lambda:self.linec61(self.l61,mainwin.background_set['length_colour']))  
        self.l61.grid(row=17,column=1)
        self.l62 =tk.Entry(self,width=6)
        self.l62.bind("<Return>", lambda nope:self.linec62())
        self.l62.insert(0,str(mainwin.background_set['length_colour']['length']))
        self.l62.grid(row=17,column=2,sticky="w")
        tk.Label(self,text="normal:").grid(row=18,column=0,sticky="w")
        self.l71 = tk.Button(self,text=f"{mainwin.background_set['normal_colour']['col']}",
        bd=1,relief='sunken',bg = "#fff", cursor = "hand2",
        command=lambda:self.linec61(self.l71,mainwin.background_set['normal_colour']))  
        self.l71.grid(row=18,column=1)
        tk.Label(self,text="None").grid(row=18,column=2,sticky="w")

        tk.ttk.Separator(self, orient='horizontal').grid(row=19,column=0,columnspan=3, sticky='we')
        
        self.lop= tk.Button(self, text = 'Collapse', fg = "blue", bd = 0, bg = "#fff", cursor = "hand2")
        self.lop.grid(row=20,column=0,sticky="w")
        self.lop.bind("<Button-1>", lambda nope:setting.collapse_switch2(0))   

    def background11(self):
        col = colorchooser.askcolor()[1]
        if col:
            mainwin.background_set['background_colour']=col 
            self.setting.setting.w.config(background=mainwin.background_set['background_colour'])
            self.l1.config(text=f"{col}")
            for c in wikipic.every:
                c.lab1.config(bg=col)
    
    def linec61(self,name,set_col):        
        col = colorchooser.askcolor()[1]
        if col:
            set_col['col'] = col
            try:
                self.setting.setting.style.configure('style1.TButton',
                bordercolor=mainwin.background_set['normal_colour']['col'])
                self.setting.setting.style.configure('style2.TButton',
                bordercolor=mainwin.background_set['length_colour']['col'])
            except:
                pass            
            try:
                for v1 in point.connt:
                    for v2 in point.connt[v1]['cor']:
                        if v2.posar[1]-v2.posar[0] > mainwin.background_set['length_colour']['length']:
                            forg = mainwin.background_set['length_colour']['col']
                        else:
                            forg = mainwin.background_set['normal_colour']['col']

                        v2.bit.config(bg= forg)                     
            except:
                pass
            name.config(text=f"{col}")

    def linec62(self):
        mainwin.background_set['length_colour']['length']=int(self.l62.get())
        try:
            for v1 in point.connt:
                for v2 in point.connt[v1]['cor']:
                    if v2.posar[1]-v2.posar[0] > mainwin.background_set['length_colour']['length']:
                        forg = mainwin.background_set['length_colour']['col']
                    else:
                        forg = mainwin.background_set['normal_colour']['col']
                    v2.bit.config(bg= forg)                     
        except:
            pass

    def linecp(self,name,set_col):
        col = colorchooser.askcolor()[1]
        if col:
            set_col['col'] = col
            name.config(text=f"{col}")       
       
    def linecd(self,name,date_dash):
        name_dash = name.get().lower()
        if name_dash == 'none' or name_dash == '0':
            date_dash['dash']=None
        else:            
            date_dash['dash']=int(name_dash) 
        
class listbox_frame(tk.Frame):

    def __init__(self,ro,stand=1,dlist=[]):        
        tk.Frame.__init__(self,ro,relief='solid',bd=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        lab1 = tk.Label(self,relief='solid',bd=1,height=2)
        lab1.grid(row=0,column=0,sticky="we")
        lab1.columnconfigure(0, weight=1) 
        but1 = tk.Button(lab1,text='delete',fg = "black", bd = 1, bg = "#fff", cursor = "hand2",command=self.deli)
        but1.grid(row=0,column=0) 
        scrollbar_l = tk.Scrollbar(self, orient='vertical')
        self.lb = tk.Listbox(self,yscrollcommand=scrollbar_l.set)
        scrollbar_l.config(command=self.lb.yview)
        scrollbar_l.grid(row=1,column=1,sticky="ns")  
        self.lb.grid(row=1,column=0,sticky="nsew")
        self.stand = stand
        self.dlist = dlist
        self.list_update()

    def list_update(self): 
        self.lb.delete(0, 'end')
        for i,x in enumerate(self.dlist):
            self.lb.insert(i,x)       

    def deli(self):
        sel = self.lb.curselection() 
        if sel:
            if self.stand == 1:
                del mainwin.data_insert[self.lb.get(sel)]
            elif self.stand == 2:
                del self.dlist[sel[0]]            
            self.lb.delete(sel[0])      

class mainwin(tk.Frame):    
    y2 = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 
    'august', 'september', 'october', 'november', 'december']
    y3 = [(0, 'jan'), (31, 'feb'), (59, 'mar'), (90, 'apr'), (120, 'may'), 
    (151, 'jun'), (181, 'jul'), (212, 'aug'), (243, 'sep'), (273, 'oct'), (304, 'nov'), (334, 'dec')]
    
    search_term = ['date','dates','reign','coronation','term','year','years',
    'serviceyears','consecrated','post','founded','built','abandoned',
    'constructed','foundation','predecessor','enthroned','ended','released','written']

    ban_term = ['record','population','gdp','hdi','gini','gsp','gva','number',
    'num','format','age','sr','code','stat']
    box_term = {'search':[],'ban':[]}

    zoom = {'move':False,'move2':False,'zoomn':1,'zoomp':1,'gatez':None}
    pat = ''
    look = None
    length_line = {'skip':15,'year':3,'month':2}
    length_skip = 15

    loop = {'loop1':False,'links':[],'win':None,'sec1':'','sec2':'',
    'text':False,'text_mid':False,'text_info':False,'len_data':None,'looptext':False} 

    background_set = {'background_colour':'#eee',
    'length_colour':{'col': 'navajo white', 'length': 52000},'normal_colour':{'col': '#cce6e6', 'length': 0}}

    ruall = []
    nodate = []
    specs1 = {}
    add_data_specs = {}
    data_insert = {}    

    def __init__(self,ro):
        tk.Frame.__init__(self,ro)
        self.ro = ro
        ro.resizable(0,0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)        
        self.w = tk.Canvas(self,background=mainwin.background_set['background_colour'])
        self.w.columnconfigure(1, weight=1)
        self.w.rowconfigure(0, weight=1)

        self.w.bind("<MouseWheel>",lambda event:self.zoom_func(event))
        self.w.bind("<Button-3>",lambda event:self.gate_zoom(1))
        self.w.bind("<ButtonRelease-3>",lambda event:self.gate_zoom(2))
        self.w.bind("<B1-Motion>", lambda event:self.finditem(event)) 

        self.setting = settingmain(self)
        self.scrollbarx = tk.Scrollbar(self,orient='horizontal')
        self.scrollbary = tk.Scrollbar(self,orient='vertical')

        style = ttk.Style()
        self.style = style
        style.theme_use('clam')
        style.configure('style1.TButton',bordercolor="turquoise3",
        foreground ="black",background = "#fff",focuscolor='')
        style.configure('style2.TButton',bordercolor="orange red",
        foreground ="black",background = "#fff", focuscolor='')      
        style.configure("bar.Horizontal.TProgressbar", foreground='gold',
        bordercolor='sienna3',background='gold',troughcolor ='AntiqueWhite2')        
        
        self.pb = ttk.Progressbar(self,orient ="horizontal", mode ="determinate",
        length=200,style="bar.Horizontal.TProgressbar")
        self.pb["maximum"] = 100
        self.pb["value"] = 0
        self.pb.grid(row=1,column=0,sticky="ew")
        
        self.frame_begin = wbegin(self)
        self.frame_begin.grid(row=0,column=0)
        self.fset = None        
        self.scrollbarx.config(command = self.w.xview )
        self.scrollbary.config(command = self.w.yview )
        self.w.config(xscrollcommand=self.scrollbarx.set,
        yscrollcommand=self.scrollbary.set,scrollregion=self.w.bbox("all"))

        self.menu_or = tk.Menu(self.ro)        
        menu1 = tk.Menu(self.menu_or,tearoff=0)
        self.menu_or.add_cascade(label = "Setting", menu = menu1)
        menu1.add_command(label="Save timeline", command=self.save_json)
        menu1.add_command(label="Add wiki json", command=self.open_json)
        menu1.add_command(label="json keyword", command=self.json_keyword)
        menu1.add_command(label="Infobox filter", command=self.box_keyword)    
        menu1.add_command(label="Add date", command=self.insertdate)
        menu1.add_command(label="Add wiki url", command=self.save_wiki)  
        menu1.add_command(label="List", command=self.listbox_data)
        menu1.add_command(label="Run", command=self.mainbut)
        menu1.add_separator()
        menu1.add_command(label="Random images", command=self.randpic)
        menu1.add_command(label="Recover all points", command=self.recover_all)
        menu1.add_command(label="Path enwiki.xml", command=self.path_wikixml)
        menu1.add_command(label="Configure timeline", command=self.linelenght)        
        menu1.add_command(label="Date's without year", command=self.lisbox_nodate)
        menu1.add_command(label="Exit", command=self.ro.quit)  

    def finditem(self,event):
        x = self.w.canvasx(event.x)
        y = self.w.canvasy(event.y) 
        over = self.w.find_overlapping(x,y,x+8,y+8)
        cor = linepoint.cor

        if cor:
            if mainwin.look != None and mainwin.look.bit.winfo_exists() == 1:
                width = mainwin.look.bit.winfo_reqwidth()
                height = mainwin.look.bit.winfo_reqheight()
                if abs(cor[0]-x) > (width/2) or abs(cor[1]-y) > (height/2):
                    mainwin.look.leave()
                    return 

        overn = None               
        if len(over) == 1:
            if over[0] in point.mot_point:
                overn = over[0]
        elif len(over) > 1:
            if all([x in point.mot_point for x in over]):
                overn = over[0]

        if overn:
            if mainwin.look == None:
                poi = point.mot_point[overn][0]
                years = point.mot_point[overn][1]
                mainwin.look = linepoint(poi.w,x,y,poi.every,years)
                linepoint.cor = [x,y]

    def reset(self):
        point.ycor = {}     
        point.connt = {}    
        point.stindex = {}
        point.mot_point = {}
        point.del_list = {}
        point.chdrag['check_yu'] = 0
        point.chdrag['check_yd'] = 0
        point.chdrag['change_y'] = False    
        mainwin.zoom['move'] = False
        mainwin.zoom['move2'] = False
        mainwin.zoom['zoomn'] = 1
        mainwin.zoom['zoomp'] = 1
        mainwin.zoom['gatez'] = None           

    def delete_all(self):
        for v1 in point.connt:
            for v2 in point.connt[v1]['cor']:
                for c in range(0,3):
                    try:
                        if c == 0:
                            self.w.delete(v2.u0)
                            v2.stru0=None
                        elif c == 1:
                            self.w.delete(v2.u1)
                            v2.stru1=None
                        elif c == 2:
                            self.w.delete(v2.u2)
                            v2.stru2=None                                    
                    except:
                        pass
         
    def recover_all(self):
        if point.del_list != {}:
            for x in point.del_list:
                for z in point.del_list[x]:                    
                    point.connt[x]['cor'].append(z)                    
                    z.win = self.w.create_window(z.x* mainwin.zoom['zoomn'], z.y* mainwin.zoom['zoomn'], window=z.bit)
                point.del_list[x] = []
                point.connt[x]['cor'] = sorted(point.connt[x]['cor'], key = lambda k: k.x)
    
    def randpic(self):
        if self.w.winfo_exists() == 1:

            def listpic():
                l = list_pic.pop()
                l.open_wikipic()
                if len(list_pic) > 0:
                    self.w.after(1200,lambda:listpic())

            list_pic = []
            if point.connt != []:
                change = int(len(point.connt)**0.7)
                for x in point.connt:
                    if randrange(change) == 0:
                        list_pic.append(point.connt[x]['cor'][0])

            if list_pic != []:
                listpic()
    
    def open_json(self,dul=None):  
        filename1 = filedialog.askopenfilename(title = "Select file",filetypes = (("json files","*.json"),))
        if filename1 == '':
            return 
        self.datejson(filename1)
        if dul != None:
            dul.box1.list_update()

    def gate_zoom(self,stand):    
        if stand == 1:        
            mainwin.zoom['gatez'] = True    
        if stand == 2:
            mainwin.zoom['gatez'] = None

    def zoom_func(self,event):       
        if mainwin.zoom['gatez']:
            oldz = mainwin.zoom['zoomn']
            oldzp = mainwin.zoom['zoomp']

            if event.delta > 0:
                scalen = 1+(1/3)
                scalenp = 1+(1/9)
            elif event.delta < 0:
                scalen = 0.75
                scalenp = 0.9

            if oldz*scalen <= 0.75**6 or oldz*scalen > 1:
                return  

            mainwin.zoom['zoomn'] = oldz*scalen
            mainwin.zoom['zoomp'] = oldzp*scalenp            
            viewx = self.w.xview()[0]
            viewy = self.w.yview()[0]    
            self.w.scale('all',0,0,scalen, scalen)

            if mainwin.zoom['zoomn'] <= (0.75**2):
                self.w.itemconfig("month3",state='hidden')
                self.w.itemconfig("day1",state='hidden')

                if mainwin.zoom['zoomn'] <= (0.75**3): 
                    self.w.itemconfig("month1",state='hidden')

                    if mainwin.zoom['move2'] == False:
                        self.w.move("year4",0,110*mainwin.zoom['zoomn'])
                        mainwin.zoom['move2'] = True

                    if mainwin.zoom['zoomn'] <= (0.75**4):
                        self.w.itemconfig("day2",state='hidden')
                        self.w.itemconfig("year1",state='hidden') 

                        if mainwin.zoom['move'] == False:
                            self.w.move("year2",0,120*mainwin.zoom['zoomn'])
                            self.w.move("year4",0,100*mainwin.zoom['zoomn'])
                            self.w.move("year3",0,135*mainwin.zoom['zoomn'])
                            mainwin.zoom['move'] = True 

                    else:
                        self.w.itemconfig("day2",state='normal')
                        self.w.itemconfig("year1",state='normal') 

                        if mainwin.zoom['move'] == True:
                            self.w.move("year2",0,-120*mainwin.zoom['zoomn'])
                            self.w.move("year4",0,-100*mainwin.zoom['zoomn'])
                            self.w.move("year3",0,-135*mainwin.zoom['zoomn'])
                            mainwin.zoom['move'] = False 

                else:
                    if mainwin.zoom['move2'] == True:
                        self.w.move("year4",0,-110*mainwin.zoom['zoomn'])
                        mainwin.zoom['move2'] = False       
                    self.w.itemconfig("month1",state='normal')

            else:
                self.w.itemconfig("day1",state='normal')
                self.w.itemconfig("month3",state='normal')        
            self.w.config(scrollregion=self.w.bbox("all"))

            for x in wikipic.every:                           
                w, h = x.orimage.size          
                wikiimage = ImageTk.PhotoImage(x.orimage.resize((int(w*min(1,(mainwin.zoom['zoomp']))), int(h*min(1,(mainwin.zoom['zoomp']))))))        
                x.lab1.config(image=wikiimage)
                x.lab1.image = wikiimage 
            self.w.xview_moveto(viewx)
            self.w.yview_moveto(viewy)

        else:
            if event.delta > 0:
                scrolld = 1      
            elif event.delta < 0:
                scrolld = -1
            self.w.xview_moveto(self.w.xview()[0]+(scrolld*(1/(self.w.winfo_reqwidth()*mainwin.zoom['zoomn']))))      

    def save_json(self):
        filename1 = filedialog.asksaveasfilename(title = "Select file",defaultextension=".json",filetypes = (("json files","*.json"),))
        if filename1 == '':
            return 

        for v1 in point.connt:
            for v2 in point.connt[v1]['cor']:   
                v2.every['rcor']=v2.y
                for c in range(0,3):
                    try:
                        if c == 0:
                            if v2.stru0 != None:
                                v2.every['u0']=v2.stru0
                        elif c == 1:
                            if v2.stru1 != None:
                                v2.every['u1']=v2.stru1
                        elif c == 2:
                            if v2.stru2 != None:
                                v2.every['u2']=v2.stru2                             
                    except:
                        pass        
        for z in point.del_list:
            for z2 in point.del_list[z]:
                z2.every['del'] = True
        save_dict = {
            'data':{
                'ruall':mainwin.ruall,'ycor':point.ycor,'setting':point.setting,
                'colour_line':point.colour_line,'pat':mainwin.pat,'background_set':mainwin.background_set,
                'search_term':mainwin.search_term,'ban_term':mainwin.ban_term,'length_line':mainwin.length_line}}
        with open(filename1, 'w') as jr:        
            json.dump(save_dict,jr)
        
    def open_timeline(self):
        filename1 = filedialog.askopenfilename(title = "Select file",filetypes = (("json files","*.json"),))
        if filename1 == '':
            return 

        with open(filename1, 'r') as jr:        
            f1 = json.load(jr)
            f = f1['data']
            mainwin.ruall = f['ruall']
            point.ycor = f['ycor']
            point.setting = f['setting']
            point.colour_line = f['colour_line']
            mainwin.pat = f['pat']
            mainwin.background_set = f['background_set']
            mainwin.search_term = f['search_term']
            mainwin.ban_term = f['ban_term']
            mainwin.length_line = f['length_line']            
        self.main_time()

    def path_wikixml(self):
        filename1 = filedialog.askopenfilename(title = "Select file",filetypes = (("xml files","*.xml"),))
        if filename1 == '':
            return               
        mainwin.pat = filename1

    def reslink_list(self,title):
        list_titles = []       
        if title in mainwin.add_data_specs:
            for x1 in mainwin.add_data_specs[title]:
                if x1 in mainwin.data_insert:
                    for x2 in mainwin.data_insert[x1]:
                        list_titles.append(x2['spec'])

        if title in point.connt:
            for y1 in point.connt[title]['cor']:                
                list_titles.append(y1.spec)

        for sp in list_titles:
            for nn in range(2):                            
                if sp[nn]:
                    spn0 = re.search(r'(.*?)(\d+)\Z',sp[nn]).groups()
                    if len(spn0) == 2:
                        if spn0[0].isdigit() == False and spn0[1].isdigit() == True:
                            spnd0 = int(spn0[1])
                            if spn0[0] in mainwin.specs1:
                                if spnd0 >= mainwin.specs1[spn0[0]]:
                                    mainwin.specs1[spn0[0]] = spnd0 +1
                            else:
                                mainwin.specs1[spn0[0]] = spnd0

    def linelenght(self):  

        def l1_date():
            get = float(l1.get())
            if get >= 1:
                mainwin.length_line['year'] = get
                l11.config(fg = "green")
                fset.after(600,lambda:l11.config(fg = "black"))  

        def l2_date():
            get = float(l2.get())
            if get <= 12:
                mainwin.length_line['month'] = get
                l21.config(fg = "green")
                fset.after(600,lambda:l21.config(fg = "black"))  

        fset = tk.Toplevel(self)
        tk.Label(fset,text="Configure timeline\tpress enter to confirm").grid(row=0,column=0,columnspan=2)
        tk.ttk.Separator(fset, orient='horizontal').grid(row=1,column=0,columnspan=2,sticky='we')
        l11 = tk.Label(fset,text="Display years after amount of years: > ")
        l11.grid(row=2,column=0,sticky="e") 
        l1 =tk.Entry(fset,width=5)
        l1.insert(0,mainwin.length_line['year'])
        l1.bind("<Return>", lambda nope:l1_date())    
        l1.grid(row=2,column=1,sticky="w")
        l21 = tk.Label(fset,text="Display months after amount of months: > ")
        l21.grid(row=3,column=0,sticky="e")
        l2 =tk.Entry(fset,width=5)
        l2.insert(0,mainwin.length_line['month'])
        l2.bind("<Return>", lambda nope:l2_date())    
        l2.grid(row=3,column=1,sticky="w")        

    def insertdate(self,dul = None):
        time_raw = {}
        mainwin.specs1 = {}
        time_raw['pos'] = [0,0]    

        def l1_date():
            if l1.get():                
                date_l = finddate.date_find(l1.get())                
                if date_l == []:
                    l11.config(fg = "SystemButtonText")
                else:
                    l11.config(fg = "green")

                time_raw['date'] = l1.get()                
                l12.config(text=date_l)

        def l2_date():
            time_raw['title'] = l2.get()
            l22.config(text=time_raw['title'])
            l21.config(fg = "green")

        def l3_date():
            time_raw['key'] = l3.get()
            l32.config(text=time_raw['key'])
            l31.config(fg = "green")

        def b1_add():
            if 'date' in time_raw and 'title' in time_raw and 'key' in time_raw:                
                title_date = f"{time_raw['title']}-{time_raw['date']}"

                if title_date in mainwin.data_insert:
                    l11.config(fg = "red")
                    fset.after(1000,lambda:l11.config(fg = "green"))
                    l21.config(fg = "red") 
                    fset.after(1000,lambda:l21.config(fg = "green"))
                    b1.config(fg = "red")
                    fset.after(1000,lambda:b1.config(fg = "SystemButtonText"))               
                else:
                    mainwin.data_insert[title_date]=[]
                    time_raw['every'] = [time_raw['key'],time_raw['date']]

                    mainwin.specs1 = {'to':1000,'or':1000,'and':1000,'brace':1000}
                    mainwin.reslink_list('nope',time_raw['title'])
                    if time_raw['title'] in mainwin.add_data_specs:
                        mainwin.add_data_specs[time_raw['title']].append(title_date)
                    else:
                        mainwin.add_data_specs[time_raw['title']] = [title_date]

                    final = self.datedata(time_raw)
                    mainwin.specs1 = {}                    
                    for x in final:               
                        mainwin.data_insert[title_date].append(x)
                        mainwin.data_insert[title_date] = [k for i,k in enumerate(mainwin.data_insert[title_date]) \
                            if k not in (mainwin.data_insert[title_date][i+1:])]

                    b1.config(fg = "green")                    
                    fset.after(1000,lambda:b1.config(fg = "SystemButtonText"))

                    if dul != None:
                        dul.box1.list_update()            
            else:
                b1.config(fg = "red")
                fset.after(1000,lambda:b1.config(fg = "SystemButtonText")) 

        fset = tk.Toplevel(self)
        fset.columnconfigure(1, weight=1)
        tk.Label(fset,text="press enter to confirm").grid(row=0,column=0,columnspan=2)
        
        l11 = tk.Label(fset,text="Date:")
        l11.grid(row=1,column=0,sticky="w") 
        l1 =tk.Entry(fset,width=30)
        l1.bind("<Return>", lambda nope:l1_date())    
        l1.grid(row=1,column=1,sticky="we")
        l12 = tk.Label(fset)
        l12.grid(row=1,column=2,sticky="w")

        l21 = tk.Label(fset,text="Title:")
        l21.grid(row=2,column=0,sticky="w")
        l2 =tk.Entry(fset,width=30)
        l2.bind("<Return>", lambda nope:l2_date())    
        l2.grid(row=2,column=1,sticky="we")
        l22 = tk.Label(fset)
        l22.grid(row=2,column=2,sticky="w")

        l31 = tk.Label(fset,text="Key:")
        l31.grid(row=3,column=0,sticky="w")
        l3 =tk.Entry(fset,width=30)
        l3.bind("<Return>", lambda nope:l3_date())    
        l3.grid(row=3,column=1,sticky="we")
        l32 = tk.Label(fset)
        l32.grid(row=3,column=2,sticky="w")

        b1 = tk.Button(fset,text = 'Add',bg='white',relief='solid',command=b1_add)
        b1.grid(row=4,column=0)

    def text_an(self,rr,title,posart):
        wor = [r'\*\*',r'\*','by','in','between','before','after','on','at',
        'around','until','year of','date of','since','from',r'approx\.']

        wor2 = [r'(?:\(|.?)c\.(?=\d+|\s\d+)',r'(?:\(|.?)circa(?=\d+|\s\d+)',
        r'(?:\(|.?)ca\.(?=\d+|\s\d+)',r'dated to(?=\d+|\s\d+)']

        stoppar = ['bibliography','references','citations','see also']
        wiki_brack = ['circa','sc']
        endcheck = ['s','%','people',"''",'million','thousand','hundred']
        endcheck2 = ['is','was','as'] 
        endcheck3 = ['%',':']  
        firstcheck = ['chapter','age','volume','page']           
        pat7 = re.compile(r'&lt;ref.*?/(ref|ref\s|\sref|)&gt;',flags=re.DOTALL)
        newl = re.compile(r'(?<=\w)(\.(?![^[[]*?\]\]))(?=(\Z|[^a-zA-Z\d]+[A-Z]))')
        mainwin.specs1 = {}        
        res = []
        titletext = f'Text:{title}'  

        if rr:
            if titletext in mainwin.data_insert:
                return len(mainwin.data_insert[titletext])

            mainwin.specs1 = {'to':2000,'or':2000,'and':2000,'brace':2000}
            mainwin.reslink_list('nope',title)           
            l = re.sub(pat7,' ',rr)
            
            escape = balance(0, len(l), l, ['&lt;', '&gt;'], [], None)           
            for rp in escape:
                l = l[:rp[0]] + '$'*((rp[1]+3)-rp[0]) + l[(rp[1]+3):]
            l = re.sub(r'\$+',' ',l)

            l = re.sub(r'{{[dD]ate.?\|([^{]*?)(\|[^{]*?}}|}})',r'\g<1>',l)
            
            for wi in wiki_brack:
                w1 = wi[0].lower()
                w2 = wi[0].upper()
                w3 = f"[{w1}{w2}]{wi[1:]}"
                w4 = '@@!%@@'
                if wi == 'circa':
                    w4 = '@@!!%@@'

                l = re.sub(r'({{)(%s\s*?\|[^{}]+)(}})'%w3,'%s'%w4+r'\g<2>'+'@@%!@@',l)

            l = l.replace('{{snd}}','-')

            brace1 = balance(0, len(l), l, ['{{', '}}'], [], None)
            for rp in  brace1: 
                l = l[:rp[0]] + '$'*((rp[1]+2)-rp[0]) + l[(rp[1]+2):]
            l = l.replace('@@!!%@@','#@# {{')
            l = l.replace('@@!%@@','{{')
            l = l.replace('@@%!@@','}}')             
            l = ' '.join([x for x in l.split(' ') if x != ''])
            l = re.sub(r'\$+',r' bracket ',l)

            l = re.sub(r'\sbracket\s(,|;|:)',r' bracket ',l)
            l = re.sub(newl,'\n',l)        
            l = l.lower()            
            yy1 = re.search(r'(\'\'\'(.*?\w+.*?)\'\'\')\s?((\(.*?\)|\sbracket\s)\s\(.*?(\d+|\d+\s)\)|\(.*?(\d+|\d+\s)\))',
            l[:int(len(l)/2)])

            if yy1 != None:
                beg = l[:yy1.end()].replace(yy1.groups()[0],'#@#')
                if yy1.groups()[5] == None and yy1.groups()[4] != None:
                    beg = beg.replace(yy1.groups()[3],'')
                l = beg + l[yy1.end():]

            else:
                yy2 = re.search(r"\'\'\'.*?\w+.*?\'\'\'\s?\(([\s+bracket\s+]+)[^()]+?\d+[^()]+?\)",l[:int(len(l)/2)])
                if yy2 != None:                
                    beg = l[:yy2.end()].replace(yy2.groups()[0],'#@#')
                    l = beg + l[yy2.end():]

            pages = {0:''}
            list_line = l.splitlines()
            for ip,ll in enumerate(list_line): 
                page = re.finditer(r'=(?P<tussen>===|==|=)([^=]*?\w+[^=]*?)(?P=tussen)=',ll)
                for p in page:               
                    pages.update({ip:p.groups()[1]})
            ster = ''
            posn = 0            
            avrl = []                 
            for posn,x in enumerate(list_line):
                che21 = x.split(' ')                
                if len(che21) > 1:

                    if che21[0] == '*':
                        ster = x
                    if che21[0] == '**':
                        x = ster + (x.replace('**','')) 

                    titlep = pages[0]
                    stopr = False
                    for pt in pages:
                        if posn > pt:                            
                            titlep = pages[pt]
                            for stp in stoppar:                            
                                if stp in pages[pt]:
                                    stopr = True
                                    break
                            if stopr == True:
                                break  

                    if stopr == True:                                               
                        break

                    for x1 in wor:
                        x = re.sub(r'(\A|\s)%s(\s)'%x1,r'\g<1>'+'#@#'+r'\g<2>',x)
                    for x1 in wor2:
                        x = re.sub(r'(\A|\s)%s'%x1,r'\g<1>'+'#@#',x)
                    x = re.sub(r'(?<!\[)\[(\d\d|\d)\](?!\])','w',x)                  
                    x = re.sub(r'(\[\[[^]]*?)#@#([^[[]*?\]\])',r'\g<1>'+'w'+r'\g<2>',x)                    
                    brace2 = balance(0, len(x), x, ['[[', ']]'], escape, None)
                    for rp in  brace2: 
                        fis1 = x.rfind('|',rp[0],rp[1])
                        endm = rp[0]
                        rep = 2
                        if fis1 != -1:
                            rep = 1
                            endm = fis1 
                        x = x[:rp[0]] +' '*((endm+rep)-rp[0])+ x[(endm+rep):(rp[1])]+' '*2+ x[(rp[1]+2):]
                    x = ' '.join([x2 for x2 in x.split(' ') if x2 != ''])

                    if x.find('#@#') != -1: 
                        lines = x.split('#@#')                        
                        bgind = 1

                        if x.startswith('#@#') == True:
                            bgind = 0
                        for line1 in lines[bgind:]:                                                           
                            che11 = 0
                            keys = line1.replace('#@#',' ').replace('(','').replace(')','').split()
                            firstd = None
                            check1 = False                            
                            count = 0

                            for df in keys:
                                if df != 'of':
                                    count += 1
                                if firstd:
                                    if df.endswith('.') or df.endswith(','):
                                        df2 = df[:-1]
                                    else:
                                        df2 = df
                                    for ench in endcheck:                                                                           
                                        if df2.endswith(ench):
                                            if df2 not in endcheck2:
                                                firstd = None                                    
                                    break                                
                                for df1 in df:
                                    if df1.isdigit():
                                        firstd = count
                                    if df1 in endcheck3 and firstd != None:
                                        firstd = None
                                        break
                                    if df1 == "0" and firstd != None and check1 == True: 
                                        firstd = None
                                        break
                                    if df1 == "," and firstd != None:
                                        check1 = True
                                    else:
                                        check1 = False 

                                if any(map(lambda fi: df.startswith(fi),firstcheck)):
                                    break

                            if firstd == None:
                                continue
                            else:
                                che11 = max(0,firstd-1) 

                            time_raw = {'date':line1,'title':title,
                            'pos':[posart[0],posart[1]],'key':titlep,'every':[x,line1]}                            
                            l1 = mainwin.datedata('nope',time_raw)

                            if l1 != []: 
                                last_idate = 0                                                                                                   
                                for y2 in l1:
                                    che1 = []
                                    for y31 in y2:
                                        if (y31 == 'm' or y31 == 'd' or y31 == 'y'):                                            
                                            if len(y2[y31]) == 2:                                                
                                                if type(y2[y31][1]) == list:
                                                    for y41 in y2[y31][1]:
                                                        che1.append(y41)
                                                else:
                                                    che1.append(y2[y31][1]) 
                                                                                       
                                    if che1 != []:
                                        che1 = sorted(che1)

                                        if che1[0] == 0 and che11 > 0 and y2['m'][0] == None and y2['d'][0] == None:                                              
                                            fd = re.search(r'\d+',line1)
                                            if int(fd.group()) == y2['y'][0]:
                                                che11 *= 2
                                        if che1[0] == che11 and che11 > 1:
                                            che11 = 1
                                        if che1[0] + che11 > 3:                 
                                            break
                                        
                                        last_idatelist = che1[-1]
                                        last_idate += che1[-1]
                                        che1.remove(last_idatelist)

                                        if last_idatelist in che1:
                                            last_idate += 1
                                        else:
                                            che1.append(last_idatelist)
                                        if che11 > last_idate:
                                            last_idate = che11

                                        if y2['spec'][0] == None and y2['spec'][1] == None:                                         
                                            che11 += che1[-1] 
                                                                              
                                        if len(keys) <= 7+last_idate:
                                            key = ' '.join(keys[last_idate+1:])            
                                        else:
                                            key = ' '.join(keys[last_idate+1:last_idate+8])

                                        last_idate += 2
                                        
                                        if key == '':
                                            y2['key'] =  titlep
                                        else:
                                            y2['key'] =  titlep+'~'+key
                                                                                                                                                         
                                        res.append(y2)
                                        avrl.append(y2['y'][0])

                                        if line1.startswith(' {{circa'):
                                            avrl.extend([y2['y'][0] for x in range(3)])
                                    else:
                                        break 

            mainwin.specs1 = {}
            if res == []:
                return 0

            avrn = sum(avrl)/len(avrl)
            err = 10
            avrm = median(avrl)

            if len(avrl) > 1:                 
                avrst = stdev(avrl)      
                err = ((abs(avrm-avrn)**0.8)+avrst)
                if err < 50:
                    err = min(50,int(err*1.5))
                    err = max(10,err)

            fin_res_list = []                       

            for av in res:          
                if int(avrm-err) <= av['y'][0] <= int(avrm + err):
                    fin_res_list.append(av)

            if mainwin.loop['text_mid'] == True and len(fin_res_list) > 3:

                fin_res_list = sorted(fin_res_list, key = lambda k: k['tot'])
                fin_res_list_tot = [x['tot'] for x in fin_res_list]
                fin_res_list_index = [] 
                for i,fin in enumerate(fin_res_list):
                    if fin['tot'] in fin_res_list_tot[i+1:]:
                        if fin_res_list[i]['spec'][0] == None and fin_res_list[i]['spec'][1] == None and \
                        (fin_res_list[i+1]['spec'][0] != None or fin_res_list[i+1]['spec'][1] != None):
                            fin_res_list_index.append(i)
                        elif fin_res_list[i+1]['spec'][0] == None and fin_res_list[i+1]['spec'][1] == None and \
                        (fin_res_list[i]['spec'][0] != None or fin_res_list[i]['spec'][1] != None):
                            fin_res_list_index.append(i+1)

                fin_res_list_index = set(fin_res_list_index)
                if len(fin_res_list) - len(fin_res_list_index) >= 3:
                    for i in fin_res_list_index:
                        del fin_res_list[i]

                fin1 =  fin_res_list[0]
                fin3 =  fin_res_list[-1]
                fin2 =  min(fin_res_list, key=lambda k:abs(k['y'][0]-avrm)) 
                if fin2 == fin1 or fin2 == fin3:
                    fin2 = fin_res_list[1]                                                

                fin_res_list = [fin1,fin2,fin3]

            for av in fin_res_list:            
                if titletext not in mainwin.data_insert:
                    mainwin.data_insert[titletext] = [av]
                else:
                    mainwin.data_insert[titletext].append(av) 

            if titletext in mainwin.data_insert:
                mainwin.data_insert[titletext] = [k for i,k in enumerate(mainwin.data_insert[titletext]) \
                    if k not in (mainwin.data_insert[titletext][i+1:])]
                return len(mainwin.data_insert[titletext])
            else:
                return 0

    def ask_textan(self,rr,title,rowin,posart,upd=None):

        def yesres():
            dm = mainwin.text_an('nope',rr,title,posart)
            fset3 = tk.Toplevel(rowin)
            tk.Label(fset3,text=f'Found: {dm} dates').grid(row=0,column=0)
            if dm > 0:
                tk.Label(fset3,text='Check list and press Run in Setting to update').grid(row=1,column=0)

            fset3.resizable(0, 0)
            if upd != None:
                upd.box1.list_update()

            fset2.destroy()

        def nores():                
            fset2.destroy()

        def only_median():
            mainwin.loop['text_mid'] = True
            yesres()

        mainwin.loop['text_mid'] = False
        fset2 = tk.Toplevel(rowin)
        fset2.resizable(0, 0)

        mes = tk.Text(fset2, height=5,width = 55, borderwidth=0,
        font=('TkDefaultFont'),bg=rowin.cget('bg'), relief='flat')

        mes.insert(1.0,"Search for dates in text outside of brackets."
        "\nDates that deviates too much from the median will be filtered."                   
        """\nExpect a "few" amount of errors."""
        "\n*Can also only keep max 3 filtered dates:\n  (lowest,closest to the median and highest)."
        "\n\n\t\t           Are you sure?") 
        mes.grid(row=0,column=0,columnspan=3,sticky="w")
        mes.configure(state="disabled")
        fset2.columnconfigure(0, weight=1)
        fset2.columnconfigure(2, weight=1)
        tk.Button(fset2,text='Yes',bg= 'white',relief='ridge',command=yesres).grid(row=1,column=0,sticky="e")
        tk.Button(fset2,text='No',bg= 'white',relief='ridge',command=nores).grid(row=1,column=1,sticky="e")
        tk.Button(fset2,text='*Only max 3 dates',bg= 'white',
        relief='ridge',command=only_median).grid(row=1,column=2,sticky="w")

    def save_wiki(self,dul=None):

        def l1_date(texurl):

            def loop_list():
                if len(mainwin.loop['links']) == 0:
                    la1.config(text=la1text) 
                elif len(mainwin.loop['links']) > 0:
                    count = len(mainwin.loop['links'])*(countstep/1000)
                    l = mainwin.loop['links'].pop()
                    la1.config(text=f":({count:.0f}s) {l}")
                    l1_date(l)                
                    fset.after(countstep,lambda:loop_list())  

            def loop_wiki(seccheck = None):
                titleser = unquote(urlt).replace('_',' ')
                listtitle = set()               
                with open('infowiki.json', 'r') as jr:
                    f = json.load(jr)

                    if mainwin.loop['looptext'] == False:
                        for y in f['wiki']['data']:
                            listtitle.add(y['page']['title'])
                    else:
                        for y in f['wiki']['data']:
                            if y['page']['infobox'] != []:
                                listtitle.add(y['page']['title'])

                    for x in f['wiki']['data']:
                        if x['page']['title'] == titleser:                           
                            mainwin.loop['links'] = list(set([x for x in x['page']['links'] if x != texurl \
                                and x not in listtitle and "File:" not in x and "file:" not in x and "Image:" not in x \
                                and "image:" not in x and "pecial:" not in x and "ser talk:" not in x]))
                            break

                if mainwin.loop['links'] != []:
                    if seccheck != None:
                        fis1 = 0
                        fis2 = len(seccheck)

                        if mainwin.loop['sec1'] != '':
                            stringsec1 = (f'==%s=='%mainwin.loop['sec1']).encode('utf-8')
                            stringsec2 = (f'== %s =='%mainwin.loop['sec1']).encode('utf-8')  
                            fis11 = seccheck.find(stringsec1)
                            fis12 = seccheck.find(stringsec2)

                            if fis11 != -1 and fis12 != -1 and fis11 > fis12:
                                fis1 = fis12                                
                            elif fis11 != -1:
                                fis1 = fis11
                            elif fis12 != -1:
                                fis1 = fis12

                        if mainwin.loop['sec2'] != '':
                            stringsec1 = (f'==%s=='%mainwin.loop['sec2']).encode('utf-8')
                            stringsec2 = (f'== %s =='%mainwin.loop['sec2']).encode('utf-8') 
                            fis21 = seccheck.find(stringsec1)
                            fis22 = seccheck.find(stringsec2)

                            if fis21 != -1 and fis22 != -1 and fis21 > fis22:
                                fis2 = fis22
                            elif fis21 != -1:
                                fis2 = fis21
                            elif fis22 != -1:
                                fis2 = fis22
                            
                            if  mainwin.loop['sec1'] != '' and fis1 > fis2:
                                if fis21 != -1 and fis22 == -1:
                                    fis2 = seccheck.rfind(stringsec1)
                                elif fis21 == -1 and fis22 != -1:
                                    fis2 = seccheck.rfind(stringsec2)
                                if fis1 > fis2:
                                    fis2 = len(seccheck)

                        newlinklist = set()
                        for z in mainwin.loop['links']:
                            linkstring = f'[[{z}'
                            fis3 = seccheck.find(linkstring.encode('utf-8'),fis1,fis2)
                            if fis3 != -1:
                                if fis1 <= fis3 <= fis2:
                                    newlinklist.add(unescape(unescape(z)))
                        mainwin.loop['links'] = list(newlinklist)
                    else:
                        mainwin.loop['links'] = [unescape(unescape(x)) for x in mainwin.loop['links']]
                        
                    la1.config(text=':Busy')
                    del seccheck                
               
                if mainwin.loop['loop1'] == True:
                    but1.config(text='On')
                    check_secbut()
                elif mainwin.loop['loop1'] == False:
                    but1.config(text='Off')
                    check_secbut()

                if mainwin.loop['links'] != []:
                    loop_list()
                elif mainwin.loop['links'] == []:
                    la1.config(text=la1text)

            urlt = texurl.strip().replace('https://en.wikipedia.org/wiki/','')

            if urlt.startswith('https://en.wikipedia.org/wiki/') == True:
                urlt = urlt.replace('https://en.wikipedia.org/wiki/','')
            if urlt == '':
                return            
                
            urlcom = "https://en.wikipedia.org/wiki/Special:Export/"+ quote(unquote(urlt).replace(' ','_'))
            try:
                xmlp = urlopen(urlcom)
                xml_content = xmlp.read()
                xml_content = point.redirect_title('nope',xml_content,urlt)
                urlt = xml_content[1].strip()
                xml_content = xml_content[0]

                if mainwin.loop['text'] and mainwin.loop['loop1']:
                    mainwin.loop['looptext'] = True
                    file_check = os.path.isfile('infowiki.json')
                    if file_check:
                        with open('infowiki.json', 'r') as jr:
                            f = json.load(jr)
                            mainwin.loop['len_data'] = len(f['wiki']['data'])
                    else:
                        mainwin.loop['len_data'] = 0

                if mainwin.loop['loop1'] == True:
                    meta_text = f"URL(Loop):en.wiki:{urlt}"
                else:
                    meta_text = f"URL:en.wiki:{urlt}"

                alone(xml_content,metat=meta_text)
                self.datejson('infowiki.json')
                if dul != None:
                    dul.box1.list_update()

                l11.config(fg = "green")
                fset.after(800,lambda:l11.config(fg = "black"))

                if mainwin.loop['looptext']:
                    text_loop(xml_content)

                if mainwin.loop['loop1'] == True:
                    mainwin.loop['loop1'] = False
                    if mainwin.loop['sec1'] != '' or mainwin.loop['sec2'] != '':          
                        loop_wiki(xml_content)
                    else:
                        loop_wiki()

            except:
                l11.config(fg = "red") 
                fset.after(800,lambda:l11.config(fg = "black"))
                
        def loopsure():            
            if mainwin.loop['loop1'] == False:

                def yesres():
                    mainwin.loop['loop1'] = True
                    but1.config(text='On')
                    check_secbut()
                    fset2.destroy()

                def nores():
                    mainwin.loop['loop1'] = False
                    but1.config(text='Off')
                    fset2.destroy()

                fset2 = tk.Toplevel(fset)
                fset2.resizable(0, 0)
                mes = tk.Text(fset2, height=8, width= 58, borderwidth=0,
                font=('TkDefaultFont'),bg=fset.cget('bg'), relief='flat')
                
                mes.insert(1.0,"Large pages can contain hundreds of links to other articles."
                "\nThere will be a 1-second delay between each article,\nto make sure Wikipedia servers aren't overburdened."
                "\n\nPlease DO NOT alter the delay,"
                "\nat worst Wikipedia can block your IP address."
                "\n\n\t\t\tAre you sure?") 
                mes.grid(row=0,column=0,columnspan=2,sticky="w")
                mes.configure(state="disabled")
                tk.Button(fset2,text='Yes',bg= 'white',relief='ridge',command=yesres).grid(row=1,column=0,sticky="e")
                tk.Button(fset2,text='No',bg= 'white',relief='ridge',command=nores).grid(row=1,column=1,sticky="w")                
            elif mainwin.loop['loop1'] == True:
                mainwin.loop['loop1'] = False
                but1.config(text='Off')
                check_secbut()

        def check_secbut():
            if mainwin.loop['loop1'] == False:
                mainwin.loop['sec1'] = ''
                mainwin.loop['sec2'] = ''                
                but3.grid_forget()
                but4.grid_forget()

            elif mainwin.loop['loop1'] == True:
                but3.grid(row=3,column=0,sticky="w")
                but4.grid(row=4,column=1,sticky="e")
                if mainwin.loop['sec1'] != '' or mainwin.loop['sec2'] != '':
                    but3.config(text='Between section: On')
                else:
                    but3.config(text='Between section: Off')

                if mainwin.loop['text'] == True:
                    but4.config(text='Search linked pages: On')
                else:
                    but4.config(text='Search linked pages: Off')

            if mainwin.loop['text'] == False:
                mainwin.loop['text_mid'] = False
                mainwin.loop['text_info'] = False
                mainwin.loop['len_data'] = None
                mainwin.loop['looptext'] = False
            
        def section():

            def ent1(inp):
                mainwin.loop['sec1'] = inp
                if inp != '':
                    l2a1.config(text=f'== {inp} ==')
                elif inp == '':
                    l2a1.config(text=inp)
                check_secbut()  

            def ent2(inp):
                mainwin.loop['sec2'] = inp
                if inp != '':
                    l2a2.config(text=f'== {inp} ==')
                elif inp == '':
                    l2a2.config(text=inp)
                check_secbut()

            fset2 = tk.Toplevel(fset)
            fset2.columnconfigure(1, weight=1)
            fset2.columnconfigure(3, weight=1)
            tk.Label(fset2,text="Press enter to confirm").grid(row=0,column=0,sticky="w")
            tk.Label(fset2,text="Example: from |List of Roman emperors| Between section:"
            "|364–392: Valentinian dynasty| and |Eastern Emperors|").grid(row=1,column=0,columnspan=4,sticky="w")
            tk.Label(fset2,text="Between section:").grid(row=2,column=0,sticky="e")
            e1 =tk.Entry(fset2,width=40)
            e1.bind("<Return>", lambda nope:ent1(e1.get()))    
            e1.grid(row=2,column=1,sticky="we")            
            e1.insert(0,mainwin.loop['sec1'])
            tk.Label(fset2,text="and").grid(row=2,column=2)
            e2 =tk.Entry(fset2,width=40)
            e2.bind("<Return>", lambda nope:ent2(e2.get()))    
            e2.grid(row=2,column=3,sticky="we")
            e2.insert(0,mainwin.loop['sec2'])
            l2a1 = tk.Label(fset2)
            l2a1.grid(row=3,column=1,sticky="w")
            l2a2 = tk.Label(fset2)
            l2a2.grid(row=3,column=3,sticky="w")

        def ask_text_loop():
            if mainwin.loop['text'] == False:                

                def nores():
                    mainwin.loop['text'] = False
                    mainwin.loop['text_mid'] = False
                    mainwin.loop['text_info'] = False
                    mainwin.loop['len_data'] = None
                    mainwin.loop['looptext'] = False
                    but4.config(text='Search linked pages: Off')
                    check_secbut()
                    fset2.destroy()

                def res1():
                    mainwin.loop['text'] = True
                    mainwin.loop['text_mid'] = True
                    mainwin.loop['text_info'] = True
                    but4.config(text='Search linked pages: On')
                    check_secbut()
                    fset2.destroy()

                def res2():
                    mainwin.loop['text'] = True
                    mainwin.loop['text_mid'] = False
                    mainwin.loop['text_info'] = True
                    but4.config(text='Search linked pages: On')
                    check_secbut()
                    fset2.destroy()

                def res3():
                    mainwin.loop['text'] = True
                    mainwin.loop['text_mid'] = True
                    mainwin.loop['text_info'] = False
                    but4.config(text='Search linked pages: On')
                    check_secbut()
                    fset2.destroy()

                def res4():
                    mainwin.loop['text'] = True
                    mainwin.loop['text_mid'] = False
                    mainwin.loop['text_info'] = False
                    but4.config(text='Search linked pages: On')
                    check_secbut()
                    fset2.destroy()

                fset2 = tk.Toplevel(fset)
                fset2.resizable(0, 0)
                mes = tk.Text(fset2, height=8, width= 58, borderwidth=0,
                font=('TkDefaultFont'),bg=fset.cget('bg'), relief='flat')

                mes.insert(1.0,"Search for dates in text(for every linked page) outside of brackets."
                "\nDates that deviates too much from the median will be filtered."                   
                """\nExpect a "few" amount of errors."""
                "\n*Can also only keep max 3 filtered dates:\n  (lowest,closest to the median and highest)."
                "\n\n\t\t           Are you sure?")  
                mes.grid(row=0,column=0,columnspan=1,sticky="w")
                mes.configure(state="disabled")                
                tk.Button(fset2,text='No',bg= 'white',relief='ridge',command=nores).grid(row=1,column=0)
                tk.Button(fset2,text='*Max 3 dates, if there are no infobox dates',
                bg= 'white',relief='ridge',command=res1).grid(row=2,column=0)
                tk.Button(fset2,text='All dates, if there are no infobox dates',
                bg= 'white',relief='ridge',command=res2).grid(row=3,column=0)
                tk.Button(fset2,text='*Max 3 dates for every page',
                bg= 'white',relief='ridge',command=res3).grid(row=4,column=0)
                tk.Button(fset2,text='All dates for every page',
                bg= 'white',relief='ridge',command=res4).grid(row=5,column=0)

            elif mainwin.loop['text'] == True:
                mainwin.loop['text'] = False
                but4.config(text='Search linked pages: Off')
                check_secbut()

        def text_loop(read):
            if mainwin.loop['text'] and mainwin.loop['len_data'] != None:
                with open('infowiki.json', 'r') as jr:
                    f = json.load(jr)
                    len_data2 = len(f['wiki']['data'])

                    if mainwin.loop['len_data'] + 1 == len_data2:
                        mainwin.loop['len_data'] = len_data2                      

                        if (mainwin.loop['text_info'] and f['wiki']['data'][-1]['page']['infobox'] == []) or \
                            mainwin.loop['text_info'] == False:
                                
                            posart = f['wiki']['data'][-1]['page']['pos']
                            title = f['wiki']['data'][-1]['page']['title']
                            fis1 = read.rfind(b'</text>')
                            fis2 = read.find(b'<text')
                            fis3 = read.find(b'>',fis2+5,fis1)
                            if fis1 != -1 and fis2 != -1 and fis3 != -1:
                                read = read[fis2:fis1+7].decode('utf-8','replace')

                                mainwin.text_an('nope',read,title,posart)                            

        def text_date(texurl):
            urlt = texurl.strip()
            if urlt == '':
                return
                
            urlcom = "https://en.wikipedia.org/wiki/Special:Export/"+ quote(unquote(urlt).replace(' ','_'))
            try:
                xmlp = urlopen(urlcom)
                xml_content = xmlp.read()
                xml_content = point.redirect_title('nope',xml_content,urlt)
                urlt = xml_content[1].strip()
                xml_content = xml_content[0]
                if xml_content:
                    fis1 = xml_content.rfind(b'</text>')
                    fis2 = xml_content.find(b'<text')
                    fis3 = xml_content.find(b'>',fis2+5,fis1)
                    if fis1 != -1 and fis2 != -1 and fis3 != -1:
                        xml_content = xml_content[fis2:fis1+7].decode('utf-8','replace')
                        self.ask_textan(xml_content,urlt,fset,(0,len(xml_content)),upd=dul)
                        l11.config(fg = "green")
                        fset.after(800,lambda:l11.config(fg = "black"))
                    else:
                        raise Exception()
                else:
                    raise Exception()           
            except:
                l11.config(fg = "red") 
                fset.after(800,lambda:l11.config(fg = "black")) 

        try:
            self.fset.focus()
            return
        except Exception:
            pass 

        mainwin.loop['links'] = []
        mainwin.loop['len_data'] = None
        mainwin.loop['looptext'] = False        
        countstep = 1100         
        fset = tk.Toplevel(self)
        self.fset = fset       
        fset.columnconfigure(1, weight=1)
        tk.Label(fset,text="Press enter to confirm").grid(row=0,column=0,sticky="e")
        l11 = tk.Label(fset,text="Title of the wikipedia page:")
        l11.grid(row=1,column=0,sticky="e")
        tk.Label(fset,text="Data will be saved to infowiki.json").grid(row=0,column=1)  
        l1 =tk.Entry(fset,width=50)
        l1.bind("<Return>", lambda nope:l1_date(l1.get()))    
        l1.grid(row=1,column=1,sticky="we")
        la1text = ":Add all the wiki pages linked in the requested article (1s delay)"  
        la1 = tk.Label(fset,text=la1text)
        la1.grid(row=3,column=1,sticky="w")
        but1 = tk.Button(fset,text='Off',bg= 'white',relief='ridge',command=lambda:loopsure()) 

        if mainwin.loop['loop1'] == True:
            but1.config(text='On')

        but1.grid(row=3,column=0,sticky="e")
        but3 = tk.Button(fset,text='Between section: Off',
        bg= 'white',relief='ridge',command=lambda:section())
        but4 = tk.Button(fset,text='Search linked pages: Off',
        bg= 'white',relief='ridge',command=lambda:ask_text_loop())  
        check_secbut()
        la2 = tk.Label(fset,text=':For a wiki page without infobox')
        la2.grid(row=4,column=1,sticky="w")
        but2 = tk.Button(fset,text='Search for dates in text',
        bg= 'white',relief='ridge',command=lambda:text_date(l1.get())) 
        but2.grid(row=4,column=0,sticky="e")

    def json_keyword(self):

        def se1():
            if l1.get():
                mainwin.search_term.append(l1.get().lower())
                lis1.list_update()   

        def se3():
            if l1.get():
                mainwin.ban_term.append(l1.get().lower())
                lis2.list_update()

        fset = tk.Toplevel(self)
        l11 = tk.Label(fset,text="Keyword:")
        l11.grid(row=0,column=0,sticky="w")
        l1 =tk.Entry(fset,width=30)        
        l1.grid(row=0,column=1,columnspan=3,sticky="we")
        fset.columnconfigure(0,weight=1)
        fset.columnconfigure(3,weight=1)
        fset.rowconfigure(2,weight=1)
        l21 = tk.Label(fset,text="Add keyword:")
        l21.grid(row=1,column=0,sticky="w")
        but1 = tk.Button(fset,text='Add',bg='white',relief='solid',command=se1)
        but1.grid(row=1,column=1)    
        but3 = tk.Button(fset,text='Remove',bg='white',relief='solid',command=se3) 
        but3.grid(row=1,column=3)    
        lis1 = listbox_frame(fset,stand=2,dlist=mainwin.search_term)
        lis1.grid(row=2,column=0,columnspan=3,sticky="nsew")
        lis2 = listbox_frame(fset,stand=2,dlist=mainwin.ban_term)
        lis2.grid(row=2,column=3,sticky="nsew") 

    def box_keyword(self):

        def se1():
            if l1.get():
                mainwin.box_term['search'].append(l1.get().lower())
                lis1.list_update()

        def se3():
            if l1.get():
                mainwin.box_term['ban'].append(l1.get().lower())
                lis2.list_update()

        fset = tk.Toplevel(self)
        l10 = tk.Text(fset, height=1, borderwidth=0,font=('TkDefaultFont'),bg=fset.cget('bg'), relief='flat')
        l10.insert(1.0," Example: infobox military conflict.     If the list is empty all templates will be searched")
        l10.grid(row=0,column=0,columnspan=4,sticky="nsew")
        l10.configure(state="disabled")
        l11 = tk.Label(fset,text="Template:")
        l11.grid(row=1,column=0,sticky="w")
        l1 =tk.Entry(fset,width=30)        
        l1.grid(row=1,column=1,columnspan=3,sticky="we")
        fset.columnconfigure(0,weight=1)
        fset.columnconfigure(3,weight=1)
        fset.rowconfigure(3,weight=1)
        l21 = tk.Label(fset,text="Add filter:")
        l21.grid(row=2,column=0,sticky="w")
        but1 = tk.Button(fset,text='Search only',bg='white',relief='solid',command=se1)
        but1.grid(row=2,column=1)    
        but3 = tk.Button(fset,text='Remove',bg='white',relief='solid',command=se3)
        but3.grid(row=2,column=3)    
        lis1 = listbox_frame(fset,stand=2,dlist=mainwin.box_term['search'])
        lis1.grid(row=3,column=0,columnspan=3,sticky="nsew")
        lis2 = listbox_frame(fset,stand=2,dlist=mainwin.box_term['ban'])
        lis2.grid(row=3,column=3,sticky="nsew")   

    def listbox_data(self):
        fset = tk.Toplevel(self)    
        listbox_frame(fset,stand=1,dlist=mainwin.data_insert).grid(row=0,column=0,sticky="nsew")
        fset.columnconfigure(0, weight=1)
        fset.rowconfigure(0, weight=1)
        
    def lisbox_nodate(self):
        fset = tk.Toplevel(self)    
        scrollbar_l = tk.Scrollbar(fset, orient='vertical')
        lb = tk.Listbox(fset,yscrollcommand=scrollbar_l.set)
        scrollbar_l.config(command=lb.yview)
        scrollbar_l.grid(row=0,column=1,sticky="ns")  
        lb.grid(row=0,column=0,sticky="nsew")
        fset.columnconfigure(0, weight=1)
        fset.rowconfigure(0, weight=1)
        fset.geometry('500x150')     
        for i,x in enumerate(mainwin.nodate):
            lb.insert(i,f"{x['title']} | {x}")

    def datedata(self,raw):        
        list_dub_tot = []    
        z = finddate.date_find(raw['date'])
        y2 = mainwin.y2                                                                    
        for x in z:                            
            if len(x) < 1:
                continue
            spec = None  

            for y in x:
                y['title'] = raw['title']
                y['pos'] = raw['pos']                                
                y['key'] = raw['key']
                y['every'] = raw['every']                     
                if y['y'] == None:                               
                    mainwin.nodate.append(y)
                    mainwin.nodate = [k for i,k in enumerate(mainwin.nodate) if k not in mainwin.nodate[i+1:]]
                    continue
                elif (len(str(int(y['y'][0]))) > 4 and y['y'][0] > 0 or y['y'][0] > 3000):                                
                    mainwin.nodate.append(y)
                    mainwin.nodate = [k for i,k in enumerate(mainwin.nodate) if k not in mainwin.nodate[i+1:]]
                    continue

                if y['d'] == None:
                    y['d'] = [None]
                    days = 1
                else:
                    days = y['d'][0]
                    if y['m'] == None:
                        mainwin.nodate.append(y) 

                mont = 0
                if y['m'] != None:
                    if str(y['m'][0]).isdigit() == False:
                        if y['m'][0] in y2:
                            mont = y2.index(y['m'][0])                        
                            
                    else:                
                        mont = max(0,y['m'][0]-1)
                        y['m'][0] = y2[y['m'][0]-1] 

                else:
                    y['m'] = [None]

                mont_days = mainwin.y3[mont][0]
                sum_days = mont_days + days + (y['y'][0]*365)                                                                     
                y['tot']=sum_days
                y['spec'] = [spec]
                if y['set'] != None:                                    
                    count = 0
                    if y['set'] in mainwin.specs1:
                        count = mainwin.specs1[y['set']] + 1
                        mainwin.specs1[y['set']] = count
                    else:
                        mainwin.specs1[y['set']] = 0

                    spec = f"{y['set']}{count}"                                
                    y['spec'].append(spec)                                
                else:                                                                            
                    y['spec'].append(spec)                                 
                    spec = None 

                list_dub_tot.append(y)    

        return list_dub_tot

    def datejson(self,read):

        def final2(time_raw):
            final = self.datedata(time_raw)                       
            for x in final:
                if 'death' in x['key']:
                    if len(list_dub_tot) > 1:                   
                        if x['tot'] > list_dub_tot[-1]['tot'] and \
                            ((x['spec'][1] == None and list_dub_tot[-1]['spec'][0] == None) or \
                            ('brace' in str(x['spec'][1]) and 'brace' in str(list_dub_tot[-1]['spec'][0]))):
                            list_dub_tot[-1]['key'] = list_dub_tot[-1]['key'].replace('death','birth')
                            x['spec'][0] = list_dub_tot[-1]['spec'][1]

                        elif x['tot'] < list_dub_tot[-1]['tot'] and \
                            ((x['spec'][0] == None and list_dub_tot[-1]['spec'][1] == None) or \
                            ('brace' in str(x['spec'][0]) and 'brace' in str(list_dub_tot[-1]['spec'][1]))):
                            x['key'] = x['key'].replace('death','birth')
                            list_dub_tot[-1]['spec'][0] = x['spec'][1]
                    
                list_dub_tot.append(x)
                list_dub_days.append(x['tot'])  

        filebase = os.path.basename(read)
        val = 0   

        with open(read, 'r') as jr:    
            f = json.load(jr)   
            ground = 100/len(f['wiki']['data']) 
            mainwin.data_insert[filebase]=[]

            if self.frame_begin.winfo_exists() == 0:            
                self.pb.place(x=0,y=0) 

            for j1 in f['wiki']['data']:
                mainwin.specs1 = {}    
                for jy in j1['page']['infobox']:
                    if mainwin.box_term['search']:
                        temp = jy['template'].lower()
                        sbox = False
                        for sb in mainwin.box_term['search']:
                            if sb == temp:
                                sbox = True
                                break
                        if sbox == False:
                            continue

                    if mainwin.box_term['ban']:
                        if jy['template'].lower() in mainwin.box_term['ban']:
                            continue 

                    list_dub_days = []
                    list_dub_tot = []               
                    com_yd = {}                                          
                    for k in jy:                    
                        new_k = k.strip().lower()
                        new_k1 = re.sub(r"\d|[^a-zA-Z]",' ',new_k).split()
                        if new_k1 == []:
                            continue 

                        try:                        
                            for b in mainwin.ban_term:
                                if b in new_k1:
                                    raise Exception()
                            if 'years' == new_k1[0]:
                                if len(new_k1) > 1:
                                    if 'in' == new_k1[1] or 'of' == new_k1[1]:
                                        raise Exception()                                        
                        except:
                            continue

                        if any((ser == new_k1[0] or ser == new_k1[-1]) for ser in mainwin.search_term) and jy[k] !="":
                            t1 = (jy[k])
                            if t1.strip() == '|':
                                continue
                            time_raw = {'date':t1,'title':j1['page']['title'],
                            'pos':j1['page']['pos'],'key':new_k,'every':[k,t1]}

                            if 'year' in new_k or 'date' in new_k or 'start' in new_k or 'end' in new_k:
                                key_yd = None
                                if 'year' in new_k:
                                    key_yd = 'year'                        
                                elif 'date' in new_k:
                                    key_yd = 'date' 
                                elif 'start' in new_k:
                                    key_yd = 'start'
                                elif 'end' in new_k:
                                    key_yd = 'end'
                                rem = new_k.replace(f'{key_yd}','')
                                if len(rem) > 2:                                    
                                    if rem not in com_yd:
                                        com_yd[rem] = {}
                                                               
                                    com_yd[rem][key_yd] = time_raw
                                    continue
                            final2(time_raw)

                    if '_start' in com_yd and '_end' in com_yd:
                        if 'year' in com_yd['_start'] and 'year' in com_yd['_end']:
                            start_end = {}
                        else:
                            start_end = None

                    else:
                        start_end = None

                    for rem in com_yd:
                        if 'date' in com_yd[rem] and 'year' in com_yd[rem]:
                            t1 = (com_yd[rem]['date']['date'] + ' ' \
                                + com_yd[rem]['year']['date']).replace('\n|','').replace('\n','')
                            time_raw = com_yd[rem]['date']
                            time_raw['every'][1] = t1
                            time_raw['date'] = t1
                            if start_end != None and (rem == '_end' or rem == '_start'):
                                start_end[rem] = time_raw
                            else:                                 
                                final2(time_raw)
                                
                        else:
                            if 'start' in com_yd[rem] and 'end' in com_yd[rem]:
                                com_yd[rem]['end']['date'] = re.sub(r'\A\(([^()]+)\)\Z',r'\g<1>',
                                com_yd[rem]['end']['date'])

                                t1 = (com_yd[rem]['start']['date'] + ' - ' \
                                    + com_yd[rem]['end']['date']).replace('\n|','').replace('\n','')                            
                                com_yd[rem]['start']['every'][1] = t1
                                com_yd[rem]['start']['date'] = t1
                                com_yd[rem]['start']['key'] = rem.replace('  ',' ')
                                del com_yd[rem]['end']

                            if start_end != None and (rem == '_end' or rem == '_start'):
                                start_end[rem] = com_yd[rem]['year']
                            else:
                                for z in com_yd[rem]:
                                    time_raw = com_yd[rem][z]
                                    final2(time_raw)

                    if start_end != None:
                        start_end['_end']['date'] = re.sub(r'\A\(([^()]+)\)\Z',r'\g<1>',start_end['_end']['date'])                        
                        t1 = (start_end['_start']['date'] + ' - ' \
                            + start_end['_end']['date']).replace('\n|','').replace('\n','')
                        time_raw = start_end['_start']
                        time_raw['every'][1] = t1
                        time_raw['date'] = t1                        
                        time_raw['key'] = 'date'
                        final2(time_raw)  

                    dub = []
                    for i, su in enumerate(list_dub_tot):
                        if su['tot'] in list_dub_days[0:i] + list_dub_days[i+1:] and i not in dub:
                            for i2, su2 in enumerate(list_dub_tot):
                                if su2['tot'] == su['tot'] and i2 != i and su2['key'] == su['key'] and i2 not in dub:
                                    f1 = False
                                    if su['spec'][0] != None and su['spec'][1] != None:
                                        f1 = True
                                        if su2['spec'][0] == None and su2['spec'][1] == None:
                                            dub.append(i2)
                                    elif su['spec'][0] == None and su['spec'][1] != None:
                                        for su3 in list_dub_tot:
                                            if su3['spec'][0] == su['spec'][1] and su3['tot'] != su['tot']:
                                                f1 = True
                                                break
                                    elif su['spec'][0] != None and su['spec'][1] == None:
                                        for su3 in list_dub_tot:
                                            if su3['spec'][1] == su['spec'][0] and su3['tot'] != su['tot']:
                                                f1 = True
                                                break

                                    if (su['spec'][0] == None and su['spec'][1] == None) or f1 == False:
                                        dub.append(i)

                    for d in sorted(dub,reverse=True):
                        del list_dub_tot[d]
                        del list_dub_days[d]                    
                    mainwin.data_insert[filebase].extend(list_dub_tot)  
                mainwin.specs1 = {}
                val = val + ground

                if val > 1:
                    self.pb["value"] += val
                    val = 0        
                    self.pb.update_idletasks()

        if self.frame_begin.winfo_exists() == 0:            
            self.pb.place_forget()

        self.pb["value"] = 0         

    def mainbut(self):       
        mainwin.ruall = []   

        if self.frame_begin.winfo_exists() == 0:
            self.w.delete("all")                
            self.pb.place(x=0,y=0)            
            for v1 in point.connt:
                for v2 in point.connt[v1]['cor']:
                    del v2        
            self.reset() 

        for dt in mainwin.data_insert:
            mainwin.ruall.extend(mainwin.data_insert[dt])
            mainwin.data_insert[dt] = [x.copy() for x in mainwin.data_insert[dt]]                    
        
        mainwin.ruall = [k for i,k in enumerate(mainwin.ruall) if k not in mainwin.ruall[i+1:]] 
        mainwin.ruall = sorted(mainwin.ruall, key = lambda i: i['tot'])
        
        xcor = 0
        for i,k in enumerate(mainwin.ruall):
            if i > 0:            
                diflis = mainwin.ruall[i]['tot'] - mainwin.ruall[i-1]['tot']
                if mainwin.ruall[i]['tot'] > 0 and mainwin.ruall[i-1]['tot'] < 0:
                    diflis -= 365
                    xcor += 10
                    mainwin.ruall[i]['xcor']=[diflis,xcor,1]                
                    continue
            else:        
                diflis = 0 

            if diflis == 0 and i!= 0:
                mainwin.ruall[i]['xcor']=[diflis,xcor,4]
                continue   
                       
            if diflis > (365*mainwin.length_line['year']):       
                xcor += (10)
                mainwin.ruall[i]['xcor']=[diflis,xcor,0]  
            else:            
                xcor += diflis 
                stand = 2
                if diflis > (365*(mainwin.length_line['month']/12)):
                    stand = 3
                    xcor = xcor - diflis + (diflis*(1/mainwin.length_line['skip']))
                mainwin.ruall[i]['xcor']=[diflis,xcor,stand]

        self.main_time()
        
    def main_time(self):                             
        begin = 0
        remain = 0
        mainl = mainwin.length_line['skip']
        dayyear1 = mainwin.y3 + [[365,'jan']]
        val = 0
        groundlen = len(mainwin.ruall)
        yeart = None
        dayt = None

        if groundlen == 0:
            ground = 100
        else:
            ground = 100/groundlen

        for x in mainwin.ruall:                
            gap = x['xcor'][0]
            stand = x['xcor'][2]
            dayt2 = dayt 

            if (gap == 0 and stand != 4) or stand == 0 or stand == 1:                  
                dayyear = dayyear1.copy()
                year, remain = divmod(x['tot'],365)        
                for m1 in dayyear1:            
                    if remain > m1[0]:
                        del dayyear[0]                
                    else:
                        break
                begin = x['xcor'][1]*mainl 
                self.w.create_line(begin, 516, begin, 529)           
                self.w.create_text(begin,490,text=f"{x['y'][0]}",tag="year3",
                font=('Helvetica',11,'bold'))
                yeart = int(begin + (tk.Label(None,text=f"{x['y'][0]}",
                font=('Helvetica',11,'bold')).winfo_reqwidth()/2))

                if x['d'][0] != None:
                    self.w.create_text(begin,540,text=f"{x['d'][0]}",tag="day1")
                    dayt = int(begin + (tk.Label(None,text=f"{x['d'][0]}").winfo_reqwidth()/2))

                if x['m'][0] != None:
                    self.w.create_text(begin,506,text=f"{x['m'][0]}",tag="month1")

            if stand == 0:
                xc = begin - 6*mainl
                yc = 520
                self.w.create_text(begin-5*mainl,yc+30,text=f"{(gap/365):.2f}")
                self.w.create_text(begin-5*mainl,yc+48,text="years",tag="year1")
                self.w.create_line(xc-10, yc, xc, yc) 
                self.w.create_line(xc, yc, xc +10, yc+10) 
                self.w.create_line(xc +10, yc+10, xc +20, yc-10) 
                self.w.create_line(xc +20, yc-10, xc +30, yc)
                self.w.create_line(xc +30, yc, xc +40, yc)        
                chatime = False                     
            elif stand == 1:            
                self.w.create_oval(x['xcor'][1]*mainl-(5*mainl)-20,520-20,
                x['xcor'][1]*mainl-(5*mainl)+20,520+20, width=2)
                       
                self.w.create_text(x['xcor'][1]*mainl-(5*mainl),550,text=f"{(gap/365):.2f}")
                self.w.create_text(x['xcor'][1]*mainl-(5*mainl),568,text="years",tag="year1")
                chatime = False                    
            elif stand == 2 or stand == 3:        
                chatime = True
                self.w.create_line(x['xcor'][1]*mainl, 516, x['xcor'][1]*mainl, 529) 

                if x['d'][0] != None:               
                    if x['d'][0] < 5:                
                        self.w.create_text((x['xcor'][1]*mainl)+5-x['d'][0],540,text=f"{x['d'][0]}",tag="day1")
                        dayt = int((x['xcor'][1]*mainl)+5-x['d'][0] \
                            + (tk.Label(None,text=f"{x['d'][0]}").winfo_reqwidth()/2))
                    else:                    
                        if x['xcor'][0] < 2:
                            self.w.create_text(x['xcor'][1]*mainl,540,text=f"{x['d'][0]}",tag="day1")
                        else:
                            self.w.create_text(x['xcor'][1]*mainl,540,text=f"{x['d'][0]}",tag="day2")
                        dayt = int(x['xcor'][1]*mainl + (tk.Label(None,text=f"{x['d'][0]}").winfo_reqwidth()/2))  

            if chatime == True:
                self.w.create_line(begin+3, 520, x['xcor'][1]*mainl -3, 520)           
                if stand == 3:
                    end = gap
                    length = 1                
                else:
                    end = gap
                    length = mainl 

                for x2 in range(0,int(end+1)):                    
                    if length > 5:
                        self.w.create_line(begin+(x2*length), 516, begin+(x2*length), 529)                   
                    for mt in dayyear:
                        if int(remain) > mt[0]:                    
                            current = begin + ((x2)*length) 
                            step = current-4 
                            ldayl = 540

                            if dayt2:
                                if dayt2-20 <= current <= dayt2-3:
                                    ldayl = 534
                                dayt2 = None  

                            if mt[0] == dayyear1[12][0]:                                                        
                                remain = remain - 365
                                year += 1
                                yeart2 = int((step) - (tk.Label(None,text=f"{year:0.0f}",
                                font=('Helvetica',11,'bold')).winfo_reqwidth()/2))

                                hyear = 490
                                tagyear = "year3"

                                if yeart:                                      
                                    if yeart >= yeart2:
                                        tagyear = "year2"                                         
                                        hyear = 570
                                    elif yeart+75 >= yeart2:
                                        tagyear = "year4"

                                self.w.create_text(step+4,hyear,text=f"{year:0.0f}",
                                tag=tagyear,font=('Helvetica',11,'bold'))  

                                self.w.create_line(current, 515, current, ldayl)
                                self.w.create_text(step,550,text=f"{mt[1]}",
                                tag=f"month{stand}")  

                                dayyear = dayyear1.copy()   
                                del dayyear[0]
                                break  
                            else:                           
                                self.w.create_line(current, 515, current, ldayl)
                                if length == mainl:
                                    self.w.create_text(step,550,text=f"{mt[1]}",
                                    tag=f"month{stand}",font=('Helvetica',10,'bold'))
                                else: 
                                    self.w.create_text(step,550,text=f"{mt[1]}",
                                    tag=f"month{stand}")    

                                del dayyear[0]

                    if x2 != int(end):
                        remain += 1

                begin = x['xcor'][1]*mainl 
            val = val + ground
            if val > 1:
                self.pb["value"] += val
                val = 0        
                self.pb.update_idletasks()

        self.pb["value"] = 0        
        
        val = 0        
        for v in mainwin.ruall:        
            point(v,self.w)       
            val = val + ground        
            if val > 1:            
                self.pb["value"] += val
                val = 0        
                self.pb.update_idletasks()

        self.pb["value"] = 0
        self.pb.place_forget()
        self.pb.grid_forget()
        self.w.config(scrollregion=self.w.bbox("all"))

        if self.frame_begin.winfo_exists() == 1:
            self.w.config(background=mainwin.background_set['background_colour'])
            self.w.grid(row=0,column=0,padx=6,pady=1,columnspan=2,rowspan=2,sticky="nsew")
            self.setting.grid(row=1,column=0,sticky="ws")
            self.grid(row=0,column=0,sticky="nsew")
            self.scrollbarx.grid(row=2,column=0,columnspan=2,sticky="ew")        
            self.scrollbary.grid(row=0,column=2,rowspan=2,sticky="ns")            
            point.stindex={}
            self.ro.config(menu = self.menu_or)            
            self.w.xview_moveto(0)
            
        self.frame_begin.destroy()
        self.ro.resizable(1,1)
        self.ro.geometry('1200x650') 

def active():
    root = tk.Tk()
    root.title('Timeline')
    file_path = os.path.dirname(os.path.abspath(__file__))
    mainwin.pat = os.path.join(file_path,'enwiki-20190101-pages-articles-multistream.xml') #file name of xml wiki  
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.protocol('WM_DELETE_WINDOW', root.quit)
    mainwin(root).grid(row=0,column=0,sticky="nsew") 
    root.mainloop()

if __name__ == "__main__":         
    active()