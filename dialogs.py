# coding: koi8-r
#====================================================
#	Cycle - calendar for women
#	Distributed under GNU Public License
# Author: Oleg S. Gints (altgo@users.sourceforge.net)
# Home page: http://cycle.sourceforge.net
#===================================================    
import warnings
# deprecated since release 2.3
warnings.filterwarnings("ignore",
                        category=RuntimeWarning,
                        message='.*tempnam is a potential security risk to your program', module=__name__)

import os
import wx
import wx.html
import cPickle
from cal_year import cycle , Val
from save_load import Load_Cycle, get_f_name, set_color_default
from set_dir import *
#---------------------------------------------------------------------------
class Settings_Dlg(wx.Dialog):
    def __init__(self, parent):
	wx.Dialog.__init__(self,parent,-1, _('Settings'), wx.DefaultPosition)
	self.Centre(wx.BOTH)
	#======================
	box = wx.BoxSizer(wx.VERTICAL)
        
	b1=wx.StaticBoxSizer(wx.StaticBox(self,-1,_('Length of cycle')),wx.VERTICAL)
	i=wx.NewId()
	self.cb1 = wx.CheckBox(self, i, _(' by average'), style=wx.NO_BORDER)
	b1.Add(self.cb1, 0, wx.ALL, 5)
	self.Bind(wx.EVT_CHECKBOX, self.By_Average, id=i)
	self.cb1.SetValue(cycle.by_average)

	b2 = wx.BoxSizer(wx.HORIZONTAL)
	i=wx.NewId()
	self.sc = wx.SpinCtrl(self, i, "", size=wx.Size(50, -1))
        self.sc.SetRange(21,35)
        self.sc.SetValue(cycle.period)
	self.sc.Enable(not self.cb1.GetValue())
	b2.Add(self.sc, 0)
	b2.Add(wx.StaticText(self, -1, _(' days in cycle')), 0)
	b1.Add(b2, 0, wx.ALL, 5)
	box.Add(b1, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
	#======================
	self.rb = wx.RadioBox(self, -1, _('Display'),
	    choices=[_('safe sex days'),_('fertile days'),_('both')],
	    majorDimension=1, style=wx.RA_SPECIFY_COLS)
	box.Add(self.rb, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
	self.rb.SetSelection(cycle.disp)

	#======================
	self.rb1 = wx.RadioBox(self, -1, _('First week day'),
	    choices=[_('monday'),_('sunday')],
	    majorDimension=1, style=wx.RA_SPECIFY_COLS)
	box.Add(self.rb1, 0, wx.EXPAND|wx.ALL, 10)
	self.rb1.SetSelection(cycle.first_week_day)

	#======================
	i=wx.NewId()
	txt1=_('Colours')
	txt2=_('Change password')
	w1,h=self.GetTextExtent(txt1)
	w2,h=self.GetTextExtent(txt2)
	w = max(w1, w2)
	box.Add(wx.Button(self, i, txt1, size=wx.Size(w+10, -1)), 0, wx.ALIGN_CENTER)
	self.Bind(wx.EVT_BUTTON, self.OnColours, id=i)
	#======================
	i=wx.NewId()
	box.Add(wx.Button(self, i, txt2, size=wx.Size(w+10, -1)), 0, wx.TOP|wx.ALIGN_CENTER,10)
	self.Bind(wx.EVT_BUTTON, self.OnChangePasswd, id=i)

	#======================
	but_box=wx.BoxSizer(wx.HORIZONTAL)
	i=wx.NewId()
	but_box.Add(wx.Button(self, i, _('Ok')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnOk, id=i)
	
	i=wx.NewId()
	but_box.Add(wx.Button(self, i, _('Cancel')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnCancel, id=i)

	box.Add(but_box, 0, wx.ALIGN_CENTER)

	self.SetAutoLayout(True)
        self.SetSizer(box)
	box.Fit(self)

    def By_Average(self, event):
	if event.Checked():
	    self.sc.Enable(False)
	else:
	    self.sc.Enable(True)

    def OnOk(self, event):
	if not 21<=self.sc.GetValue()<=35:
	    dlg = wx.MessageDialog(self, _('Period of cycle is invalid!'),
            _('Error!'), wx.OK |wx.ICON_ERROR )
	    dlg.ShowModal()
	    dlg.Destroy()
	    return
	cycle.period=self.sc.GetValue()
	cycle.by_average=self.cb1.GetValue()
	cycle.disp=self.rb.GetSelection()
	cycle.first_week_day=self.rb1.GetSelection()
	self.EndModal(wx.ID_OK)

    def OnCancel(self, event):
	self.EndModal(wx.ID_CANCEL)

    def OnChangePasswd(self, event):
        dlg = Ask_Passwd_Dlg(self)
        dlg.ShowModal()
	dlg.Destroy()

    def OnColours(self, event):
        dlg = Colours_Dlg(self)
        dlg.ShowModal()
	dlg.Destroy()
#---------------------------------------------------------------------------
class Ask_Passwd_Dlg(wx.Dialog):
    def __init__(self, parent):
	wx.Dialog.__init__(self,parent,-1, _('Password'))

	#======================
	box = wx.BoxSizer(wx.VERTICAL)
        
	box.Add(wx.StaticText(self, -1, _('Enter your password')), 0,
	    wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.RIGHT, 10)
	self.pass1 = wx.TextCtrl(self, -1, "", wx.Point(10, 30),
		size=(130, -1), style=wx.TE_PASSWORD)
	box.Add(self.pass1, 0, wx.ALIGN_CENTER|wx.ALL, 10)
	
	box.Add(wx.StaticText(self, -1, _('Once more...')), 0,
	    wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, 10)
	self.pass2 = wx.TextCtrl(self, -1, "", wx.Point(10, 80),
		size=(130, -1), style=wx.TE_PASSWORD)
	box.Add(self.pass2, 0, wx.ALIGN_CENTER|wx.ALL, 10)
	

	b1=wx.BoxSizer(wx.HORIZONTAL)
	i=wx.NewId()
	b1.Add(wx.Button(self, i, _('Ok')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnOk, id=i)
	
	i=wx.NewId()
	b1.Add(wx.Button(self, i, _('Cancel')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnCancel, id=i)
	self.pass1.SetFocus()
	box.Add(b1, 0, wx.ALIGN_CENTER)

	self.SetAutoLayout(True)
        self.SetSizer(box)
	box.Fit(self)
	

    def OnOk(self, event):
	err=""
	if self.pass1.GetValue()=="" or self.pass2.GetValue()=="":
	    err=_('Password must be not EMPTY!')
	if self.pass1.GetValue() != self.pass2.GetValue():
	    err=_('Entering password don\'t match!')
	if err !=  "":
	    dlg = wx.MessageDialog(self, err,
            _('Error!'), wx.OK |wx.ICON_ERROR )
	    dlg.ShowModal()
	    dlg.Destroy()
	    return
	cycle.passwd=self.pass1.GetValue()
	self.EndModal(wx.ID_OK)

    def OnCancel(self, event):
	self.EndModal(wx.ID_CANCEL)


#---------------------------------------------------------------------------
def get_users():
    #Get list of users
    magic_str="UserName="
    users=[] #array of (user, file) name
    p, f_name=get_f_name()
    if os.path.exists(p):
        files=os.listdir(p)
        for f in files:
            fd=open(os.path.join(p, f),"rb")
            tmp=fd.read(len(magic_str))
            if tmp == magic_str:
                tmp=fd.read(100)
                n=tmp.find("===") #find end string
                if n <> -1:
                    users.append((cPickle.loads(tmp[:n]), f))
                else: # old format, user_name=file_name
                    users.append((f,f))
        #if not users:
        #users=[(_('empty'),"empty")]
        users.sort()
    return users

#---------------------------------------------------------------------------
class Login_Dlg(wx.Dialog):
    def __init__(self, parent):
	wx.Dialog.__init__(self,parent,-1, _('Login'))
	
	self.name=""
	self.file=""
	
	box = wx.BoxSizer(wx.VERTICAL)

	#Get list of users
	self.users = get_users()
	
#	p, f_name=get_f_name()
#	if os.path.exists(p):
#	    users=os.listdir(p)
#	else:
#	    users=[_('empty')]
#   	users.sort()
	
	#======== List users ==============
	i = wx.NewId()
        self.il = wx.ImageList(16, 16,True)
	bmp=wx.Bitmap(os.path.join(bitmaps_dir, 'smiles.bmp'), wx.BITMAP_TYPE_BMP)
	mask = wx.Mask(bmp, wx.WHITE)
	bmp.SetMask(mask)
	
	idx1 = self.il.Add(bmp)

        self.list = wx.ListCtrl(self, i, size=wx.Size(200, 200),
                   style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
	self.list.InsertColumn(0, _('Your name'))
	for k in range(len(self.users)):
	    self.list.InsertImageStringItem(k, self.users[k][0], idx1)
	self.list.SetColumnWidth(0, 180)
	self.list.SetItemState(0, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
	self.name=self.users[0][0]
	self.file=self.users[0][1]
	
	self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
	self.list.Bind(wx.EVT_LIST_KEY_DOWN, self.OnKeyDown, self.list)
	
	box.Add(self.list, 0, wx.ALL, 10)
	
        #========= Add user =============
	i=wx.NewId()
	box.Add(wx.Button(self, i, _('Add user')), 0, wx.ALIGN_CENTER)
	self.Bind(wx.EVT_BUTTON, self.OnAdd, id=i)
	
	#========= Ok - Cancel =============
	b1=wx.BoxSizer(wx.HORIZONTAL)
	i=wx.NewId()
	b1.Add(wx.Button(self, i, _('Ok')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnOk, id=i)
	
	i=wx.NewId()
	b1.Add(wx.Button(self, i, _('Cancel')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnCancel, id=i)
	box.Add(b1, 0, wx.ALIGN_CENTER)

	self.SetAutoLayout(True)
        self.SetSizer(box)
	box.Fit(self)
	self.list.SetFocus()

    def OnItemSelected(self, event):
	self.name=self.users[event.GetIndex()][0] #self.list.GetItemText(event.GetIndex())
	self.file=self.users[event.GetIndex()][1]
    
    def OnKeyDown(self, event):
	if event.GetKeyCode()==ord(" ") or event.GetKeyCode()==wx.WXK_RETURN:
	    self.OnOk()
	else:
	    event.Skip()

    def OnAdd(self, event=None):
	if ask_name(self):
	    self.EndModal(wx.ID_OK)

    def OnOk(self, event=None):
	dlg = wx.TextEntryDialog(self, self.name+_(', enter you password:'),_('Password'),'',
	     style=wx.OK | wx.CANCEL |  wx.TE_PASSWORD)
	while dlg.ShowModal() == wx.ID_OK:
	    cycle.passwd=dlg.GetValue()
	    cycle.name=self.name
	    cycle.file=self.file
	    if Load_Cycle(cycle.name, cycle.passwd, cycle.file):
		dlg.Destroy()
		self.EndModal(wx.ID_OK)
		return
	    else:
		dlg2 = wx.MessageDialog(self, _('Password is invalid!'),
		    _('Error!'), wx.OK |wx.ICON_ERROR )
		dlg2.ShowModal()
		dlg2.Destroy()
        dlg.Destroy()
	
    def OnCancel(self, event):
	self.EndModal(wx.ID_CANCEL)

#-------------------------------------------------------
def first_login():
    #Get list of users
    users = get_users()
    if users != []:
        return 'not_first' #user(s) already exists
    if ask_name():
	return 'first'
    else:
	return 'bad_login'
#-------------------------------------------------------
def get_new_file_name():
    while True:
        p, f = os.path.split( os.tempnam(None, "cycle") )
	p, f_name=get_f_name(f)
        if not os.path.isfile(f_name):
	    break
    return f
#-------------------------------------------------------
def ask_name(parent=None):
    # nobody, it is first login
    wx.MessageBox(
        _("This program is not a reliable contraceptive method.\n"
        "Neither does it help to prevent sexually transmitted diseases\n"
        "like HIV/AIDS.\n\nIt is just an electronic means of keeping track\n"
        "of some of your medical data and extracting some statistical\n"
        "conclusions from them. You cannot consider this program as a\n"
        "substitute for your gynecologist in any way."))
    dlg = wx.TextEntryDialog(parent, _('Enter your name:'),_('New user'),'',
	 style=wx.OK | wx.CANCEL)
    while dlg.ShowModal()==wx.ID_OK:
	name=dlg.GetValue()
	if name != "":
	    users=get_users()
	    exists=False
	    for i in users:
		if name == i[0]:
		    exists=True
		    break
	    if not exists:
		d=Ask_Passwd_Dlg(parent)
		if d.ShowModal()==wx.ID_OK:
		    cycle.file=get_new_file_name()
		    cycle.name=name
		    d.Destroy()
		    dlg.Destroy()
		    #self.EndModal(wx.ID_OK)
		    set_color_default()
		    return True
		else:
		    d.Destroy()
		    continue
	    else:
		err=name+_(' - already exists!')
	else:
	    err=_('Name must be not EMPTY')
	d2 = wx.MessageDialog(dlg, err,	_('Error!'), wx.OK |wx.ICON_ERROR )
	d2.ShowModal()
	d2.Destroy()
	
    dlg.Destroy()
    return False

#---------------------------------------------------------------------------
class Legend_Dlg(wx.Dialog):
    def __init__(self, parent):
	wx.Dialog.__init__(self,parent,-1, _('Legend'))

	#======================
	box = wx.BoxSizer(wx.VERTICAL)

	self._add(box, _('today'), wx.NullColour,wx.SIMPLE_BORDER)
	self._add(box, _('begin of cycle'), cycle.colour_set['begin'])
	self._add(box, _('prognosis of cycle begin'), cycle.colour_set['prog begin'])
	self._add(box, _('conception'), cycle.colour_set['conception'])
	self._add(box, _('safe sex'), cycle.colour_set['safe sex'])
	self._add(box, _('fertile'), cycle.colour_set['fertile'])
	self._add(box, _('ovulation, birth'), cycle.colour_set['ovule'])
	self._add(box, _('1-st tablet'), cycle.colour_set['1-st tablet'])
	self._add(box, _('tablets no. 22-28 or pause'), cycle.colour_set['pause'])
	self._add(box, _('next 1-st tablet'), cycle.colour_set['next 1-st tablet'])
	
	i=wx.NewId()
	box.Add(wx.Button(self, i, _('Ok')), 0, wx.ALIGN_CENTER|wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnOk, id=i)
	
	self.SetAutoLayout(True)
        self.SetSizer(box)
	box.Fit(self)
	
    def _add(self,box,txt,col,st=0):
	b=wx.BoxSizer(wx.HORIZONTAL)
        w=wx.Window(self,-1,size=wx.Size(15,15),style=st)
	w.SetBackgroundColour(col)
	b.Add(w, 0, wx.LEFT|wx.RIGHT,10)
	b.Add(wx.StaticText(self, -1, txt), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
	box.Add(b, 0, wx.TOP, 10)


    def OnOk(self, event):
	self.EndModal(wx.ID_OK)

#---------------------------------------------------------------------------
class Note_Dlg(wx.Dialog):
    def __init__(self, parent, title="",txt=""):
	wx.Dialog.__init__(self,parent,-1, title)
	self.CentreOnParent(wx.BOTH)

	#======================
	box = wx.BoxSizer(wx.VERTICAL)
	self.txt=wx.TextCtrl(self, -1, txt,
                       size=(-1, 100), style=wx.TE_MULTILINE)
        box.Add( self.txt, 0,
	    wx.EXPAND|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.RIGHT, 10)

	b1=wx.BoxSizer(wx.HORIZONTAL)
	i=wx.NewId()
	b1.Add(wx.Button(self, i, _('Ok')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnOk, id=i)
	
	i=wx.NewId()
	b1.Add(wx.Button(self, i, _('Cancel')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnCancel, id=i)
	
	i=wx.NewId()
	b1.Add(wx.Button(self, i, _('Remove')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnRemove, id=i)
	box.Add(b1, 0, wx.ALIGN_CENTER)
	
	self.SetAutoLayout(True)
        self.SetSizer(box)
	box.Fit(self)
	self.txt.SetFocus()
	

    def OnOk(self, event):
	self.EndModal(wx.ID_OK)

    def OnCancel(self, event):
	self.EndModal(wx.ID_CANCEL)

    def OnRemove(self, event):
	self.EndModal(False)

    def Get_Txt(self):
	return self.txt.GetValue()
    
#---------------------------------------------------------------------------
class MyHtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, pos = wx.DefaultPosition, size=wx.DefaultSize):
	wx.html.HtmlWindow.__init__(self, parent, id, pos, size)
	if "gtk2" in wx.PlatformInfo:
	    self.SetStandardFonts()

    def OnLinkClicked(self, linkinfo):
	pass
	
#---------------------------------------------------------------------------
class Help_Dlg(wx.Dialog):
    def __init__(self, parent, title="",txt=""):
	wx.Dialog.__init__(self,parent,-1, title)
	self.CentreOnParent(wx.BOTH)

	#======================
	box = wx.BoxSizer(wx.VERTICAL)
	self.html=MyHtmlWindow(self, -1, size=(500, 350))
	self.html.SetPage(txt)
        box.Add( self.html, 0, wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.RIGHT, 10)

	i=wx.NewId()
	box.Add(wx.Button(self, i, _('Ok')), 0, wx.ALIGN_CENTER|wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnOk, id=i)
		
	self.SetAutoLayout(True)
        self.SetSizer(box)
	box.Fit(self)
	
    def OnOk(self, event):
	self.EndModal(wx.ID_OK)

#---------------------------------------------------------------------------
class Colours_Dlg(wx.Dialog):
    def __init__(self, parent):
	wx.Dialog.__init__(self,parent,-1, _('Colours settings'))

	self.col_set = cycle.colour_set.copy()
	self.col_id = cycle.colour_set.keys()
	self.data = wx.ColourData()
	self.data.SetChooseFull(True)
	self.buttons = {}
	#======================
	box = wx.BoxSizer(wx.VERTICAL)

	self._add(box, _('begin of cycle'), 'begin')
	self._add(box, _('prognosis of cycle begin'), 'prog begin')
	self._add(box, _('conception'), 'conception')
	self._add(box, _('safe sex'), 'safe sex')
	self._add(box, _('fertile'), 'fertile')
	self._add(box, _('ovulation, birth'), 'ovule')
	self._add(box, _('1-st tablet'), '1-st tablet')
	self._add(box, _('tablets no. 22-28 or pause'), 'pause')
	self._add(box, _('next 1-st tablet'), 'next 1-st tablet')
	
	b1=wx.BoxSizer(wx.HORIZONTAL)
	i=wx.NewId()
	b1.Add(wx.Button(self, i, _('Ok')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnOk, id=i)

	i=wx.NewId()
	b1.Add(wx.Button(self, i, _('By default')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnDefault, id=i)

	i=wx.NewId()
	b1.Add(wx.Button(self, i, _('Cancel')), 0, wx.ALL, 10)
	self.Bind(wx.EVT_BUTTON, self.OnCancel, id=i)
	box.Add(b1, 0, wx.ALIGN_CENTER)
	
	self.SetAutoLayout(True)
        self.SetSizer(box)
	box.Fit(self)
	
    def _add(self, box, txt, col):
	b=wx.BoxSizer(wx.HORIZONTAL)
	i=self.col_id.index(col)
        bt=wx.Button(self, i, "", size=wx.Size(15,15))
	self.Bind(wx.EVT_BUTTON, self.get_colour, id=i)
	bt.SetBackgroundColour(self.col_set[col])
	self.buttons.update({i:bt})
	b.Add(bt, 0, wx.LEFT|wx.RIGHT,10)
	b.Add(wx.StaticText(self, -1, txt), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
	box.Add(b, 0, wx.TOP, 10)

    def get_colour(self, event):
	c = self.col_set[ self.col_id[event.GetId()] ]
	self.data.SetColour(c)
        dlg = wx.ColourDialog(self, self.data)
        if dlg.ShowModal() == wx.ID_OK:
	    self.data = dlg.GetColourData()
	    c = self.data.GetColour()
	    self.buttons[event.GetId()].SetBackgroundColour(c)
	    self.col_set[self.col_id[event.GetId()]] = c

    def OnOk(self, event):
	cycle.colour_set = self.col_set.copy()
	Val.Cal.Draw_Mark()
	self.EndModal(wx.ID_OK)

    def OnDefault(self, event):
	self.col_set = {'begin':wx.NamedColour('RED'),
	    'prog begin':wx.NamedColour('PINK'),
	    'conception':wx.NamedColour('MAGENTA'),
	    'safe sex':wx.NamedColour('WHEAT'),
	    'fertile':wx.NamedColour('GREEN YELLOW'),
	    'ovule':wx.NamedColour('SPRING GREEN'),
	    '1-st tablet':wx.NamedColour('GOLD'),
	    'pause':wx.NamedColour('LIGHT BLUE'),
	    'next 1-st tablet':wx.NamedColour('PINK')}
	for item in self.col_id:
	    self.buttons[self.col_id.index(item)].SetBackgroundColour(self.col_set[item])

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

#---------------------------------------------------------------------------
