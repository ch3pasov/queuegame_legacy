
def wnline(f, text):
	f.write(text)
	f.write('\n')

def timetoscore(hour,minute):
	#print('TIMETOSCORE')
	#print(hour)
	#print(minute)
	if hour[0] == 0:
		hour = hour[1]
	if minute[0] == 0:
		minute = minute[1]
	return(60*int(hour)+int(minute))
	
def scoretotime(score):
	hour=str(score // 60)
	minute=str(score % 60)
	if len(hour)==1:
		hour='0'+hour
	if len(minute)==1:
		minute='0'+minute
	return(hour, minute)

def scoretogoodtime(score):
	t=scoretotime(score)
	return(t[0]+':'+t[1])

#print(timetoscore(9, 55))
#print(scoretotime(595))

def parse_rows(lines):
	"""Parse HH MM NAME rows; whitespace separates fields and blank rows are skipped."""
	rows = []
	for line_number, line in enumerate(lines, 1):
		fields = line.split()
		if not fields:
			continue
		if len(fields) != 3:
			raise ValueError(f"Line {line_number}: expected hour minute name (three fields)")
		try:
			hour, minute = int(fields[0]), int(fields[1])
		except ValueError:
			raise ValueError(f"Line {line_number}: hour and minute must be integers") from None
		if not (0 <= hour <= 23 and 0 <= minute <= 59):
			raise ValueError(f"Line {line_number}: time must be between 00:00 and 23:59")
		rows.append([len(rows), timetoscore(fields[0], fields[1]), fields[2]])
	return rows


def convert(bd, f):
	playersnum=len(bd)

	#print(playersnum)
	#print(bd)


	op=600 #время открытия
	cl=660 #время закрытия
	procedure=10 #время получения услуги

	ochered=[] #список людей в очереди
	inside=-1 #кто сейчас внутри офиса
	fate=[[i,-1,-1] for i in range (playersnum)] #айди, вход, выход
	# bd - айди, время, имя


	for time in range(1440): #начинаем симуляцию
		if time==op: #открытие
			wnline(f,'---')
			wnline(f,scoretogoodtime(time) + ' - ' + 'Кабинет открылся!')
			wnline(f,'---')
		if time==cl: #закрытие
			wnline(f,'---')
			wnline(f,scoretogoodtime(time) + ' - ' + 'Кабинет закрылся!')
			wnline(f,'---')
		for aidi in range (playersnum): 
			if bd[aidi][1]==time: #человек зашёл в очередь! ШОК!
				ochered.append(aidi)
				fate[aidi][1]=time
				wnline(f,scoretogoodtime(time) + ' - ' + str(bd[aidi][2]) + ' подошёл к офису!')
		for aidi in range (playersnum): 
			if inside != -1: #проверим, не пора ли челику выйти 
				if time-fate[inside][1]==procedure:
					fate[inside][2]=time
					wnline(f,scoretogoodtime(time) + ' - ' + str(bd[inside][2]) + ' вышел из кабинета!')
					inside=-1
			if (inside == -1) and (len(ochered) != 0): #если кого-то можно запустить
				if (op <= time) and (time < cl): #и кабинет открыт
					inside=ochered.pop(0)
					fate[inside][1]=time
					wnline(f,scoretogoodtime(time) + ' - ' + str(bd[inside][2]) + ' вошёл в кабинет!')
					
					
	#print(fate)
	#print(ochered)

	wnline(f,'')
	wnline(f,'-----РЕЗУЛЬТАТЫ-----')
	wnline(f,'')

	lose=[]#список оставшихся в очереди, уже отсортированный. Время прихода, айди, имя.
	lose_id=[]#только айдишники
	for i in ochered:
		lose_id.append(i)
		lose.append([bd[i][1], i, bd[i][2]])
	losenum=len(lose_id) #число проигравших

	win=[]#список прошедших кабинет. Время ожидания, время прихода, айди, имя.
	win_id=[]#только айдишники
	for i in range(playersnum):
		if fate[i][2]!=-1:
			win_id.append(i)
			win.append([fate[i][2]-bd[i][1],bd[i][1], i, bd[i][2]])
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


def main(input_path='bd', output_path='out'):
	with open(input_path, 'r') as source:
		rows = parse_rows(source)
	# Validate the complete input before opening/truncating the output.
	with open(output_path, 'w') as output:
		convert(rows, output)


if __name__ == '__main__':
	try:
		main()
	except ValueError as error:
		raise SystemExit(str(error))
