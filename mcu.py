#!/usr/bin/python env
# -*- coding: utf-8 -*-
#import requests
# rewrite confcontent , use class 
###0.2 changed #########
# test() ,will run the cycle
# read mcuadd and confID from mcu.ini

import xml.etree.ElementTree as ET
from lxml import etree
import time 
import httplib2 # change lib requests to httplib2
import random 
from StringIO import StringIO
import threading
from ConfigParser import ConfigParser #add on 0.2
import sys
class MCU(object):
	def __init__(self, link):
		self.link = link 
	def send(self,file):
		global s
		self.file = file 
		tree = ET.ElementTree(file=self.file)
		root = tree.getroot()
		data = ET.tostring(root,encoding='UTF-8')
		headers = {'content-type':'text/xml'} # important 
		ip = self.link
		resp, content = s.request(ip,method="POST",body = data,headers = headers)
		if 'User not found' in content :
			print 'token invalid!\n'
			sys.exit()
		#print content 
		return content
	def login(self) :
		content = self.send('login.xml')
		return content
	def getstatus(self) :
		content = self.send('status.xml')
		if 'User not found' in content :
			print 'token invalid!\n'
			sys.exit()
		return content 
		
		
	def gettoken(self) :
		content = self.login()
		mcu_root = etree.XML(content)
		mcu_tokens  = mcu_root.xpath('/RESPONSE_TRANS_MCU/ACTION/LOGIN/MCU_TOKEN')
		mcu_user_tokens = mcu_root.xpath('/RESPONSE_TRANS_MCU/ACTION/LOGIN/MCU_USER_TOKEN')
		mcu_token = mcu_tokens[0].text
		mcu_user_token = mcu_user_tokens[0].text
		return mcu_token,mcu_user_token
	def get_profielist(self):
		content = self.send('req_getProfileList.xml')
		return content 
	def start_conference(self):
		pass
class xml :
	def __init__(self,file):
		self.file = file

		
	def updatebase(self,MCU_token,MCU_USER_token,messageID):
		file = self.file 
		self.MCU_token = MCU_token
		self.MCU_USER_token = MCU_USER_token
		self.messageID = messageID
		MCU_token = self.MCU_token
		MCU_USER_token = self.MCU_USER_token 
		message = self.messageID
		tree = etree.parse(file)
		root = tree.getroot()
		for element in root.iter("MESSAGE_ID"):
			element.text = message
		for element in root.iter("MCU_TOKEN"):
			element.text = MCU_token
		for element in root.iter("MCU_USER_TOKEN"):
			element.text = MCU_USER_token
		tree.write(file)

	def updateconfID(self,confID):
		self.confID = confID
		confID = self.confID
		file = self.file
		tree = ET.parse(file)
		root = tree.getroot()
		for element in root.iter("ID"):
			element.text = confID
		tree.write(file)
	def update_video_layout_xpath(self,confID,sID,forcename):
		self.confID = confID
		confID = self.confID
		self.sID = sID
		sID = self.sID
		self.forcename = forcename
		forcename = self.forcename
		file = self.file
		tree = etree.parse(file)
		root = tree.getroot()	
		IDs = root.xpath('/TRANS_CONF_1/ACTION/SET_VIDEO_LAYOUT/ID')
		IDs[0].text = confID
		
		forceIDs = root.xpath('/TRANS_CONF_1/ACTION/SET_VIDEO_LAYOUT/FORCE/CELL/FORCE_ID')
		forceIDs[0].text = str(sID)
		sourceIDs = root.xpath('/TRANS_CONF_1/ACTION/SET_VIDEO_LAYOUT/FORCE/CELL/SOURCE_ID')

		sourceIDs[0].text = str(sID)
		forcenames = root.xpath('/TRANS_CONF_1/ACTION/SET_VIDEO_LAYOUT/FORCE/CELL/FORCE_NAME')
		forcenames[0].text = forcename
		tree.write(file)
	def updatePartID(self,partID):
		self.partID = partID
		partID = self.partID
		file = self.file
		tree = ET.parse(file)
		root = tree.getroot()
		for element in root.iter("PARTY_ID"):
			element.text = partID
		tree.write(file)
	def updatePartname(self,partname):
		self.partname = partname
		partname = self.partname
		file = self.file
		tree = ET.parse(file)
		root = tree.getroot()
		for element in root.iter("LECTURE_NAME"):
			element.text = partname
		tree.write(file)
	def update_connect(self,t_f):
		self.t_f = t_f
		t_f = self.t_f
		file = self.file
		tree = ET.parse(file)
		root = tree.getroot()
		for element in root.iter("CONNECT"):
			element.text = t_f
		tree.write(file)
	def updateconfID_base(self,MCU_token,MCU_USER_token,messageID,confID):
		self.updatebase(MCU_token,MCU_USER_token,messageID)
		self.updateconfID(confID)
		
	def updateconfID_PartID_base(self,MCU_token,MCU_USER_token,messageID,confID,partID):	
		self.updatebase(MCU_token,MCU_USER_token,messageID)
		self.updateconfID(confID)
		self.updatePartID(partID)
		
		
class conference :
	def __init__(self,link):
		self.link = link
		
	def add_participant(self):
		pass
	def get_allpartIDs(self):
		link = self.link
		xml_req_getConferenceContent = xml('req_getConferenceContent.xml') 
		xml_req_getConferenceContent.updateconfID_base(MCU_token,MCU_USER_token,messageID,confID)
		mcu = MCU(link)
		content = mcu.send('req_getConferenceContent.xml')
		mcu_root = etree.XML(content)
		conf_partIDs = mcu_root.xpath('/RESPONSE_TRANS_CONF/ACTION/GET/CONFERENCE/ONGOING_PARTY_LIST/ONGOING_PARTY/PARTY/ID')
		return conf_partIDs
	def get_allpartnames(self):
		link = self.link
		xml_req_getConferenceContent = xml('req_getConferenceContent.xml') 
		xml_req_getConferenceContent.updateconfID_base(MCU_token,MCU_USER_token,messageID,confID)
		mcu = MCU(link)
		content = mcu.send('req_getConferenceContent.xml')
		mcu_root = etree.XML(content)
		conf_partnames = mcu_root.xpath('/RESPONSE_TRANS_CONF/ACTION/GET/CONFERENCE/ONGOING_PARTY_LIST/ONGOING_PARTY/PARTY/NAME')
		return conf_partnames
	

# this function for keep alive 
def getstatus():
	while True :
		#print "Get Status!!!\n"
		global MCU_token
		global MCU_USER_token
		message = random.randint(0,65535)
		messageID = str(message)
		time.sleep(15)
		xml_status = xml('status.xml')
		xml_status.updatebase(MCU_token,MCU_USER_token,messageID) # token, and message id update
		mcu = MCU(link)
		mcu.getstatus()
		print '%s'   %time.ctime()
#def muteall(num_party,MCU_token,MCU_USER_token,messageID,confID,link):
# mute all from MCU
def muteall():
	global MCU_token
	global MCU_USER_token
	global confID
	global link
	global num_party
	i = 0
	while i < num_party :
		time.sleep(10)
		partID = partIDs[i].text
		print partIDs[i].text
		partname = partnames[i].text
		print "%s will be mute" %partname
		i +=1
		xml_req_muteParticipant = xml('req_muteParticipant.xml')
		xml_req_muteParticipant.updateconfID_PartID_base(MCU_token,MCU_USER_token,messageID,confID,partID)
		mcu = MCU(link)
		mcu.send('req_muteParticipant.xml')
		
#def unmuteall(num_party,MCU_token,MCU_USER_token,messageID,confID,link):
def unmuteall():
	global MCU_token
	global MCU_USER_token
	global confID
	global link
	global num_party
	i = 0
	while i < num_party :
		time.sleep(10)
		partID = partIDs[i].text
		print partIDs[i].text
		partname = partnames[i].text
		print "%s will be unmuted" %partname
		i +=1
		xml_req_muteParticipant = xml('req_muteParticipant.xml')
		xml_req_muteParticipant.updateconfID_PartID_base(MCU_token,MCU_USER_token,messageID,confID,partID)
		mcu = MCU(link)
		mcu.send('req_muteParticipant.xml')
#def set_lecture_cyc(num_party,MCU_token,MCU_USER_token,messageID,confID,link):
def set_lecture_cyc():
	global MCU_token
	global MCU_USER_token
	global confID
	global link
	global num_party
	message = random.randint(0,65535)
	messageID = str(message)
	i = 0
	while i < num_party :
		time.sleep(10)
		partID = partIDs[i].text
		partname = partnames[i].text
		print partIDs[i].text
		print "switching lecture to %s" %partname
		i +=1
		xml_req = xml('req_setLecturer.xml')
		xml_req.updateconfID_PartID_base(MCU_token,MCU_USER_token,messageID,confID,partID)
		xml_req.updatePartname(partname)
		mcu = MCU(link)
		mcu.send('req_setLecturer.xml')
def set_lecture_layout_cyc():
	global MCU_token
	global MCU_USER_token
	global confID
	global link
	global num_party
	message = random.randint(0,65535)
	messageID = str(message)
	
	i = 0
	while i < num_party :
		time.sleep(10)
		partID = partIDs[i].text
		partname = partnames[i].text
		print partIDs[i].text
		print "%s  switch lecture to %s" %(time.ctime(),partname)
		i +=1
		xml_req = xml('req_setLecturer.xml')
		xml_req.updateconfID_PartID_base(MCU_token,MCU_USER_token,messageID,confID,partID)
		xml_req.updatePartname(partname)
		mcu = MCU(link)
		mcu.send('req_setLecturer.xml')
		time.sleep(10)
		v = num_party
		while v > 0:
			time.sleep(10)
			v -=1
			sID = v
			forcename = partnames[sID].text
			xml_req2 = xml('req_setVideoLayout.xml')
			xml_req2.updatebase(MCU_token,MCU_USER_token,messageID)
			xml_req2.update_video_layout_xpath(confID,sID,forcename)
			print "lecture will see %s" %forcename
			mcu.send('req_setVideoLayout.xml')
#def dis_part_all(num_party,MCU_token,MCU_USER_token,messageID,confID,link):
def dis_part_all():
	global MCU_token
	global MCU_USER_token
	global confID
	global link
	global num_party
	message = random.randint(0,65535)
	messageID = str(message)
	i = 0
	while i < num_party :
		time.sleep(10)
		partID = partIDs[i].text
		print partIDs[i].text
		print partIDs[i].text
		partname = partnames[i].text
		print "%s will disconnected" %partname
		i +=1
		xml_req = xml('req_connectParticipant.xml')
		xml_req.updateconfID_PartID_base(MCU_token,MCU_USER_token,messageID,confID,partID)
		xml_req.update_connect(t_f = 'false')
		mcu = MCU(link)
		mcu.send('req_connectParticipant.xml')
#def connect_part_all(num_party,MCU_token,MCU_USER_token,messageID,confID,link):
def connect_part_all():
	global MCU_token
	global MCU_USER_token
	global confID
	global link
	global num_party
	message = random.randint(0,65535)
	messageID = str(message)
	i = 0
	while i < num_party :
		time.sleep(10)
		partID = partIDs[i].text
		print partIDs[i].text
		print partIDs[i].text
		partname = partnames[i].text
		print "%s will be connected" %partname
		i +=1
		xml_req = xml('req_connectParticipant.xml')
		xml_req.updateconfID_PartID_base(MCU_token,MCU_USER_token,messageID,confID,partID)
		xml_req.update_connect(t_f = 'true')
		mcu = MCU(link)
		mcu.send('req_connectParticipant.xml')

# this function for test action 
 
def test():
	while 1:# changed on 0.2
		set_lecture_cyc()
		unmuteall()
		muteall()
		dis_part_all()
		connect_part_all()
		set_lecture_layout_cyc()
config = ConfigParser()
config.read("mcu.ini")
#mcuadd = '172.21.88.140' # will be read from ini file
mcuadd = config.get('MCU','mcu1')
link = 'http://'+ mcuadd 
#confID = '46' # will update a var
confID = config.get('MCU','confID')
s = httplib2.Http() # global var , for keeplive 
message = random.randint(0,65535)
messageID = str(message)
confname = 'pgsauto'+ str(message)
mcu = MCU(link)
mcu_tokens = mcu.gettoken() # login to mcu and get mcu token & mcu user token . return value is tunple 
MCU_token = mcu_tokens[0]
MCU_USER_token = mcu_tokens[1]
print MCU_token
print MCU_USER_token
conf = conference(link)
partIDs = conf.get_allpartIDs()  # 
partnames = conf.get_allpartnames()  # part names
print len(partIDs)
num_party = len(partIDs)
print num_party
d = threading.Thread(name='daemon', target=test)
t = threading.Thread(name='non-daemon', target=getstatus)
t.setDaemon(True)
t.start()
d.start()

t.join()
d.join()





