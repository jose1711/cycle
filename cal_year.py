# coding: koi8-r
#====================================================
#	Cycle - calendar for women
#	Distributed under GNU Public License
# Author: Oleg S. Gints (altgo@users.sourceforge.net)
# Home page: http://cycle.sourceforge.net
#===================================================    

import wx
import wx.calendar
import calendar
import operator

class Val:
    pass
    
MARK_BEGIN  = 1
MARK_FERT   = 1<<1
MARK_OVUL   = 1<<2
MARK_SAFESEX= 1<<3
MARK_TODAY  = 1<<4
MARK_NOTE   = 1<<5
MARK_PROG   = 1<<6
MARK_LAST   = 1<<7 #last cycle, conception begin
MARK_BIRTH  = 1<<8
MARK_TABLET = 1<<9 #1-st hormonal tablet
MARK_T22_28 = 1<<10 #tablets 22-28 or pause 7 days
MARK_NEXT_TABLET = 1<<11 

#-------------------- class Month_Cal -------------------
class Month_Cal(wx.calendar.GenericCalendarCtrl):
    def __init__(self, parent, id, dt, pos=wx.DefaultPosition,
		size=wx.DefaultSize, style=0 ):
		
	style = wx.calendar.CAL_NO_MONTH_CHANGE | wx.NO_BORDER
	if cycle.first_week_day==0:
	    style = style | wx.calendar.CAL_MONDAY_FIRST
	else:
	    style = style | wx.calendar.CAL_SUNDAY_FIRST
	try:
	    style = style | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION
	except NameError:
	    pass
		    
	wx.calendar.GenericCalendarCtrl.__init__(self, parent, id, dt, pos, size, style)
	self.SetBackgroundColour(wx.WHITE)
	self.SetHeaderColours(wx.BLACK,wx.WHITE)
	if '__WXMSW__' in wx.PlatformInfo:
	    font = self.GetFont()
	    font.SetFaceName("MS Sans Serif")
	    self.SetFont(font)
	
	self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
	self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
	self.Bind(wx.EVT_KEY_UP, self.OnKey)
	self.Bind(wx.EVT_KEY_DOWN, self.OnKey)
	self.d_click=wx.DateTime()#FromDMY(1, 0,2002)
	
    def OnLeftDown(self, event):
	#HitTest(Point pos) -> (result, date, weekday) 
	res,d,w=self.HitTest(event.GetPosition())
	if res==wx.calendar.CAL_HITTEST_DAY:
	    Val.frame.SetStatusText(info(d))

    def OnRightDown(self, event):
	res,d,w=self.HitTest(event.GetPosition())
	if res==wx.calendar.CAL_HITTEST_DAY:
	    #now d contain clicked day
	    self.d_click=d
	    menu = wx.Menu()
	    menu.Append(1, d.Format('%d %B'))
	    menu.AppendSeparator()
	    menu.AppendCheckItem(2, _('Beginning of cycle'))
	    menu.Check(2,is_set_mark(d, MARK_BEGIN, d.GetYear()))
	    menu.AppendCheckItem(5, _('1-st tablet'))
	    menu.Check(5,is_set_mark(d, MARK_TABLET, d.GetYear()))
	    if is_set_mark(d, MARK_BEGIN, d.GetYear()):
		menu.AppendCheckItem(3, _('Conception'))
		menu.Check(3,is_set_mark(d, MARK_LAST, d.GetYear()))
	    menu.AppendCheckItem(4, _('Note'))
	    menu.Check(4,is_set_mark(d, MARK_NOTE, d.GetYear()))
	    
	    self.Bind(wx.EVT_MENU, self.OnBegin, id=2)
	    self.Bind(wx.EVT_MENU, self.OnLast, id=3)
	    self.Bind(wx.EVT_MENU, self.OnNote, id=4)
	    self.Bind(wx.EVT_MENU, self.OnTablet, id=5)
	    self.PopupMenu(menu, event.GetPosition())
	    menu.Destroy()

    def OnBegin(self, event):
	if self.d_click in cycle.begin:
	    cycle.begin.remove(self.d_click)
	    if self.d_click in cycle.last:
		cycle.last.remove(self.d_click)
	    remove_mark(self.d_click, MARK_BEGIN, self.d_click.GetYear())
	    remove_mark(self.d_click, MARK_LAST, self.d_click.GetYear())
	else:
	    cycle.begin.append(self.d_click)
	    cycle.begin.sort()
	    add_mark(self.d_click, MARK_BEGIN, self.d_click.GetYear())
	Val.Cal.Draw_Mark()

    def OnLast(self, event):
  	if self.d_click in cycle.begin:
	    if self.d_click in cycle.last:
		cycle.last.remove(self.d_click)
		remove_mark(self.d_click, MARK_LAST, self.d_click.GetYear())
	    else:
		cycle.last.append(self.d_click)
		cycle.last.sort()
		add_mark(self.d_click, MARK_LAST, self.d_click.GetYear())
	    Val.Cal.Draw_Mark()
 
    def OnNote(self, event):
	txt=get_note(self.d_click)
	dlg = Note_Dlg(self, self.d_click.Format('%d %B'), txt)
	ret = dlg.ShowModal()
	t= dlg.Get_Txt()
	dlg.Destroy()
	if ret == wx.ID_OK:
	    add_note(self.d_click, t )
	    add_mark(self.d_click, MARK_NOTE, self.d_click.GetYear())
	elif ret == False:
	    remove_note(self.d_click)
	    remove_mark(self.d_click, MARK_NOTE, self.d_click.GetYear())
	elif ret ==wx.ID_CANCEL:
	    return
	Val.Cal.Draw_Mark()

    def OnTablet(self, event):
	if self.d_click in cycle.tablet:
	    cycle.tablet.remove(self.d_click)
	    remove_mark(self.d_click, MARK_TABLET, self.d_click.GetYear())
	else:
	    cycle.tablet.append(self.d_click)
	    cycle.tablet.sort()
	    add_mark(self.d_click, MARK_TABLET, self.d_click.GetYear())
	Val.Cal.Draw_Mark()

    def OnKey(self, event):
	k=event.GetKeyCode()
	if k==wx.WXK_LEFT or k==wx.WXK_RIGHT or \
	   k==wx.WXK_UP or k==wx.WXK_DOWN:
	    pass
	else:
	    event.Skip()
	    

#-------------------- class Cal_Year -------------------
class Cal_Year(wx.ScrolledWindow):
    def __init__(self, parent):
	wx.ScrolledWindow.__init__(self, parent,-1)
#	self.SetScrollbars(20, 20, 39, 40)
	self.SetBackgroundColour(wx.NamedColour('LIGHT BLUE'))
	
	dt=wx.DateTime_Today()
	self.year=dt.GetYear()

	self.day_of_year=[]
	self.month=[]
	Val.Cal=self
	self.Init_Year()
#	self.Draw_Mark()


    def Inc_Year(self):
	self.year += 1
	self.Draw_Year()
	reset_mark(self.year)
	self.Draw_Mark()

    def Dec_Year(self):
	self.year -= 1
	self.Draw_Year()
	reset_mark(self.year)
	self.Draw_Mark()

    def Set_Year(self,year):
	self.year=year
	self.Draw_Year()
	reset_mark(self.year)
	self.Draw_Mark()


    def Init_Year(self):
	m=0
	box = wx.BoxSizer(wx.VERTICAL)
	box.Add(wx.StaticLine(self,-1,style=wx.LI_HORIZONTAL), 0, wx.EXPAND )
	for y in range(3):
	    row_box=wx.BoxSizer(wx.HORIZONTAL)
	    for x in range(4):
		t=wx.DateTimeFromDMY(1, m, self.year)
		id=wx.NewId()
		self.month.append(Month_Cal(self, id, t, ))
		row_box.Add(self.month[m], 0, wx.ALL, 5)
		m+=1
	    box.Add(row_box, 0, wx.LEFT|wx.RIGHT, 10)
	
	self.SetAutoLayout(True)
        self.SetSizer(box)
	box.Fit(self)
	w = box.GetSize().GetWidth()
	h = box.GetSize().GetHeight()
	Val.frame.SetClientSize( wx.Size(w+10,h+90) )
	self.SetScrollbars(20, 20, w/20, h/20)

    def Draw_Year(self):
	Val.frame.SetTitle(cycle.name+" - "+str(self.year))
	for m in range(12):
	    t=wx.DateTimeFromDMY(1, m, self.year)
	    self.month[m].EnableMonthChange(True)
	    self.month[m].SetDate(t)
	    self.month[m].EnableMonthChange(False)
	    self.month[m].Refresh()

    def Draw_Mark(self):
	
	f_norm=self.month[1].GetFont()
	f_norm.SetUnderlined(False)
	f_ul=self.month[1].GetFont()
	f_ul.SetUnderlined(True)

	dt=wx.DateTime_Today()
	if self.year==dt.GetYear():
	    add_mark(dt, MARK_TODAY, self.year)

	calc_fert(self.year)
	calc_tablet(self.year)
	k=1
	for m in range(12):
	    sel_hide=True# need hide selection
	    for d in range(1,wx.DateTime_GetNumberOfDaysInMonth(m, self.year)+1):
		can_hide=True
		lab=cycle.mark.get(k,0)
 		at=wx.calendar.CalendarDateAttr(wx.BLACK)
		at.SetBackgroundColour(wx.WHITE)
		at.SetFont(f_norm)
		
		dt=wx.DateTimeFromDMY(d, m, self.year)
		if not dt.IsWorkDay(): # mark weekend
		    at.SetTextColour(wx.NamedColour('firebrick'))

		if lab & MARK_BEGIN:
		    at.SetBackgroundColour(cycle.colour_set['begin'])
		    at.SetTextColour(wx.WHITE)
		
		if lab & MARK_PROG:
		    at.SetBackgroundColour(cycle.colour_set['prog begin'])
		    at.SetTextColour(wx.BLACK)

		if lab & MARK_SAFESEX and (cycle.disp==0 or cycle.disp==2):
		    at.SetBackgroundColour(cycle.colour_set['safe sex'])
		    
		if lab & MARK_FERT and (cycle.disp==1 or cycle.disp==2):
		    at.SetBackgroundColour(cycle.colour_set['fertile'])

		if lab & MARK_OVUL and (cycle.disp==1 or cycle.disp==2):
		    at.SetBackgroundColour(cycle.colour_set['ovule'])
	        
		if lab & MARK_TODAY :
		    at.SetBorderColour(wx.NamedColour('NAVY'))
		    at.SetBorder(wx.calendar.CAL_BORDER_SQUARE)
		    can_hide=False

		if lab & MARK_LAST :
		    at.SetBackgroundColour(cycle.colour_set['conception'])

		if lab & MARK_NOTE:
		    at.SetFont(f_ul)
		    can_hide=False

   		if lab & MARK_BIRTH :
		    at.SetBackgroundColour(cycle.colour_set['ovule'])
		    
   		if lab & MARK_TABLET :
		    at.SetBackgroundColour(cycle.colour_set['1-st tablet'])
		
   		if lab & MARK_T22_28 :
		    at.SetBackgroundColour(cycle.colour_set['pause'])
   		
		if lab & MARK_NEXT_TABLET :
		    at.SetBackgroundColour(cycle.colour_set['next 1-st tablet'])
		
		if sel_hide and can_hide:
		    #we can hide selection when don't use border and underlined
		    sel_hide=False
		    self.month[m].SetDate(dt)
		    self.month[m].SetHighlightColours(at.GetTextColour(),
				at.GetBackgroundColour())

		self.month[m].SetAttr(d,at)

		k+=1

	# so visual refresh is more fast
	for m in range(12):
	    self.month[m].Refresh()


#-------------------- work with cycle -------------------
class cycle:
    begin=[]
    last=[]
    tablet=[]
    period=28
    mark={}
    passwd="123"
    name="empty"
    file="empty"
    by_average=False
    disp=0
    first_week_day=0
    note={}
    colour_set={}
#    colour_set={'begin':wx.NamedColour('red'),
#	'prog begin':wx.NamedColour('pink'),
#        'conception':wx.NamedColour('MAGENTA'),
#	'safe sex':wx.NamedColour('wheat'),
#	'fertile':wx.NamedColour('green yellow'),
#	'ovule':wx.NamedColour('SPRING GREEN'),
#	'1-st tablet':wx.NamedColour('gold'),
#	'pause':wx.NamedColour('light blue'),
#	'next 1-st tablet':wx.NamedColour('pink')}

def min_max(i):
    """Return length max and min of 6 last cycles
    from i item cycle.begin"""

    if len(cycle.begin)<2 or i==0:
	return cycle.period, cycle.period

    last_6=[]
    for k in range(i,0,-1):
	span=(cycle.begin[k]-cycle.begin[k-1]+wx.TimeSpan.Hours(1)).GetDays()
	# wx.TimeSpan.Hours(1) - компенсация потери часа на летнем времени
	if 20 < span <36: # остальное в расчет не берем
	    last_6.append(span)
	    if len(last_6)>=6: break

    if cycle.by_average and len(last_6) != 0:
	s=float(reduce( operator.add, last_6 )) # sum of last_6
	cycle.period=int(round(s/len(last_6),0))
	
    if last_6==[]:
	return cycle.period, cycle.period
    return min(last_6),max(last_6)


def calc_fert(year):
    """Рассчитывает фертильные периоды для year"""

    for k in cycle.mark.keys():
	cycle.mark[k]=cycle.mark[k] & ~MARK_FERT &\
	~MARK_OVUL & ~MARK_PROG & ~MARK_SAFESEX & ~MARK_BIRTH &\
	~MARK_T22_28 & ~MARK_NEXT_TABLET
    
    #по прошлым циклам
    if cycle.begin==[]: return
    year_b=wx.DateTimeFromDMY(1, 0, year)
    year_e=wx.DateTimeFromDMY(31, 11, year)
    for d in cycle.begin:
	i=cycle.begin.index(d)
	if i<len(cycle.begin)-1:
	    if (cycle.begin[i+1]-cycle.begin[i]+wx.TimeSpan.Hours(1)).GetDays()<21:
		# wx.TimeSpan.Hours(1) - потеря одного часа при переходе на
		# летнее время
		continue

	min, max = min_max(i)
	begin = d+wx.DateSpan.Days( min-18 ) # begin fertile
	end = d+wx.DateSpan.Days( max-11 ) # end fertile
        ovul=end-wx.DateSpan.Days(((max-11)-(min-18))/2) #day of ovul
	if year_b<=ovul<=year_e:
	    add_mark(ovul, MARK_OVUL, year)

	start=d+wx.DateSpan_Day()
	if i<len(cycle.begin)-1:
	    last_cycle=(cycle.begin[i+1]-cycle.begin[i]+wx.TimeSpan.Hours(1)).GetDays()
	    if last_cycle>35:
		stop=d+wx.DateSpan.Days( 35 )
	    else:
		stop=cycle.begin[i+1]-wx.DateSpan_Day()
	else:
	    stop=d+wx.DateSpan.Days( cycle.period-1 )

	if (stop<year_b or start>year_e) and (d not in cycle.last):
	    continue
	f=start
	while f.IsBetween(start, stop):
	    if f.IsBetween(begin, end):
		add_mark(f, MARK_FERT, year)
	    else:
		add_mark(f, MARK_SAFESEX, year)
	    f=f+wx.DateSpan_Day()
	
	if d in cycle.last: # calc birthday
	    birth = d+wx.DateSpan.Days(280+cycle.period-28)
	    if i<len(cycle.begin)-1: # not last item
		if birth < cycle.begin[i+1]:
		    add_mark(birth, MARK_BIRTH, year)
	    else: #last item
		add_mark(birth, MARK_BIRTH, year)
		return
		
    # prognosis to future cycles
    cycle.prog_begin=[]
    d=d+wx.DateSpan.Days( cycle.period )
    while d.GetYear()<=year:
	if cycle.tablet<>[] and cycle.tablet[-1]<=d and \
	    cycle.begin[-1]<=cycle.tablet[-1]: return
	if d.GetYear()==year: 
	    #	    cycle.prog_begin.append(d)
	    add_mark(d, MARK_PROG, year)

	begin = d+wx.DateSpan.Days( min-18 ) #начало периода
	end = d+wx.DateSpan.Days( max-11 ) #конец периода
	ovul=end-wx.DateSpan.Days(((max-11)-(min-18))/2) #day of ovul
	if year_b<=ovul<=year_e:
	    add_mark(ovul, MARK_OVUL, year)

	start=d+wx.DateSpan.Day()
	stop=d+wx.DateSpan.Days( cycle.period-1 )
	d=d+wx.DateSpan.Days( cycle.period )
	
        if stop<year_b or start>year_e : continue
	
	f=start
	while f.IsBetween(start, stop):
	    if f.IsBetween(begin, end):
		add_mark(f, MARK_FERT, year)
	    else:
		add_mark(f, MARK_SAFESEX, year)
	    f=f+wx.DateSpan_Day()


def calc_tablet(year):
    """calculation result of using hormonal tablets"""
    
    if cycle.tablet==[]: return
    year_b=wx.DateTimeFromDMY(1, 0, year)
    year_e=wx.DateTimeFromDMY(31, 11, year)
    for d in cycle.tablet:
	i=cycle.tablet.index(d)
	if i<len(cycle.tablet)-1:
	    if (cycle.tablet[i+1]-cycle.tablet[i]+wx.TimeSpan.Hours(1)).GetDays()<28:
		#incorrect using - must more 28 days
		continue
	for k in range(28):
	    remove_mark(d+wx.DateSpan.Days(k), MARK_PROG | MARK_FERT |
	    MARK_NEXT_TABLET | MARK_OVUL | MARK_SAFESEX | MARK_BIRTH, year)
        for k in range(21,28):
	    add_mark(d+wx.DateSpan.Days(k), MARK_T22_28, year)
	add_mark(d+wx.DateSpan.Days(28), MARK_NEXT_TABLET, year)
		

	    
def add_mark(date, mark, year):
    if date.GetYear()==year:
        k=date.GetDayOfYear()
	cycle.mark[k]=cycle.mark.get(k,0) | mark

def remove_mark(date, mark, year):
    if date.GetYear()==year:
        k=date.GetDayOfYear()
	cycle.mark[k]=cycle.mark.get(k,0) & ~mark


def is_set_mark(date, mark, year):
    if date.GetYear()==year:
        k=date.GetDayOfYear()
	return cycle.mark.get(k,0) & mark
    else:
	return False


def reset_mark(year):
    cycle.mark.clear()
    for k in cycle.begin:
	if k.GetYear()==year:
	    add_mark(k, MARK_BEGIN, year)
    for k in cycle.last:
	if k.GetYear()==year:
	    add_mark(k, MARK_LAST, year)
    for k in cycle.tablet:
	if k.GetYear()==year:
	    add_mark(k, MARK_TABLET, year)
    for k in cycle.note.keys():
	if str(year)==k[0:4]:
	    d=wx.DateTimeFromDMY(int(k[6:8]), int(k[4:6])-1, int(k[0:4]))
	    add_mark(d, MARK_NOTE, year)
    

def info(day):
    """Возвращает строку информации по переданной дате."""

    s=day.Format('%d %B')
    if cycle.tablet<>[]:
	for d in cycle.tablet:
	    if day.IsBetween(d, d+wx.DateSpan.Days(28)):
		t=(day-d+wx.TimeSpan.Hours(1)).GetDays()+1
		s+=" - "
		if t<=28:
		    s+=_('tablet N ')+str(t)
		if 22<= t <=28:
		    s+=_(' or pause')
		if t==29:
		    s+=_('next 1-st tablet')
		return s
    
    if cycle.begin==[]: return s
    if day<cycle.begin[0]: return s #день до начала первого цикла

    find=0
    gestation=0
    for d in cycle.begin:
	if day<d:
	    find=1
	    break

    if find==0:
	if d in cycle.last:
	    gestation=1
	    d2=d
	else:
	    #ищем в будущих периодах
	    while d<=day:
		if cycle.tablet<>[] and cycle.tablet[-1]<=d and \
		    cycle.begin[-1]<=cycle.tablet[-1]: return s
		d=d+wx.DateSpan.Days(cycle.period)
	    find=2


    #найдем следующее начало цикла
    if find==1:
	i=cycle.begin.index(d)
	d2=cycle.begin[i-1]
	if d2 in cycle.last:
	    gestation=1
    elif find==2:
        d2=d-wx.DateSpan.Days(cycle.period)
    
    if gestation:
	k=(day-d2+wx.TimeSpan.Hours(1)).GetDays()+1
	w=(k-1)/7
	s+=" - "+str(k)+_('% day of gestation, ')+str(w)
	if w == 1: s+=_('1 week')
	else: s+=_('% weeks')
	s+=' + '+str(k-w*7)
	if (k-w*7) == 1: s+=_('1 day')
	else: s+=_('% days')
    else:
	p=(d-d2+wx.TimeSpan.Hours(1)).GetDays()
	k=(day-d2+wx.TimeSpan.Hours(1)).GetDays()+1

	d=d-wx.DateSpan.Day()
    s+=" - "+_('%s day of period from %s to %s') % (str(k),d2.Format('%d %b'), d.Format('%d %b')) +' ' + _('length %s days') % (str(p))
    return s


#-------------------- Note --------------------
def add_note(date,txt):
    d=date.Format('%Y%m%d')
    cycle.note[d]=txt

def get_note(date):
    d=date.Format('%Y%m%d')
    return cycle.note.get(d,"")

def remove_note(date):
    d=date.Format('%Y%m%d')
    if cycle.note.has_key(d):
	del cycle.note[d]

#-------------------- Report --------------------
def report_year(year):
    if cycle.first_week_day == 0:
	calendar.setfirstweekday(calendar.MONDAY)
	days = range(1,7) + [0]
    else:
	calendar.setfirstweekday(calendar.SUNDAY)
	days = range(7)
    #sp=' '
    s='<html><body><H3 align=center>%s</H3><pre>' % year
    dn = ''
    for i in days:
	dn += '%.2s ' % wx.DateTime_GetWeekDayName(i, wx.DateTime.Name_Abbr)
    dn = dn[:-1]
    dn = '%s  %s  %s<br>\n' % (dn, dn, dn)  # week days names
    for m in range(0,12,3):
	s += '<br>\n%s  %s  %s<br>\n' % (
	    wx.DateTime_GetMonthName( m ).center(20),
	    wx.DateTime_GetMonthName( m+1 ).center(20),
	    wx.DateTime_GetMonthName( m+2 ).center(20) )
	s += dn
	data = []
	h = 0
	for k in range(m+1, m+4):
	    cal = calendar.monthcalendar(year, k)
	    data.append( calendar.monthcalendar(year, k) )
	    if h < len(cal):
		h = len(cal)
	for i in range(h):
	    d_str = ''
	    for n in range(3):
		for k in range(7):
		    if i< len(data[n]):
			day_of_month = data[n][i][k]
			if day_of_month:
			    d = wx.DateTimeFromDMY(day_of_month, m+n, year)
			    if is_set_mark(d, MARK_BEGIN, d.GetYear()):
				d_str += '<u>%2s</u> ' % day_of_month
			    else:
				d_str += '%2s ' % day_of_month
			else:
			    d_str += '   '
		    else:
			d_str += '   '
		d_str += ' '
	    s += d_str[:-2] +'<br>\n'
    

    s+='</pre></body></html>'
    print s
    return s

def report_year_ical(year, fileobj):
    import socket
    hostname = socket.gethostname()

    def get_string(mark):
        if mark & MARK_LAST: return _("Conception")
        elif mark & MARK_BEGIN: return _("Beginning of cycle")
        elif mark & MARK_PROG: return _("Probable beginning of cycle")
        elif mark & MARK_TABLET: return _("1-st tablet")
        elif mark & MARK_OVUL: return _("Ovulation")
        elif mark & MARK_BIRTH: return _("Birth")
        else: return ""

    def make_event(description, mark, date):
        date2 = date + wx.TimeSpan.Days(1)
        datestr = "%04d%02d%02d" % (
            date.GetYear(), date.GetMonth() + 1, date.GetDay())
        datestr2 = "%04d%02d%02d" % (
            date2.GetYear(), date2.GetMonth() + 1, date2.GetDay())
        uid = "UID:cycle-%d-%sZ@%s" % (mark, datestr, hostname)
        return ["BEGIN:VEVENT", uid,
                "DTSTART;VALUE=DATE:" + datestr,
                "DTEND;VALUE=DATE:" + datestr2,
                "SUMMARY:" + description,
                "DESCRIPTION:" + description,
                "CLASS:PUBLIC",
                "END:VEVENT"]

    s = ["BEGIN:VCALENDAR",
         "CALSCALE:GREGORIAN",
         "PRODID:-//Cycle//NONSGML Cycle//EN",
         "VERSION:2.0"]

    days = cycle.mark.items()
    days.sort()
    for day, marks in days:
        if get_string(marks):
            d = wx.DateTime()
            d.SetYear(year)
            d.SetToYearDay(day)
            s.extend(make_event(get_string(marks), marks, d))

    s.append("END:VCALENDAR")

    print >>fileobj, "\n".join(s)

#-------------------- Add import --------------------
from dialogs import Note_Dlg 
   
