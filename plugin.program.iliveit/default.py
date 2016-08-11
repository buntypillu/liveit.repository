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


instalador_nome = "Instalador Live!t"
base_server = "http://liveitkodi.com"
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
base='liveit'
ADDON=xbmcaddon.Addon(id='plugin.program.i'+base)
dialog = xbmcgui.Dialog()    
VERSION = "0.0.9"
PATH = "i"+base    
__ALERTA__ = xbmcgui.Dialog().ok
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

def CATEGORIES():
    packages = json.loads(OPEN_URL(base_server+'/InstalerPackage'))['Packages']
    for package in packages:
        addDir(package['name'],package['url'],1,package['icon'],package['fanart'],package['description'],package['pk'],package['isaddon'],package['restart'],package['forceRestart'])
    setView('movies', 'MAIN')
        
    
def OPEN_URL(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link
    
    
def wizard(name,url,description,pk,isaddon,restart,forceRestart):
	#PURGEPACKAGES()
	#path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
	dp = xbmcgui.DialogProgress()
	dp.create(name,"Download: " + name,'', url)
	lib=os.path.join(PACKAGES, name+'.zip')
	try:
		os.remove(lib)
	except:
		pass
	downloader.download(url, lib, dp)
	addonfolder = '';
	time.sleep(2)
	dp.update(0,name, "Extraindo: " + name)
	
	if isaddon != False:
		addonfolder = ADDONS
	else:
		addonfolder = USERDATA
	extract.all(lib,addonfolder,dp)
	#log_insertion(addonfolder)
	xbmc.executebuiltin('UnloadSkin()')
	xbmc.executebuiltin('ReloadSkin()')
	xbmc.executebuiltin("LoadProfile()")
	xbmc.executebuiltin('UpdateLocalAddons')
	dialog = xbmcgui.Dialog()
	
	if platform() == 'android':
		dialog.ok("Concluido", 'Tudo instalado', 'caso seu kodi trave, reinicie seu dispositivo', 'em caso de duvida contacte o nosso suporte.')
	else:
		dialog.ok("Concluido", 'Tudo instalado', 'volte ao menu para visualizar o conteudo instalado,', 'em caso de duvida contacte o nosso suporte.')
	
	if restart != False:
		dialog = xbmcgui.Dialog()
		dialog.ok("Download Concluido", 'Infelizmente a unica forma de persistir o pacote e', 'compelir o fechamento abrupto do kodi,', 'em seguida re-abra o kodi.')
	
	if forceRestart != False:
		dialog = xbmcgui.Dialog()
		dialog.ok("Download Concluido", 'Infelizmente a unica forma de persistir o pacote e', 'compelir o fechamento abrupto do kodi,', 'jamais saia do kodi manualmente, caso o kodi continue aberto, reinicie sua box ou mate a tarefa do kodi.')
	
	killxbmc()

def PURGEPACKAGES():
	packages_cache_path = xbmc.translatePath(os.path.join('special://home/addons/packages', ''))
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
	#print "Plataforma: " + str(myplatform)
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
		#dialog.ok("[COLOR=red][B]Cuidado  !!![/COLOR][/B]", "Se esta vendo esta mensagem o fechamento do kodi", "foi mal sucedido, por favor mate o kodi ou reinicie sua box",'')
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
		#dialog.ok("[COLOR=red][B]Cuidado  !!![/COLOR][/B]", "Se esta vendo esta mensagem o fechamento do kodi", "foi mal sucedido, por favor mate o kodi ou reinicie sua box",'')
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
		#dialog.ok("[COLOR=red][B]Cuidado  !!![/COLOR][/B]", "Se esta vendo esta mensagem o fechamento do kodi", "foi mal sucedido, por favor mate o kodi ou reinicie sua box",'')
	else: #ATV
		try: os.system('killall AppleTV')
		except: pass
		try: os.system('sudo initctl stop kodi')
		except: pass
		try: os.system('sudo initctl stop xbmc')
		except: pass
		#dialog.ok("[COLOR=red][B]Cuidado  !!![/COLOR][/B]", "Se esta vendo esta mensagem o fechamento do kodi", "foi mal sucedido, por favor mate o kodi ou reinicie sua box",'')    


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

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if ADDON.getSetting('auto-view')=='true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % ADDON.getSetting(viewType) )
        
        
if mode==None or url==None or len(url)<1:
	CATEGORIES()
       
elif mode==1:
	wizard(name,url,description,pk,isaddon,restart,forceRestart)
        

        
xbmcplugin.endOfDirectory(int(sys.argv[1]))

