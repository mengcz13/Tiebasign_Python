# -*- coding: utf-8 -*-

import json, requests

headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,en-US;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Content-Type':'application/x-www-form-urlencoded',
'Host':'passport.baidu.com',#注意这里host可以不要，如果要的话tiebasign里的host也要改！
'Origin':'https://www.baidu.com',
'Referer':'https://www.baidu.com/',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36',
}

BaiduURL = 'https://www.baidu.com/'
TokenURL = 'https://passport.baidu.com/v2/api/?getapi&tpl=mn&apiver=v3'
LoginURL = 'https://passport.baidu.com/v2/api/?login'

class BaiduLogin(object):

	def __init__(self):
		baiduid = requests.get(LoginURL, headers=headers).cookies['BAIDUID']
		headersfortoken = headers
		headersfortoken['Cookie'] = 'BAIDUID='+baiduid
		self.__token = json.loads(requests.get(TokenURL, headers=headersfortoken).text.replace('\'','\"'))['data']['token']

	def login(self, uname, pw):
		forms = {'staticpage':'https://www.baidu.com/cache/user/html/v3Jump.html', 'token':self.__token, 'tpl':'mn', 'username':uname, 'password':pw}
		return requests.post(LoginURL, headers=headers, data=forms)



if (__name__=='__main__'):
	bd = BaiduLogin()
	username = raw_input()
	password = raw_input()
	print bd.login(username, password).cookies
	#cookies中返回的BDUSS应该是百度识别用户的凭据，若登录失败则无BDUSS
	
	