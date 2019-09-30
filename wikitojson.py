import re
import json
import mmap
import io
import os
import time
from multiprocessing import Process, Pipe


#Write the founded values inside the function to 'infowiki.json'
#Variables - (pos1 = beginning of the article, pos2 = end of the article, f = text as bytes).
def an(pos1, pos2, f):
    end = pos2 - pos1
    beg = 0 
    ti1 = f.find(b'<title>',beg)
    ti2 = f.find(b'</title>',beg)

    if ti1 == -1 or ti2 == -1:
        return 

    title = f[ti1+len(b'<title>'):ti2].decode('utf-8', errors='ignore')
    if title.startswith('Module:') == True or title.startswith('Wikipedia:') == True:
        return

    print(title)
    new = {
        'page':{
            'pos':[pos1,pos2],
            'title':title,
            'length':len(f[beg:end]),
            'infobox':aninfo(beg, end, f),
            'links':links(beg, end, f)
            }
    }     
    with open('infowiki.json', 'r+') as jm:
        jm.seek(jm.seek(0,2) -3)
        jm.write(',')        
        json.dump(new, jm)
        jm.write(']}}')    

#Finds the postion between balanced variable p1 and p2.
#Variables - (sta = beginning of the search section, end = end of the search section, y = text,
#e = list of postion to ignore between the two values,
#out = string that while found between positions in list 'e' will ignore the given position).
def balance(sta, end, y, d, e, out): 
    q = sta 
    p1 = d[0]
    p2 = d[1]    
    z1 = []
    z2 = []    
    l = len(p1) 
    while True:
        fis1 = y.find(p1, q, end) 

        if fis1 != -1:
            inside = False            
            try:
                for x in e:                    
                    if x[0] <= fis1 < x[1]:                                    
                        inside = True                       
                        try:
                            if out in y[x[0]:x[0] + len(out) + 3]:                               
                                inside = False
                        except:
                            continue
                        break
            except TypeError:
                inside = False

            if inside == False:                                 
                z1.append(fis1)
        else:
            break

        q = fis1 + l
    q = sta
    l = len(p2)     
    while True:
        fis2 = y.find(p2, q, end)

        if fis2 != -1:
            inside = False            
            try:
                for x in e:                    
                    if x[0] <= fis2 < x[1]:                                    
                        inside = True                        
                        try:
                            if out in y[x[0]:x[0] + len(out) + 3]:                                
                                inside = False
                        except:
                            continue
                        break
            except TypeError:
                inside = False

            if inside == False:                               
                z2.append(fis2)

        else:
            break

        q = fis2 + l 
    new = []
    done = []    
    for x in z2:
        for y in z1[::-1]:
            if y < x and y not in done:
                if y == z1[0]:
                    new.insert(0,[y,x])                    
                else:
                    new.append([y,x])
                done.append(y) 
                break 

    return new 

#Search for links inside the text and ruturns a list of the links.
#Variables - (beg = beginning of the article, end = end of the article, s = text as bytes).
def links(beg, end, s):
    end = end - beg
    beg = 0    
    i = []
    search_link = [[b'[[',b']]'],[b'{{details|',b'}}'],[b'{{section link|',b'}}'],[b'{{slink|',b'}}']]
    for x in search_link:
        fis1 = 0
        fis2 = 0
        while True:
            fis1 = s.find(x[0], fis2, end)
            fis2 = s.find(x[1], fis1, end)

            if fis1 == -1 or fis2 == -1:            
                break

            fis1 += len(x[0])
            fis3 = s.find(b'|', fis1, fis2)
            fis4 = s.find(b'#', fis1, fis2)
            fis5 = s.find(b'&lt;', fis1, fis2)
            sor = []

            if fis3 != -1:
                sor.append(fis3)
            if fis4 != -1:
                sor.append(fis4)
            if fis5 != -1:
                sor.append(fis5)
            if sor:
                fisend = sorted(sor)[0]
            else:
                fisend = fis2

            fis6 = s.find(b'&gt;', fis1, fisend)
            if fis6 != -1:
                continue

            try:     
                i.append(s[fis1:fisend].decode('utf-8').strip())
            except:
                pass
    return i

#Search through the text for infoboxes and format it to a dictionary.
#It will first search for xml escape characters inside the text and there positions.
#With created "balance" function it will search where brackets of the infobox ends while ignoring the xml escape characters.
#Variables - (beg = beginning of the article, end = end of the article, s = text as bytes).
def aninfo(beg, end, s):    
    end = end - beg
    beg = 0
    i =[]    
    st = re.search(b'{{(.?|#invoke:)[iI]nfobox', s)

    if st:
        inb = st.start() + beg
        con1 = s.rfind(b'&lt;', beg, inb)
        if con1 != -1:
            con2 = s.rfind(b'&gt;', con1, inb)
            if con2 == -1:
                return []
        escape = balance(inb, end, s, [b'&lt;', b'&gt;'], [], None)
    else:        
        escape = []

    while st != None:        
        box ={}                           
        inbeg = s.rfind(b'{{', beg, inb + 2) 
        brace = balance(inbeg, end, s, [b'{{', b'}}'], escape, None)              
        inend = brace[0][1] + 2
        st = re.search(b'{{(.?|#invoke:)[iI]nfobox', s[inend:end])

        if st:
            inb = st.start() + inend
            con1 = s.rfind(b'&lt;', beg, inb)
            if con1 != -1:
                con2 = s.rfind(b'&gt;', con1, inb)
                if con2 == -1:
                    st = None

        rtem_list = []                           
        rtem1= s.find(b'|', inbeg, inend)
        if rtem1 != -1:
            rtem_list.append(rtem1)            
        rtem2= s.find(b'\n', inbeg, inend)
        if rtem2 != -1:
            rtem_list.append(rtem2)
        rtem3= s.find(b'}}', inbeg, inend)
        if rtem3 != -1:
            rtem_list.append(rtem3)
        rtem4= s.find(b'&lt;', inbeg, inend)
        if rtem4 != -1:
            rtem_list.append(rtem4)

        rtem = min(rtem_list)       
        i1 ={'template':s[inbeg+2:rtem].decode('utf-8').strip()}
        box.update(i1)
        escape1 = balance(inbeg, inend, s, [b'[[', b']]'], escape, None)
        escape_ref = balance(inbeg, inend, s, [b'&lt;ref', b'/ref&gt;'], [], None)
        escape2 = escape + brace[1:] + escape1 + escape_ref
        fis = balance(inbeg, inend, s, [b'|', b'='], escape2, b'nfobox')        
        for x in fis: 
            r = fis.index(x)
            try:
                if x[1] > fis[r+1][1]:
                    continue
            except IndexError:
                pass             
            er1 = s[x[0] + 1:x[1]].decode('utf-8', errors='ignore')
            try:
                er2 = s[x[1] + 1:fis[r+1][0]].decode('utf-8', errors='ignore').lower().strip()
            except IndexError:
                er2 = s[x[1] + 1:inend-2].decode('utf-8', errors='ignore').strip()                                  
            i2 = {er1:er2}                            
            box.update(i2)
        i.append(box)
        
    return i     

#Ask the user for a key search word and filter statements/words. 
def search():
    text_begin = """\
Search global keyword.\n
For information on what term too look for use https://en.wikipedia.org/wiki/Special:Export/Title_of_the_article.\n
For infoboxes search: nfobox, instead of Infobox,
wikipedia infobox can have either lower or uppercase I,
example: nfobox book (https://en.wikipedia.org/wiki/Special:Export/The_Book_of_the_New_Sun).\n
For links to other pages search: [[title, instead of [[title]],
example: [[Emperor Huizong of Song.""" 
    print(text_begin)
    while True:        
        sear = []
        print('_'*110)             
        glo = input('\nGlobal:')
        sear.append(glo)
        while True:
            print('Ignore upper and lower case in filter (not global keyword) y = yes, n = no,')
            nex = input('next?:')
            
            if nex == 'n':
                sear.append('ignore case = n')
                break
            elif nex == 'y':
                sear.append('ignore case = y')
                break

        while True:
            lis = []            
            while True:                        
                if lis == []:
                    while True:
                        print('y = add a filter, not = add filter with NOT operator, n = enough,')
                        nex = input('next?:')

                        if nex == 'n' or nex == 'y':
                            break
                        elif nex == 'not':
                            lis.append({nex:'op'})
                            break
                        else:
                            print('invalid answer, please try again')

                else:
                    while True:
                        print('(Operators): and = and, or = or, and not = and not, '
                        'or not = or not\n{:<13}AND = new (and) filter, OR = new (or) filter n = enough'.format(''))
                        nex = input('next?:')

                        if nex == 'n':
                            break
                        elif nex == 'AND' or nex == 'OR':
                            lis.append({nex:'end'})
                            break
                        elif nex == 'and' or nex == 'or' or nex == 'and not' or nex == 'or not':
                            lis.append({nex:'op'})
                            break                
                        else:
                            print('invalid answer, please try again')

                if nex == 'n' or nex == 'AND' or nex == 'OR':
                    break

                y1 = input('type term:')
                lis.append({y1:'term'})               
                print(search_terminal(lis, sear))         
            sear.append(lis)            
            if nex == 'n':
                break

        print(search_terminal([], sear))     
        while True:
            print('are you sure to apply this search filter?\ny = yes, n = no')        
            sure = input('next?:')        
            if sure == 'y' or sure == 'n':
                break 

        if sure == 'n':
            continue

        return sear

#Format the string values inside the filter list in readable string to display.
def search_terminal(lis, sear):
    notline = False
    terminal = []
    line = False
    for x in lis:                    
        for k, v in x.items():
            if v == 'end' and k == 'AND':                                
                terminal.append(') and (')
                line = True
            elif v == 'end' and k == 'OR':                                
                terminal.append(') or (')
                line = True
            elif v == 'op' and k == 'not':
                terminal.append('not (')
                notline = True
            else:
                terminal.append(k)

    if notline == True:
        if line == True:
            terminal.insert(len(terminal) - 1,')')
        else:
            terminal.append(')')
        notline = False

    terminal2 = []
    for x1 in sear[2:]:
        line = False
        for x in x1:                        
            for k, v in x.items():
                if v == 'end' and k == 'AND':                                
                    terminal2.append(') and (')
                    line = True
                elif v == 'end' and k == 'OR':                                
                    terminal2.append(') or (')
                    line = True
                elif v == 'op' and k == 'not':
                    terminal2.append('not (')
                    notline = True
                else:
                    terminal2.append(k)

        if notline == True:
            if line == True:
                terminal2.insert(len(terminal2) - 1,')')
            else:
                terminal2.append(')')

            notline = False  
    prin = '{}, {}, ( {} )'.format(sear[0],sear[1],' '.join(terminal2 + terminal))
    return prin

#Evaluate the string inside the giving list and return False if the giving conditions aren't found.
#Variables - (beg = beginning of the article, end = end of the article, s = text as bytes,
#t = list with [position 0 = key word only used in digger function,
#position 1 = string that dictate whether to convert the text to lowercase, position 2 = string that wil be evaluted].
def search_filter(beg, end, s, t):
    end = end - beg
    beg = 0
    line = False
    notline = False

    if t[1] == 'ignore case = y':        
        s = s.lower()

    for x in t[2:]:
        if line == True:            
            line = False
        elif line == False:
            sent =[]

        if x == []:
            break
            
        for y in x:
            for k, v in y.items():               
                if v == 'term':
                    if t[1] == 'ignore case = y':        
                        k = k.lower()
                    if s.find(k.encode('utf-8'), beg, end) == -1:
                        sent.append(str(False))
                    else:
                        sent.append(str(True))                
                elif v == 'end' and k == 'OR':
                    line = True
                    sent.append(') or (')
                elif v == 'end' and k == 'AND':
                    pass
                elif v == 'op' and k == 'not':
                    sent.append('not (')
                    notline = True
                else:
                    sent.append(k)

        if notline == True:
            if line == True:
                sent.insert(len(sent) - 1,')')
            else:
                sent.append(')')

            notline = False        
        if line == False:  
            new = '({})'.format(' '.join(sent))
            if eval(new) == False:
                return False

#Calculate the amount of time a search through the whole xml file takes
#and ask if the user wants to stop after x amount of result.
#The constant 11 in calculation the time is found through using the script with a HHD.
#Variables - (pathf = path xml file)
def count_break(pathf):
    size = os.path.getsize(pathf)/(1024**3)
    name = os.path.basename(pathf)
    print('\nstop after x amount of result hits?\ny = yes, '
    'n = no\nif no than the average time for {}({:.3f}GB) is {:.1f}s'.format(name,size,size*11))
    while True:
        an1 = input('(y/n):')
        if an1 == 'y':
            while True:
                try:
                    an2 = int(input('amount:'))
                    return an2
                except:
                    pass
        elif an1 == 'n':            
            break 

#Function to use the script as import.
#Variables - (text = text as bytes, beg = beginning of the article, end = end of the article, metat = string that will be saved in meta)
def alone(text,beg=None,end=None,metat=None):    
    file_check = os.path.isfile('infowiki.json')

    if file_check:        
        ans = 'e'    
    else:
        ans = 'o' 

    if ans == 'o':            
        test = {'wiki':{'data':[None]}}
        cr = open('infowiki.json', 'w')
        json.dump(test, cr)
        cr.close()
        meta_json = []
    elif ans == 'e':            
        cr = open('infowiki.json', 'r')
        f = json.load(cr)

        if f['wiki']['data'] == []:
            f['wiki']['data'].append(None)

        meta = f['wiki']['meta'] 
        del f['wiki']['meta']
        with open('infowiki.json', 'w') as jw:
            json.dump(f, jw)
        cr.close()
        meta_json = meta
        
    if beg == None:
        beg = 0
    if end == None:
        end = len(text)-1
    if metat == None:
        metat = 'alone'

    an(beg,end,text)

    with open('infowiki.json', 'r') as jr:
        f = json.load(jr)
        if f['wiki']['data'][0] == None:
            del f['wiki']['data'][0]
        f['wiki']['meta'] = meta_json        
        f['wiki']['meta'].append(metat)          
        with open('infowiki.json', 'w') as jw:
            json.dump(f, jw, indent=4)      

#Ask the file name of the xml file.
#Returns the joined path of the file name and the script path.   
def path_file():
    file_path = os.path.dirname(os.path.abspath(__file__))
    print(file_path)
    while True:
        file_name = input('filename:')
        file_join = os.path.join(file_path,file_name)
        file_check = os.path.isfile(file_join)
        if file_check:
            return file_join
        else:
            print("File doesn't exist")    

#Checks if infowiki.json exist and either overwrite (delete and create a new file)
#or extend the current json file.
#If extend is chosen, it will return the meta value, so new values in data can be written before saving it as a json file.
#If overwrite is chosen it will add a None value at the beginning of the data list and delete it at the end of the script,
#so the first new data value can be written as a list before saving it as a json file.      
def open_file():
    print('\nDefault json filename is infowiki.json')
    file_check = os.path.isfile('infowiki.json')  

    if file_check:
        print('o = overwrite file, e = extend existing file')
        an = input('(o/e):')        
    else:
        an = 'o'

    while True: 
        if an == 'o':            
            test = {'wiki':{'data':[None]}}
            cr = open('infowiki.json', 'w')
            json.dump(test, cr)
            cr.close()
            return []
        elif an == 'e':            
            cr = open('infowiki.json', 'r')
            f = json.load(cr)

            if f['wiki']['data'] == []:
                f['wiki']['data'].append(None)

            meta = f['wiki']['meta']
            del f['wiki']['meta']
            with open('infowiki.json', 'w') as jw:
                json.dump(f, jw)
            cr.close()

            return meta 

        an = input('(o/e):')   
                    
#Search word in xml file and send the position of the article back trough a pipe.
#Variables - (cor = pipe variable = [begin position, end position], search_word = search word,
#pathf = path xml file, se = list with search filter, count_se = None or amount of times will loop before break)   
def digger(cor, search_word, pathf, se, count_se):
    count = 0
    cur = 0
    ma = io.DEFAULT_BUFFER_SIZE    
    with open(pathf, 'rb', 0) as fi:
        s = mmap.mmap(fi.fileno(), 0, access=mmap.ACCESS_READ)   
        while True:                       
            if count_se == count:
                inveniet = -1       
            else:
                inveniet = s.find(search_word, cur)
                                 
            if inveniet != -1:
                end = s.find(b'</page>', max(0, inveniet -7))              
                if end == -1:
                    s.seek(inveniet + 1)
                    cur = s.tell()
                    continue

                end += 7 
                beg = s.rfind(b'<page>', max(0, inveniet - ma), inveniet + 7)                
                ma1 = ma
                while beg == -1:                    
                    ma1 += ma1
                    beg = s.rfind(b'<page>', max(0, inveniet - ma1), inveniet + 7)

                if se[1] == []:
                    pass
                    se_f = True               
                else:
                    se_f = search_filter(beg, end, s[beg:end], se) 

                s.seek(end)
                cur = s.tell()
                if se_f == False:
                    continue
                cor.send([beg,end])
                count += 1                                                 
            else:                
                cor.send(None)
                cor.send(count)
                cor.close()               
                break

        s.close()

#Establish a pipe process for function 'digger', so that while function 'an' is still busy 'digger' will continue searching. 
if __name__ == '__main__':
    pathf = path_file()
    print(pathf,'\n')  
    se = search()
    se_ter = search_terminal([], se)
    meta_json = open_file()
    count_se = count_break(pathf)        
    search_word = se[0].encode('utf-8')
    start = time.time()
    ma = io.DEFAULT_BUFFER_SIZE
    print(ma) 
     
    y, x = Pipe()
    p = Process(target=digger, args=(x, search_word, pathf, se, count_se))
    p.start()

    with open(pathf, 'rb', 0) as fi:
        s = mmap.mmap(fi.fileno(), 0, access=mmap.ACCESS_READ)    
        while True:
            i = y.recv()        
            if i == None:
                break            
            beg = i[0]
            end = i[1]
            an(beg, end, s[beg:end])
            endt = time.time()
            print(f'{endt-start:.2f}')
        s.close()
        
    count = y.recv()     
    p.join()
    endt = time.time()

    with open('infowiki.json', 'r') as jr:
        f = json.load(jr)        
        if f['wiki']['data'][0] == None:
            del f['wiki']['data'][0]

        f['wiki']['meta'] = meta_json        
        f['wiki']['meta'].append({'search':se_ter,
                            'count':count,
                            'time':endt-start})

        with open('infowiki.json', 'w') as jw:
            json.dump(f, jw, indent=4)

    print('finis')            
    print('time:',endt-start)
    print('count:',count) 
    input()