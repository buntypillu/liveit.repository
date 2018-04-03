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
import xbmc, xbmcaddon, xbmcgui, xbmcplugin,os,sys
import shutil
import urllib2,urllib
import re
import extract
import time
import downloader
import plugintools
import zipfile
import ntpath
import json
import xml.etree.ElementTree as ET
from t0mm0.common.net import Net

__ADDON_ID__   = xbmcaddon.Addon().getAddonInfo("id")
__ADDON__	= xbmcaddon.Addon(__ADDON_ID__)
__ADDON_FOLDER__	= __ADDON__.getAddonInfo('path')
__FANART__ 		= os.path.join(__ADDON_FOLDER__,'fanart.jpg')
base_server = "http://liveitkodi.com"
_ICON_ = base_server + '/Logos/liveitaddon.png'
__SKIN__ = 'v2'
instalador_nome = "Instalador Live!t"
__COOKIE_FILE__ = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.program.iliveit/').decode('utf-8'), 'cookie.iliveittv')
__HEADERS__ = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
base='liveit'

dialog = xbmcgui.Dialog()    
VERSION = "1.1.2"
__ALERTA__ = xbmcgui.Dialog().ok

ADDON		   = xbmcaddon.Addon(id='plugin.program.i'+base)
_BASE_ 		   = xbmc.translatePath(os.path.join('special://','home'))
HOME           = xbmc.translatePath('special://home/')
LOG            = xbmc.translatePath('special://logpath/')
PROFILE        = xbmc.translatePath('special://profile/')

ADDONS         = os.path.join(HOME,     'addons')
USERDATA       = os.path.join(HOME,     'userdata')
PACKAGES       = os.path.join(ADDONS,   'packages')

def log_insertion(string):
    path = xbmc.translatePath(os.path.join('special://home/addons','plugin.program.i'+base))
    file_ = path + '/plugin.program.i' +base + '.log'
    with open(file_, "a") as myfile:
        myfile.write(str(string)+'\n')

def abrirDefinincoesMesmo():
	__ADDON__.openSettings()
	xbmc.executebuiltin("Container.SetViewMode(51")

def loginAgora():
	if (not __ADDON__.getSetting('login_name') or not __ADDON__.getSetting('login_password')):
		__ALERTA__('Live!t', 'Precisa de definir o seu Utilizador e Senha')
		abrirDefinincoesMesmo()
	else:
		try:
			net = Net()
			net.set_cookies(__COOKIE_FILE__)
			dados = {'username': __ADDON__.getSetting("login_name"), 'password': __ADDON__.getSetting("login_password")}
			codigo_fonte = net.http_POST(base_server+'/PHP/LoginAddon2.php',form_data=dados,headers=__HEADERS__).content
			elems = ET.fromstring(codigo_fonte)
			
			servid = ''
			nomeus = ''
			tipous = ''
			sucesso = ''
			for child in elems:
				if(child.tag == 'sucesso'):
					sucesso = child.text
				elif(child.tag == 'user'):
					for d in child:
						if(d.tag == 'Nome'):
							nomeus = d.text
						elif(d.tag == 'Tipo'):
							tipous = d.text
						elif(d.tag == 'Servidor'):
							servid = d.text
			
			if sucesso == 'utilizador':
				__ALERTA__('Live!t', 'Utilizador incorreto.')
				__ADDON__.openSettings()
				addDir2('Entrar novamente', 'url', None, None, 'Miniatura', base_server+'/Addon/Imagens/retroceder.png','','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
				xbmc.executebuiltin("Container.SetViewMode(50)")
			elif sucesso == 'senha':
				__ALERTA__('Live!t', 'Senha incorreta.')
				__ADDON__.openSettings()
				addDir2('Entrar novamente', 'url', None, None, 'Miniatura', base_server+'/Addon/Imagens/retroceder.png','','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
				xbmc.executebuiltin("Container.SetViewMode(50)")
			elif sucesso == 'ativo':
				__ALERTA__('Live!t', 'O estado do seu Utilizador encontra-se Inactivo. Para saber mais informações entre em contacto pelo email liveitkodi@gmail.com.')
				xbmc.executebuiltin("Container.SetViewMode(50)")
			elif sucesso == 'yes':
				if servid == '':
					__ALERTA__('Live!t', 'Não foi possível abrir a página. Por favor tente novamente mais tarde.')
				elif servid == 'Teste':
					__ALERTA__('Live!t', 'O seu utilizador é um servidor de teste. Logo não pode instalar a Build. Adquira um pack através do site: http://liveitkodi.com/Aquisicao e após isso terá a sua conta e pode instalar a build.')
				else:
					xbmc.executebuiltin('Notification(%s, %s, %i, %s)'%('Live!t-TV','Secção Iniciada: '+nomeus, 8000, _ICON_))
					CATEGORIES()
			else:
				__ALERTA__('Live!t', 'Não foi possível abrir a página. Por favor tente novamente.')
		except:
			__ALERTA__('Live!t', 'Não foi possível abrir a página. Por favor tente novamente.')

def addDir2(name,url,senha,mode,estilo,iconimage,tipo,tipo_user,servidor_user,data_user,fanart,pasta=True,total=1):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', fanart)
	liz.setArt({'fanart': fanart})
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)
	return ok

def CATEGORIES():
    packages = json.loads(OPEN_URL(base_server+'/InstalerPackage'))['Packages']
    for package in packages:
		if package['pk'] == 1:
			addDir(package['name'],package['url'],1,package['icon'],package['fanart'],package['description'],package['pk'],package['isaddon'],package['restart'],package['forceRestart'])
		elif(package['pk'] == 3):
			addDir(package['name'],package['url'],2,package['icon'],package['fanart'],package['description'],package['pk'],package['isaddon'],package['restart'],package['forceRestart'])
    xbmc.executebuiltin("Container.SetViewMode(50)")
        
    
def OPEN_URL(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link
    
    
def wizard(name,url,description,pk,isaddon,restart,forceRestart):
	#PURGEPACKAGES()
	dp = xbmcgui.DialogProgress()
	dp.create(name,"A fazer download: " + name,'')
	lib=os.path.join(HOME, name+'.zip')
	try:
		os.remove(lib)
	except:
		pass
	downloader.download(url, lib, dp)
	addonfolder = '';
	time.sleep(2)
	dp.update(0,name, "A extrair: " + name)
	extract.all(lib,HOME,dp)
	xbmc.executebuiltin('UnloadSkin()')
	xbmc.executebuiltin('ReloadSkin()')
	xbmc.executebuiltin("LoadProfile()")
	xbmc.executebuiltin('UpdateLocalAddons')
	dialog = xbmcgui.Dialog()
	
	if platform() == 'android':
		dialog.ok("Concluido", 'Tudo instalado', 'caso seu kodi trave, reinicie seu dispositivo', 'em caso de duvida contacte o nosso suporte.')
	else:
		dialog.ok("Concluido", 'Tudo instalado', 'volte ao menu para visualizar o conteudo instalado,', 'em caso de duvida contacte o nosso suporte.')
	
	if restart == True:
		dialog = xbmcgui.Dialog()
		dialog.ok("Download Concluido", 'Infelizmente a unica forma de persistir o pacote e', 'compelir o fechamento abrupto do kodi,', 'em seguida re-abra o kodi.')
	
	if forceRestart == True:
		dialog = xbmcgui.Dialog()
		dialog.ok("Download Concluido", 'Infelizmente a unica forma de persistir o pacote e', 'compelir o fechamento abrupto do kodi,', 'jamais saia do kodi manualmente, caso o kodi continue aberto, reinicie sua box ou mate a tarefa do kodi.')
	
	killxbmc()

def wizard2(name,url,description,pk,isaddon,restart,forceRestart):
	#PURGEPACKAGES()
	dp = xbmcgui.DialogProgress()
	dp.create(name,"A fazer download: " + name,'')
	lib=os.path.join(PACKAGES, name+'.zip')
	try:
		os.remove(lib)
	except:
		pass
	downloader.download(url, lib, dp)
	time.sleep(2)
	dp.update(0,name, "A extrair: " + name)
	extract.all(lib,ADDONS,dp)
	xbmc.executebuiltin('UnloadSkin()')
	xbmc.executebuiltin('ReloadSkin()')
	xbmc.executebuiltin("LoadProfile()")
	xbmc.executebuiltin('UpdateLocalAddons')
	dialog = xbmcgui.Dialog()
	
	if platform() == 'android':
		dialog.ok("Concluido", 'Tudo instalado', 'caso seu kodi trave, reinicie seu dispositivo', 'em caso de duvida contacte o nosso suporte.')
	else:
		dialog.ok("Concluido", 'Tudo instalado', 'volte ao menu para visualizar o conteudo instalado,', 'em caso de duvida contacte o nosso suporte.')
	
	if restart == True:
		dialog = xbmcgui.Dialog()
		dialog.ok("Download Concluido", 'Infelizmente a unica forma de persistir o pacote e', 'compelir o fechamento abrupto do kodi,', 'em seguida re-abra o kodi.')
	
	if forceRestart == True:
		dialog = xbmcgui.Dialog()
		dialog.ok("Download Concluido", 'Infelizmente a unica forma de persistir o pacote e', 'compelir o fechamento abrupto do kodi,', 'jamais saia do kodi manualmente, caso o kodi continue aberto, reinicie sua box ou mate a tarefa do kodi.')
	
	killxbmc()


def PURGEPACKAGES():
	packages_cache_path = PACKAGES
	try:    
		for root, dirs, files in os.walk(packages_cache_path):
			file_count = 0
			file_count += len(files)
			if file_count > 0:
				for f in files:
					os.unlink(os.path.join(root, f))
				for d in dirs:
					shutil.rmtree(os.path.join(root, d))
				dialog = xbmcgui.Dialog()
			else:
				pass
	except: 
		pass

		
def killxbmc():
	choice = xbmcgui.Dialog().yesno('Fechar Kodi abruptamente', 'Estas prestes a fechar Kodi', 'Queres continuar?', nolabel='Nao, Cancelar',yeslabel='Sim, Fechar')
	if choice == 0:
		return
	elif choice == 1:
		pass
	myplatform = platform()
	if myplatform == 'osx': # OSX
		try: os.system('killall -9 XBMC')
		except: pass
		try: os.system('killall -9 Kodi')
		except: pass
	elif myplatform == 'linux': #Linux
		try: os.system('killall XBMC')
		except: pass
		try: os.system('killall Kodi')
		except: pass
		try: os.system('killall -9 xbmc.bin')
		except: pass
		try: os.system('killall -9 kodi.bin')
		except: pass
		dialog.ok("[COLOR=red][B]Cuidado  !!![/COLOR][/B]", "Se esta vendo esta mensagem o fechamento do kodi", "foi mal sucedido, por favor mate o kodi ou reinicie sua box",'')
	elif myplatform == 'android': # Android  
		try: os.system('adb shell am force-stop org.xbmc.kodi')
		except: pass
		try: os.system('adb shell am force-stop org.kodi')
		except: pass
		try: os.system('adb shell am force-stop org.xbmc.xbmc')
		except: pass
		try: os.system('adb shell am force-stop org.xbmc')
		except: pass
		try: os.system("ps | grep org.kodi | awk '{print $2}' | xargs kill")
		except: pass
		try: os.system("ps | grep org.xbmc.kodi | awk '{print $2}' | xargs kill")
		except: pass
		dialog.ok("[COLOR=red][B]Cuidado  !!![/COLOR][/B]", "Se esta vendo esta mensagem o fechamento do kodi", "foi mal sucedido, por favor mate o kodi ou reinicie sua box",'')
	elif myplatform == 'windows': # Windows
		try:
			os.system('@ECHO off')
			os.system('tskill XBMC.exe')
		except: pass
		try:
			os.system('@ECHO off')
			os.system('tskill Kodi.exe')
		except: pass
		try:
			os.system('@ECHO off')
			os.system('TASKKILL /im Kodi.exe /f')
		except: pass
		try:
			os.system('@ECHO off')
			os.system('TASKKILL /im XBMC.exe /f')
		except: pass
		dialog.ok("[COLOR=red][B]Cuidado  !!![/COLOR][/B]", "Se esta vendo esta mensagem o fechamento do kodi", "foi mal sucedido, por favor mate o kodi ou reinicie sua box",'')
	else: #ATV
		try: os.system('killall AppleTV')
		except: pass
		try: os.system('sudo initctl stop kodi')
		except: pass
		try: os.system('sudo initctl stop xbmc')
		except: pass
		dialog.ok("[COLOR=red][B]Cuidado  !!![/COLOR][/B]", "Se esta vendo esta mensagem o fechamento do kodi", "foi mal sucedido, por favor mate o kodi ou reinicie sua box",'')		
	
def platform():
	if xbmc.getCondVisibility('system.platform.android'):
		return 'android'
	elif xbmc.getCondVisibility('system.platform.linux'):
		return 'linux'
	elif xbmc.getCondVisibility('system.platform.windows'):
		return 'windows'
	elif xbmc.getCondVisibility('system.platform.osx'):
		return 'osx'
	elif xbmc.getCondVisibility('system.platform.atv2'):
		return 'atv2'
	elif xbmc.getCondVisibility('system.platform.ios'):
		return 'ios'


def addDir(name,url,mode,iconimage,fanart,description,pk,isaddon,restart,forceRestart):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)+"&pk="+urllib.quote_plus(str(pk))+"&isaddon="+str(isaddon)+"&restart="+str(restart)+"&forceRestart="+str(forceRestart)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
	liz.setProperty( "Fanart_Image", fanart )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok
       
        
def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
			params=sys.argv[2]
			cleanedparams=params.replace('?','')
			if (params[len(params)-1]=='/'):
					params=params[0:len(params)-2]
			pairsofparams=cleanedparams.split('&')
			param={}
			for i in range(len(pairsofparams)):
					splitparams={}
					splitparams=pairsofparams[i].split('=')
					if (len(splitparams))==2:
							param[splitparams[0]]=splitparams[1]
							
	return param
        
                      
params=get_params()
url=None
name=None
mode=None
iconimage=None
fanart=None
description=None
pk=None
isaddon=None
restart=None
forceRestart=None


try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:        
        mode=int(params["mode"])
except:
        pass
try:        
        fanart=urllib.unquote_plus(params["fanart"])
except:
        pass
try:        
        description=urllib.unquote_plus(params["description"])
except:
        pass
try:        
        pk=urllib.unquote_plus(params["pk"])
except:
        pass
try:        
        isaddon=params["isaddon"]
except:
        pass
try:        
        restart=params["restart"]
except:
        pass
try:        
        forceRestart=params["forceRestart"]
except:
        pass
    
if mode==None or url==None or len(url)<1: loginAgora()
elif mode==1: wizard(name,url,description,pk,isaddon,restart,forceRestart)
elif mode==2: wizard2(name,url,description,pk,isaddon,restart,forceRestart)
elif mode==3: loginAgora()
elif mode==4: CATEGORIES()
   
xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False)