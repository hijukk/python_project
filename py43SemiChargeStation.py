#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar
from tkinter import messagebox

import sqlite3

import json
import requests
import xmltodict # xml 데이터를 dictionary로 변환해줌

import wx
import wx.xrc
from wx.lib.plot import PlotCanvas, PlotGraphics, PolyLine, PolyMarker

import requests
import json
import numpy as np
import pandas as pd

packages = [('abiword', '5.8M', 'base'), ('adie', '145k', 'base'),
    ('airsnort', '71k', 'base'), ('ara', '717k', 'base'), ('arc', '139k', 'base'),
    ('asc', '5.8M', 'base'), ('ascii', '74k', 'base'), ('ash', '74k', 'base')]
    

    
class MyEditReserv(wx.Frame):
	def __init__(self,select_data):
		super(MyEditReserv,self).__init__(None,title="변경페이지",size=(300,250),pos=(0,0))
		print("myedit...", select_data)
		self.initGUI()
		self.select_data = select_data
		
	def initGUI(self):
		panel = wx.Panel(self)
		panel.SetBackgroundColour('#999999')
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		midPan = wx.Panel(panel)
		midPan.SetBackgroundColour('#ededed')
		
		label = wx.StaticText(midPan,label='변경/취소',pos=(50,10))
		btn_UpdatePage = wx.Button(midPan,label='날짜/시간 변경',pos=(50,60))
		btn_UpdatePage.id = 1
		btn_DeletePage = wx.Button(midPan,label='예약취소',pos=(50,120))
		btn_DeletePage.id = 2
		
		btn_UpdatePage.Bind(wx.EVT_BUTTON, self.onClick)
		btn_DeletePage.Bind(wx.EVT_BUTTON, self.onClick)

		vbox.Add(midPan, wx.ID_ANY, wx.EXPAND | wx.ALL, 30)
		panel.SetSizer(vbox)
        
	def onClick(self,event):
		print("event.GetEventObject().id:",event.GetEventObject().id)
		
		conn = sqlite3.connect("py43SemiChargeStation.db")
		cursor = conn.cursor()
		
		if event.GetEventObject().id == 1:
			print("update...")
			cursor.execute("SELECT * FROM chargestation where name = ?",(self.select_data[0], ))
			vo = cursor.fetchall() #리스트안에 튜플있음
			for i in vo:
				vo = list(i)
				
			
			self.Destroy()
			Reservation(vo)
			
			
		elif event.GetEventObject().id == 2:
			print("delete....")
			##예약취소
			cursor.execute("DELETE FROM mychargestation where name = ?",(self.select_data[0], ))
			conn.commit()
			
			self.Destroy()
			select_data=()
			app = wx.App()
			MyReservation(select_data).Show()	
			app.MainLoop()
    
    
    


#=====================MyReservation======================

class MyReservation(wx.Frame):
	def __init__(self,select_data):
		super(MyReservation,self).__init__(None,title="예약내역",size=(500,400),pos=(0,0))
		
		self.create_table(select_data)
		
		self.initGUI()
	
	def create_table(self, select_data):
		###DB CREATE TABLE
		conn = sqlite3.connect("py43SemiChargeStation.db")
		cursor = conn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS mychargestation (name TEXT UNIQUE, reserv_date DATE, reserv_hour TEXT)")
		
		if len(select_data) > 0 :
			print("len..", select_data)
			print("more than one....")
			values = (select_data[1],select_data[4],select_data[5])
			cursor.execute("INSERT OR REPLACE INTO mychargestation (name, reserv_date, reserv_hour) VALUES(?,?,?)", values)
			conn.commit()
	
		
	def initGUI(self):
		
		self.m_panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		
		bSizer = wx.BoxSizer(wx.VERTICAL)
		
		self.lstView = wx.ListCtrl(self.m_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT)
		self.lstView.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onSelected) #더블클릭.
		
		bSizer.Add(self.lstView, 1, wx.ALL | wx.EXPAND, 5)
		self.m_panel.SetSizer(bSizer)
		self.m_panel.Layout()
		bSizer.Fit(self.m_panel)
		
		self.lstView.InsertColumn(0, '충전소', width=200) 	
		self.lstView.InsertColumn(1, '예약날짜', width=150)
		self.lstView.InsertColumn(2, '예약시간', width=150)
		
		conn = sqlite3.connect("py43SemiChargeStation.db")
		cursor = conn.cursor()
		
		cursor.execute("SELECT * FROM mychargestation order by reserv_date asc")
		self.vos = cursor.fetchall()
		for i in range(len(self.vos)):
			print(self.vos[i])
			index = self.lstView.InsertItem(1000, i)
			self.lstView.SetItem(index, 0, self.vos[i][0])
			self.lstView.SetItem(index, 1, self.vos[i][1])
			self.lstView.SetItem(index, 2, self.vos[i][2])
		
    
	def onSelected(self,event):
		print("onSelected...",event.GetIndex(), self.vos[event.GetIndex()])
		dialog = wx.MessageDialog(self,'예약변경페이지로 이동하시겠습니까?','OK',wx.YES_NO)
		if dialog.ShowModal() == wx.ID_YES:
			print("Close...YES")
			#print(self.vos[event.GetIndex()][0])
			
			self.Destroy()
			MyEditReserv(self.vos[event.GetIndex()]).Show()	
			
		else :
			print("Close...NO")
    
        
#select_data=()
#app = wx.App()
#MyReservation(select_data).Show()	
#app.MainLoop()	







#======================Reservation Calendar=====================================

class Reservation:
	def __init__(self, select_data):
		print("select_data: ",select_data)
		
		#https://www.codespeedy.com/create-a-date-picker-calendar-in-python-tkinter/
		tk = Tk()
		tk.title("예약")
		width = 400
		height = 400
		screen_width = tk.winfo_screenwidth()
		screen_height = tk.winfo_screenheight()
		x = (screen_width/2) - (width/2)
		y = (screen_height/2) - (height/2)
		tk.geometry("%dx%d+%d+%d" % (width, height, x, y))

		
		tkc = Calendar(tk,selectmode = "day",date_pattern='yyyy-MM-dd',year=2022,month=4,date=17)

		tkc.pack(pady=40)
		
		
		###예약하기 버튼
		def get_date_hour():
			#date.config(text = "Selected Date is: " + tkc.get_date() + reserv_hour.get())
			select_data.append(tkc.get_date())
			select_data.append(reserv_hour.get())
			print("select_data append:",select_data)
			
			tk.destroy()
			
			app = wx.App()
			MyReservation(select_data).Show()
			app.MainLoop()	
			
			
			
		reserv_hour = StringVar()
		combo = ttk.Combobox(tk, width=20, textvariable=reserv_hour)
		
		combo['values'] = ()
		##시간별로 조건문 쓰기
		if select_data[3] == '24시간 이용가능':
			print("24시간 이용가능")
			combo['values'] = ('00:00 ~ 01:00', '01:00 ~ 02:00', '02:00 ~ 03:00', '03:00 ~ 04:00', '04:00 ~ 05:00',  '05:00 ~ 06:00', 
								'07:00 ~ 08:00', '08:00 ~ 09:00', '09:00 ~ 10:00', '10:00 ~ 11:00', '11:00 ~ 12:00', '12:00 ~ 13:00',
								'13:00 ~ 14:00', '14:00 ~ 15:00', '15:00 ~ 16:00', '16:00 ~ 17:00', '17:00 ~ 18:00', '19:00 ~ 20:00',
								'20:00 ~ 21:00', '21:00 ~ 22:00', '22:00 ~ 23:00', '23:00 ~ 24:00'
								)
		elif "~" in select_data[3]:
			print("~ in ...")
			#~구분후 배열에 넣기
			hour = select_data[3].split("~")
			print(hour)
			for i in range(len(hour)):
				try:
					#:로 구분해서 앞숫자만 배열에 넣기
					hour[i] = int(hour[i].split(":")[0])
				except ValueError as ve:
					# ValueError뜨면 그냥 그대로 넣기
					hour[i] = hour[i]
					
			print(hour)
			print(type(hour[1]))
			hour_list = []
			last_hour = 24 if (str(type(hour[1])) == "<class 'str'>") else hour[1]
			print("last_hour:",last_hour)
			for i in range(hour[0], last_hour):
				str_hour = str(i) + ":00 ~ " + str(int(i)+1) + ":00"
				hour_list.append(str_hour)
			
			#익일들어가있으면 타입이 문자니, 00:00~01:00추가	
			if (str(type(hour[1])) == "<class 'str'>") :
				hour_list.append("00:00 ~ 01:00")	
				
			
			print(tuple(hour_list))
			combo['values'] = tuple(hour_list)
			
		else:
			print("else...")
			combo['values'] = (select_data[2],)
		
		combo.pack()
		combo.current(0)
		
		okButton = Button(tk,text="예약하기",command=get_date_hour, bg="black", fg='white')
		okButton.pack()
		
		tk.mainloop()
		
		
#Reservation()	
		



class CSList:
	#https://www.sourcecodester.com/tutorials/python/11382/python-simple-table-search-filter.html
	def __init__(self):
		
		#=====껍데기=====
		root = Tk()
		root.title("급속 충전소")
		width = 500
		height = 400
		screen_width = root.winfo_screenwidth()
		screen_height = root.winfo_screenheight()
		x = (screen_width/2) - (width/2)
		y = (screen_height/2) - (height/2)
		root.geometry("%dx%d+%d+%d" % (width, height, x, y))
		root.resizable(0, 0)

		#======METHODS======
		#CSTable
		def createCSTable():
			
			#https://shaula0.tistory.com/34
			url = "http://apis.data.go.kr/B552584/EvCharger/getChargerInfo" 

			api_key = "gesCHu5JHbrjYez9amNdrNyXID9dG0Kg2tAKtrlpTZdOLfEC4etkbtkUC9YR7561lp2dbowO4NLHHcHD97CFkQ=="
			api_key_decode = requests.utils.unquote(api_key)
			api_key_decode

			parameters = {"ServiceKey":api_key_decode, "numOfROws":1, "zcode":11}
			parameters

			req = requests.get(url, params = parameters)
			req.text # -> xml 데이터 확보

			xml_data = xmltodict.parse(req.text)
			#print(xml_data)

			informations = xml_data['response']['body']['items']['item']
			#print(informations)

			data_list = []
			for data in informations:
				str_data = (data['statNm'],data['addr'],data['useTime'])
				#print(str_data)
				data_list.append(str_data)
			#print(data_list)

			
			###DB CREATE TABLE
			conn = sqlite3.connect("py43SemiChargeStation.db")
			cursor = conn.cursor()
			cursor.execute("CREATE TABLE IF NOT EXISTS chargestation (cs_id INTEGER NOT NULL PRIMARY KEY  AUTOINCREMENT, name TEXT, addr TEXT, hour TEXT)")
			cursor.execute("SELECT * FROM chargestation")
			if cursor.fetchone() is None:
				for i in range(len(data_list)):
					cursor.execute("INSERT INTO chargestation (name, addr, hour) VALUES(?,?,?)", data_list[i])
					conn.commit()

			cursor.execute("SELECT * FROM chargestation ORDER BY cs_id ASC")
			fetch = cursor.fetchall()
			for data in fetch:
				tree.insert('', 'end', values=(data))
			cursor.close()
			conn.close()
		
		
		def Search():
			if SEARCH.get() != "":
				tree.delete(*tree.get_children())
				conn = sqlite3.connect("py43SemiChargeStation.db")
				cursor = conn.cursor()
				cursor.execute("SELECT * FROM chargestation WHERE name LIKE ? OR addr LIKE ?", ('%'+str(SEARCH.get())+'%', '%'+str(SEARCH.get())+'%'))
				fetch = cursor.fetchall()
				for data in fetch:
					tree.insert('', 'end', values=(data))
				cursor.close()
				conn.close()
				
		def Reset():
			conn = sqlite3.connect("py43SemiChargeStation.db")
			cursor = conn.cursor()
			tree.delete(*tree.get_children())
			cursor.execute("SELECT * FROM chargestation ORDER BY cs_id ASC")
			fetch = cursor.fetchall()
			for data in fetch:
				tree.insert('', 'end', values=(data))
			cursor.close()
			conn.close()



		###VARIABLES
		SEARCH = StringVar()
		
		###FRAME
		Top = Frame(root, width=500, bd=1, relief=SOLID)
		Top.pack(side=TOP)
		TopFrame = Frame(root, width=500)
		TopFrame.pack(side=TOP)
		TopForm= Frame(TopFrame, width=300)
		TopForm.pack(side=LEFT, pady=10)
		TopMargin = Frame(TopFrame, width=260)
		TopMargin.pack(side=LEFT)
		MidFrame = Frame(root, width=500)
		MidFrame.pack(side=TOP)
		 
		 
		###SEARCH FORM
		search = Entry(TopForm, textvariable=SEARCH)
		search.pack(side=LEFT)
		 
		#BUTTON
		btn_search = Button(TopForm, text="검색", command=Search)
		btn_search.pack(side=LEFT)
		btn_reset = Button(TopForm, text="초기화", command=Reset)
		btn_reset.pack(side=LEFT)
		
		#LIST FORM
		scrollbarx = Scrollbar(MidFrame, orient=HORIZONTAL)
		scrollbary = Scrollbar(MidFrame, orient=VERTICAL)
		tree = ttk.Treeview(MidFrame, columns=("cs_id", "name", "addr", "hour"), selectmode="extended", height=400, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
		scrollbary.config(command=tree.yview)
		scrollbary.pack(side=RIGHT, fill=Y)
		scrollbarx.config(command=tree.xview)
		scrollbarx.pack(side=BOTTOM, fill=X)
		tree.heading('cs_id', text="지점ID",anchor=W)
		tree.heading('name', text="충전소",anchor=W)
		tree.heading('addr', text="주소",anchor=W)
		tree.heading('hour', text="운영시간",anchor=W)
		tree.column('#0', stretch=NO, minwidth=0, width=0)
		tree.column('#1', stretch=NO, minwidth=0, width=80)
		tree.column('#2', stretch=NO, minwidth=0, width=120)
		tree.column('#3', stretch=NO, minwidth=0, width=170)
		tree.pack()

			
		########click#########
		def click_item(event): 
			selectedItem = tree.focus() 
			getValue = tree.item(selectedItem).get('values') # 딕셔너리의 값만 가져오기 
			print(getValue)
			
			root.destroy()
			##캘린더
			Reservation(getValue)
					
				
		tree.bind('<ButtonRelease-1>', click_item)
		
		
		createCSTable() ##폼만든후 db에 데이터가져와서 넣기
		root.mainloop()


#=============실행=================
#CSList()

########################################################################
class MyReservGraph(wx.Frame):
        #----------------------------------------------------------------------
        def __init__(self):
                super(MyReservGraph,self).__init__(None,title="예약내역 충전소",size=(500,400),pos=(100, 100))
                
                # Add a panel so it looks the correct on all platforms
                panel = wx.Panel(self, wx.ID_ANY)
		
                # create some sizers
                mainSizer = wx.BoxSizer(wx.VERTICAL)
                checkSizer = wx.BoxSizer(wx.HORIZONTAL)

                # create the widgets
                self.canvas = PlotCanvas(panel)
                self.canvas.Draw(self.drawBarGraph())
                self.canvas.enableGrid = False


                # layout the widgets
                mainSizer.Add(self.canvas, 1, wx.EXPAND)
                mainSizer.Add(checkSizer)
                panel.SetSizer(mainSizer)
        
        
        
       
	#----------------------------------------------------------------------
        def drawBarGraph(self):
                conn = sqlite3.connect("py43SemiChargeStation.db")
                cursor = conn.cursor()

                cursor.execute("select strftime('%m', reserv_date) rd, count(*) from mychargestation group by rd order by rd asc")
                vos = cursor.fetchall()
                
                points = []
                for i in range(len(vos)):
                    point = [(vos[i][0],0), vos[i]]
                    #print(point)
                    points.append(point)

                print(points)
                
                lines = []
                for point in points:
                        line = PolyLine(point, colour='#a5d9b7', width=40)
                        lines.append(line)
                #print("lines:",lines)
                
                
                return PlotGraphics(lines, "예약건수", "Months", "") 
                
                
                
        
 #----------------------------------------------------------------------       



class WxMenu:

	def __init__(self):
		menu_bar = wx.MenuBar()

		menu1 = wx.Menu()
		menu_bar.Append(menu1, '메뉴')
		self.SetMenuBar(menu_bar)

		menu1.Append(101, 'Home')
		self.Bind(wx.EVT_MENU, self.buttonClick, id=101) 

		quit_submenu = menu1.Append(wx.ID_EXIT, 'Exit', 'Close Window..')
		self.Bind(wx.EVT_MENU, self.onQuit, quit_submenu)
		#---------------------------------

		menu2 = wx.Menu()
		menu_bar.Append(menu2, '충전소')
		self.SetMenuBar(menu_bar)

		menu2.Append(102, '예약')
		self.Bind(wx.EVT_MENU, self.doCSList, id=102) 

		#---------------------------------

		menu3 = wx.Menu()
		menu_bar.Append(menu3, '회원정보')
		self.SetMenuBar(menu_bar)

		menu3.Append(103, '예약내역')
		self.Bind(wx.EVT_MENU, self.doMyReservation, id=103) 
		menu3.Append(104, '예약건수')
		self.Bind(wx.EVT_MENU, self.doMyReservGraph, id=104) 



	def buttonClick(self, event): 
	##멈춤 안됨
		event.Skip()

	def doCSList(self, event):
		print("cslist...")
		CSList()

	def doMyReservation(self, event):
		select_data=()
		app = wx.App()
		MyReservation(select_data).Show()	
		app.MainLoop()	

	def doMyReservGraph(self, event):
		app = wx.App()
		MyReservGraph().Show()
		app.MainLoop()


	def onQuit(self, event):
		self.Destroy()






########################################################################
class MainMenu(wx.Frame, WxMenu):
    
    def __init__(self):
        
        ####GUI
        super(MainMenu,self).__init__(None,title="전기차 충전소",size=(2000,1200),pos=(0, 0))
        
        ##메뉴바 상속
        WxMenu.__init__(self)
        panel = wx.Panel(self, wx.ID_ANY)
        
        # create some sizers
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        checkSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # create the widgets
	#https://linuxtut.com/en/e7d3f9e67d06c55998a3/
        self.canvas = PlotCanvas(panel)
        self.canvas.Draw(self.drawGraph())
        self.canvas.enableLegend = True
        self.canvas.fontSizeLegend = 18
        self.canvas.fontSizeTitle = 32
        self.canvas.fontSizeAxis = 24
        
	# layout the widgets
        mainSizer.Add(self.canvas, 1, wx.EXPAND)
        mainSizer.Add(checkSizer)
        panel.SetSizer(mainSizer)
        
        
    #----------------------------------------------------------------------
    
    #https://www.blog.pythonlibrary.org/2010/09/27/wxpython-pyplot-graphs-with-python/
    def drawGraph(self):
        
        url = "https://api.odcloud.kr/api/15039555/v1/uddi:86638e67-8e24-4cb3-8bc4-d37489a1e271?page=1&perPage=10&serviceKey=gesCHu5JHbrjYez9amNdrNyXID9dG0Kg2tAKtrlpTZdOLfEC4etkbtkUC9YR7561lp2dbowO4NLHHcHD97CFkQ%3D%3D"

        response = requests.get(url)
        #print(response.text)
        r_dict = json.loads(response.text)
        #print(r_dict)

        r_data = r_dict.get("data")
        #print(r_data)

        #지역전체 데이터 프레임
        df = pd.DataFrame(r_data)
        #print(df)
        df.set_index("지역", drop=True, inplace=True)
        #print(df)

        #========================================================
        #print(df.mean())
        #print(pd.DataFrame(df.mean()))

        #지역 전체 평균 데이터 프레임
        mean_df = pd.DataFrame(df.mean())
        mean_arr = []
        for idx, row in mean_df.iterrows():
            #print(idx,row.values)
            mean_arr.append(int(idx))
            mean_arr.extend(row.values)
        print(mean_arr)


        #서울 데이터만 추출
        seoul_df = df.loc[["서울특별시"],:].T
        #print(df.loc[["서울특별시"],:].T)

        seoul_arr = []
        #서울데이터 행과 데이터로 받아서 리스트에 넣음
        for idx, row in seoul_df.iterrows():
            #print(idx,row.values)
            seoul_arr.append(int(idx))
            seoul_arr.extend(row.values)
        print(seoul_arr)
        
        seoul_data = np.array(seoul_arr)
        #x축 단위로 묶어서 형변환
        seoul_data.shape = (5, 2)
        #print(seoul_data)
        
        mean_data = np.array(mean_arr)
        #x축 단위로 묶어서 형변환
        mean_data.shape = (5, 2)
        print(mean_data)
        
        
        line1 = PolyLine(seoul_data, legend='서울', colour='#0c5bed', width=3)
        line2 = PolyLine(mean_data, legend='전국', colour='#7cd98b', width=3)
        
        return PlotGraphics([line1, line2], "서울 충전소 현황정보", "연도", "")
    

'''app = wx.App(False)
frame = MainMenu()
frame.Show()
app.MainLoop()'''





class LoginPage:
	url = "http://192.168.216.1:8090/semiproject/json_cslogin.do"
	def __init__(self):
		#1.껍데기
		top = Tk()
		width = 250
		height = 100
		screen_width = top.winfo_screenwidth()
		screen_height = top.winfo_screenheight()
		x = (screen_width/2) - (width/2)
		y = (screen_height/2) - (height/2)
		top.geometry("%dx%d+%d+%d" % (width, height, x, y))
		top.title("Login")
		
		
		#2.
		idLabel = Label(top,text="ID:")
		pwLabel = Label(top,text="PASSWORD:")
		idLabel.grid() #grid 정렬
		pwLabel.grid()
		
		idEntry = Entry(top)
		pwEntry = Entry(top)
		
		idEntry.insert(0,"user2") 
		pwEntry.insert(0,"hi123456") 
		
		idEntry.grid(row=0,column=1) 
		pwEntry.grid(row=1,column=1)
		
		#3. 전송 정보보내기
		def onclick():
			print("onclick()...")
			user_id = idEntry.get()
			user_pw = pwEntry.get()
			
			print("id:",user_id)
			print("pw:",user_pw)
			
			url = self.url + "?id=" + user_id + "&pw=" + user_pw
			print(url)
			
			response = requests.get(url)
			str_text = response.content.decode("utf-8")
			print(str_text)
			
			json_vo = json.loads(str_text)
			print(json_vo["id"], json_vo["pw"])
			
			if (json_vo["id"]==user_id) & (json_vo["pw"]==user_pw):
				print("login success..")
				top.destroy() #window close
				
				#홈화면
				app = wx.App(False)
				frame = MainMenu()
				frame.Show()
				app.MainLoop()
				
			else :
				print("login fail...")
				top.quit()
				messagebox.showinfo(title="메세지 상자", message="패쓰워드 확인 후 다시 로그인해주세요")
					
		okButton = Button(top,text="OK",command=onclick) #command:event(명령, 함수명적어줌)
		okButton.grid(row=2,column=1)
		
		#1.껍데기
		top.mainloop()


LoginPage()
print("--------------------------")


