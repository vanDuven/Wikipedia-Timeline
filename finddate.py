import re
from datetime import date as current

y1 = ['ce','bce','ah','bh']
y5 = {'ce':['c.e.','a.d.','c.e','a.d','ad'],'bce':['b.c.e.','b.c.','b.c.e','b.c','bc'],
'ah':['a.h.','a.h',"hijri year"],'bh':['b.h.','b.h'],
'th':['rd','st','nd'],'century':['c.','centuries','-century'],
'th century':['th-century'],'th millennium':['th-millennium']}

#qq = space or a non alpha numeric character
hijri = {
"Muharram":["muharram","muḥarram"],
"Safar":["safar","safar"],
"Rabiqqalqqawwal":["rabi' al-awwal","rabī’ al-thānī","rabi’ i"], 
"RabiqqalqqThani":["rabi' al-thani","rabī’ al-thānī","rabī’ al-ākhir","rabi’ ii"],
"Jumadaqqalqqawwal":["jumada al-awwal","jumādā al-awwal","jumādā al-ūlā","jumada i","jumādā i"],
"JumadaqqalqqThani":["Jumada al-Thani","jumaada al-akhir","jumada al-akhira","jumada ii"],
"Rajab":["rajab"],
"Shaqqban":["sha'ban","shaaban","shaban"],
"Ramadanqq":["ramadan (calendar month)","ramadhan"],
"Shawwal":["shawwal","shawwāl"],
"DhuqqalqqQidah":["dhu al-qidah","dhu al-qi'dah","dhu'l-qi'dah","dhu'l-qa'dah","zulqida"],
"DhuqqalqqHijjah":["dhu al-hijjah","dhu'l-hijjah","dhū al-ḥijja","zulhijja","zil-hajj"]
}

y2 = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 
'september', 'october', 'november', 'december']
y3 = {'jan': 'january', 'feb': 'february', 'mar': 'march', 'apr': 'april',
'may': 'may', 'jun': 'june', 'jul': 'july', 'aug': 'august',
'sep': 'september','sept': 'september','oct': 'october', 'nov': 'november', 'dec': 'december'}

y4 = {'spring':['march',1],'summer':['june',1],'fall':['september',1],'autumn':['september',1],'winter':['december',1]}
y6 = {'early':1/6,'beginning':1/12,'mid':1/2,'middle':1/2,'late':5/6}

current_words = ['present','current','ongoing']

mir = {'n1a1ar':['-','−','–','—','to','@#SND#@','until'],'o1f':['or','/','~'],'e1n':['and',';',',']}
mirword1 = [';','/',','] 
mirword2= ['to','or','and','until']
mirn = ['=',':']
sep = ['|','@#@','\n']

box = [['[[','|',']]'],['{{circa','|','}}'],['{{dts','|','}}'],['{{','age|','}}'],
['{{','date|','}}'],['{{','year|','}}'],['{{','age2|','}}'],['{{d-da','|','}}'],
['{{age','|','}}'],['{{b-da','|','}}'],['{{birth','|','}}'],['{{death','|','}}'],
['{{oldstyledate','|','}}'],['{{','|','ce}}'], ['{{','|','bce}}'],['{{','|','ad}}'],
['{{','|','bc}}'], ['{{','|','ah}}'],['{{','|','bh}}'],['{{nowrap','|','}}'],['{{sc','|','}}']]

ya = y2 + list(y3.keys())
totya = ya+list(y4.keys())+list(y6.keys())+list(y5.keys())+['millennium','half']

pat1 = re.compile(
    r'{{.*?(dts|age|date|year|age2|d-da|b-da|birth|death).*?'
    r'\|(\d\d\d\d).*?\|(1[0-2]|\d)(\|.*?}}|}})',flags=re.DOTALL)
pat2 = re.compile(
    r'{{.*?(dts|age|date|year|age2|d-da|b-da|birth|death).*?'
    r'\|(month|day|year).*?=.*?\|(month|day|year).*?=.*?(\|.*?}}|}})',flags=re.DOTALL)
pat3 = re.compile(
    r'({{#tag:ref.*}})|({{sfnp.*}})|(&lt;.*?&gt;)|((\d\d|\d):\d\d(:\d\d|))|(\d+\.\d+)|'
    r'(\d+\,0\d+)|(\d+\,\d00)|\[\[(?!.*?\[\[.*?calendar(\]\]|\|.*?\]\])).*?calendar(\]\]|\|.*?\]\])', flags=re.DOTALL)
pat4 = re.compile(
    r'\b(\d+|\d+ )(?P<tussen>[^a-z\d\s])( \d+|\d+|\d+ )(?P=tussen)( \d+|\d+)\b') 
pat5 = re.compile(
    r'(\(.*?\))|({{.*?}})|(\[\[.*?\]\])',flags=re.DOTALL) 
pat6 = re.compile(
    r'(&amp;#\d+)|(&amp;|nbsp;|(?<!\[)\[\b.*?\b\])',flags=re.DOTALL)
pat7 = re.compile(
    r'(&lt;ref.*?/(.?ref.?|)&gt;)|({{efn((?:[^}}]*?{{[^{{]*?}})+[^{{]*?}}|[^{{]*?}}))|({{vague.*?}})',flags=re.DOTALL)
pat8 = re.compile(
    r'{{(bbad|birth based on age as of date).?\|\s?(\d+)\s?\|(((\s?\d+\s?)\|(\s?\d+\s?)\|(\s?\d+\s?))|'
    r'((\s?\d+\s?)\|(\s?\d+\s?))|(\s?\d+\s?))(\||}})')

#Find and returns a list with dates and whether there is a period between the dates as dictionaries.
#A date contains a dictionary with: (y = year of date, d = day of date m = month of date, set = period condition to next date)
#y,m and d when found (else will be None) contains a list with: position 0 = value,
#position 1 = postion where the value was found in the adjusted string. 
#If the date was a century or millennium position 1 will be a list of positions.   
#Variables - (s = string with date(s))
def date_find(s):

    def stand0(s11):
        nodate =False
        datu_brace = []  
        f1 = re.finditer(pat4, s11)
        f2 = []           
        for l in f1:                
            num = l.groups()
            ind = l.start()
            f2.append([int(num[0]),int(num[2]),int(num[3]),ind]) 

        if f2 != []:                
            for x in f2:    
                datu1 = {}
                fi = x                                                       
                count_notday = 0
                count_notmonth = 0
                for l in range(3):                        
                    if fi[l] > 32:
                        count_notday +=1
                    if fi[l] > 12:
                        count_notmonth +=1 

                if count_notday > 1 or count_notmonth > 2:
                    nodate = True                        
                    continue

                year = fi[0]
                month = fi[1]
                day = fi[2]

                if month > 31:
                    year = month
                    month = None
                elif day > 31:
                    year = day
                    day = None
                    
                if day == None:                   
                    if month > 12:
                        day = month
                        month = fi[0]
                    else:                        
                        day = fi[0]

                elif month == None:
                    if fi[0] < 13:
                        month = fi[0]
                    else:
                        month = day
                        day = fi[0] 

                if month > 12:
                    month,day = day,month
                    if month > 12:
                        month,year = year,month

                if year == fi[0]:
                    if fi[3] > 0:
                        if s11[fi[3]-1] == '-':
                            year = (year*-1)-1

                if year == 0:
                    year = None
                else:
                    year = [year,fi[3]]
                if month == 0:
                    month = None
                else:
                    month = [month,fi[3]]
                if day == 0:
                    day = None
                else:
                    day = [day,fi[3]]

                datu1.update({'y':year,'m':month,'d':day})                                   
                datu1['set']='brace'                    
                datu_brace.append(datu1)                    
        else:
            difstand(s11)
            return

        if nodate == True and datu_brace == []:
            difstand(s11)
            return

        datu.append(datu_brace)

    def stand2(s11):
        datu_brace = []        
        f2 = list(re.finditer(pat1, s11)) 

        if f2 != []:            
            for x in f2:
                x1 = x.start()
                x2 = x.end()
                pat_string = s11[x1:x2]
                list_year = list(re.finditer(r'\|(\d\d\d\d)(\||}})', pat_string))
                for z in range(len(list_year)):                 
                    datu1 = {}
                    year_group = list_year[z].groups()
                    year_end = list_year[z].end()-1

                    if z == len(list_year)-1:
                        year_start = len(pat_string)
                    else:  
                        year_start = list_year[z+1].start()+1

                    year_string = pat_string[year_end:year_start]                      
                    year_box = [int(year_group[0]),x1]                    
                    list_month = list(re.finditer(r'\|(1[0-2]|\d)(\||}})',year_string))

                    if list_month != []:                                
                        month_group = list_month[0].groups()
                        month_end = list_month[0].end()-1                            
                        month_string = year_string[month_end:year_start]                            
                        month_box = [int(month_group[0]),x1]                   
                        list_day = list(re.finditer(r'\|([0-2]\d|\d|3[0-2])(\||}})', month_string))

                        if list_day != []:
                            day_group = list_day[0].groups()
                            day_box = [int(day_group[0]),x1]                         
                        else:
                            day_box = None

                    else:
                        day_box = None
                        month_box = None

                    datu1 = {'y':year_box,'m':month_box,'d':day_box}
                    datu1['set']='brace'
                    datu_brace.append(datu1)                          
        else:
            difstand(s11)
            return 

        datu.append(datu_brace)

    def stand3(s11):
        datu_brace = []        
        f2 = list(re.finditer(pat2, s11))

        if f2 != []:          
            for x in f2:                
                x1 = x.start()
                x2 = x.end()
                pat_string = s11[x1:x2]
                list_yearn = list(re.finditer(r'\|year.*?=.*?(\d+).*?(?=(\||}}))', pat_string))
                list_year = list(re.finditer(r'\|year(\d).*?=.*?(\d+).*?(?=(\||}}))', pat_string))
                for z in range(len(list_yearn)):                   
                    if list_year != []:
                        year_group = list_year[z].groups() 
                        n_box = year_group[0]
                    else:
                        n_box = ''  

                    datu1 = {}
                    year_group = list_yearn[z].groups()                                                                    
                    year_box = [int(year_group[0]),x1]               
                    list_month = list(re.finditer(r'\|month%s.*?=.*?(1[0-2]|0\d|\d).*?(?=(\||}}))' %n_box,
                    pat_string))   

                    if list_month != []:
                        if len(list_month) < 2:
                            z1 = 0
                        else:
                            z1 = z 
                                                   
                        month_group = list_month[z1].groups()
                        month_box = [int(month_group[0]),x1]
                    else:
                        month_box = None

                    list_day = list(re.finditer(r'\|day%s.*?=.*?([0-2]\d|3[0-2]|0\d|\d).*?(?=(\||}}))' %n_box,
                    pat_string)) 

                    if list_day != []:
                        if len(list_month) < 2:
                            z2 = 0
                        else:
                            z2 = z

                        day_group = list_day[z2].groups()
                        day_box = [int(day_group[0]),x1]
                    else:
                        day_box = None 

                    datu1 = {'y':year_box,'m':month_box,'d':day_box}
                    datu1['set']='brace'
                    datu_brace.append(datu1)                          
        else:
            stand1(s11) 

        datu.append(datu_brace)

    def stand4(s11):
        nodate = False
        datu_brace = []        
        f1 = list(re.finditer(pat8, s11))
        f2 = []           
        for l in f1:                
            num = l.groups()
            ind = l.start()

            if num[2] != None:
                f2.append([int(num[4]),int(num[5]),int(num[6]),ind,int(num[1])])
            elif num[6] != None:
                f2.append([int(num[8]),int(num[9]),None,ind,int(num[1])])
            elif num[9] != None:
                f2.append([int(num[10]),None,None,ind,int(num[1])])

        if f2 != []:                
            for xf in f2:    
                datu1 = {}
                year = xf[0]
                month = xf[1]  
                day = xf[2]
                curyear = int((str(current.today()).split('-'))[0])

                if year > curyear or month > 12 or day > 32:
                    nodate = True
                    continue

                dify = year-xf[4]                
                datu1.update({'y':[dify-1,xf[3]],'m':[month,xf[3]],'d':[day,xf[3]]})                                   
                datu1['set']='or'                    
                datu_brace.append(datu1)
                datu_brace.append({'y':[dify,xf[3]],'m':[month,xf[3]],'d':[day,xf[3]],'set':None})
        else:
            difstand(s11)
            return

        if nodate == True and datu_brace == []:
            difstand(s11)
            return

        datu.append(datu_brace)        

    def stand1(ty1):
        almir = mirn 
        for xm in almir:
            if xm in ty1:
                spl1new = ty1.replace(xm,f' @l@i@s@t@ ')
                spl1new = [x for x in spl1new.split(' ') if x != '']
                ind = spl1new.index('@l@i@s@t@')  

                if ind -1 != -1:
                    try:
                        dig = False
                        nondig = False
                        for xn1 in spl1new[ind-1]:

                            if xn1.isdigit() == True:
                                dig = True
                            elif xn1.isalnum() == False:
                                if xn1 != '_' and xn1 not in mir['n1a1ar']:
                                    break                                
                            else:
                                nondig = True

                            if dig == True and nondig == True:                                                                               
                                raise Exception()

                    except:                                
                        spl1new[ind] = '@#@'                                                                                       
                        del spl1new[ind-1]                     
                        ty1 = ' '.join(spl1new)

        for x in sep:     
            ty1 = ty1.replace(x,'#@#')
        ty1 = ty1.split('#@#')   

        if type(ty1) != list:       
            ty1 = [ty1] 
                  
        ty1 =[x for x in ty1 if x != '']
        datu3 = []        
        for x in ty1:                 
            if datu3 != None:           
                spl1 = x
                spl1 = spl1.replace('october',' @#@ ')                        
                spl1 = re.sub(r'\d+',r' \g<0> ',spl1)

                for nsp1 in y5:
                    for nsp2 in y5[nsp1]:
                        if nsp2 in spl1:
                            spl1 = re.sub(r'(?<=[^.a-z\d])%s(\Z|\]\]|(?=[^a-z\d]))'%re.escape(nsp2),f' {nsp1} ',spl1)

                spl1 = ' '.join(spl1.split()) 

                for x in mir:
                    for y in mir[x]:                        
                        if y in spl1:
                            if y in mirword1:                                
                                if re.search(r"(?<=[a-z])({0}|\s*?{0})".format(re.escape(y)),spl1):
                                    chc = re.finditer(r"(\b[a-z]+)({0}|\s*?{0})".format(re.escape(y)),spl1)
                                    for y2 in chc:
                                        if y2.groups()[0] not in totya:                                            
                                            spl1 = spl1[:y2.end()-len(y)]+' '+spl1[y2.end():] 

                            elif y in mirword2:
                                if re.search(r'(?<=[a-z]){0}|{0}(?=[a-z])'.format(re.escape(y)),spl1):
                                    chc = re.finditer(r'(\b[a-z]+){0}|{0}([a-z]+\b)'.format(re.escape(y)),spl1)
                                    for y2 in chc:
                                        if y2.groups()[0]:
                                            if y2.groups()[0] not in totya:
                                                spl1 = spl1[:y2.end()-len(y)]+spl1[y2.end():]
                                        else:
                                            if y2.groups()[1] not in totya:
                                                spl1 = spl1[:y2.start()-1]+spl1[y2.start()+len(y):]  

                        spl1 = spl1.replace(y,f' {x}#$#') 

                spl1 = spl1.replace('@#@','october')                              
                spl1 = spl1.split('#$#') 

                if type(spl1) != list:
                    spl1 = [spl1] 

                spl3 = []
                for x in spl1:                     
                    spl2 = re.sub(r'\W',' ',x).strip()                                      
                    spl2 = spl2.split()

                    if 'age' in spl2 or 'aged' in spl2:
                        continue   

                    if 'century' in spl2 or 'millennium' in spl2:
                        spl2 = [m for m in spl2 if m != 'of' and m != 'c' and m != 's']
                    else:
                        spl2 = [m for m in spl2 if m != 'of' and m != 'th' and m != 'c' and m != 's'] 

                    spl3.append(spl2) 
                if spl3 == [['']] or spl3 == [[]]:
                    continue

                datu3 = filter_string(spl3)
                if datu3 != []:
                    datu.append(datu3) 

    def difstand(s11): 
        s = s11                      
        for nsp1 in hijri:        
            for nsp2 in hijri[nsp1]:
                if nsp2 in s:                
                    s = re.sub(r'(\[\[|\A|\s)%s(\Z|\]\]|\||(?=[^a-z\d]))'%re.escape(nsp2),f' {nsp1} ',s) 

        for b in box:
            fis1 = s.find(b[1])
            while fis1 != -1:                       
                fis2 = s.rfind(b[0],0,fis1)
                fis3 = -1
                oldlen = len(s)

                if fis2 != -1:                                                                   
                    fis3_check = s.find(b[2],fis2,fis1)                    
                    fis3 = s.find(b[2],fis1) 

                    if fis3_check == -1 and fis3 != -1:  
                        fis3_brac1 = s.rfind(b[0][:2],fis1,fis3) 

                        if fis3_brac1 != -1:                           
                            fis3_brac2 = s.find(b[2],fis3+1)
                            
                            if fis3_brac2 == -1:
                                fis1 = s.find(b[1],fis1+1)
                                continue                                                                                                
                            elif fis3_brac2 != -1:
                                fis3_brac21 = s.find(b[0],fis1,fis3)                                
                                if fis3_brac21 == fis3_brac1:
                                    fis1 = s.find(b[1],fis1+1)
                                    continue
                                else:                                     
                                    fis3 = fis3_brac2 

                        if s.find('oldstyledate',fis2,fis1+len(b[1])) != -1:                        
                            olfdfis = s.find('|',fis1+1+len(b[1]),fis3) 

                            if olfdfis != -1:                                                                                  
                                s = s[:olfdfis]+';'+s[olfdfis+1:]
                                fis3 = s.find(b[2],olfdfis)                                                                                                       
                                olfdfis = s.find('|',olfdfis+1,fis3)

                                if olfdfis != -1:                                                                                                                                                                                                                                                  
                                    s = s[:olfdfis]+s[fis3:]                                    
                                    fis3 = s.find(b[2],olfdfis)                                                         
                                    s = s.replace('|',';')

                        if s.find('-date',fis2,fis1+len(b[1])) != -1:
                            olfdfis = s.find('|',fis1+1+len(b[1]),fis3) 

                            if olfdfis != -1:                                                                                  
                                s = s[:olfdfis]+s[fis3:]
                                fis3 = s.find(b[2],olfdfis)

                        repsep = ' '
                        plusbrac = 0
                        oldlen = len(s)

                        if len(b[2]) > 2:
                            plusbrac = len(b[2]) -2
                        if b[0] == '{{circa':
                            s = (s[:fis2] +' '+ s[fis1+len(b[1]):fis3+plusbrac] +repsep).replace('|','@#SND#@') \
                            + s[fis3+len(b[2]):]
                        else:
                            s = s[:fis2] +' '+ s[fis1+len(b[1]):fis3+plusbrac] +repsep+ s[fis3+len(b[2]):] 
                
                if fis3 != -1:
                    fis1 = s.find(b[1],fis3+2-(oldlen-len(s)))
                else:
                    fis1 = s.find(b[1],fis1+1)

        count = 0
        found_num = False
        for x in s:        
            if x.isdigit() == True:          
                first_dig = count
                found_num = True            
                break
            else:
                first_dig = 0

            count += 1   
        if found_num == True:         
            ty2 = re.sub(pat5,' ',s[:first_dig])   
            ty1 = re.sub(pat5,' ',s[first_dig:])   
            ty1 = ty2 + ty1          
        else:
            ty1 = s 

        ty1 = re.sub(pat6,' ',ty1)   
        f3 = re.search(pat2, ty1)
        if f3 != None:
            stand3(ty1)                      
        else: 
            stand1(ty1)  

    datu = []
    s = s.lower() 
    s = re.sub(r'{{snd}}|ndash;|{{(?!.*?{{.*?dash}}).*?dash}}|mdash;|horbar;','@#SND#@',s)
    s = re.sub(r'&lt;br(.|./)?&gt;',' @#@ ',s) 
    s11 = re.sub(pat7,' ',s)
    s11 = re.sub(pat3,' ',s11)    
    f1 = re.search(pat4, s11)
    f2 = re.search(pat1, s11)
    f4 = re.search(pat8, s11)

    if f4 != None:
        stand4(s11) 
    elif f1 != None:
        stand0(s11)        
    elif f2 != None:        
        stand2(s11)
    else:
        difstand(s11)

    return datu

def filter_string(spl3):
    datu1 = {}
    datu2 =[]
    datu3 = {}    
    times = 'ce' 
    new_or = False
    check_day = False
    check_day2 = False
    check_hijri = False
    lenres = False
    lenres2 = False
    lenres3 = False    
    years_cen = None
    spl21 = [] 
    res_list1 = [] 

    for spl2 in spl3[::-1]:

        def monthlook(start):
            yfound = False
            index_month = []
            if 'd' in datu:
                if datu['d']:
                    index_month.append(datu['d'][1])
            if 'y' in datu:
                if datu['y']:
                    if type(datu['y'][1]) == list:
                        index_month.extend(datu['y'][1])
                    else:
                        index_month.append(datu['y'][1])
                                                                    
            ve = start+2
            try:
                voor = spl2[ve]                    
                if voor.isdigit() == True and 'y' not in datu and ve not in index_month:
                    datu.update({'y':[int(voor),ve]})
                    yfound = True                    
            except:
                pass                    
            te = start-2

            if te >= 0:
                achter = spl2[te]                    
                if achter.isdigit() == True and 'y' not in datu and te not in index_month:                        
                    datu.update({'y':[int(achter),te]})
                    yfound = True

            ve = start+1
            try:                
                voor = spl2[ve]                   
                if voor.isdigit() == True and ve not in index_month:
                    if int(voor) > 31:                               
                        datu.update({'y':[int(voor),ve]})
                        yfound = True
                    elif 'd' not in datu and int(voor) < 32:                                
                        datu.update({'d':[int(voor),ve]})
            except:
                pass

            te = start-1
            if te >= 0:                     
                achter = spl2[te]
                if achter.isdigit() == True and te not in index_month:
                    if int(achter) > 31:                           
                        datu.update({'y':[int(achter),te]})
                        yfound = True
                    elif int(achter) < 32 and 'd' not in datu:  
                        datu.update({'d':[int(achter),te]})
            
            if yfound == True and len(datu2) > 0 and exten_mir != None:
                if datu2[0]['y'] != None and datu2[0]['m'] == None and datu2[0]['d'] == None:
                    if datu2[0]['y'][1] == 0 and datu['y'][1] == len(spl2)-2:
                        newu = earlier_date(datu['y'][0],datu2[0]['y'][0])
                        if newu:
                            datu2[0]['y'][0] = newu                                                    

        def earlier_date(pre_date,af_date):
            newu = None
            lenght_pre = len(str(pre_date))
            lenght_af = len(str(af_date))

            comp_res = calendar_con(pre_date,cal=times)['y']
            comp_datu = af_date

            if comp_res < 0:
                if pre_date > 0:
                    lenght_pre += 1
                if (abs(comp_res) - abs(comp_datu)) > 50:
                    comp_res = abs(comp_res)

            if lenght_af < lenght_pre and comp_datu < comp_res:                    
                newu = calendar_con(int(str(pre_date)[:lenght_pre - lenght_af] + str(abs(comp_datu))),cal=times)['y']

            return newu

        if spl2 == []:
            continue

        res_list = []
        res = None
        exten_mir = None
        gatecen2 = False
        lenres4 = False
        cen = None
        season = False
        att = None                                 
        count = 0
        datu = {}
        month_found = False 
        ad_found = False
        ad_found2 = False

        if spl2[-1] == 'n1a1ar':
            exten_mir = 'to'           
        elif spl2[-1] == 'o1f':
            exten_mir = 'or'           
        elif spl2[-1] == 'e1n':
            exten_mir = 'and'

        if exten_mir == None:
            times = 'ce' 

        if exten_mir != None:
            if len(res_list1) > 0 and len(datu2) > 0:           
                if lenres == True and datu2[0]['y'] != res_list1[0]:                 
                    if res_list1[0][0]>31:                    
                        datu4 = dictcopy(datu2[0])
                        datu4['y']=[calendar_con(res_list1[0][0],cal=times)['y'],res_list1[0][1]]
                        datu4['d']=None
                        datu4['m']=None
                        datu4['set']=None                
                        datu2.insert(0,datu4)
                        datu3 = datu4
                    elif res_list1[0][0]<=31:
                        datu2[0]['d'] = res_list1[0]
                        check_day = True 

            try:                        
                if type(datu3['y'][1]) == list:                            
                    gatecen = True                           
                else:
                    raise Exception()
            except:                        
                gatecen = False
        else:
            gatecen = False

        for x in spl2:            
            if x in current_words:
                vand = str(current.today()).split('-')
                datu.update({'y':[int(vand[0]),count],'m':[int(vand[1]),count+1],'d':[int(vand[2]),count+2]})

            if ad_found == False and ad_found2 == False: 
                if x in y1:                    
                    ad_found = True 

            if ad_found == True and ad_found2 == False:                
                te = count - 1                
                try:
                    ye2 = spl2[count+1]
                except:
                    ye2 = '' 

                if te < 0:
                    if ye2 == '':                    
                        te = -1
                    else:
                        te = count+1  

                if te >= 0:
                    ad_found = False
                    ye = spl2[te]  

                    if x == 'bce':
                        times = 'bce' 
                    elif x == 'ce':
                        times = 'ce'
                    elif x == 'ah':
                        times = 'ah'
                    elif x == 'bh':
                        times = 'bh' 

                    if ye.isdigit() == True:
                        ye = ye
                    elif ye2.isdigit() == True:
                        ye = ye2
                        te = count+1

                    if ye.isdigit() == True:
                        ad_found2 = True
                        switch_d_y = None                                          
                        for x in datu:                            
                            try:
                                if datu[x][1] == te:
                                    if x != 'y':                                     
                                        datu[x] = None
                                        if x == 'd':
                                            switch_d_y = x
                            except:
                                pass
                        ye = int(ye) 
                        datu.update({'y':[ye,te]})
                        if switch_d_y:
                            del datu[switch_d_y]                            
                            if 'm' in datu:
                                monthlook(datu['m'][1])


            if month_found == False:                
                if x in ya:
                    indm = ya.index(x)
                    if indm > 11:
                        indm = y2.index(y3[x])
                    datu.update({'m':[y2[indm],count]})
                    month_found = True
                    monthlook(count) 

                elif x in y4:                
                    datu.update({'d':[y4[x][1],count]})
                    datu.update({'m':[y4[x][0],count]})
                    month_found = True
                    season = True
                    monthlook(count)
                    del datu['d']

                elif x in hijri:
                    datu.update({'m':[x,count]})
                    month_found = True
                    if times == 'ce':
                        times = 'ah' 
                    monthlook(count)

            if 'century' in x or 'millennium' in x or gatecen == True: 
                index_cen = []
                count_c = count
                if gatecen == True:
                    gatecen = False                                              
                    count_c = len(spl2) 
                te = count_c-1                
                cenfound = False
                while te >= 0 and gatecen2 == False:                    
                    achter = spl2[te]  

                    if achter == 'th' and cenfound == False:
                        index_cen.append(te)
                        te2 = te-1

                        if te2 >= 0:
                            achter = spl2[te2]
                            if achter.isdigit():   
                                cen = achter
                                index_cen.insert(0,te2)                            
                                prob1 = 0
                                cenfound = True
                        te3 = te + 1

                        try:
                            if 'century' in spl2[te3] or 'century' in x:
                                years_cen = 100
                            elif 'millennium' in spl2[te3] or 'millennium' in x:
                                years_cen = 1000
                        except:
                            pass

                    if achter in y6:
                        prob1 = y6[achter]
                        index_cen.append(te)
                    elif 'half' == achter or 'part' == achter:                        
                        prob1 = 1/2
                        te2 = te-1

                        if te2 >= 0:
                            achter = spl2[te2]

                            if 'first' == achter:
                                prob1 = 1/6
                                index_cen.append(te2)
                            elif 'second' == achter:
                                prob1 = 4/6
                                index_cen.append(te2)
                            elif 'th' == achter:
                                te3 = te2-1
                                if te3 >= 0:
                                    achter3 = spl2[te3]
                                    if '1' == achter3:
                                        prob1 = 1/6
                                        index_cen.append(te3)
                                    elif '2' == achter3:
                                        prob1 = 4/6
                                        index_cen.append(te3) 

                        index_cen.append(te)

                    if te == 0 and years_cen != None:
                        if cen != None:
                            cenn = int((int(cen) * years_cen) - years_cen + (years_cen*prob1))
                            if cenn == 0:
                                cenn = 1                         
                            datu.update({'y':[cenn,index_cen]})
                        elif cen == None and exten_mir != None:
                            try:                                
                                if type(datu3['y'][1]) == list and spl21[datu3['y'][1][0]].isdigit():
                                    if spl2[-2].isdigit() and sorted(datu3['y'][1])[0] == 0:
                                        if  (int(spl2[-2]) -15 <= int(spl21[datu3['y'][1][0]]) <= int(spl2[-2]) + 15):
                                            cen = int(spl2[-2])
                                            cenn = int((int(cen) * years_cen) - years_cen + (years_cen*prob1))
                                            if cenn == 0:
                                                cenn = 1
                                            index_cen.append((len(spl2)-2))                         
                                            datu.update({'y':[cenn,index_cen]})
                                    elif len(index_cen) != 0:
                                        if spl2[sorted(index_cen)[-1]] == spl2[-2]:                                   
                                            if datu3['y'][0] < 0:
                                                cenn = int((int(spl21[datu3['y'][1][0]]) * years_cen) \
                                                    - (years_cen*prob1)) * -1
                                            else:
                                                cenn = int((int(spl21[datu3['y'][1][0]]) * years_cen) \
                                                    - years_cen + (years_cen*prob1))                                   
                                            if sorted(datu3['y'][1])[0] == 0:
                                                datu3['y'][0] = cenn
                                            elif datu3['y'][1][0] > 0:
                                                if datu3['y'][0] < 0:
                                                    cen = spl21[datu3['y'][1][0]]
                                                    cenn = cenn *-1                                       
                                                datu.update({'y':[cenn,index_cen]}) 

                            except:
                                pass                                                         
                        gatecen2 = True                        
                    te = te-1

            if x in y6:
                att = [x,count]

            if x.isdigit() == True:
                res = x
                count_res = count
                try: 
                    res_list.append([int(res),count_res])
                except:
                    del spl2[count_res]
                    
            count += 1 
        if lenres == True and exten_mir != None and datu != {}:
            if datu2[0]['y'] != None and datu2[0]['d'] == None and datu2[0]['m'] == None:
                if type(datu2[0]['y'][1]) != list:
                    if datu2[0]['y'][1] == 0:                        
                        resy = None
                        resd = None

                        if 'y' in datu:
                            if type(datu['y'][1]) != list:
                                if datu['y'][1] == len(spl2)-2:
                                    resy = datu['y'][0]

                        if 'd' in datu:
                            if datu['d'][1] == len(spl2)-2 and (0 <= datu2[0]['y'][0] < 32):
                                resd = datu['d'][0] 
                                                       
                        if resy != None and resd == None:
                            if len(res_list1) > 0 and (exten_mir == 'or' or exten_mir == 'to'):
                                if datu2[0]['y'][0] == res_list1[0][0] and res_list1[0][1] == 0:
                                    newu = earlier_date(resy,datu2[0]['y'][0])
                                    if newu:
                                        datu2[0]['y'][0] = newu

                        elif resy == None and resd != None:
                            datu2[0]['d'] = datu2[0]['y']

                            if 'y' in datu:
                                datu2[0]['y'] = datu['y']
                            else:
                                datu2[0]['y'] = None
                            if 'm' in datu:
                                datu2[0]['m'] = datu['m'] 

        lenres = False
        if datu == {} and res != None:
            lenres = True
            res = int(res)

            if exten_mir != None and datu3 != {}:
                mir_gate = True
                if datu3['y'] == None and datu3['d'] == None:
                    mir_gate = False
            else:
                mir_gate = False

            if mir_gate == True:
                lenres2 = True
                templ = None

                if datu3['y'] != None:                    
                    if type(datu3['y'][1]) == list:
                        templ = datu3['y'][1].copy()                        
                        datu3['y'][1] = sorted(datu3['y'][1])[0]

                mirindex = sorted([[datu3[x][1],x] for x in datu3 if (x == 'd' or x == 'y') \
                    and datu3[x] != None and type(datu3[x]) != str])

                if templ != None:
                    datu3['y'][1] = templ

                if len(mirindex) > 0:                 
                    mirindex = mirindex[0][1]

                    if mirindex == 'y':
                        if len(res_list1) > 0 and (exten_mir == 'or' or exten_mir == 'to'):
                            if datu3[mirindex][0] == calendar_con(res_list1[0][0],cal=times)['y'] \
                                and res_list1[0][1] == 0:
                                newu = earlier_date(res,datu3[mirindex][0])                                
                                if newu:
                                    datu3[mirindex][0] = newu

                        try:
                            if (datu2[0]['m'] == None or datu2[0]['d'] == None) and datu2[0]['y'] != None and res < 32:
                                if spl2 == spl3[0] and datu2[0]['m'] == None:
                                    raise Exception()
                                mirindex = 'd'
                                check_day2 = True                           
                            else:
                                raise Exception()

                        except:                                    
                            mirindex = 'y'  

                    if res > 31:
                        mirindex = 'y'
                        if datu3['y'] != None:
                            datu['d'] = None
                            datu['m'] = None 

                    datu.update({f'{mirindex}':[res,count_res]})
            else:
                lenres2 = False
                for zr in res_list[::-1]:
                    res = zr[0]
                    count_res = zr[1]                 
                    te = count_res + 1
                    try:
                        ve = spl2[te]
                    except:
                        ve = ''                
                    te = count_res - 1

                    if te < 0:
                        achter = ''                    
                    else:
                        achter = spl2[te] 

                    acht2 = False

                    if len(spl3) > 1 and achter == '' and spl3[-1] == spl2:
                        if len(spl3[-2]) > 1:
                            achter = spl3[-2][-2]
                            acht2 = True

                    if (achter.isdigit() == False or ve.isdigit() == False) and res < 32 and \
                        (spl2 == spl3[0] or acht2 == True or (spl2 != spl3[0] and datu2 == [])):
                        lenres = False
                        if res < 32 and achter.isdigit() == True and ve.isdigit() == False and count_res == 0:                        
                            lenres3 = True
                            lenres4 = True                       
                    else: 
                        datu.update({'y':[res,count_res]})
                        lenres = True
                        break

        if check_day == True:         
            if 'y' in datu:          
                if res_list[-1] == datu['y'] and datu3['d'] != None:
                    if len(res_list1) > 0:
                        if res_list1[0][0] == datu3['d'][0] and res_list1[0][1] == 0 and datu['y'][1] == len(spl2)-2:                 
                            lenght_pre = len(str(datu['y'][0]))
                            lenght_af = len(str(datu3['d'][0]))

                            if lenght_af < lenght_pre and datu3['d'][0] < (datu['y'][0]):                    
                                newu = calendar_con(int(str(datu['y'][0])[:lenght_pre - lenght_af] \
                                    + str(datu3['d'][0])),cal=times)['y']

                                if datu3['y'] != None:                                                      
                                    datu5 = dictcopy(datu3)
                                    datu5['d'] = None
                                    datu2.insert(1,datu5)
                                datu3['y'] = [newu,datu3['d'][1]]
                                datu3['d'] = None

            elif 'm' in datu and 'd' in datu and datu3['m'] == None:
                if res_list[-1] == datu['d'] and datu3['d'] != None:
                    datu3['m'] = datu['m']
            elif 'd' in datu and datu3['m'] == None and datu3['d'] != None and lenres2 == True:
                switch_d_y = True
                if datu3['y'] != None:
                    if datu3['y'][0] - datu3['d'][0] > 30:
                        switch_d_y = False
                if switch_d_y:
                    datu3['y'] = [calendar_con(datu3['d'][0],cal=times)['y'],datu3['d'][1]]
                    datu3['d'] = None
                    datu['y'] = datu['d']
                    datu['d'] = None 

            check_day = False

        calen = None
        y = None
        m = None
        d = None
        if 'y' in datu or times != 'ce':

            if 'y' in datu:
                if datu['y'] != None:
                    if type(datu['y'][1]) == list and times == 'bce' and cenn > 0:                                    
                        cenn = int((int(cen) * years_cen) - (years_cen*prob1))           
                        datu['y'][0] = cenn
                    y = datu['y'][0]

            if  'm' in datu:
                if datu['m'] != None:
                    m = datu['m'][0]

            if  'd' in datu:
                if datu['d'] != None:
                    d = datu['d'][0]

            if times == 'bh' or times == 'ah':
                if check_hijri == True:
                    check_hijri = False
                    if len(datu2) != 0 and y and check_hijri_y:
                        if abs(y-check_hijri_y) > 100:
                            times = 'ce'
                            
                check_hijri = True
                check_hijri_y = y               
            
            calen = calendar_con(y,m,d,cal=times)

            if calen['y'] != None:                
                if 'y' in datu:
                    if datu['y'] == None:
                        ind = count
                    else:
                        ind = datu['y'][1]

                else:
                    ind = count

                datu['y'] = [calen['y'],ind] 

            if calen['m'] != None:
                if 'm' in datu:
                    if datu['m'] == None:
                        ind = count
                    else:
                        ind = datu['m'][1]
                else:
                    ind = count

                datu['m'] = [calen['m'],ind]

            if calen['d'] != None:
                if 'd' in datu:
                    if datu['d'] == None:
                        ind = count
                    else:
                        ind = datu['d'][1]

                else:
                    ind = count

                datu['d'] = [calen['d'],ind]

        if exten_mir != None and len(datu2) > 0 and new_or == True:
            if 'm' in datu and 'y' not in datu and datu2[0]['m'] == None and datu2[0]['y'] != None:                
                if datu['m'] != None:
                    datu2[0]['m'] = datu['m']
                    new_or = False

        if exten_mir == 'or' or exten_mir == 'and':           
            if len(datu2) > 0: 
                if ('m' in datu or 'd' in datu) and 'y' not in datu and (datu2[0]['m'] == None or \
                    datu2[0]['d'] == None) and datu2[0]['y'] != None:

                    same = True
                    datu['y']=datu2[0]['y']

                    if datu2[0]['m'] != None:
                        if 'm' in datu and lenres2 == False:
                            same = False
                        elif 'm' not in datu:
                            datu['m']=datu2[0]['m']

                    if datu2[0]['d'] != None:
                        if 'd' in datu and lenres2 == False:
                            same = False
                        elif 'd' not in datu:
                            datu['d']=datu2[0]['d']

                    if same == True:
                        if datu2[0]['set'] != None:
                            exten_mir = datu2[0]['set']
                        else:
                            exten_mir = None

                        del datu2[0]

                    new_or = True
                    
        if datu != {} and gatecen2 == False and att != None:
            templ = None

            if 'y' in datu:
                if datu['y'] != None:                    
                    if type(datu['y'][1]) == list:
                        templ = datu['y'][1].copy()                        
                        datu['y'][1] = sorted(datu3['y'][1])[0]

            mirindex = sorted([[datu[x][1],x] for x in datu if (x == 'm' or x == 'y') and datu[x] != None])

            if templ != None:
                datu['y'][1] = templ

            if len(mirindex) > 0:
                if att[1] > mirindex[0][0]:
                    if len(mirindex) > 1:
                        attr = mirindex[1][1]
                    else:
                        attr = None
                else:
                    attr = mirindex[0][1]

                if attr != None:
                    if attr == 'y':                        
                        if 'm' in datu:
                            if datu['m'] == None:
                                datu.update({'m':[y2[max(0,int(y6[att[0]]*12)-1)],att[1]]})
                        else:
                            datu.update({'m':[y2[max(0,int(y6[att[0]]*12)-1)],att[1]]})

                    elif attr == 'm':
                        if season == True:
                            days = int(y6[att[0]]*90)
                            month, day = divmod(days,30)
                            ind = None
                            if datu['m'][0] in y2:
                                ind = y2.index(datu['m'][0])
                            if ind != None:
                                if ind + month > 11:
                                    ind = ind - 11
                                datu.update({'m':[y2[min(11,ind+month)],att[1]+1]})
                                
                                if day < 32:
                                    datu.update({'d':[day,att[1]]})
                        else:
                            if 'd' in datu:
                                if datu['d'] == None:
                                    datu.update({'d':[int(y6[att[0]]*31),att[1]]})
                            else:
                                datu.update({'d':[int(y6[att[0]]*31),att[1]]})

        if len(datu2) != 0:
            datu1 = dictcopy(datu2[0])

        if lenres2 == True and lenres == False:
            lenres2 =False 
        
        if check_day2 == True:
            check_day = True
            check_day2 = False

        if exten_mir != None and len(spl2) == 1 and datu == {}:
            datu3 = {}
            continue
        
        spl21 = spl2

        if datu != {}:
            if 'd' in datu1:
                if datu1['d'] != None:
                    datu1['d'][1] = datu1['d'][1]+1

            if 'm' in datu1:
                if datu1['m'] != None:
                    datu1['m'][1] = datu1['m'][1]+1

                    if 'm' in datu:                        
                        if 'd' not in datu and datu['m'] != None and 'd' in datu1:
                            if datu1['d'] != None:
                                datu['d'] = None

            if 'y' in datu1:
                if datu1['y'] != None:
                    if type(datu1['y'][1]) == list:
                        datu1['y'][1] = [x+1 for x in datu1['y'][1]]
                    else:
                        datu1['y'][1] = datu1['y'][1]+1

            datu1.update(datu)
        else:
            res_list1 = res_list.copy()
            if lenres3 == True and lenres4 == False:
                lenres3 = False
            datu3 = {}
            continue  

        datu3 = dictcopy(datu1)

        if datu3 != {}:
            if 'd' not in datu3:
                datu3['d']=None
            if 'm' not in datu3:
                datu3['m']=None
            if 'y' not in datu3:
                datu3['y']=None 

            datu3['set']=exten_mir            

            if lenres3 == True and lenres4 == False and exten_mir != None:
                lenres3 = False
                mirindex = [] 

                if datu3['y']:
                    if type(datu3['y'][1]) != list:
                        mirindex.append([datu3['y'][1],'y'])

                if datu3['d']:
                    mirindex.append([datu3['d'][1],'d'])

                if mirindex != [] and calen != None:
                    mirindex = sorted(mirindex)

                    if mirindex[-1][0] == len(spl2)-2 and res_list1[0][1] == 0:
                        if mirindex[-1][1] == 'y' and calen['y'] == datu3['y'][0] and \
                            (exten_mir == 'or' or exten_mir == 'to'):

                            res = y
                            res_pre = res_list1[0][0]
                            lenght_pre = len(str(res))
                            lenght_af = len(str(res_pre))

                            if lenght_af < lenght_pre and res_pre < res:                                   
                                newu = calendar_con(int(str(res)[:lenght_pre-lenght_af]+ str(res_pre)),m,d,cal=times)                  
                                datures = dictcopy(datu3)

                                if newu['y'] != None:
                                    datures['y'][0]=newu['y']

                                if newu['m'] != None:
                                    datures['m'][0]=newu['m']

                                if newu['d'] != None:
                                    datures['d'][0]=newu['d']

                                datures['set']=None        
                                datu2.insert(0,datures)

                        elif mirindex[-1][1] == 'd':
                            datures = dictcopy(datu3)
                            datures['d'][0] = res_list1[0][0] 
                            datures['set']=None 
                            datu2.insert(0,datures)
            
            datu2.insert(0,datu3)

        res_list1 = res_list.copy()

    return datu2 

def dictcopy(dict2):
    dict1 = {}
    for xx in dict2:
        try:
            dict1[xx] = dict2[xx].copy()
        except:
            dict1[xx] = dict2[xx]

    return dict1

def calendar_con(y=None,m=None,d=None,cal='ce'):    
    cce = [(0, 'january'), (31, 'february'), (59, 'march'), (90, 'april'), (120, 'may'), (151, 'june'),
    (181, 'july'), (212, 'august'), (243, 'september'),(273, 'october'), (304,'november'), (334, 'december')]

    def days_ce(day):        
        year, remain = divmod(day,365.242199)
        monthi = 0
        for i,x in enumerate(cce):
            if remain > x[0]:
                monthi = i
            else:
                break 

        if int(year) == 0:
            out['y'] = None
        else:
            out['y'] = int(year)
        
        out['m'] = cce[monthi][1]

        rest_day = int(remain - cce[monthi][0])
        if rest_day == 0:
            out['d'] = None
        else:
            out['d'] = rest_day  

    def anno():
        if d:
            out['d'] = d
        if m:
            out['m'] = m

    def ce():
        anno()        
        if y:
            out['y'] = y    

    def bce():
        anno()
        if y:
            out['y'] = int(y*-1)

    def hijriday():
        days = 0
        if d:
            days += d            
        if m:
            monthh = False
            for x in hijri:
                if x == m:
                    monthh = True
                    break
                days += 29.53056
            if monthh == False:
                if m in y2:                    
                    days += cce[y2.index(m)][0]
        return days

    def ah():        
        days = hijriday()                  
        if y:
            days = days + ((0.970229 * y + 621.5643)*365.242199)
        days_ce(days)  

    def bh():
        days = hijriday()            
        if y:
            days = days + ((0.970229 * (y*-1) + 621.5643)*365.242199)
        days_ce(days)   

    out = {'d':d,'m':m,'y':y}
    switch = {'ce':ce,'bce':bce,'ah':ah,'bh':bh}        
    switch[cal]()
    
    return out

if __name__ == "__main__":    
    inpd = input('Date:')
    print(inpd,'\n',date_find(inpd))    