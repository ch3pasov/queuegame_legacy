from math import sqrt

def swap(i,j):
	a=ochered[j]
	ochered[j]=ochered[i]
	ochered[i]=a
	
def wnline(f, text): #вписать строчку текста
	f.write(text)
	f.write('\n')

def timetoscore(hour,minute): #перевести чч мм во время-число
	if str(hour)[0] == 0:
		hour = str(hour)[1]
	if str(minute)[0] == 0:
		minute = str(minute)[1]
	return(60*int(hour)+int(minute))
	
def scoretotime(score): #перевести время-число во (часов, минут)
	hour=str(score // 60)
	minute=str(score % 60)
	if len(hour)==1:
		hour='0'+hour
	if len(minute)==1:
		minute='0'+minute
	return(hour, minute)

def scoretogoodtime(score): #перевести время-число в текст 'чч:мм'
	t=scoretotime(score)
	return(t[0]+':'+t[1])

def askprocedure(): #время процедуры от параметра
	return(int((cl-op-(lunch_finish-lunch_start))/(0.83 * playersnum)))

f=open('bd', 'r') #переносим бд в программу
bd=[] #база данных
label=0
for line in f:
	stroka=line.split(' ')
	stroka = [slovo.rstrip() for slovo in stroka]
	bd.append([label , timetoscore(stroka[0] , stroka[1]) , int(stroka[2]) , stroka[3]])
	label+=1
f.close()

print(bd)

playersnum=len(bd) #число игроков
op=955 #время открытия
cl=1060 #время закрытия
lunch_start=-1 #время начала ланча, -1 если его нет
lunch_finish=-1 #аналогично, конец ланча
#procedure=askprocedure() #время получения услуги, если для каждого время своё - комментируем

#print(procedure)

ochered=[] #список людей в очереди
inside=-1 #кто сейчас внутри офиса, -1 - никто
fate=[[i,-1,-1] for i in range (playersnum)] #айди, вход, выход
# bd                                          айди, время, k ,имя


f=open('out', 'w')

#wnline(f, 'Сегодня кабинет обслуживает человека за ' + str(askprocedure()) + ' минут!')
for time in range(1440): #начинаем симуляцию
	if time==op: #открытие
		wnline(f,'---')
		wnline(f,scoretogoodtime(time) + ' - ' + 'Кабинет открылся!')
		wnline(f,'---')
	if time==cl: #закрытие
		wnline(f,'---')
		wnline(f,scoretogoodtime(time) + ' - ' + 'Кабинет закрылся!')
		wnline(f,'---')
	if time==lunch_start: #обед_начало
		wnline(f,'---')
		wnline(f,scoretogoodtime(time) + ' - ' + 'обеденный перерыв!')
		if inside != -1: #кто-то в кабинете!
			wnline(f,scoretogoodtime(time) + ' - В этот момент ' + str(bd[inside][-1]) + ' был в кабинете! Земля тебе пухом.')
	if time==lunch_finish: #обед_конец
		wnline(f,'---')
		wnline(f,scoretogoodtime(time) + ' - ' + 'конец обеденного перерыва!')

	for aidi in range (playersnum): #новые пришедшие
		if bd[aidi][1]==time:
			ochered.append(aidi)
			fate[aidi][1]=time
			wnline(f, scoretogoodtime(time) + ' - #' + str(len(ochered)) + ' ' + str(bd[aidi][-1]) + ' ↪️ 🏠! k=' +str(bd[aidi][2]))
			if bd[aidi][2]<=len(ochered):
				wnline(f, bd[ochered[bd[aidi][2]-1]][-1] + ' ↔️ ' + bd[ochered[0]][-1])
				swap(0, bd[aidi][2]-1)
			else:
				wnline(f, 'k > ' + str(len(ochered)) + ' ☹️️')
			#wnline(f,str(ochered))
	if inside != -1: #проверим, не пора ли челику выйти 
		if time-fate[inside][1]>=procedure:
			if not(lunch_start<=time and time<lunch_finish):
				fate[inside][2]=time
				wnline(f,scoretogoodtime(time) + ' - ' + str(bd[inside][-1]) + ' ⬅️ 🛎 ! ⌚️ - ' + scoretogoodtime(time-bd[inside][1]))
				inside=-1
	if (op <= time) and (time < cl): #если кабинет открыт
		if not(lunch_start<=time and time<lunch_finish) or lunch_start==-1: #и не ланч
			if (inside == -1) and (len(ochered) != 0): #и кого-то можно запустить			
				procedure=askprocedure()
				inside=ochered.pop(0)
				fate[inside][1]=time
				wnline(f,scoretogoodtime(time) + ' - ' + str(bd[inside][-1]) + ' ➡️ 🛎 !')
				wnline(f, str(len(ochered)) + 'x😀. ⏳ - ' + scoretogoodtime(procedure))
				
				
				
#print(fate)
#print(ochered)

wnline(f,'')
wnline(f,'-----РЕЗУЛЬТАТЫ-----')
wnline(f,'')

lose=[]#список оставшихся в очереди, уже отсортированный. Время прихода, айди, имя.
lose_id=[]#только айдишники
for i in ochered:
	lose_id.append(i)
	lose.append([bd[i][1], i, bd[i][-1]])
losenum=len(lose_id) #число проигравших

win=[]#список прошедших кабинет. Время ожидания, время прихода, айди, имя.
win_id=[]#только айдишники
for i in range(playersnum):
	if fate[i][2]!=-1:
		win_id.append(i)
		win.append([fate[i][2]-bd[i][1],bd[i][1], i, bd[i][-1]])
win.sort()
winnum=len(win) #число победивших
win_id=[win[i][2] for i in range(winnum)]

wnline(f,'Не успели:')
for i in range(losenum):
	wnline(f,'(' + scoretogoodtime(lose[i][0]) + ') - ' + lose[i][2] + '.')
wnline(f,'Успели:')
for i in range(winnum):
	wnline(f,scoretogoodtime(win[i][0]) + ' (' + scoretogoodtime(win[i][1]) + ') - ' + win[i][3] + '.')
#print(lose,lose_id,win,win_id)

wnline(f,'')
wnline(f,'MVP сегодняшней очереди:')

if winnum !=0:
	wnline(f,win[0][3])
else:
	wnline(f,'Никто ¯\_(ツ)_/¯')
