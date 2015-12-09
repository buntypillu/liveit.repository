#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


##############BIBLIOTECAS A IMPORTAR E DEFINICOES####################
import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os,json,threading,xbmcvfs,cookielib,sys,platform,time,gzip,glob,datetime,thread
from t0mm0.common.net import Net
import xml.etree.ElementTree as ET

####################################################### CONSTANTES #####################################################

global g_timer

__estilagem__ = 'novo'
__ADDON_ID__   = xbmcaddon.Addon().getAddonInfo("id")
__ADDON__	= xbmcaddon.Addon(__ADDON_ID__)
__ADDON_FOLDER__	= __ADDON__.getAddonInfo('path')
__SETTING__	= xbmcaddon.Addon().getSetting
__ART_FOLDER__	= os.path.join(__ADDON_FOLDER__,'resources','img')
__FANART__ 		= os.path.join(__ADDON_FOLDER__,'fanart.jpg')
__SKIN__ = 'v1'
__SITE__ = 'http://www.pcteckserv.com/GrupoKodi/PHP/'
__SITEAddon__ = 'http://www.pcteckserv.com/GrupoKodi/Addon/'
__EPG__ = 'http://www.pcteckserv.com/GrupoKodi/epg.gz'
__FOLDER_EPG__ = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.LiveTV/').decode('utf-8'), 'epg')
__ALERTA__ = xbmcgui.Dialog().ok

__COOKIE_FILE__ = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.LiveTV/').decode('utf-8'), 'cookie.livetv')
__HEADERS__ = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
user_agent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
###################################################################################
#                              Iniciar Addon		                                  #
###################################################################################

def mac_for_ip():
	macadresses = xbmc.getInfoLabel("Network.MacAddress")
	if xbmc.getInfoLabel('Network.MacAddress') != None:
		if not ":" in macadresses:
			time.sleep(3)
			macadresses = xbmc.getInfoLabel('Network.MacAddress')
	#g_timer = time.time()
	return macadresses
  
def menu():
	check_login = login()
	if check_login['mac']['tem'] == 'no':
		xbmc.executebuiltin("Container.SetViewMode(51)")
	else:
		if check_login['sucesso']['resultado'] == 'yes':
			menus = {
				'nome': '',
				'logo': '',
				'link': '',
				'tipo': '',
				'senha': ''
				}
			menus['nome'] = "Participacoes"
			menus['logo'] = check_login['info']['logo']
			menus['link'] = check_login['info']['link']
			menus['tipo'] = "patrocinadores"
			menus['senha'] = ""
			check_login['menus'].append(menus)

			Menu_inicial(check_login)
			print "rei"
			print check_login['datafim']['data']
			print "rei 2"
			addDir(check_login['datafim']['data'], 'url', None, 2000, 'Lista Grande', __SITEAddon__+"Imagens/doacoes.png", 0)
			addDir('Definições', 'url', None, 1000, 'Lista Grande', __SITEAddon__+"Imagens/definicoes.png", 0)
			xbmc.executebuiltin("Container.SetViewMode(51)")
		elif(check_login['sucesso']['resultado'] == 'ocupado'):
			__ALERTA__('Live!t TV', 'Entre novamente para iniciar a sua Secção.')
		else:
			addDir('Alterar Definições', 'url', None, 1000, 'Lista Grande', __SITEAddon__+"Imagens/definicoes.png", 0)
			addDir('Entrar novamente', 'url', None, None, 'Lista Grande', __SITEAddon__+"Imagens/retroceder.png", 0)
			xbmc.executebuiltin("Container.SetViewMode(51)")
###################################################################################
#                              Login Addon		                                  #
###################################################################################

def login():
	informacoes = {
		'user' : {
			'nome': '',
			'email': '',
			'senhaadulto': ''
		},
		'sucesso' :{
			'resultado': ''
		},
		'mac' :{
			'tem': ''
		},
		'macestado' :{
			'mac': ''
		},
		'datafim' :{
			'data': ''
		},
		'info' : {
			'epg': '',
			'logo': '',
			'link': ''
		},
		'menus': []
	} # 
	
	if __ADDON__.getSetting("login_name") == '' or __ADDON__.getSetting('login_password') == '':
		__ALERTA__('Live!t TV', 'Precisa de definir o seu Utilizador e Senha')
		return informacoes
	else:
		try:
			# ipmac = socket.gethostbyname(socket.gethostname())

			# ts = time.time()
			# dtt = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y (%H:%M:%S)')
			# , 'data_nova': dtt
			macaddr = mac_for_ip();
			
			if macaddr == 'Ocupada':
				informacoes['mac']['tem'] = 'yes'
				informacoes['sucesso']['resultado'] = 'ocupado'
			else:
				sisss = platform.system()
				if sisss == 'Windows':
					trrrr = macaddr.replace(':', '-')
					macadd = trrrr.upper()
				else:
					macadd = macaddr.lower()

				print "mac"
				print macadd
				
				net = Net()
				net.set_cookies(__COOKIE_FILE__)
				dados = {'username': __ADDON__.getSetting("login_name"), 'password': __ADDON__.getSetting("login_password"), 'macadress': macadd}
				codigo_fonte = net.http_POST(__SITE__+'LoginAddon2.php',form_data=dados,headers=__HEADERS__).content
				informacoes['macestado']['mac'] == macadd
				
				elems = ET.fromstring(codigo_fonte)
				for child in elems:
					if(child.tag == 'sucesso'):
						informacoes['sucesso']['resultado'] = child.text
					elif(child.tag == 'mac_adress'):
						informacoes['mac']['tem'] = child.text
					elif(child.tag == 'user'):
						for d in child:
							if(d.tag == 'Nome'):
								informacoes['user']['nome'] = d.text
							elif(d.tag == 'Email'):
								informacoes['user']['email'] = d.text
							elif(d.tag == 'DataFim'):
								try:
									informacoes['datafim']['data'] = "Membro Ativo até "+ d.text
								except:
									informacoes['datafim']['data'] = "Membro Ativo Sem Doacao!"
							elif(d.tag == 'SenhaAdultos'):
								informacoes['user']['senhaadulto'] = d.text		
					elif(child.tag == 'info'):
						for e in child:
							if(e.tag == 'epg'):
								informacoes['info']['epg'] = e.text
							elif(e.tag == 'logo'):
								informacoes['info']['logo'] = e.text
							elif(e.tag == 'link'):
								informacoes['info']['link'] = e.text
					elif(child.tag == 'menus'):
						menu = {
								'nome': '',
								'logo': '',
								'link': '',
								'tipo': '',
								'senha': ''
							}
						for g in child:
							if(g.tag == 'nome'):
								menu['nome'] = g.text
							elif(g.tag == 'logo'):
								menu['logo'] = g.text
							elif(g.tag == 'link'):
								menu['link'] = g.text
							elif(g.tag == 'tipo'):
								menu['tipo'] = g.text
							elif(g.tag == 'senha'):
								menu['senha'] = informacoes['user']['senhaadulto']
						informacoes['menus'].append(menu)
					else: 
						print("Não sei o que estou a ler")
		except:
			__ALERTA__('Live!t TV', 'Não foi possível abrir a página. Por favor tente novamente.')
			return informacoes
		if informacoes['sucesso']['resultado'] != '':
			if informacoes['sucesso']['resultado'] == 'no':
				__ALERTA__('Live!t TV', 'Utilizador e/ou Senha incorretos.')
			else:
				if informacoes['mac']['tem'] == 'no':
					__ALERTA__('Live!t TV', 'Equipamento ainda não registado. Por favor registe.')
				else:						
					xbmc.executebuiltin("XBMC.Notification(Live!t TV, Sessão iniciada: "+ informacoes['user']['nome'] +", '10000', "+__ADDON_FOLDER__+"/icon.png)")
		else:
			if informacoes['mac']['tem'] == 'no':
				__ALERTA__('Live!t TV', 'Equipamento ainda não registado. Por favor registe.')
				
			else:
				net.save_cookies(__COOKIE_FILE__)
				xbmc.executebuiltin("XBMC.Notification(Live!t TV, Sessão iniciada: "+ informacoes['user']['nome'] +", '10000', "+__ADDON_FOLDER__+"/icon.png)")
		return informacoes

###############################################################################################################
#                                                   Menus                                                     #
###############################################################################################################

def Menu_inicial(men):
	for menu in men['menus']:
		nome = menu['nome']
		logo = menu['logo']
		link = menu['link']
		tipo = menu['tipo']
		senha = menu['senha']
		if(tipo == 'adulto'):
			addDir(nome,link,senha,3,'Miniatura',logo)
		elif(tipo == 'patrocinadores'):
			addDir(nome,link,None,1,'Lista',logo)
		else:
			addDir(nome,link,None,1,'Miniatura',logo)
			
	thread.start_new_thread( obter_ficheiro_epg, () )

def listar_grupos_adultos(url,senha,estilo):
	if(__ADDON__.getSetting("login_adultos") == ''):
		__ALERTA__('Live!t TV', 'Preencha o campo senha para adultos.')
	elif(__ADDON__.getSetting("login_adultos") != senha):
		__ALERTA__('Live!t TV', 'Senha para adultos incorrecta. Verifique e tente de novo.')
	else:
		listar_grupos(url,estilo)
	
def listar_grupos(url,estilo):
	page_with_xml = urllib2.urlopen(url).readlines()
	for line in page_with_xml:
		params = line.split(',')
		try:
			nomee = params[0]
			imag = params[1]
			urlll = params[2]
			estil = params[3]
			paramss = estil.split('\n')
			addDir(nomee,urlll,None,2,paramss[0],imag)
		except:
			pass
	estiloSelect = returnestilo(estilo)
	xbmc.executebuiltin(estiloSelect)
	
def listar_canais_url(nome,url,estilo):
	if url != 'nada':
		page_with_xml = urllib2.urlopen(url).readlines()
		f = open(os.path.join(__FOLDER_EPG__, 'epg'), mode="r")
		codigo = f.read()
		f.close()
		ts = time.time()
		st = int(datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S'))
	
		# page_with_xml = urllib2.urlopen(url).readlines()
		for line in page_with_xml:
			params = line.split(',')
			try:
				nomee = params[0]
				img = params[1].replace(' rtmp','rtmp').replace(' rtsp','rtsp').replace(' http','http')
				rtmp = params[2].replace(' rtmp','rtmp').replace(' rtsp','rtsp').replace(' http','http')
				grup = params[3]
				id_it = params[4].rstrip()
				if(grup == nome):
					twrv = ThreadWithReturnValue(target=getProgramacaoDiaria, args=(id_it, st,codigo))

					twrv.start()
					programa = twrv.join() 

					if programa != '':
						nomewp = nomee + " | "+ programa
					else:
						nomewp = nomee
					
					addLink(nomewp,rtmp,img,id_it)
			except:
				pass
		estiloSelect = returnestilo(estilo)
		xbmc.executebuiltin(estiloSelect)
		
###############################################################################################################
#                                                   EPG                                                     #
###############################################################################################################
def obter_ficheiro_epg():

	if not xbmcvfs.exists(__FOLDER_EPG__):
		xbmcvfs.mkdirs(__FOLDER_EPG__)

	"""horaAtual = time.strftime("%d/%m/%Y")
	
	ficheiroData = os.path.join(__FOLDER_EPG__, 'ultima.txt')

	if not xbmcvfs.exists(ficheiroData):
		f = open(ficheiroData, mode="w")
		f.write("")
		f.close()

	f = open(ficheiroData, mode="r")
	dataAntiga = f.read()
	f.close()

	if (time.strptime(dataAntiga, "%d/%m/%Y")) < horaAtual or not dataAntiga:
		f = open(ficheiroData, mode="w")
		f.write(str(horaAtual))
		f.close()"""

	urllib.urlretrieve(__EPG__, os.path.join(__FOLDER_EPG__, 'epg.gz'))		

	for gzip_path in glob.glob(__FOLDER_EPG__ + "/*.gz"):
		inf = gzip.open(gzip_path, 'rb')
		s = inf.read()
		inf.close()

		gzip_fname = os.path.basename(gzip_path)
		fname = gzip_fname[:-3]
		uncompressed_path = os.path.join(__FOLDER_EPG__, fname)

		open(uncompressed_path, 'w').write(s)


def getProgramacaoDiaria(idCanal, diahora, codigo):

	source = re.compile('<programme channel="'+idCanal+'" start="(.+?) \+0100" stop="(.+?) \+0100">\s+<title lang="pt">(.+?)<\/title>').findall(codigo)

	programa = ''

	for start, stop, programa1  in source:

		if(int(start) < diahora and int(stop) > diahora):
			programa = programa1
	return programa


def programacao_canal(idCanal):

	f = open(os.path.join(__FOLDER_EPG__, 'epg'), mode="r")
	codigo = f.read()
	f.close()

	ts = time.time()
	st = int(datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d'))

	diahora = int(str(st)+'060000')
	diaamanha = int(str(st+1)+'060000')

	source = re.compile('<programme channel="'+idCanal+'" start="(.+?) \+0100" stop="(.+?) \+0100">\s+<title lang="pt">(.+?)<\/title>').findall(codigo)

	programa = ''

	titles=['[B][COLOR white]Programação:[/COLOR][/B]']

    
	for start, stop, programa1 in source:

		start1 = re.compile('([0-9]{4}[0-1][0-9][0-3][0-9])([0-9]{2})([0-9]{2})([0-9]{2})').findall(start)
		stop1 = re.compile('([0-9]{4}[0-1][0-9][0-3][0-9])([0-9]{2})([0-9]{2})([0-9]{2})').findall(stop)

		if(int(start) > diahora and int(start) < diaamanha ):
			titles.append('\n[B]%s:%s -> %s:%s[/B] - %s' % (start1[0][1], start1[0][2], stop1[0][1], stop1[0][2], programa1))


	programacao = '\n'.join(titles)
	try:
		xbmc.executebuiltin("ActivateWindow(10147)")
		window = xbmcgui.Window(10147)
		xbmc.sleep(100)
		window.getControl(1).setLabel('Live!t TV')
		window.getControl(5).setText(programacao)
	except:
		pass


####################### THREADS ######################

from threading import Thread

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None
    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)
    def join(self):
        Thread.join(self)
        return self._return

###################################################################################
#                              DEFININCOES		                                  #
###################################################################################	
def returnestilo(estilonovo):
	__estilagem__ = ""
	if estilonovo == "Lista Grande":
		__estilagem__ = "Container.SetViewMode(51)"
	elif estilonovo == "Lista":
		__estilagem__ ="Container.SetViewMode(50)"
	elif estilonovo == "Miniatura":
		__estilagem__ ="Container.SetViewMode(500)"
	elif estilonovo == "Amplo":
		__estilagem__ = "Container.SetViewMode(551)"
	return __estilagem__
	
def abrirDefinincoes():
	__ADDON__.openSettings()
	addDir('Entrar novamente', 'url', None, None, 'Lista Grande', __SITEAddon__+"Imagens/retroceder.png", 0)
	xbmc.executebuiltin("Container.SetViewMode(51)")

def abrirNada():
	xbmc.executebuiltin("Container.SetViewMode(51)")
	
def addDir(name,url,senha,mode,estilo,iconimage,pasta=True,total=1):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&senha="+str(senha)+"&estilo="+urllib.quote_plus(estilo)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	contextMenuItems = []
	contextMenuItems.append(('Movie Information', 'XBMC.Action(Info)'))
	liz.addContextMenuItems(contextMenuItems, replaceItems=True)
	liz.setProperty('fanart_image', iconimage)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)
	return ok
	
def addFolder(name,url,mode,iconimage,folder):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)
	return ok
	
def addLink(name,url,iconimage,idCanal):
	cm=[]
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	cm.append(('Ver programação', 'XBMC.RunPlugin(%s?mode=31&name=%s&url=%s&iconimage=%s&idCanal=%s)'%(sys.argv[0],urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage), urllib.quote_plus(idCanal))))
	#cm.append(('Ver programação', "XBMC.RunPlugin(%s?mode=%s&name=%s&url=%s)"%(sys.argv[0],31,name,url)))
	liz.addContextMenuItems(cm, replaceItems=False)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok

############################################################################################################
#                                               GET PARAMS                                                 #
############################################################################################################          
def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'): params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2: param[splitparams[0]]=splitparams[1]
	return param


params=get_params()
url=None
name=None
mode=None
iconimage=None
link=None
senha=None
estilo=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        estilo=urllib.unquote_plus(params["estilo"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:        
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:        
        senha=urllib.unquote_plus(params["senha"])
except:
        pass
try:
		idCanal=urllib.unquote_plus(params["idCanal"])
except:
		pass

###############################################################################################################
#                                                   MODOS                                                     #
###############################################################################################################

if mode==None or url==None or len(url)<1: menu()
elif mode==1: listar_grupos(str(url),estilo)
elif mode==2: listar_canais_url(str(name),str(url),estilo)
elif mode==3: listar_grupos_adultos(str(url),str(senha),estilo)
elif mode==10: minhaConta()
elif mode==1000: abrirDefinincoes()
elif mode==2000: abrirNada()
elif mode==31: programacao_canal(idCanal)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
