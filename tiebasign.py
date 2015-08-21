# -*- coding: utf-8 -*-

import baidulogin
import requests, urllib, re, json, time
import getpass

#签到延时，单位为秒，最好不要小于1s以避开验证码
latency = 1

headers = baidulogin.headers
headers['Host'] = 'tieba.baidu.com'
LikeURL = 'http://tieba.baidu.com/f/like/mylike' #贴吧列表URL
SignURL = 'http://tieba.baidu.com/sign/add'      #签到URL

tiebalink = re.compile(r'<a href="/f\?kw=.*?" title=".*?">.*?</a>') #匹配贴吧链接的正则
picktiebalink = re.compile(r'/f\?kw=.*?(?=")')#进一步提取出内部链接

pagelink = re.compile(r'<a href="/f/like/mylike\?&pn=.*?">\d*</a>')#匹配页面链接
pickpagelink = re.compile(r'/f/like/mylike\?&pn=.*?(?=")')#提取页面链接

# 目测贴吧tbs位置有两种：
# 1. <script >
#     // 页面的基本信息
#     var PageData = {
#         'tbs': "40e08ff4a1e4ee841440146445"    };（二战吧）
# 2. <script>PageData.tbs = "49a62bd157e6f43c1440146092";（matlab吧）

tbsre = re.compile(r'(?<=\'tbs\': \").*(?=\")')#提取当前贴吧tbs
tbsre2 = re.compile(r'(?<=PageData\.tbs \= ").*?(?=")')#备选tbs

tiebanamere = re.compile(r'(?<=\=).*')

class AutoSign(object):

	def __init__(self, uname, pw):
		bd = baidulogin.BaiduLogin()
		try:
			self.__BDUSS = bd.login(uname, pw).cookies['BDUSS']
		except KeyError:
			print u'登录失败！'
			exit()
		self.__headersforlist = headers
		self.__headersforlist['Cookie'] = 'BDUSS='+self.__BDUSS#手工填写cookies
		self.__tiebalist = self.fetch_list_all()

	def fetch_list_singlepage(self, singleurl):
		likesource = requests.get(singleurl, headers=self.__headersforlist).content
		tiebalist = tiebalink.findall(likesource)
		tiebalist = map(picktiebalink.findall, tiebalist)#本页面内所有贴吧链接
		return tiebalist

	def fetch_list_all(self):
		tiebalist = self.fetch_list_singlepage(LikeURL)
		pagesource = requests.get(LikeURL, headers=self.__headersforlist).content
		pagelinklist = map(pickpagelink.findall, pagelink.findall(pagesource))
		for l in pagelinklist:
			for sl in self.fetch_list_singlepage('http://tieba.baidu.com'+l[0]):
				tiebalist.append(sl)
		return tiebalist

	def sign_one(self, singleurl):
		headersforsign = self.__headersforlist
		headersforsign['Referer'] = singleurl
		headersforsign['Origin'] = 'http://tieba.baidu.com'
		headersforsign['X-Requested-With'] = 'XMLHttpRequest'
		headersforsign['Cookie'] = 'showCardBeforeSign=1; '+'BDUSS='+self.__BDUSS
		tiebasource = requests.get(singleurl, headers=headersforsign).content
		tbs = tbsre.search(tiebasource)
		if (tbs == None):
			tbs = tbsre2.search(tiebasource)
			if (tbs == None):
				print 'No tbs!'
				return (-1)
		tbs = tbs.group()
		kw = (urllib.unquote(tiebanamere.search(singleurl).group())).decode('gbk')
		formdata = {'ie':'utf-8', 'kw':kw, 'tbs':tbs}
		signreq = requests.post(SignURL, data=formdata, headers=headersforsign)
		# print formdata
		return {'name':kw,'stat':json.loads(signreq.content)['no'],'info':json.loads(signreq.content)['error']}

	def sign_all(self):
		succ = 0
		fail = 0
		total = 0
		signed = 0
		for tieba in self.__tiebalist:
			time.sleep(latency)
			status = self.sign_one('http://tieba.baidu.com'+tieba[0])
			total = total + 1
			if (status['stat'] == 0):
				print u'贴吧：%s 签到成功！'%(status['name'])
				succ = succ + 1
			elif (status['stat'] == 1101):
				print u'贴吧：%s 今天已签到！'%(status['name'])
				signed = signed + 1
			else:
				print u'贴吧：%s 未知错误，错误码：%d！提示信息：%s'%(status['name'], status['stat'], status['info'])
				if (status['stat'] == 1010):
					print u'可能此贴吧已被和谐！'
				fail = fail + 1
		print u'共操作%d个贴吧，其中成功%d个，失败%d个，之前已签%d个！'%(total, succ, fail, signed)

if (__name__=='__main__'):
	print u'请输入贴吧用户名：'
	username = raw_input()
	print u'请输入密码：'
	password = getpass.getpass()
	asrobot = AutoSign(username, password)
	asrobot.sign_all()