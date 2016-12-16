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
import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os,json,glob,threading,gzip,xbmcvfs,cookielib,pprint,datetime,thread,time,urlparse,base64
import xml.etree.ElementTree as ET
from resources.lib import common
import fileUtils as fu
from datetime import date
from bs4 import BeautifulSoup
from resources.lib import Downloader #Enen92 class
from resources.lib import Player
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from t0mm0.common.net import HttpResponse
from resources.lib import URLResolverMedia
from resources.lib import Trakt
from resources.lib import Database
from unicodedata import normalize

####################################################### CONSTANTES #####################################################

global g_timer

AddonTitle = "Live!t TV"
__ADDON_ID__   = xbmcaddon.Addon().getAddonInfo("id")
__ADDON__	= xbmcaddon.Addon(__ADDON_ID__)
__ADDONVERSION__ = __ADDON__.getAddonInfo('version')
__ADDON_FOLDER__	= __ADDON__.getAddonInfo('path')
__SETTING__	= xbmcaddon.Addon().getSetting
__ART_FOLDER__	= __ADDON_FOLDER__ + '/resources/img/'
__FANART__ 		= os.path.join(__ADDON_FOLDER__,'fanart.jpg')
_ICON_ = __ADDON_FOLDER__ + '/icon.png'
__SKIN__ = 'v2'
__SITE__ = 'http://liveitkodi.com/PHP/'
__SITEAddon__ = 'http://liveitkodi.com/Addon/'
__EPG__ = __ADDON__.getSetting("lista_epg")
__FOLDER_EPG__ = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.LiveTV/').decode('utf-8'), 'epgliveit')
__ALERTA__ = xbmcgui.Dialog().ok
__COOKIE_FILE__ = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.LiveTV/').decode('utf-8'), 'cookie.liveittv')
__HEADERS__ = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
check_login = {}
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7', 'Content-Type': 'application/json'}
__PASTA_DADOS__ = Addon(__ADDON_ID__).get_profile().decode("utf-8")
__PASTA_FILMES__ = xbmc.translatePath(__ADDON__.getSetting('bibliotecaFilmes'))
__PASTA_SERIES__ = xbmc.translatePath(__ADDON__.getSetting('bibliotecaSeries'))
__SITEAPI__ = base64.urlsafe_b64decode('aHR0cDovL215YXBpbXAudGsv')
__SITEFILMES__ = base64.urlsafe_b64decode('aHR0cDovL215YXBpbXAudGsvYXBpLw==')
__SITEFILMES2__ = base64.urlsafe_b64decode('aHR0cDovL21ycGlyYWN5Lm1sLw==')

###################################################################################
#                              Iniciar Addon		                                  #
###################################################################################
def menu():
	if (not __ADDON__.getSetting('login_name') or not __ADDON__.getSetting('login_password')):
		__ALERTA__('Live!t TV', 'Precisa de definir o seu Utilizador e Senha')
		abrirDefinincoes()
		
	else:
		check_login = login()
		database = Database.isExists()
		if check_login['user']['nome'] != '':
			if check_login['sucesso']['resultado'] == 'yes':
				menus = {
					'nome': '',
					'logo': '',
					'link': '',
					'tipo': '',
					'senha': ''
					}
				menus1 = {
					'nome': '',
					'logo': '',
					'link': '',
					'tipo': '',
					'senha': ''
					}
				menus3 = {
					'nome': '',
					'logo': '',
					'link': '',
					'tipo': '',
					'senha': ''
					}
				if check_login['datafim']['data'] != "Membro Ativo Sem Doacao!":
					if check_login['user']['dias'] == '5' or check_login['user']['dias'] == '4' or check_login['user']['dias'] == '3' or check_login['user']['dias'] == '2' or check_login['user']['dias'] == '1':
						__ALERTA__('Live!t TV', 'Faltam '+check_login['user']['dias']+' dias para o serviço expirar.')
					if check_login['user']['dias'] == '0':
						__ALERTA__('Live!t TV', 'É hoje que o seu serviço expira. Faça a sua Renovação. Caso não faça irá ficar Inactivo Hoje.')
				if check_login['datafim']['data'] != "Membro Ativo Sem Doacao!":
					menus2 = {
					'nome': '',
					'logo': '',
					'link': '',
					'tipo': '',
					'senha': ''
					}
					menus2['nome'] = check_login['datafim']['data']
					menus2['logo'] = __SITEAddon__+"Imagens/estadomembro.png"
					menus2['link'] = 'url'
					menus2['tipo'] = "estado"
					menus2['senha'] = ""
					menus2['fanart'] = os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png')
					check_login['menus'].append(menus2)
				#menus['nome'] = "Participacoes"
				#menus['logo'] = check_login['info']['logo']
				#menus['link'] = check_login['info']['link']
				#menus['tipo'] = "patrocinadores"
				#menus['senha'] = ""
				#menus['fanart'] = os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png')
				#check_login['menus'].append(menus)
				menus1['nome'] = "Novidades"
				menus1['logo'] = check_login['info']['logo2']
				menus1['link'] = check_login['info']['link2']
				menus1['tipo'] = "novidades"
				menus1['senha'] = ""
				menus1['fanart'] = os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png')
				check_login['menus'].append(menus1)
				menus3['nome'] = "Pesquisa"
				menus3['logo'] = os.path.join(__ART_FOLDER__, __SKIN__, 'pesquisa.png')
				menus3['link'] = __SITEFILMES__
				menus3['tipo'] = "pesquisa"
				menus3['senha'] = ""
				menus3['fanart'] = os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png')
				check_login['menus'].append(menus3)
				Menu_inicial(check_login,False,'')
			elif check_login['sucesso']['resultado'] == 'utilizador':
				__ALERTA__('Live!t TV', 'Utilizador incorreto.')
				addDir('Alterar Definições', 'url', None, 1000, 'Miniatura', __SITEAddon__+"Imagens/definicoes.png",'','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
				addDir('Entrar novamente', 'url', None, None, 'Miniatura', __SITEAddon__+"Imagens/retroceder.png",'','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
				vista_menu()
			elif check_login['sucesso']['resultado'] == 'senha':
				__ALERTA__('Live!t TV', 'Senha incorreta.')
				addDir('Alterar Definições', 'url', None, 1000, 'Miniatura', __SITEAddon__+"Imagens/definicoes.png",'','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
				addDir('Entrar novamente', 'url', None, None, 'Miniatura', __SITEAddon__+"Imagens/retroceder.png",'','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
				vista_menu()
			elif check_login['sucesso']['resultado'] == 'ativo':
				__ALERTA__('Live!t TV', 'O estado do seu Utilizador encontra-se Inactivo. Para saber mais informações entre em contacto pelo email liveitkodi@gmail.com.')
				vista_menu()
			else:
				__ALERTA__('Live!t TV', 'Não foi possível abrir a página. Por favor tente novamente.')
				vista_menu()
		else:
			addDir('Alterar Definições', 'url', None, 1000, 'Miniatura', __SITEAddon__+"Imagens/definicoes.png",'','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
			addDir('Entrar novamente', 'url', None, None, 'Miniatura', __SITEAddon__+"Imagens/retroceder.png",'','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
			vista_menu()

###################################################################################
#                              Login Addon		                                  #
###################################################################################
def minhaConta(data_user,estilo):
	addDir(data_user, 'url', None, None, estilo, __SITEAddon__+"Imagens/estadomembro.png",'','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
	addDir('Definições', 'url', None, 1000, estilo, __SITEAddon__+"Imagens/definicoes.png",'','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
	vista_menu()

def login():
	informacoes = {
		'user' : {
			'nome': '',
			'nome': '',
			'email': '',
			'tipo': '',
			'dias': '',
			'lista': '',
			'servidor': '',
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
			'logo2': '',
			'log': '',
			'user': '',
			'password': '',
			'link2': '',
			'link': ''
		},
		'menus': []
	} # 
	
	try:
		net = Net()
		net.set_cookies(__COOKIE_FILE__)
		dados = {'username': __ADDON__.getSetting("login_name"), 'password': __ADDON__.getSetting("login_password")}
		
		codigo_fonte = net.http_POST(__SITE__+'LoginAddon2.php',form_data=dados,headers=__HEADERS__).content
		elems = ET.fromstring(codigo_fonte)
		for child in elems:
			if(child.tag == 'sucesso'):
				informacoes['sucesso']['resultado'] = child.text
			elif(child.tag == 'user'):
				for d in child:
					if(d.tag == 'Nome'):
						informacoes['user']['nome'] = d.text
					elif(d.tag == 'Email'):
						informacoes['user']['email'] = d.text
					elif(d.tag == 'Servidor'):
						informacoes['user']['servidor'] = d.text
					elif(d.tag == 'Tipo'):
						informacoes['user']['tipo'] = d.text
					elif(d.tag == 'dias'):
						informacoes['user']['dias'] = d.text
					elif(d.tag == 'Lista'):
						informacoes['user']['lista'] = d.text
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
					elif(e.tag == 'logo2'):
						informacoes['info']['logo2'] = e.text
					elif(e.tag == 'link2'):
						informacoes['info']['link2'] = e.text
					elif(e.tag == 'log'):
						informacoes['info']['log'] = e.text
					elif(e.tag == 'user'):
						informacoes['info']['user'] = e.text
					elif(e.tag == 'password'):
						informacoes['info']['password'] = e.text
			elif(child.tag == 'menus'):
				menu = {
						'nome': '',
						'logo': '',
						'link': '',
						'tipo': '',
						'senha': '',
						'fanart': ''
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
					elif(g.tag == 'fanart'):
						menu['fanart'] = g.text
					elif(g.tag == 'senha'):
						menu['senha'] = informacoes['user']['senhaadulto']
				if informacoes['datafim']['data'] == "Membro Ativo Sem Doacao!":
					if menu['nome'] != 'Adultos':
						informacoes['menus'].append(menu)
				else:
					informacoes['menus'].append(menu)
			else: 
				print "Não sei o que estou a ler"
	except:
		__ALERTA__('Live!t TV', 'Não foi possível abrir a página. Por favor tente novamente.')
		return informacoes

	return informacoes

def login2():
	resultado = False
	try:
		post = {'username': __ADDON__.getSetting('email'), 'password': __ADDON__.getSetting('password'),'grant_type': 'password', 'client_id': 'kodi', 'client_secret':'pyRmmKK3cbjouoDMLXNtt2eGkyTTAG' }
		
		resultado = abrir_url(__SITEFILMES__+'login', post=json.dumps(post), header=headers)
		
		if resultado == 'DNS':
			__ALERTA__('Live!t TV', 'Tem de alterar os DNS para poder usufruir do addon.')
			return False
		resultado = json.loads(resultado)
		#colocar o loggedin
		token = resultado['access_token']
		refresh = resultado['refresh_token']
		headersN = headers
		headersN['Authorization'] = 'Bearer %s' % token
		
		resultado = abrir_url(__SITEFILMES__+'me', header=headersN)
		resultado = json.loads(resultado)
		try:
			username = resultado['username'].decode('utf-8')
		except:
			username = resultado['username'].encode('utf-8')
		
		#__ALERTA__('Live!t TV', 'Email: '+resultado['email'])
		#__ALERTA__('Live!t TV', 'User: '+username)
		
		if resultado['email'] == __ADDON__.getSetting('email'):
			__ADDON__.setSetting('tokenMrpiracy', token)
			__ADDON__.setSetting('refreshMrpiracy', refresh)
			__ADDON__.setSetting('loggedin', username)
			return True
	except:
		__ALERTA__('Live!t TV', 'Não foi possível abrir a página. Por favor tente novamente.')
		return False

def minhaContabuild():
	if (not __ADDON__.getSetting('login_name') or not __ADDON__.getSetting('login_password')):
		__ALERTA__('Live!t TV', 'Precisa de definir o seu Utilizador e Senha')
		abrirDefinincoesMesmo()
	else:
		check_login = login()
		if check_login['datafim']['data'] == '':
			abrirDefinincoesMesmo()
		else:
			data_user = check_login['datafim']['data']
			addDir(data_user, 'url', None, None, 'Lista', __SITEAddon__+"Imagens/estadomembro.png",'','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))

def loginPesquisa():
	if (not __ADDON__.getSetting('login_name') or not __ADDON__.getSetting('login_password')):
		__ALERTA__('Live!t TV', 'Precisa de definir o seu Utilizador e Senha')
		abrirDefinincoesMesmo()
	else:
		check_login = login()
		if check_login['datafim']['data'] == '':
			abrirDefinincoesMesmo()
		else:
			_tipouser = check_login['user']['tipo']
			_servuser = check_login['user']['servidor']
			_nomeuser = check_login['user']['nome']
			pesquisa('',_servuser)

def buildLiveit(tipologia):
	if (not __ADDON__.getSetting('login_name') or not __ADDON__.getSetting('login_password')):
		__ALERTA__('Live!t TV', 'Precisa de definir o seu Utilizador e Senha')
		abrirDefinincoesMesmo()
	else:
		if(tipologia == 'FilmesLive') or (tipologia == 'SeriesLive') or (tipologia == 'AnimesLive'):
			check_login = login2()
			if check_login == True:
				if(tipologia == 'FilmesLive'):
					menuFilmes(os.path.join(__ART_FOLDER__, __SKIN__, 'filmes.png'),__SITEAddon__+'Imagens/filme1.png')
				elif(tipologia == 'SeriesLive'):
					menuSeries(os.path.join(__ART_FOLDER__, __SKIN__, 'series.png'),__SITEAddon__+'Imagens/series1.png')
				elif(tipologia == 'AnimesLive'):
					menuAnimes(os.path.join(__ART_FOLDER__, __SKIN__, 'animes.png'),__SITEAddon__+'Imagens/animes1.png')
		else:
			check_login = login()
			if check_login['user']['nome'] != '':
				if check_login['sucesso']['resultado'] == 'yes':
					Menu_inicial(check_login,True,tipologia)
				elif check_login['sucesso']['resultado'] == 'utilizador':
					__ALERTA__('Live!t TV', 'Utilizador incorreto.')
				elif check_login['sucesso']['resultado'] == 'senha':
					__ALERTA__('Live!t TV', 'Senha incorreta.')
				elif check_login['sucesso']['resultado'] == 'ativo':
					__ALERTA__('Live!t TV', 'O estado do seu Utilizador encontra-se Inactivo. Para saber mais informações entre em contacto pelo email liveitkodi@gmail.com')
				else:
					__ALERTA__('Live!t TV', 'Não foi possível abrir a página. Por favor tente novamente.')
			else:
				__ALERTA__('Live!t TV', 'Não foi possível abrir a página. Por favor tente novamente.')

################################
###       Clear Cache        ###
################################

def CLEARCACHE():
    xbmc_cache_path = os.path.join(xbmc.translatePath('special://home'), 'cache')
    if os.path.exists(xbmc_cache_path)==True:    
        for root, dirs, files in os.walk(xbmc_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Apagar Cache no XBMC.", str(file_count) + " ficheiros encontrados.", "Quer apagar todos os ficheiros em cache?"):
                
                    for f in files:
                        try:
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
                        
            else:
                pass
    if xbmc.getCondVisibility('system.platform.ATV2'):
        atv2_cache_a = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')
        
        for root, dirs, files in os.walk(atv2_cache_a):
            file_count = 0
            file_count += len(files)
        
            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Apagar ficheiros ATV2.", str(file_count) + " ficheiros encontrados em 'Outros'", "Quer apagar todos os ficheiros em cache?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
        atv2_cache_b = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')
        
        for root, dirs, files in os.walk(atv2_cache_b):
            file_count = 0
            file_count += len(files)
        
            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Apagar ficheiros ATV2.", str(file_count) + " ficheiros encontrados em 'Local'", "Quer apagar todos os ficheiros em cache?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
              # Set path to Cydia Archives cache files
                             

    # Set path to What th Furk cache files
    wtf_cache_path = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.whatthefurk/cache'), '')
    if os.path.exists(wtf_cache_path)==True:    
        for root, dirs, files in os.walk(wtf_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Apagar a cache WTF.", str(file_count) + " ficheiros encontrados.", "Quer apagar todos os ficheiros em cache?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
                
                # Set path to 4oD cache files
    channel4_cache_path= os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.4od/cache'), '')
    if os.path.exists(channel4_cache_path)==True:    
        for root, dirs, files in os.walk(channel4_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Apagar ficheiros 4oD em cache.", str(file_count) + " ficheiros encontrados.", "Quer apagar todos os ficheiros em cache?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
                
                # Set path to BBC iPlayer cache files
    iplayer_cache_path= os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.iplayer/iplayer_http_cache'), '')
    if os.path.exists(iplayer_cache_path)==True:    
        for root, dirs, files in os.walk(iplayer_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Apagar ficheiros BBC iPlayer em cache.", str(file_count) + " ficheiros encontrados.", "Quer apagar todos os ficheiros em cache?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
                
                
                # Set path to Simple Downloader cache files
    downloader_cache_path = os.path.join(xbmc.translatePath('special://profile/addon_data/script.module.simple.downloader'), '')
    if os.path.exists(downloader_cache_path)==True:    
        for root, dirs, files in os.walk(downloader_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Apagar ficheiros Simple Downloader em cache.", str(file_count) + " ficheiros encontrados.", "Quer apagar todos os ficheiros em cache?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
    
    itv_cache_path = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.itv/Images'), '')
    if os.path.exists(itv_cache_path)==True:    
        for root, dirs, files in os.walk(itv_cache_path):
            file_count = 0
            file_count += len(files)
			
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Apagar items em cache", str(file_count) + " ficheiros encontrados.", "Quer apagar todos os ficheiros em cache?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
    dialog = xbmcgui.Dialog()
    dialog.ok(AddonTitle, "       Cache apagada com sucesso!")


################################
###     Purge Packages       ###
################################

def PURGEPACKAGES():
    packages_cache_path = xbmc.translatePath(os.path.join('special://home/addons/packages', ''))
    try:    
        for root, dirs, files in os.walk(packages_cache_path):
            file_count = 0
            file_count += len(files)
            
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Excluir informação em Cache.", str(file_count) + " ficheiros encontrados.", "Quer apagar todos os ficheiros?"):
                            
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                    dialog = xbmcgui.Dialog()
                    dialog.ok(AddonTitle, "       Kodi limpo com sucesso.")
                else:
                        pass
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok(AddonTitle, "       Não foram encontrados ficheiros a apagar.")
    except: 
        dialog = xbmcgui.Dialog()
        dialog.ok(AddonTitle, "Erro ao tentar apagar ficheiros em cache.")

###############################################################################################################
#                                                   Menus                                                     #
###############################################################################################################

def Menu_inicial(men,build,tipo):
	_tipouser = men['user']['tipo']
	_servuser = men['user']['servidor']
	_nomeuser = men['user']['nome']
	_listauser = men['user']['lista']
	_datauser = men['datafim']['data']
	
	_senhaadultos = __ADDON__.getSetting("login_adultos")
	_fanart = ''
	
	tiposelect = ''
	opcaoselec = __ADDON__.getSetting("lista_m3u")
	if opcaoselec == '0': tiposelect = 'm3u8'
	elif opcaoselec == '1': tiposelect = 'ts'
	elif opcaoselec == '2': tiposelect = 'rtmp'
	
	passanovo = True
	if _tipouser == 'Teste' and _servuser == 'Teste':
		passanovo = False
	
	if build == True and passanovo == False:
		__ALERTA__('Live!t TV', 'É um utilizador Free logo não tem acesso á nossa build a funcionar.')
	elif(build == True):
		tipocan = ''
		urlbuild = ''
		nomebuild = ''
		senhaadu = men['user']['senhaadulto']
		if tipo == 'Desporto' or tipo == 'Crianca' or tipo == 'Canal' or tipo == 'Documentario' or tipo == 'Musica' or tipo == 'Filme' or tipo == 'Noticia' or tipo == 'DE' or tipo == 'FR' or tipo == 'UK' or tipo == 'BR' or tipo == 'ES' or tipo == 'IT' or tipo == 'USA':
			thread.start_new_thread( obter_ficheiro_epg, () )
			if _servuser == 'Servidor1':
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/desportoservidor1.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/canaisaddonservidor1.txt"
			elif(_servuser == 'Servidor2'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/desportoservidor2.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/canaisaddonservidor2.txt"
			elif(_servuser == 'Servidor3'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/desportoservidor3.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/canaisaddonservidor3.txt"
			elif(_servuser == 'Servidor4'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/desportoservidor4.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/canaisaddonservidor4.txt"
			elif(_servuser == 'Servidor5'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/desportoservidor5.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/canaisaddonservidor5.txt"
			elif(_servuser == 'Servidor6'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/desportoservidor6.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/canaisaddonservidor6.txt"
			elif(_servuser == 'Servidor7'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/desportoservidor7.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/canaisaddonservidor7.txt"
		
		if tipo == 'Desporto':
			tipocan = 'Normal'
			nomebuild = 'Desporto PT'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'Crianca'):
			tipocan = 'Normal'
			nomebuild = 'Desenhos Animados PT'
			_fanart = __SITEAddon__+"Imagens/criancas.png"
		elif(tipo == 'Canal'):
			tipocan = 'Normal'
			nomebuild = 'Canais PT'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'Documentario'):
			tipocan = 'Normal'
			nomebuild = 'Documentários PT'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'Musica'):
			tipocan = 'Normal'
			nomebuild = 'Música PT'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'Filme'):
			tipocan = 'Normal'
			nomebuild = 'Canais Filmes PT'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'Noticia'):
			tipocan = 'Normal'
			nomebuild = 'Notícias PT'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'DE'):
			tipocan = 'Normal'
			nomebuild = 'Alemanha'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'FR'):
			tipocan = 'Normal'
			nomebuild = 'França'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'UK'):
			tipocan = 'Normal'
			nomebuild = 'UK'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'BR'):
			tipocan = 'Normal'
			nomebuild = 'Brasil'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'ES'):
			tipocan = 'Normal'
			nomebuild = 'Espanha'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'IT'):
			tipocan = 'Normal'
			nomebuild = 'Itália'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'USA'):
			tipocan = 'Normal'
			nomebuild = 'USA'
			_fanart = __SITEAddon__+"Imagens/tv1.png"
		elif(tipo == 'Radio'):
			tipocan = 'Normal'
			nomebuild = 'Radios PT'
			_fanart = __SITEAddon__+"Imagens/radio.png"
			if _servuser == 'Servidor1':
				urlbuild = __SITEAddon__+"Ficheiros/radiosaddonservidor1.txt"	
			elif(_servuser == 'Servidor2'):
				urlbuild = __SITEAddon__+"Ficheiros/radiosaddonservidor2.txt"
			elif(_servuser == 'Servidor3'):
				urlbuild = __SITEAddon__+"Ficheiros/radiosaddonservidor3.txt"
			elif(_servuser == 'Servidor4'):
				urlbuild = __SITEAddon__+"Ficheiros/radiosaddonservidor4.txt"
			elif(_servuser == 'Servidor5'):
				urlbuild = __SITEAddon__+"Ficheiros/radiosaddonservidor5.txt"
			elif(_servuser == 'Servidor6'):
				urlbuild = __SITEAddon__+"Ficheiros/radiosaddonservidor6.txt"
			elif(_servuser == 'Servidor7'):
				urlbuild = __SITEAddon__+"Ficheiros/radiosaddonservidor7.txt"
		elif(tipo == 'Adulto'):
			tipocan = 'Adulto'
			nomebuild = 'Adultos'
			_fanart = __SITEAddon__+"Imagens/adultos1.png"
			if _servuser == 'Servidor1':
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor1desp.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor1.txt"
			elif(_servuser == 'Servidor2'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor2desp.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor2.txt"
			elif(_servuser == 'Servidor3'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor3desp.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor3.txt"
			elif(_servuser == 'Servidor4'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor4desp.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor4.txt"
			elif(_servuser == 'Servidor5'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor5desp.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor5.txt"
			elif(_servuser == 'Servidor6'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor6desp.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor6.txt"
			elif(_servuser == 'Servidor7'):
				if _tipouser == 'Desporto':
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor7desp.txt"
				else:
					urlbuild = __SITEAddon__+"Ficheiros/adultosaddonservidor7.txt"
		elif(tipo == 'Novidades'):
			tipocan = 'novidades'
			nomebuild = 'Novidades'
			_fanart = __SITEAddon__+"Imagens/novidadestv.png"
			urlbuild = __SITEAddon__+"Ficheiros/novidades.txt"
		elif(tipo == 'Patrocinadores'):
			tipocan = 'patrocinadores'
			nomebuild = 'Patrocinadores'
			_fanart = __SITEAddon__+"Imagens/participa.jpg"
			urlbuild = __SITEAddon__+"Ficheiros/patrocinadores.txt"
		
		if(tipo == 'Novidades') or (tipo == 'Patrocinadores'):
			listar_grupos('',urlbuild,'Lista',tipocan,_tipouser,_servuser,_fanart)
		else:
			if _servuser == 'Servidor3':
				urlbuild = _listauser+'get.php?username='+__ADDON__.getSetting("login_name")+'&password='+__ADDON__.getSetting("login_password")+'&type=m3u_plus&output=hls'
			else:
				urlbuild = _listauser+'get.php?username='+__ADDON__.getSetting("login_name")+'&password='+__ADDON__.getSetting("login_password")+'&type=m3u_plus&output='+tiposelect
			
			abrim3u(urlbuild,_datauser)
			xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=True)
		#	if(__ADDON__.getSetting("login_adultos") == ''):
		#		__ALERTA__('Live!t TV', 'Preencha o campo senha para adultos. No subMenu Credênciais que está no menu Utilizador.')
		#	elif(__ADDON__.getSetting("login_adultos") != senhaadu):
		#		__ALERTA__('Live!t TV', 'Senha para adultos incorrecta. Verifique e tente de novo.')
		#	else:
		#		if _tipouser == 'Teste' and _servuser == 'Teste':
		#			__ALERTA__('Live!t TV', 'É um utilizador Teste logo não tem acesso a esta Secção.')
		#		else:
		#			addDir('Refresh', tipo, 8000, os.path.join(__ART_FOLDER__, __SKIN__, 'retroceder.png'), 0)
		#			listar_canais_url(nomebuild,urlbuild,'Miniatura',tipocan,_tipouser,'',_fanart,tipo,True)
		#			xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=True)
		#else:
		#	if (_tipouser == 'Desporto' and tipo == 'Radio'):
		#		__ALERTA__('Live!t TV', 'Como tem o pack Desporto não tem associado as Rádios. Logo não tem qualquer rádio a ouvir. Se entender na próxima renovação peça o pack Total.')
		#	else:
		#		if(urlbuild == ''):
		#			__ALERTA__('Live!t TV', 'Defina as suas Credênciais.')
		#			abrirDefinincoesMesmo()
		#		else:
		#			if(tipo == 'Novidades' or tipo == 'Patrocinadores'):
		#				listar_grupos('',urlbuild,'Lista',tipocan,_tipouser,_servuser,_fanart)
		#			else:
		#				addDir('Refresh', tipo, 8000, os.path.join(__ART_FOLDER__, __SKIN__, 'retroceder.png'), 0)
		#				listar_canais_url(nomebuild,urlbuild,'Miniatura',tipocan,_tipouser,'',_fanart,tipo)
		#				xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=True)
	else:
		for menu in men['menus']:
			nome = menu['nome']
			logo = menu['logo']
			link = menu['link']
			tipo = menu['tipo']
			senha = menu['senha']
			fanart = menu['fanart']
			#if _tipouser == 'Desporto':
			#	if nome == 'TVs - Desporto':
			#		addDir(nome,link,None,1,'Miniatura',logo,tipo,_tipouser,_servuser,'',fanart)
			#	elif(nome == 'Adultos - Desporto'):
			#		addDir(nome,link,senha,3,'Miniatura',logo,tipo,_tipouser,_servuser,'',fanart)
			#	elif(tipo == 'estado'):
			#		addDir(nome,link,None,10,'Lista',logo,tipo,_tipouser,_servuser,'',fanart)
			#else:
			if nome != 'TVs - Desporto' and nome != 'Adultos - Desporto':
				if tipo == 'Adulto' :
					addDir(nome,link,senha,3,'Miniatura',logo,tipo,_tipouser,_servuser,'',fanart)
				elif tipo == 'patrocinadores' or tipo == 'novidades':
					addDir(nome,link,None,1,'Lista',logo,tipo,_tipouser,_servuser,'',fanart)
				elif(tipo == 'Anime'):
					addDir(nome,link,None,24,'Miniatura',logo,tipo,_tipouser,_servuser,'',fanart)
				elif(tipo == 'Filme'):
					addDir(nome,link,None,21,'Miniatura',logo,tipo,_tipouser,_servuser,'',fanart)
				elif(tipo == 'Serie'):
					addDir(nome,link,None,20,'Miniatura',logo,tipo,_tipouser,_servuser,'',fanart)
				elif(tipo == 'estado'):
					addDir(nome,link,None,10,'Lista',logo,tipo,_tipouser,_servuser,'',fanart)
				elif(tipo == 'pesquisa'):
					if _tipouser != 'Teste':
						addDir(nome,link,None,120,'Lista',logo,tipo,_tipouser,_servuser,'',fanart)
				else:
					if _tipouser == 'Administrador' or _tipouser == 'Patrocinador' or _tipouser == 'PatrocinadorPagante':
						if nome == 'TVs':
							if _servuser == 'Servidor3':
								urllis = _listauser+'get.php?username='+__ADDON__.getSetting("login_name")+'&password='+__ADDON__.getSetting("login_password")+'&type=m3u_plus&output=mpgets'
							else:
								urllis = _listauser+'get.php?username='+__ADDON__.getSetting("login_name")+'&password='+__ADDON__.getSetting("login_password")+'&type=m3u_plus&output=ts'
							
							addDir(nome,urllis,None,3333,'Miniatura',logo,tipo,_tipouser,_servuser,_datauser,fanart)
							addDir('TVs-Free',link,None,1,'Miniatura',logo,tipo,_tipouser,_servuser,'',fanart)
						else:
							addDir(nome,link,None,1,'Miniatura',logo,tipo,_tipouser,_servuser,nome,fanart)
					else:
						if nome == 'TVs' and _tipouser != 'Teste':
							if _servuser == 'Servidor3':
								urllis = _listauser+'get.php?username='+__ADDON__.getSetting("login_name")+'&password='+__ADDON__.getSetting("login_password")+'&type=m3u_plus&output=hls'
							else:
								urllis = _listauser+'get.php?username='+__ADDON__.getSetting("login_name")+'&password='+__ADDON__.getSetting("login_password")+'&type=m3u_plus&output='+tiposelect
							
							addDir(nome,urllis,None,3333,'Miniatura',logo,tipo,_tipouser,_servuser,_datauser,fanart)
						else:
							if tipo != 'Adulto' or nome != 'Radios':
								if _servuser == 'Teste':
									addDir(nome,link,None,1,'Miniatura',logo,tipo,_tipouser,_servuser,nome,fanart)
								else:
									if _servuser == 'Servidor3':
										urllis = _listauser+'get.php?username='+__ADDON__.getSetting("login_name")+'&password='+__ADDON__.getSetting("login_password")+'&type=m3u_plus&output=hls'
									else:
										urllis = _listauser+'get.php?username='+__ADDON__.getSetting("login_name")+'&password='+__ADDON__.getSetting("login_password")+'&type=m3u_plus&output='+tiposelect
									
									addDir(nome,urllis,None,3333,'Miniatura',logo,tipo,_tipouser,_servuser,_datauser,fanart)
							else:
								if _servuser == 'Teste':
									addDir(nome,link,None,1,'Miniatura',logo,tipo,_tipouser,_servuser,nome,fanart)	
		
		#xbmc.executebuiltin('Notification(%s, %s, %i, %s)'%(_nomeuser, Versão do addon: '+_VERSAO_, 8000, _ICON_))
		thread.start_new_thread( obter_ficheiro_epg, () )
		xbmc.executebuiltin('Notification(%s, %s, %i, %s)'%('Live!t-TV','Secção Iniciada: '+_nomeuser, 8000, _ICON_))
		vista_Canais_Lista()
	#check_version()

def abrim3u(url, datauser):	
	tmpList = []
	list = common.m3u2list(url)
	addDir('Atualizar Lista',url,None,3333,'Miniatura',os.path.join(__ART_FOLDER__, __SKIN__, 'retroceder.png'),'','','',datauser,os.path.join(__ART_FOLDER__, __SKIN__, 'retroceder.png'))
	addLinkCanal('Vídeo Instalação Build','plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=PulxztcAHks&t','','','')
	addLinkCanal('Dúvidas: liveitkodi@gmail.com ','','','','')
	addLinkCanal(datauser,'','','','')
	for channel in list:
		name = common.GetEncodeString(channel["display_name"])
		image = channel.get("tvg_logo", "")
		url = common.GetEncodeString(channel["url"])
		id_ip = channel.get("tvg-ID", "")
		
		addLinkCanal(name,url,image,id_ip,'')
	
	vista_Canais_Lista()

def PlayUrl(name, url, iconimage=None):
	listitem = xbmcgui.ListItem(path=url, thumbnailImage=iconimage)
	listitem.setInfo(type="Video", infoLabels={ "Title": name })
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

###############################################################################################################
#                                                   Listar Grupos                                             #
###############################################################################################################
def listar_grupos_adultos(url,senha,estilo,tipo,tipo_user,servidor_user,fanart):
	passa = True
	if tipo_user == 'Teste':
		if servidor_user == "Teste":
			passa = False
			__ALERTA__('Live!t TV', 'Não tem acesso a este menu. Faça a sua doação.')
		else:
			if servidor_user == 'Teste':
				passa = False
				__ALERTA__('Live!t TV', 'Não tem acesso a este menu. Faça a sua doação.')	
	if passa:
		if(__ADDON__.getSetting("login_adultos") == ''):
			__ALERTA__('Live!t TV', 'Preencha o campo senha para adultos.')
		elif(__ADDON__.getSetting("login_adultos") != senha):
			__ALERTA__('Live!t TV', 'Senha para adultos incorrecta. Verifique e tente de novo.')
		else:
			listar_grupos('',url,estilo,tipo,tipo_user,servidor_user,fanart)

def listar_grupos(nome_nov,url,estilo,tipo,tipo_user,servidor_user,fanart):
	if url != 'url':
		page_with_xml = urllib2.urlopen(url).readlines()
		for line in page_with_xml:
			objecto = line.decode('latin-1').encode("utf-8")
			params = objecto.split(',')
			try:
				nomee = params[0]
				imag = params[1]
				urlll = params[2]
				estil = params[3]
				urlllserv1 = params[4]
				urlllserv2 = params[5]
				urlllserv3 = params[6]
				urlllserv4 = params[7]
				urlllserv5 = params[8]
				urlllserv6 = params[9]
				urlllserv7 = params[10]
				paramss = estil.split('\n')
				if tipo_user == 'Administrador' or tipo_user == 'Pagante' or tipo_user == 'PatrocinadorPagante' or tipo_user == 'Desporto':
					if nome_nov == 'TVs-Free':
						addDir(nomee,urlll,None,2,'TesteServer',imag,tipo,tipo_user,servidor_user,'',fanart)
					elif servidor_user == 'Servidor1':
						addDir(nomee,urlllserv1,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,nome_nov,fanart)
					elif servidor_user == 'Servidor2':
						addDir(nomee,urlllserv2,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,nome_nov,fanart)
					elif servidor_user == 'Servidor3':
						addDir(nomee,urlllserv3,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,nome_nov,fanart)
					elif servidor_user == 'Servidor4':
						addDir(nomee,urlllserv4,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,nome_nov,fanart)
					elif servidor_user == 'Servidor5':
						addDir(nomee,urlllserv5,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,nome_nov,fanart)
					elif servidor_user == 'Servidor6':
						addDir(nomee,urlllserv6,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,nome_nov,fanart)
					else:
						addDir(nomee,urlllserv7,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,nome_nov,fanart)
				elif tipo_user == 'Patrocinador':
					if nome_nov == 'TVs-Free':
						addDir(nomee,urlll,None,2,'TesteServer',imag,tipo,tipo_user,servidor_user,'',fanart)
				else:
					if tipo_user == 'Teste':
						if servidor_user == "Teste":
							addDir(nomee,urlll,None,2,'TesteServer',imag,tipo,tipo_user,servidor_user,'',fanart)
						else:
							if servidor_user != '':
								if servidor_user == 'Servidor1':
									addDir(nomee,urlllserv1,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,'',fanart)
								elif servidor_user == 'Servidor2':
									addDir(nomee,urlllserv2,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,'',fanart)
								elif servidor_user == 'Servidor3':
									addDir(nomee,urlllserv3,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,'',fanart)
								elif servidor_user == 'Servidor4':
									addDir(nomee,urlllserv4,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,'',fanart)
								elif servidor_user == 'Servidor5':
									addDir(nomee,urlllserv5,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,'',fanart)
								elif servidor_user == 'Servidor6':
									addDir(nomee,urlllserv6,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,'',fanart)
								else:
									addDir(nomee,urlllserv7,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,'',fanart)
							else:
								addDir(nomee,urlll,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,'',fanart)
					else:
						addDir(nomee,urlll,None,2,paramss[0],imag,tipo,tipo_user,servidor_user,nome_nov,fanart)
			except:
				pass
	
	if tipo == 'patrocinadores' or tipo == 'novidades' or tipo == 'Praia' or tipo == 'pesquisa' or tipo == 'estado' or tipo == 'ProgramasTV' or nome_nov == 'Eventos Diários':
		estiloSelect = returnestilo(estilo)
		xbmc.executebuiltin(estiloSelect)
	else:
		if tipo == 'Filme' or tipo == 'Serie':
			vista_filmesSeries()
		else:
			vista_Canais()	


###############################################################################################################
#                                                   Listar Canais                                             #
###############################################################################################################
def listar_canais_url(nome,url,estilo,tipo,tipo_user,servidor_user,fanart,tippoo,adultos=False):
	if url != 'nada':
		page_with_xml = urllib2.urlopen(url).readlines()
		passaepg = True
		if tippoo == 'Desporto' or tippoo == 'Crianca' or tippoo == 'Canal' or tippoo == 'Documentario' or tippoo == 'Musica' or tippoo == 'Filme' or tippoo == 'Noticia' or tippoo == 'TVs':
			if(__EPG__ != ''):
				urlqqq = urllib.urlopen(__EPG__)
				codigo = urlqqq.read()
				urlqqq.close
			else:
				passaepg = False
	
		ts = time.time()
		st = int(datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S'))
		if tipo == 'Filme' or tipo == 'Serie':
			refres = '**'
		else:
			refres = ','
		for line in page_with_xml:
			total = len(line)
			objecto = line.decode('latin-1').encode("utf-8")
			params = objecto.split(refres)	
			try:
				nomee = params[0]
				rtmp = params[2].replace(' rtmp','rtmp').replace(' rtsp','rtsp').replace(' http','http').replace('utilizadorliveit',__ADDON__.getSetting("login_name")).replace('senhaliveit',__ADDON__.getSetting("login_password"))
				img = params[1].replace(' rtmp','rtmp').replace(' rtsp','rtsp').replace(' http','http')
				grup = params[3]
				id_it = params[4].rstrip()
				id_p = params[5]
				srt_f = ''
				descri = ''
				_fanart = ''
				
				if grup == nome:
					programa = ''
					if tippoo == 'Desporto' or tippoo == 'Crianca' or tippoo == 'Canal' or tippoo == 'Documentario' or tippoo == 'Musica' or tippoo == 'Filme' or tippoo == 'Noticia' or tippoo == 'TVs':
						if id_it != '':
							if passaepg:
								twrv = ThreadWithReturnValue(target=getProgramacaoDiaria, args=(id_it, st,codigo))
								twrv.start()
								programa = twrv.join()
					
					if programa != '':
						nomewp = nomee + " | "+ programa
					else:
						nomewp = nomee
					
					if	tipo == 'Filme' or tipo == 'Serie':
						srt_f = params[6]
						ano = params[7]
						realizador = 'Director: '+params[8]
						descri = params[9]
						detalhes1 = grup
						argumento = 'Live!t-TV'
						plot = 'Enredo: '+descri
						detalhes2 = ano
						imdb = '4510398'
						votes = '5 estrelas'
						infoLabels = {'title':nomewp, 'plot':plot, 'writer': argumento, 'director':realizador, 'genre':detalhes1, 'year': detalhes2, 'aired':detalhes2, 'IMDBNumber':imdb, 'votes':votes, "credits": nomewp}
					else:
						infoLabels = {"title": nomewp, "genre": tipo, "credits": nomewp}
					
					
					addLink(nomewp,rtmp,img,id_it,srt_f,descri,tipo,tipo_user,id_p,infoLabels,fanart,tippoo,adultos,total)				
			except:
				pass
		
		if tipo == 'patrocinadores' or tipo == 'novidades' or tipo == 'Praia' or tipo == 'pesquisa' or tipo == 'estado' or tipo == 'ProgramasTV' or nome == 'Eventos Diários':
			estiloSelect = returnestilo(estilo)
			xbmc.executebuiltin(estiloSelect)
		else:
			if tipo == 'Filme' or tipo == 'Serie':
				vista_filmesSeries()
			else:
				vista_Canais()
	
	#xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=True)

###############################################################################################################
#                                                   EPG                                                     #
###############################################################################################################
def obter_ficheiro_epg():
	if not xbmcvfs.exists(__FOLDER_EPG__):
		xbmcvfs.mkdirs(__FOLDER_EPG__)

	uncompressed_path = os.path.join(__FOLDER_EPG__, 'epg.xml')
	url = urllib.urlopen(__EPG__)
	codigo = url.read()
	url.close
	
	open(uncompressed_path, 'w').write(codigo)

def getProgramacaoDiaria(idCanal, diahora, codigo):
	source = re.compile('<programme start="(.+?) \+0100" stop="(.+?) \+0100" channel="'+idCanal+'">\s+<title lang="pt">(.+?)<\/title>').findall(codigo)

	programa = ''

	for start, stop, programa1  in source:

		if(int(start) < diahora and int(stop) > diahora):
			programa = programa1
	return programa


def programacao_canal(idCanal):
	url = urllib.urlopen(__EPG__)
	codigo = url.read()
	url.close
	
	ts = time.time()
	st = int(datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d'))

	diahora = int(str(st)+'060000')
	diaamanha = int(str(st+1)+'060000')

	source = re.compile('<programme start="(.+?) \+0100" stop="(.+?) \+0100" channel="'+idCanal+'">\s+<title lang="pt">(.+?)<\/title>').findall(codigo)

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

############################################################################################################
#                                               Addon Filmes e Series                                      #
############################################################################################################
def listamenusseries(nome_nov,url,estilo,tipo,tipo_user,servidor_user,iconimage,fanart):
	check_login = login2()
	if check_login == True:
		menuSeries(os.path.join(__ART_FOLDER__, __SKIN__, 'series.png'),__SITEAddon__+'Imagens/series1.png')

def listamenusfilmes(nome_nov,url,estilo,tipo,tipo_user,servidor_user,iconimage,fanart):
	check_login = login2()
	if check_login == True:
		menuFilmes(os.path.join(__ART_FOLDER__, __SKIN__, 'filmes.png'),__SITEAddon__+'Imagens/filme1.png')
		

def listamenusanimes(nome_nov,url,estilo,tipo,tipo_user,servidor_user,iconimage,fanart):
	check_login = login2()
	if check_login == True:
		menuAnimes(os.path.join(__ART_FOLDER__, __SKIN__, 'animes.png'),__SITEAddon__+'Imagens/animes1.png')

def menuFilmes(iconimage,fanart):
	database = Database.isExists()
	addDir2('Todos os Filmes', __SITEFILMES__+'filmes', 111, 'filmes', iconimage, 1, None, None, fanart)
	addDir2('Filmes em Destaque',  __SITEFILMES__+'filmes/destaque', 111, 'filmes', iconimage, 1, None, None, fanart)
	addDir2('Filmes por Ano', __SITEFILMES__+'filmes/ano', 119, 'listagemAnos', os.path.join(__ART_FOLDER__, __SKIN__, 'ano.png'), 1, None, None, fanart)
	addDir2('Filmes por Genero', __SITEFILMES__+'filmes/categoria', 118, 'listagemGeneros', os.path.join(__ART_FOLDER__, __SKIN__, 'genero.png'), 1, None, None, fanart)

	vista_menu()

def menuSeries(iconimage,fanart):
	database = Database.isExists()
	addDir2('Todas as Series', __SITEFILMES__+'series', 123, 'series', iconimage, 1, None, None, fanart)
	addDir2('Series em Destaque',  __SITEFILMES__+'series/destaque', 123, 'series', iconimage, 1, None, None, fanart)
	addDir2('Series por Ano', __SITEFILMES__+'series/ano', 119, 'listagemAnos', os.path.join(__ART_FOLDER__, __SKIN__, 'ano.png'), 1, None, None, fanart)
	addDir2('Series por Genero', __SITEFILMES__+'series/categoria', 118, 'listagemGeneros', os.path.join(__ART_FOLDER__, __SKIN__, 'genero.png'), 1, None, None, fanart)

	vista_menu()

def menuAnimes(iconimage,fanart):
	database = Database.isExists()
	addDir2('Todos os Animes', __SITEFILMES__+'animes', 123, 'animes', iconimage, 1, None, None, fanart)
	addDir2('Animes em Destaque',  __SITEFILMES__+'animes/destaque', 123, 'animes', iconimage, 1, None, None, fanart)
	addDir2('Animes por Ano', __SITEFILMES__+'animes/ano', 119, 'listagemAnos', os.path.join(__ART_FOLDER__, __SKIN__, 'ano.png'), 1, None, None, fanart)
	addDir2('Animes por Genero', __SITEFILMES__+'animes/categoria', 118, 'listagemGeneros', os.path.join(__ART_FOLDER__, __SKIN__, 'genero.png'), 1, None, None, fanart)

	vista_menu()

def removerAcentos(txt, encoding='utf-8'):
	return normalize('NFKD', txt.decode(encoding)).encode('ASCII','ignore')

def filmes(url, pagina):
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	resultado = abrir_url(url, header=headers)
	if resultado == 'DNS':
		__ALERTA__('Live!t-TV', 'Tem de alterar os DNS para poder usufruir do addon.')
		return False
	resultado = json.loads(resultado)
	for i in resultado['data']:
		categoria = i['categoria1']
		if i['categoria2'] != '':
			categoria += ','+i['categoria2']
		if i['categoria3'] != '':
			categoria += ','+i['categoria3']
		visto = False
		pt = ''
		cor = "white"
		br = ''
		if 'Brasileiro' in categoria:
			br = '[B][COLOR green]B[/COLOR][COLOR yellow]R[/COLOR]: [/B]'
		if 'Portu' in categoria:
			pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
		if 'PT' in i['IMBD']:
			i['IMBD'] = re.compile('(.+?)PT').findall(i['IMBD'])[0]
			pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
		if i['visto'] == 1:
			visto = True

		infoLabels = {'Title': i['nome_ingles'], 'Year': i['ano'], 'Genre': categoria, 'Plot': i['descricao_video'], 'Cast':i['atores'].split(','), 'Trailer': i['trailer'], 'Director': i['diretor'], 'Rating': i['imdbRating'], 'IMDBNumber': i['IMBD'] }
		
		try:
			nome = i['nome_ingles'].decode('utf-8')
		except:
			nome = i['nome_ingles'].encode('utf-8')
		if 'http' not in i['foto']:
			i['foto'] = __SITEFILMES2__+'images/capas/'+i['foto'].split('/')[-1]
		
		nomeee = '[COLOR '+cor+']'+pt+br+removerAcentos(nome)+' ('+i['ano']+')[/COLOR]'
		urlnoo = __SITEFILMES__+'filme/'+str(i['id_video'])
		fotooo = i['foto']
		fanarttt = __SITEFILMES2__+i['background']
		addVideo(nomeee, urlnoo, 113, fotooo,visto, 'filme', 0, 0, infoLabels, fanarttt, trailer=i['trailer'])
		
	current = resultado['meta']['pagination']['current_page']
	total = resultado['meta']['pagination']['total_pages']
	try: proximo = resultado['meta']['pagination']['links']['next']
	except: pass 
	if current < total:
		addDir2('Próxima página ('+str(current)+'/'+str(total)+')', proximo, 111, 'filmes', os.path.join(__ART_FOLDER__, __SKIN__, 'proximo.png'),1)
	vista_filmesSeries()

def series(url):
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	resultado = abrir_url(url, header=headers)
	if resultado == 'DNS':
		__ALERTA__('Live!t-TV', 'Tem de alterar os DNS para poder usufruir do addon.')
		return False
	resultado = json.loads(resultado)
	if 'serie' in url:
		tipo = 'serie'
	elif 'anime' in url:
		tipo = 'anime'
	for i in resultado['data']:
		categoria = i['categoria1']
		if i['categoria2'] != '':
			categoria += ','+i['categoria2']
		if i['categoria3'] != '':
			categoria += ','+i['categoria3']
		br = ''
		pt = ''
		if 'Brasileiro' in categoria:
			br = '[B][COLOR green]B[/COLOR][COLOR yellow]R[/COLOR]: [/B]'
		if 'Portu' in categoria:
			pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
		if 'PT' in i['IMBD']:
			pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
		infoLabels = {'Title': i['nome_ingles'], 'Year': i['ano'], 'Genre': categoria, 'Plot': i['descricao_video'], 'Cast':i['atores'].split(','), 'Trailer': i['trailer'], 'Director': i['diretor'], 'Rating': i['imdbRating'], 'Code': i['IMBD'] }
	
		try:
			nome = i['nome_ingles'].decode('utf-8')
		except:
			nome = i['nome_ingles'].encode('utf-8')
		if 'http' not in i['foto']:
			i['foto'] = __SITEFILMES2__+'images/capas/'+i['foto'].split('/')[-1]
		if i['visto'] == 1:
			visto=True
		else:
			visto=False
		
		nomeee = pt+br+removerAcentos(nome)+' ('+i['ano']+')'
		addDir2(nomeee, __SITEFILMES__+tipo+'/'+str(i['id_video']), 114, 'temporadas', i['foto'], tipo='serie', infoLabels=infoLabels,poster=__SITEFILMES2__+i['background'],visto=visto)
	
	current = resultado['meta']['pagination']['current_page']
	total = resultado['meta']['pagination']['total_pages']
	try: proximo = resultado['meta']['pagination']['links']['next']
	except: pass 
	if current < total:
		addDir2('Proxima pagina ('+str(current)+'/'+str(total)+')', proximo, 123, 'series', os.path.join(__ART_FOLDER__, __SKIN__, 'proximo.png'))
	
	vista_filmesSeries()

def getSeasons(url):
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	resultado = abrir_url(url, header=headers)
	if resultado == 'DNS':
		__ALERTA__('Live!t-TV', 'Tem de alterar os DNS para poder usufruir do addon.')
		return False
	resultado = json.loads(resultado)
	j=1
	while j <= resultado['temporadas']:
		addDir2("[B]Temporada[/B] "+str(j), url+'/temporada/'+str(j), 115, 'episodios', os.path.join(__ART_FOLDER__, __SKIN__,'temporadas', 'temporada'+str(j)+'.png'),poster=__SITEFILMES2__+resultado['background'])
		j+=1
	
	vista_temporadas()

def getEpisodes(url):
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	resultado = abrir_url(url, header=headers)
	if resultado == 'DNS':
		__ALERTA__('Live!t-TV', 'Tem de alterar os DNS para poder usufruir do addon.')
		return False
	resultado = json.loads(resultado)
	if 'serie' in url:
		tipo = 'serie'
	elif 'anime' in url:
		tipo = 'anime'
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	resultadoS = abrir_url(__SITEFILMES__+tipo+'/'+url.split('/')[5], header=headers)
	resultadoS = json.loads(resultadoS)
	for i in resultado['data']:
		if i['URL'] == '' and i['URL2'] == '':
			continue
		pt = ''
		categoria = resultadoS['categoria1']
		if resultadoS['categoria2'] != '':
			categoria += ','+resultadoS['categoria2']
		if resultadoS['categoria3'] != '':
			categoria += ','+resultadoS['categoria3']
		infoLabels = {'Title': i['nome_episodio'], 'Code': i['IMBD'], 'Episode': i['episodio'], 'Season': i['temporada'] }
		try:
			nome = i['nome_episodio'].decode('utf-8')
		except:
			nome = i['nome_episodio'].encode('utf-8')
		br = ''
		final = ''
		semLegenda = ''
		if i['fimtemporada'] == 1:
			final = '[B]Final da Temporada [/B]'
		if i['semlegenda'] == 1:
			semLegenda = '[COLOR red][B]S/ LEGENDA [/B][/COLOR]'
		if 'Brasileiro' in categoria:
			br = '[B][COLOR green]B[/COLOR][COLOR yellow]R[/COLOR]: [/B]'
		if 'Portu' in categoria:
			pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
		if 'PT' in i['IMBD']:
			i['IMBD'] = re.compile('(.+?)PT').findall(i['IMBD'])[0]
			pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
		visto = False
		cor = 'white'
		if i['visto'] == 1:
			visto = True	
		
		if i['imagem'] == 1:
			imagem = __SITEFILMES2__+'images/capas/'+i['IMBD']+'.jpg'
		elif i['imagem'] == 0:
			if 'http' not in resultadoS['foto']:
				imagem = __SITEFILMES2__+'images/capas/'+resultadoS['foto'].split('/')[-1]
			else:
				imagem = resultadoS['foto']
		
		nomeee = pt+br+final+semLegenda+'[COLOR '+cor+'][B]Episodio '+str(i['episodio'])+'[/B][/COLOR] '+removerAcentos(nome)
		addVideo(nomeee, __SITEFILMES__+tipo+'/'+str(i['id_serie'])+'/episodio/'+str(i['id_episodio']), 113, imagem, visto, 'episodio', i['temporada'], i['episodio'], infoLabels, __SITEFILMES2__+i['background'])
	
	vista_episodios()

def getGeneros(url):
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	resultado = abrir_url(__SITEFILMES__+'categorias', header=headers)
	if resultado == 'DNS':
		__ALERTA__('Live!t-TV', 'Tem de alterar os DNS para poder usufruir do addon.')
		return False
	resultado = json.loads(resultado)

	for i in resultado:
		if i['id_categoria'] == 0:
			continue
		if 'filme' not in url and i['tipo'] == 1:
			continue
		addDir2(i['categorias'], url+'/'+str(i['id_categoria']), 122, 'categorias', os.path.join(__ART_FOLDER__, __SKIN__, 'genero.png'))
	
	vista_menu()

def categorias(url):
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	resultado = abrir_url(url, header=headers)
	if resultado == 'DNS':
		__ALERTA__('Live!t-TV', 'Tem de alterar os DNS para poder usufruir do addon.')
		return False
	resultadoa = json.loads(resultado)
	
	for i in resultadoa["data"]:
		if 'filme' in url:
			resultado = abrir_url(__SITEFILMES__+'filme/'+str(i['id_video']), header=headers)
			resultado = json.loads(resultado)
			categoria = resultado['categoria1']
			if resultado['categoria2'] != '':
				categoria += ','+resultado['categoria2']
			if resultado['categoria3'] != '':
				categoria += ','+resultado['categoria3']
			
			try:
				nome = resultado['nome_ingles'].decode('utf-8')
			except:
				nome = resultado['nome_ingles'].encode('utf-8')
			if 'http' not in resultado['foto']:
				resultado['foto'] = __SITEFILMES__+'images/capas/'+resultado['foto'].split('/')[-1]
			pt = ''
			br = ''
			if 'Brasileiro' in categoria:
				br = '[B][COLOR green]B[/COLOR][COLOR yellow]R[/COLOR]: [/B]'
			if 'Portu' in categoria:
				pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
			cor = "white"
			if 'PT' in i['IMBD']:
				i['IMBD'] = re.compile('(.+?)PT').findall(i['IMBD'])[0]
				pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
			visto = False
			
			infoLabels = {'Title': resultado['nome_ingles'], 'Year': resultado['ano'], 'Genre': categoria, 'Plot':resultado['descricao_video'], 'Cast':resultado['atores'].split(','), 'Trailer': resultado['trailer'], 'Director': resultado['diretor'], 'Rating': resultado['imdbRating'], 'IMDBNumber': resultado['IMBD'] }
			nomeee = '[COLOR '+cor+']'+pt+br+removerAcentos(nome)+' ('+i['ano']+')[/COLOR]'
			urlnoo = __SITEFILMES__+'filme/'+str(resultado['id_video'])
			fotooo = resultado['foto']
			fanarttt = __SITEFILMES2__+resultado['background']
			addVideo(nomeee, urlnoo, 113, fotooo,visto, 'player', 0, 0, infoLabels, fanarttt, trailer=resultado['trailer'])
		elif 'serie' in url or 'anime' in url:
			cor = "white"
			if 'serie' in url:
				tipo = 'serie'
			elif 'anime' in url:
				tipo = 'anime'
			resultado = abrir_url(__SITEFILMES__+tipo+'/'+str(i['id_video']), header=headers)
			resultado = json.loads(resultado)
			categoria = resultado['categoria1']
			if resultado['categoria2'] != '':
				categoria += ','+resultado['categoria2']
			if resultado['categoria3'] != '':
				categoria += ','+resultado['categoria3']
			pt = ''
			br = ''
			if 'Brasileiro' in categoria:
				br = '[B][COLOR green]B[/COLOR][COLOR yellow]R[/COLOR]: [/B]'
			if 'Portu' in categoria:
				pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
			if 'PT' in resultado['IMBD']:
				pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
			try:
				nome = resultado['nome_ingles'].decode('utf-8')
			except:
				nome = resultado['nome_ingles'].encode('utf-8')
			if 'http' not in resultado['foto']:
				resultado['foto'] = __SITEFILMES__+'images/capas/'+resultado['foto'].split('/')[-1]
			visto = False
			if resultado['visto'] == 1:
				visto=True
			
			infoLabels = {'Title': resultado['nome_ingles'], 'Year': resultado['ano'], 'Genre': categoria, 'Plot': resultado['descricao_video'], 'Cast':resultado['atores'].split(','), 'Trailer': resultado['trailer'], 'Director': resultado['diretor'], 'Rating': resultado['imdbRating'], 'Code': resultado['IMBD'] }
			
			nomeee = pt+br+removerAcentos(nome)+' ('+i['ano']+')'
			addDir2(nomeee, __SITEFILMES__+tipo+'/'+str(resultado['id_video']), 114, 'temporadas', resultado['foto'], tipo='serie', infoLabels=infoLabels,poster=__SITEFILMES2__+resultado['background'],visto=visto)
	
	current = resultadoa['meta']['pagination']['current_page']
	total = resultadoa['meta']['pagination']['total_pages']
	try: proximo = resultadoa['meta']['pagination']['links']['next']
	except: pass 
	if current < total:
		addDir2('Próxima página ('+str(current)+'/'+str(total)+')', proximo, 121, 'anos', os.path.join(__ART_FOLDER__, __SKIN__, 'proximo.png'),1)
	
	vista_filmesSeries()

def getYears(url):
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	conteudo = abrir_url(__SITEFILMES2__+'filmes.php', header=headers)
	match = re.compile('\?anos=.+?\">\s+<img.+?>\s+(.+?)<\/').findall(conteudo)
	
	for i in match:
		addDir2(i, url+'/'+i, 121, 'anos', os.path.join(__ART_FOLDER__, __SKIN__, 'ano.png'))
		
	vista_menu()

def anos(url):
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	resultado = abrir_url(url, header=headers)
	if resultado == 'DNS':
		__ALERTA__('Live!t-TV', 'Tem de alterar os DNS para poder usufruir do addon.')
		return False
	resultadoa = json.loads(resultado)
	
	for i in resultadoa["data"]:
		if 'filme' in url:
			resultado = abrir_url(__SITEFILMES__+'filme/'+str(i['id_video']), header=headers)
			resultado = json.loads(resultado)
			categoria = resultado['categoria1']
			if resultado['categoria2'] != '':
				categoria += ','+resultado['categoria2']
			if resultado['categoria3'] != '':
				categoria += ','+resultado['categoria3']
			
			visto = False
			pt = ''
			br = ''
			if 'Brasileiro' in categoria:
				br = '[B][COLOR green]B[/COLOR][COLOR yellow]R[/COLOR]: [/B]'
			if 'Portu' in categoria:
				pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
			cor = "white"
			if 'PT' in i['IMBD']:
				i['IMBD'] = re.compile('(.+?)PT').findall(i['IMBD'])[0]
				pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
			if i['visto'] == 1:
				visto = True
			
			try:
				nome = resultado['nome_ingles'].decode('utf-8')
			except:
				nome = resultado['nome_ingles'].encode('utf-8')
			if 'http' not in resultado['foto']:
				resultado['foto'] = __SITEFILMES2__+'images/capas/'+resultado['foto'].split('/')[-1]
	
			infoLabels = {'Title': resultado['nome_ingles'], 'Year': resultado['ano'], 'Genre': categoria, 'Plot':resultado['descricao_video'], 'Cast':resultado['atores'].split(','), 'Trailer': resultado['trailer'], 'Director': resultado['diretor'], 'Rating': resultado['imdbRating'], 'IMDBNumber': resultado['IMBD'] }
			nomeee = '[COLOR '+cor+']'+pt+br+removerAcentos(nome)+' ('+i['ano']+')[/COLOR]'
			urlnoo = __SITEFILMES__+'filme/'+str(resultado['id_video'])
			fotooo = resultado['foto']
			fanarttt = __SITEFILMES2__+resultado['background']
			addVideo(nomeee, urlnoo, 113, fotooo,visto, 'player', 0, 0, infoLabels, fanarttt, trailer=resultado['trailer'])
		elif 'serie' in url or 'anime' in url:
			cor = "white"
			if 'serie' in url:
				tipo = 'serie'
			elif 'anime' in url:
				tipo = 'anime'
			resultado = abrir_url(__SITEFILMES__+tipo+'/'+str(i['id_video']), header=headers)
			resultado = json.loads(resultado)
			categoria = resultado['categoria1']
			if resultado['categoria2'] != '':
				categoria += ','+resultado['categoria2']
			if resultado['categoria3'] != '':
				categoria += ','+resultado['categoria3']
			pt=''
			br = ''
			if 'Brasileiro' in categoria:
				br = '[B][COLOR green]B[/COLOR][COLOR yellow]R[/COLOR]: [/B]'
			if 'Portu' in categoria:
				pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
			if 'PT' in resultado['IMBD']:
				pt = '[B][COLOR green]P[/COLOR][COLOR red]T[/COLOR]: [/B]'
			try:
				nome = resultado['nome_ingles'].decode('utf-8')
			except:
				nome = resultado['nome_ingles'].encode('utf-8')
			if 'http' not in resultado['foto']:
				resultado['foto'] = __SITEFILMES2__+'images/capas/'+resultado['foto'].split('/')[-1]
			if resultado['visto'] == 1:
				visto=True
			else:
				visto=False
			infoLabels = {'Title': resultado['nome_ingles'], 'Year': resultado['ano'], 'Genre': categoria, 'Plot': resultado['descricao_video'], 'Cast':resultado['atores'].split(','), 'Trailer': resultado['trailer'], 'Director': resultado['diretor'], 'Rating': resultado['imdbRating'], 'Code': resultado['IMBD'] }
			
			nomeee = pt+br+removerAcentos(nome)+' ('+i['ano']+')'
			addDir2(nomeee, __SITEFILMES__+tipo+'/'+str(resultado['id_video']), 114, 'temporadas', resultado['foto'], tipo='serie', infoLabels=infoLabels,poster=__SITEFILMES2__+resultado['background'],visto=visto)
	
	current = resultadoa['meta']['pagination']['current_page']
	total = resultadoa['meta']['pagination']['total_pages']
	try: proximo = resultadoa['meta']['pagination']['links']['next']
	except: pass 
	if current < total:
		addDir2('Próxima página ('+str(current)+'/'+str(total)+')', proximo, 121, 'anos', os.path.join(__ART_FOLDER__, __SKIN__, 'proximo.png'),1)
	
	vista_filmesSeries()


def player(name,url,iconimage,temporada,episodio,serieNome):
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	resultado = abrir_url(url, header=headers)
	if resultado == 'DNS':
		__ALERTA__('Live!t-TV', 'Tem de alterar os DNS para poder usufruir do addon.')
		return False
	
	resultado = json.loads(resultado)
	infolabels = dict()

	pastaData = ''
	if 'filme' in url:
		infolabels['Code'] = resultado['IMBD']
		infolabels['Year'] = resultado['ano']
		idVideo = resultado['id_video']
		nome = resultado['nome_ingles']
		temporada = 0
		episodio = 0
	else:
		idVideo = resultado['id_serie']
		nome = resultado['nome_episodio']
		temporada = resultado['temporada']
		episodio = resultado['episodio']

	mensagemprogresso = xbmcgui.DialogProgress()
	mensagemprogresso.create('Live!t-TV', u'Abrir emissão','Por favor aguarde...')
	mensagemprogresso.update(25, "", u'Obter video e legenda', "")

	stream, legenda, ext_g = getStreamLegenda(resultado)

	mensagemprogresso.update(50, "", u'Prepara-te, vai começar!', "")

	playlist = xbmc.PlayList(1)
	playlist.clear()
	listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)

	listitem.setInfo(type="Video", infoLabels=infolabels)
	listitem.setProperty('mimetype', 'video/x-msvideo')
	listitem.setProperty('IsPlayable', 'true')
	
	listitem.setPath(path=stream)
	playlist.add(stream, listitem)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
	mensagemprogresso.update(75, "", u'Boa Sessão!!!', "")

	if stream == False:
		__ALERTA__('Live!t-TV', 'O servidor escolhido não disponível, escolha outro ou tente novamente mais tarde.')
	else:
		#__ALERTA__('Live!t TV', 'Stream: '+stream)
		player_mr = Player.Player(url=url, idFilme=idVideo, pastaData=__PASTA_DADOS__, temporada=temporada, episodio=episodio, nome=name, logo=os.path.join(__ADDON_FOLDER__,'icon.png'))
		
		mensagemprogresso.close()
		player_mr.play(playlist)
		player_mr.setSubtitles(legenda)

		while player_mr.playing:
			xbmc.sleep(5000)
			#player_mr.trackerTempo()

def getStreamLegenda(resultado):
	i = 0
	servidores = []
	titulos = []
	if resultado['URL'] != '':
		i+=1
		servidores.append(resultado['URL'])
		if 'openload' in resultado['URL']:
			nome = "OpenLoad"
		elif 'vidzi' in resultado['URL']:
			nome = 'Vidzi'
		elif 'google' in resultado['URL'] or 'cloud.mail.ru' in resultado['URL']:
			nome = 'MrPiracy'
		elif 'uptostream.com' in resultado['URL']:
			nome = 'UpToStream'
		elif 'rapidvideo.com' in resultado['URL']:
			nome = 'RapidVideo'
		titulos.append('Servidor #%s: %s' % (i, nome))
	if resultado['URL2'] != '':
		i+=1
		servidores.append(resultado['URL2'])
		if 'openload' in resultado['URL2']:
			nome = "OpenLoad"
		elif 'vidzi' in resultado['URL2']:
			nome = 'Vidzi'
		elif 'google' in resultado['URL2'] or 'cloud.mail.ru' in resultado['URL2']:
			nome = 'MrPiracy'
		elif 'uptostream.com' in resultado['URL2']:
			nome = 'UpToStream'
		elif 'rapidvideo.com' in resultado['URL2']:
			nome = 'RapidVideo'
		titulos.append('Servidor #%s: %s' % (i, nome))
	try:
		if resultado['URL3'] != '':
			i+=1
			servidores.append(resultado['URL3'])
			if 'openload' in resultado['URL3']:
				nome = "OpenLoad"
			elif 'vidzi' in resultado['URL3']:
				nome = 'Vidzi'
			elif 'google' in resultado['URL3'] or 'cloud.mail.ru' in resultado['URL3']:
				nome = 'MrPiracy'
			elif 'uptostream.com' in resultado['URL3']:
				nome = 'UpToStream'
			elif 'rapidvideo.com' in resultado['URL3']:
				nome = 'RapidVideo'
			titulos.append('Servidor #%s: %s' % (i, nome))
	except:
		pass
	try:
		if resultado['URL4'] != '':
			i+=1
			servidores.append(resultado['URL4'])
			if 'openload' in resultado['URL4']:
				nome = "OpenLoad"
			elif 'vidzi' in resultado['URL4']:
				nome = 'Vidzi'
			elif 'google' in resultado['URL4'] or 'cloud.mail.ru' in resultado['URL4']:
				nome = 'MrPiracy'
			elif 'uptostream.com' in resultado['URL4']:
				nome = 'UpToStream'
			elif 'rapidvideo.com' in resultado['URL4']:
				nome = 'RapidVideo'
			titulos.append('Servidor #%s: %s' % (i, nome))
	except:
		pass
	legenda = ''
	if '://' in resultado['legenda'] or resultado['legenda'] == '':
		legenda = __SITEAPI__+'subs/%s.srt' % resultado['IMBD']
	elif resultado['legenda'] != '':
		if not '.srt' in resultado['legenda']:
			resultado['legenda'] = resultado['legenda']+'.srt'
		legenda = __SITEAPI__+'subs/%s' % resultado['legenda']
	try:
		if resultado['semlegenda'] == 1:
			legenda = ''
	except:
		pass
	ext_g = 'coiso'
	if len(titulos) > 1:
		servidor = xbmcgui.Dialog().select('Escolha o servidor', titulos)
		if 'vidzi' in servidores[servidor]:
			vidzi = URLResolverMedia.Vidzi(servidores[servidor])
			stream = vidzi.getMediaUrl()
			legenda = vidzi.getSubtitle()
		elif 'uptostream.com' in servidores[servidor]:
			stream = URLResolverMedia.UpToStream(servidores[servidor]).getMediaUrl()
		elif 'server.mrpiracy.win' in servidores[servidor]:
			stream = servidores[servidor]
		elif 'openload' in servidores[servidor]:
			stream = URLResolverMedia.OpenLoad(servidores[servidor]).getMediaUrl()
			legenda = URLResolverMedia.OpenLoad(servidores[servidor]).getSubtitle()
		elif 'drive.google.com/' in servidores[servidor]:
			stream, ext_g = URLResolverMedia.GoogleVideo(servidores[servidor]).getMediaUrl()
		elif 'cloud.mail.ru' in servidores[servidor]:
			stream, ext_g = URLResolverMedia.CloudMailRu(servidores[servidor]).getMediaUrl()
		elif 'rapidvideo.com' in servidores[servidor]:
			rapid = URLResolverMedia.RapidVideo(servidores[servidor])
			stream = rapid.getMediaUrl()
			legenda = rapid.getLegenda()
	else:
		if 'vidzi' in servidores[0]:
			vidzi = URLResolverMedia.Vidzi(servidores[0])
			stream = vidzi.getMediaUrl()
			legenda = vidzi.getSubtitle()
		elif 'uptostream.com' in servidores[0]:
			stream = URLResolverMedia.UpToStream(servidores[0]).getMediaUrl()
		elif 'server.mrpiracy.win' in servidores[0]:
			stream = servidores[servidor]
		elif 'openload' in servidores[0]:
			stream = URLResolverMedia.OpenLoad(servidores[0]).getMediaUrl()
			legenda = URLResolverMedia.OpenLoad(servidores[0]).getSubtitle()
		elif 'drive.google.com/' in servidores[0]:
			stream, ext_g = URLResolverMedia.GoogleVideo(servidores[0]).getMediaUrl()
		elif 'cloud.mail.ru' in servidores[0]:
			stream, ext_g = URLResolverMedia.CloudMailRu(servidores[0]).getMediaUrl()
		elif 'rapidvideo.com' in servidores[servidor]:
			rapid = URLResolverMedia.RapidVideo(servidores[servidor])
			stream = rapid.getMediaUrl()
			legenda = rapid.getLegenda()
	
	return stream, legenda, ext_g


def pesquisa(url,servuss):
	codigo_fonte = ''
	dados = ''
	net = Net()
	net.set_cookies(__COOKIE_FILE__)
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	tabela = ''
	if 'filmes' in url:
		ficheiro = os.path.join(__PASTA_DADOS__,'filmes_pesquisa.liveit')
		tipo = 0
	elif 'series' in url:
		ficheiro = os.path.join(__PASTA_DADOS__,'series_pesquisa.liveit')
		tipo = 1
	elif 'animes' in url:
		ficheiro = os.path.join(__PASTA_DADOS__,'animes_pesquisa.liveit')
		tipo = 2
	
	if 'page' not in url:
		#tipo = xbmcgui.Dialog().select(u'Onde quer pesquisar?', ['Filmes', 'Series', 'Animes', 'Canais', 'Praias', 'Rádios'])
		tipo = xbmcgui.Dialog().select(u'Onde quer pesquisar?', ['Filmes', 'Series', 'Animes'])
		teclado = xbmc.Keyboard('', 'O que quer pesquisar?')
		if tipo == 0:
			url = __SITEFILMES__+'filmes/pesquisa'
			ficheiro = os.path.join(__PASTA_DADOS__,'filmes_pesquisa.liveit')
		elif tipo == 1:
			url = __SITEFILMES__+'series/pesquisa'
			ficheiro = os.path.join(__PASTA_DADOS__,'series_pesquisa.liveit')
		elif tipo == 2:
			url = __SITEFILMES__+'animes/pesquisa'
			ficheiro = os.path.join(__PASTA_DADOS__,'animes_pesquisa.liveit')
		elif tipo == 3 or  tipo == 4 or tipo == 5:
			url = __SITE__+'search.php'
			if tipo == 3:
				tabela = 'canais_kodi'
				ficheiro = os.path.join(__PASTA_DADOS__,'canais.liveit')
			elif tipo == 4:
				tabela = 'praias_kodi'
				ficheiro = os.path.join(__PASTA_DADOS__,'praias.liveit')
			elif tipo == 5:
				tabela = 'radios_kodi'
				ficheiro = os.path.join(__PASTA_DADOS__,'radios.liveit')
			else:
				tabela = 'programas_kodi'
				ficheiro = os.path.join(__PASTA_DADOS__,'programas.liveit')
		
		if xbmcvfs.exists(ficheiro):
			f = open(ficheiro, "r")
			texto = f.read()
			teclado.setDefault(texto)
		teclado.doModal()

		if teclado.isConfirmed():
			strPesquisa = teclado.getText()
			dados = {'pesquisa': strPesquisa}
			try:
				f = open(ficheiro, mode="w")
				f.write(strPesquisa)
				f.close()
			except:
				traceback.print_exc()
				print "Não gravou o conteudo em %s" % ficheiro

			resultado = abrir_url(url,post=json.dumps(dados), header=headers)
	else:
		if xbmcvfs.exists(ficheiro):
			f = open(ficheiro, "r")
			texto = f.read()
		dados = {'pesquisa': texto}
		resultado = abrir_url(url,post=json.dumps(dados), header=headers)
	
	if resultado == 'DNS':
		__ALERTA__('Live!t-TV', 'Tem de alterar os DNS para poder usufruir do addon.')
		return False
	
	if tipo == 3 or  tipo == 4 or tipo == 5:
		if strPesquisa == '':
			__ALERTA__('Live!t-TV', 'Insira algo na pesquisa.')
			addDir2('Alterar Pesquisa', 'url', 7000, '', os.path.join(__ART_FOLDER__, __SKIN__, 'pesquisa.png'), 0)
		else:
			dados = {'searchBox': strPesquisa, 'tabela': tabela}
			codigo_fonte = net.http_POST(url, form_data=dados, headers=__HEADERS__).content.decode('latin-1').encode("utf-8")
			informa = {
					'servidor' : {
						'nome': '',
						'serv': ''
					},
					'servidores': [],
					'canais': []
				}
			sucesso = 'no'
			elems = ET.fromstring(codigo_fonte)
			
			for childee in elems:
				if(childee.tag == 'servidores'):
					servidor = {
						'nome': '',
						'link': ''
					}
					for gg in childee:	
						if(gg.tag == 'Nome'):
							servidor['nome'] = gg.text	
						elif(gg.tag == 'Servidor'):
							servidor['link'] = gg.text		
						informa['servidores'].append(servidor)
				
			for servvvv in informa['servidores']:
				if(servvvv['nome'] == servuss):
					informa['servidor']['nome'] = servvvv['nome']
					informa['servidor']['serv'] = servvvv['link']			
			
			for child in elems:
				if(child.tag == 'sucesso'):
					sucesso = child.text
				elif(child.tag == 'canais'):
					canal = {
						'nome': '',
						'logo': '',
						'link': '',
						'grupo': '',
						'nomeid': '',
						'idnovo': ''
					}
					adiciona = True
					pagante = False
					for g in child:
						adiciona = True
						if(g.tag == 'Nome'):
							canal['nome'] = g.text
						elif(g.tag == 'Imagem'):
							canal['logo'] = g.text
						elif(g.tag == 'Pagante'):
							if(g.text == 'true'):
								pagante = True
						elif(g.tag == 'Url'):
							urlchama = g.text.split(';')
							urlnoo = g.text
							try:
								if(servuss == 'Servidor1'):
									urlnoo = urlchama[0]
								elif(servuss == 'Servidor2'):
									urlnoo = urlchama[1]
								elif(servuss == 'Servidor3'):
									urlnoo = urlchama[2]
								elif(servuss == 'Servidor4'):
									urlnoo = urlchama[3]
								elif(servuss == 'Servidor5'):
									urlnoo = urlchama[4]
								elif(servuss == 'Servidor6'):
									urlnoo = urlchama[5]
								elif(servuss == 'Servidor7'):
									urlnoo = urlchama[6]
								elif(servuss == 'Servidor8'):
									urlnoo = urlchama[7]
								
								if(urlnoo == 'nada'):
									adiciona = False
								else:
									if pagante:
										canal['link'] = informa['servidor']['serv']+'live/utilizadorliveit/senhaliveit/'+urlnoo
									else:
										canal['link'] = urlnoo
							except:
								canal['link'] = g.text
						elif(g.tag == 'Grupo'):
							canal['grupo'] = g.text
						elif(g.tag == 'NomeID'):
							canal['nomeid'] = g.text
						elif(g.tag == 'ID'):
							canal['idnovo'] = g.text
					if adiciona:
						informa['canais'].append(canal)

			if sucesso == 'yes':
				addDir2('Alterar Pesquisa', 'url', 7000, '', os.path.join(__ART_FOLDER__, __SKIN__, 'pesquisa.png'), 0)
				for cann in informa['canais']:
					nomee = cann['nome']
					img = cann['logo']
					rtmp = cann['link'].replace(' rtmp','rtmp').replace(' rtsp','rtsp').replace(' http','http').replace('utilizadorliveit',__ADDON__.getSetting("login_name")).replace('senhaliveit',__ADDON__.getSetting("login_password"))
					grup = cann['grupo']
					id_it = cann['nomeid']
					id_p = cann['idnovo']
					srt_f = ''
					descri = ''
					
					addLink2(nomee,rtmp,'http://liveitkodi.com/Logos/'+img)
				
				vista_Canais()
			
	else:
		resultado = json.loads(resultado)
		if resultado['data'] != '':
			if tipo == 0:
				for i in resultado['data']:
					categoria = i['categoria1']
					if i['categoria2'] != '':
						categoria += ','+i['categoria2']
					if i['categoria3'] != '':
						categoria += ','+i['categoria3']
					infoLabels = {'Title': i['nome_ingles'], 'Year': i['ano'], 'Genre': categoria, 'Plot': i['descricao_video'], 'Cast':i['atores'].split(','), 'Trailer': i['trailer'], 'Director': i['diretor'], 'Rating': i['imdbRating'], 'IMDBNumber': i['IMBD'] }				
					try:
						nome = i['nome_ingles'].decode('utf-8')
					except:
						nome = i['nome_ingles'].encode('utf-8')
					pt = ''
					if 'Portu' in categoria:
						pt = '[B]PT: [/B]'
					cor = "white"
					if 'http' not in i['foto']:
						i['foto'] = __SITEFILMES2__+'images/capas/'+i['foto'].split('/')[-1]
					if 'PT' in i['IMBD']:
						i['IMBD'] = re.compile('(.+?)PT').findall(i['IMBD'])[0]
						pt = '[B]PT: [/B]'
					visto = False
					
					nomeee = pt+removerAcentos(nome)+' ('+i['ano']+')'
					urlnoo = __SITEFILMES__+'filme/'+str(i['id_video'])
					fotooo = i['foto']
					fanarttt = __SITEFILMES2__+i['background']
					addVideo(nomeee, urlnoo, 113, fotooo,visto, 'filme', 0, 0, infoLabels, fanarttt, trailer=i['trailer'])
			elif tipo == 1 or tipo == 2:
				for i in resultado['data']:
					categoria = i['categoria1']
					if i['categoria2'] != '':
						categoria += ','+i['categoria2']
					if i['categoria3'] != '':
						categoria += ','+i['categoria3']
					if 'Portu' in categoria:
						pt = '[B]PT: [/B]'
					infoLabels = {'Title': i['nome_ingles'], 'Year': i['ano'], 'Genre': categoria, 'Plot': i['descricao_video'], 'Cast':i['atores'].split(','), 'Trailer': i['trailer'], 'Director': i['diretor'], 'Rating': i['imdbRating'], 'Code': i['IMBD'] }
					cor = "white"
					pt=''
					if 'PT' in i['IMBD']:
						i['IMBD'] = re.compile('(.+?)PT').findall(i['IMBD'])[0]
						pt = '[B]PT: [/B]'
					try:
						nome = i['nome_ingles'].decode('utf-8')
					except:
						nome = i['nome_ingles'].encode('utf-8')
					if 'http' not in i['foto']:
						i['foto'] =__SITEFILMES2__+'images/capas/'+i['foto'].split('/')[-1]
					if tipo == 1:
						link = 'serie'
					elif tipo == 2:
						link = 'anime'
					visto=False	
					nomeee = pt+removerAcentos(nome)+' ('+i['ano']+')'
					urlnoo = __SITEFILMES__+link+'/'+str(i['id_video'])
					fotooo = i['foto']
					fanarttt = __SITEFILMES2__+i['background']
					addDir2(nomeee, urlnoo, 114, 'temporadas', fotooo, tipo='serie', infoLabels=infoLabels,poster=fanarttt,visto=visto)

			current = resultado['meta']['pagination']['current_page']
			total = resultado['meta']['pagination']['total_pages']
			try: proximo = resultado['meta']['pagination']['links']['next']
			except: pass 
			if current < total:
				addDir2('Proxima pagina ('+str(current)+'/'+str(total)+')', proximo, 120, 'pesquisa', os.path.join(__ART_FOLDER__, __SKIN__, 'proximo.png'))
			
			vista_filmesSeries()


def download(url,name, temporada,episodio,serieNome):
	headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
	links = url.split('/')
	if 'filme' in url:
		id_video = links[-1]
		tipo = 0
	elif 'serie' in url:
		id_video = links[5]
		temporada = links[7]
		episodio = links[-1]
		tipo = 1
	elif 'anime' in url:
		id_video = links[5]
		temporada = links[7]
		episodio = links[-1]
		tipo = 2

	resultado = abrir_url(url, header=headers)
	if resultado == 'DNS':
		__ALERTA__('Live!t-TV', 'Tem de alterar os DNS para poder usufruir do addon.')
		return False
	
	resultado = json.loads(resultado)

	stream, legenda, ext_g = getStreamLegenda(resultado)

	folder = xbmc.translatePath(__ADDON__.getSetting('pastaDownloads'))
	if(folder == 'Escolha a pasta para Download'):
		__ALERTA__('Live!t TV', 'Seleccione uma pasta primeiro no submenu Credênciais ou nas Configurações do Addon.')
	else:
		if tipo > 0:
			if tipo == 1:
				resultadoa = abrir_url(__SITEFILMES__+'serie/'+id_video, header=headers)
			elif tipo == 2:
				resultadoa = abrir_url(__SITEFILMES__+'anime/'+id_video, header=headers)
			resultadoa = json.loads(resultadoa)
			if not xbmcvfs.exists(os.path.join(folder,'series')):
				xbmcvfs.mkdirs(os.path.join(folder,'series'))
			if not xbmcvfs.exists(os.path.join(folder,'series',resultadoa['nome_ingles'])):
				xbmcvfs.mkdirs(os.path.join(folder,'series',resultadoa['nome_ingles']))
			if not xbmcvfs.exists(os.path.join(folder,'series',resultadoa['nome_ingles'],"Temporada "+str(temporada))):
				xbmcvfs.mkdirs(os.path.join(folder,'series',resultadoa['nome_ingles'],"Temporada "+str(temporada)))
			folder = os.path.join(folder, 'series', resultadoa['nome_ingles'], "Temporada", str(temporada))
			name = "e"+str(episodio)+" - "+clean(resultado['nome_episodio'])
		else:
			if not xbmcvfs.exists(os.path.join(folder,'filmes')):
				xbmcvfs.mkdirs(os.path.join(folder,'filmes'))
			folder = os.path.join(folder,'filmes')
			name = resultado['nome_ingles']

		streamAux = clean(stream.split('/')[-1])
		extensaoStream = clean(streamAux.split('.')[-1])

		if '?mim' in extensaoStream:
			extensaoStream = re.compile('(.+?)\?mime=').findall(extensaoStream)[0]

		if ext_g != 'coiso':
			extensaoStream = ext_g

		nomeStream = name+'.'+extensaoStream
		nomelegenda = ''
		Downloader.Downloader().download(os.path.join(folder.decode("utf-8"), nomeStream), stream, name)
		
		if legendasOn:
			legendaAux = clean(legenda.split('/')[-1])
			extensaoLegenda = clean(legendaAux.split('.')[1])
			nomeLegenda = name+'.'+extensaoLegenda
			download_legendas(legenda, os.path.join(folder, nomeLegenda))

def download_legendas(url,path):
    contents = abrir_url(url)
    if contents:
        fh = open(path, 'w')
        fh.write(contents)
        fh.close()
    return

def clean(text):
	command={'&#8220;':'"','&#8221;':'"', '&#8211;':'-','&amp;':'&','&#8217;':"'",'&#8216;':"'"}
	regex = re.compile("|".join(map(re.escape, command.keys())))
	return regex.sub(lambda mo: command[mo.group(0)], text)

def addVideo(name,url,mode,iconimage,visto,tipo,temporada,episodio,infoLabels,poster,trailer=False,serieNome=False):
	menu = []
	
	if infoLabels: infoLabelsAux = infoLabels
	else: infoLabelsAux = {'Title': name}

	if poster: posterAux = poster
	else: posterAux = iconimage
	
	try:
		name = name.encode('utf-8')
	except:
		name = name
	
	try:
		serieNome = serieNome.encode('utf-8')
	except:
		serieNome = serieNome
	else:
		pass

	fanart = __FANART__
	
	if tipo == 'filme':
		xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
		if __ADDON__.getSetting('trailer-filmes') == 'true':
			try:
				idYoutube = trailer.split('?v=')[-1].split('/')[-1].split('?')[0].split('&')[0]
				linkTrailer = 'plugin://plugin.video.youtube/play/?video_id='+idYoutube
				#idYoutube=trailer.split('=')
				#__ALERTA__('Live!t TV', 'ID: '+idYoutube[1])
				#linkTrailer = 'plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid='+idYoutube[1]
				#linkTrailer = trailer
			except:
				linkTrailer = ''
		else:
			linkTrailer = ''
	elif tipo == 'serie':
		xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
		idIMDb = re.compile('imdb=(.+?)&').findall(url)[0]
		linkTrailer = ""
	elif tipo == 'episodio':
		xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
		linkTrailer = ""
	else:
		xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
		linkTrailer = ""
	
	overlay = 6
	playcount = 0

	infoLabelsAux["overlay"] = overlay
	infoLabelsAux["playcount"] = playcount

	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image',poster)
	liz.setInfo( type="Video", infoLabels=infoLabelsAux)
	
	if not serieNome:
		serieNome = ''

	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&temporada="+str(temporada)+"&episodio="+str(episodio)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&serieNome="+urllib.quote_plus(serieNome)
	ok=True
	
	if linkTrailer != "":
		menu.append(('Ver Trailer', 'XBMC.PlayMedia(%s)' % (linkTrailer)))
		#menu.append(('Ver Trailer', 'XBMC.RunPlugin(%s?mode=105&name=%s&url=%s&iconimage=%s)'%(sys.argv[0],urllib.quote_plus(name), linkTrailer, urllib.quote_plus(iconimage))))
	
	menu.append(('Download', 'XBMC.RunPlugin(%s?mode=117&name=%s&url=%s&iconimage=%s&serieNome=%s&temporada=%s&episodio=%s)'%(sys.argv[0],urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage), urllib.quote_plus(serieNome), str(temporada), str(episodio))))
	liz.addContextMenuItems(menu, replaceItems=True)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok

###################################################################################
#                               FUNCOES JA FEITAS                                 #
###################################################################################
def abrirNada():
	xbmc.executebuiltin("Container.SetViewMode(51)")
	
def addDir(name,url,senha,mode,estilo,iconimage,tipo,tipo_user,servidor_user,data_user,fanart,pasta=True,total=1):
	if(tipo == 'pesquisa'):
		u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&tipologia="+str(tipo)+"&tipo_user="+str(tipo_user)+"&servidor_user="+str(servidor_user)
	else:

		u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&senha="+str(senha)+"&estilo="+urllib.quote_plus(estilo)+"&tipologia="+str(tipo)+"&tipo_user="+str(tipo_user)+"&servidor_user="+str(servidor_user)+"&data_user="+str(data_user)+"&fanart="+str(fanart)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', fanart)
	liz.setArt({'fanart': fanart})
	#liz.setArt({'fanart': os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png')})
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)
	return ok
	
def addFolder(name,url,mode,iconimage,folder):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)
	return ok

def addLinkCanal(name,url,iconimage,idcanal,id_p):
	infoLabelssss = {"title": name, "genre": 'All'}
	ok=True
	cm=[]
	
	cm.append(('Ver programação', 'XBMC.RunPlugin(%s?mode=31&name=%s&url=%s&iconimage=%s&idCanal=%s&idffCanal=%s)'%(sys.argv[0],urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage), idCanal, id_p)))
	
	liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	#liz.setProperty('fanart_image', fanart)
	#liz.setArt({'fanart': fanart})
	liz.setInfo( type="Video", infoLabels=infoLabelssss)
	liz.addContextMenuItems(cm, replaceItems=False)
	liz.setProperty('IsPlayable', 'true')
	u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=3334&name=" + urllib.quote_plus(name) + "&iconimage=" + urllib.quote_plus(iconimage)+"&data_user="+str(idcanal)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok
	
def addLink(name,url,iconimage,idCanal,srtfilm,descricao,tipo,tipo_user,id_p,infoLabelssss,fanart,tipppp,adultos=False,total=1):
	ok=True
	cm=[]
	
	if tipo != 'Praia' and tipo != 'ProgramasTV' and tipo != 'Filme' and tipo != 'Serie':
		cm.append(('Ver programação', 'XBMC.RunPlugin(%s?mode=31&name=%s&url=%s&iconimage=%s&idCanal=%s&idffCanal=%s)'%(sys.argv[0],urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage), idCanal, id_p)))
	
	liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', fanart)
	liz.setArt({'fanart': fanart})
	liz.setInfo( type="Video", infoLabels=infoLabelssss)
	liz.addContextMenuItems(cm, replaceItems=False)
	
	canaisproprios = False
	
	urlverifica = url.split('.ts')
	totalver = len(urlverifica)
	if totalver != 1:
		canaisproprios = True;
		
	if 'acestream://' in url:
		canaisproprios = True;
	
	if canaisproprios == False:
		urlverifica2 = url.split('.m3u8')
		totalver2 = len(urlverifica2)
		if totalver2 != 1:
			canaisproprios = True;
	
	if tipo == 'ProgramasTV' or tipo == 'Praia' or tipo == 'Filme' or tipo == 'Serie':
		u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=105&name=" + urllib.quote_plus(name) + "&iconimage=" + urllib.quote_plus(iconimage)
	else:
		if canaisproprios == False:
			u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=105&name=" + urllib.quote_plus(name) + "&iconimage=" + urllib.quote_plus(iconimage)
		else:
			if 'acestream://' in url:
				reizinho = ''
			else:
				liz.setProperty('IsPlayable', 'true')
			
			u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=106&name=" + urllib.quote_plus(name) + "&iconimage=" + urllib.quote_plus(iconimage)
	
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok

def abrir_url(url, post=None, header=None, code=False, erro=False):
	if header == None:
		header = headers
	if post:
		req = urllib2.Request(url, data=post, headers=header)
	else:
		req = urllib2.Request(url, headers=header)
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError as response:
		if erro == True:
			return str(response.code), "asd"
	link=response.read()
	
	if 'myapimp.tk' in url:
		coiso = json.loads(link)
		if 'error' in coiso:
			if coiso['error'] == 'access_denied':
				headers['Authorization'] = 'Bearer %s' % __ADDON__.getSetting('tokenMrpiracy')
				dados = {'refresh_token': __ADDON__.getSetting('refreshMrpiracy'),'grant_type': 'refresh_token', 'client_id': 'kodi', 'client_secret':'pyRmmKK3cbjouoDMLXNtt2eGkyTTAG' }
				resultado = abrir_url('http://myapimp.tk/api/token/refresh',post=json.dumps(dados), headers=headers)
				resultado = json.loads(resultado)
				__ADDON__.setSetting('tokenMrpiracy', resultado['access_token'])
				__ADDON__.setSetting('refreshMrpiracy', resultado['refresh_token'])
				if post:
					return abrir_url(url, post=post, headers=header)
				else:
					return abrir_url(url, headers=header)
	
	if 'judicial' in link:
		return 'DNS'
	if code:
		return str(response.code), link
	
	response.close()
	return link

def addLink2(name,url,iconimage):
	ok=True
	liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	liz.setArt({'fanart': iconimage})
	liz.setInfo( type="Video", infoLabels={ "Title": name })
	liz.setProperty('IsPlayable', 'true')
	u = sys.argv[0] + "?url=" + url + "&mode=106&name=" + name + "&iconimage=" + iconimage
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok

def play_mult_canal(arg, icon, nome):
	urlchama = arg.split(';;;')
	total2 = len(urlchama)
	urlcorrecto = ''
	if total2 == 1:
		urlcorrecto = arg.replace(' rtmp','rtmp').replace(' rtsp','rtsp').replace(' http','http').replace('utilizadorliveit',__ADDON__.getSetting("login_name")).replace('senhaliveit',__ADDON__.getSetting("login_password"))
	else:
		net = Net()
		net.set_cookies(__COOKIE_FILE__)
		dados = {'url': urlchama[1], 'canal': urlchama[0]}
		codigo_fonte = net.http_POST(__SITE__+'searchurl.php',form_data=dados,headers=__HEADERS__).content
		elems = ET.fromstring(codigo_fonte)
		for child in elems:
			if(child.tag == 'info'):
				for d in child:
					if(d.tag == 'url'):
						urlcorrecto = d.text
	
	#__ALERTA__('Live!t TV', 'Url: '+urlcorrecto)
	
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlist.clear()
	listitem = xbmcgui.ListItem(nome, thumbnailImage=iconimage)
	listitem.setInfo('video', {'Title': nome})
	playlist.add(url=urlcorrecto, listitem=listitem, index=1)
	xbmc.Player().play(playlist)

def play_canal(arg, icon, nome):
	listitem = xbmcgui.ListItem( label = str(nome), iconImage = icon, thumbnailImage = icon, path=arg )
	listitem.setProperty('fanart_image', icon)
	listitem.setArt({'fanart': icon})
	listitem.setProperty('mimetype', 'video/x-msvideo')
	listitem.setInfo(type="Video", infoLabels={ "Title": nome })
	if 'acestream://' in arg:
		from resources.lib.acecore import TSengine as tsengine
		xbmc.executebuiltin('Action(Stop)')
		lock_file = xbmc.translatePath('special://temp/'+ 'ts.lock')
		if xbmcvfs.exists(lock_file):
			xbmcvfs.delete(lock_file)
		aceport=62062
		chid=arg.replace('acestream://','').replace('ts://','')
		TSPlayer = tsengine()
		out = None
		if chid.find('http://') == -1 and chid.find('.torrent') == -1:
			out = TSPlayer.load_torrent(chid,'PID',port=aceport)
		elif chid.find('http://') == -1 and chid.find('.torrent') != -1:
			out = TSPlayer.load_torrent(chid,'TORRENT',port=aceport)
		else:
			out = TSPlayer.load_torrent(chid,'TORRENT',port=aceport)
		if out == 'Ok':
			TSPlayer.play_url_ind(0,nome + ' (' + chid + ')',icon,icon)
			TSPlayer.end()
			return
		else:    
			__ALERTA__('Live!t TV', 'Erro ao abrir o canal Acestream. ')
			TSPlayer.end()
			return	
	else:
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

def addDir2(name,url,mode,mode2,iconimage,pagina=1,tipo=None,infoLabels=None,poster=None,visto=False):
	if infoLabels: infoLabelsAux = infoLabels
	else: infoLabelsAux = {'Title': name}
	fanart = ''
	if poster: fanart = poster
	else: fanart = iconimage
	
	try:
		name = name.encode('utf-8')
	except:
		name = name

	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&modo="+mode2+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	
	ok=True

	#fanart = __FANART__

	if tipo == 'filme':
		#fanart = posterAux
		xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
	elif tipo == 'serie':
		#fanart = posterAux
		xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	elif tipo == 'episodio':
		#fanart = posterAux
		xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
	else:
		if name != 'Refresh':
			xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
	
	overlay = 6
	playcount = 0
	
	infoLabelsAux["overlay"] = overlay
	infoLabelsAux["playcount"] = playcount
	
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setProperty('fanart_image', fanart)
	liz.setArt({'fanart': fanart})
	liz.setInfo( type="Video", infoLabels=infoLabelsAux )

	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

###################################################################################
#                              DEFININCOES		                                  #
###################################################################################	
def returnestilo(estilonovo):
	__estilagem__ = ""
	
	if estilonovo == "Lista":
		__estilagem__ ="Container.SetViewMode(50)"
	elif estilonovo == "Lista Grande":
		__estilagem__ = "Container.SetViewMode(51)"
	elif estilonovo == "Miniatura":
		__estilagem__ ="Container.SetViewMode(500)"
	elif estilonovo == "Posters":
		__estilagem__ ="Container.SetViewMode(501)"
	elif estilonovo == "Fanart":
		__estilagem__ = "Container.SetViewMode(508)"
	elif estilonovo == "Media Info 1":
		__estilagem__ = "Container.SetViewMode(504)"
	elif estilonovo == "Media Info 2":
		__estilagem__ = "Container.SetViewMode(503)"
	elif estilonovo == "Media Info 3":
		__estilagem__ = "Container.SetViewMode(515)"
	return __estilagem__
	
def vista_Canais():
	opcao = __ADDON__.getSetting('canaisView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
	elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(509)")
	elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(508)")
	elif opcao == '5': xbmc.executebuiltin("Container.SetViewMode(504)")
	elif opcao == '6': xbmc.executebuiltin("Container.SetViewMode(503)")
	elif opcao == '7': xbmc.executebuiltin("Container.SetViewMode(515)")

def vista_Canais_Lista():
	opcao = __ADDON__.getSetting('canaisView2')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
	elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(509)")
	elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(508)")
	elif opcao == '5': xbmc.executebuiltin("Container.SetViewMode(504)")
	elif opcao == '6': xbmc.executebuiltin("Container.SetViewMode(503)")
	elif opcao == '7': xbmc.executebuiltin("Container.SetViewMode(515)")

def abrirDefinincoes():
	__ADDON__.openSettings()
	addDir('Entrar novamente', 'url', None, None, 'Miniatura', __SITEAddon__+"Imagens/retroceder.png",'','','','',os.path.join(__ART_FOLDER__, __SKIN__, 'fundo_addon.png'))
	vista_menu()

def abrirDefinincoesMesmo():
	__ADDON__.openSettings()
	vista_menu()

def vista_menu():
	opcao = __ADDON__.getSetting('menuView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
	elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(509)")
	elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(508)")

def vista_filmesSeries():
	opcao = __ADDON__.getSetting('filmesSeriesView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
	elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(509)")
	elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(508)")
	elif opcao == '5': xbmc.executebuiltin("Container.SetViewMode(504)")
	elif opcao == '6': xbmc.executebuiltin("Container.SetViewMode(503)")
	elif opcao == '7': xbmc.executebuiltin("Container.SetViewMode(515)")


def vista_temporadas():
	opcao = __ADDON__.getSetting('temporadasView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
	elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(509)")

def vista_episodios():
	opcao = __ADDON__.getSetting('episodiosView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
	elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(509)")
	elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(504)")
	elif opcao == '5': xbmc.executebuiltin("Container.SetViewMode(503)")
	elif opcao == '6': xbmc.executebuiltin("Container.SetViewMode(515)")

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
buildtipo=None
name=None
mode=None
iconimage=None
link=None
senha=None
estilo=None
srtfilm=None
idCanal=None
idffCanal=None
tipologia=None
descricao=None
tipo_user=None
servidor_user=None
data_user=None
s_serv=None
s_user=None
s_pass=None
legenda=None
pagina=None
temporada=None
episodio=None
serieNome=None
fanart=None


try: url=urllib.unquote_plus(params["url"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: estilo=urllib.unquote_plus(params["estilo"])
except: pass
try: mode=int(params["mode"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass
try: senha=urllib.unquote_plus(params["senha"])
except: pass
try: idCanal=urllib.unquote_plus(params["idCanal"])
except: pass
try: idffCanal=params["idffCanal"]
except: pass
try: srtfilm=urllib.unquote_plus(params["srtfilm"])
except: pass
try: tipologia=urllib.unquote_plus(params["tipologia"])
except: pass
try: descricao=urllib.unquote_plus(params["descricao"])
except: pass
try: tipo_user=urllib.unquote_plus(params["tipo_user"])
except: pass
try: servidor_user=urllib.unquote_plus(params["servidor_user"])
except: pass
try: s_serv=urllib.unquote_plus(params["lolserv"])
except: pass
try: s_user=urllib.unquote_plus(params["loluser"])
except: pass
try: s_pass=urllib.unquote_plus(params["lolpass"])
except: pass
try: link=urllib.unquote_plus(params["link"])
except: pass
try: legenda=urllib.unquote_plus(params["legenda"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: temporada=int(params["temporada"])
except: pass
try: episodio=int(params["episodio"])
except: pass
try: mode=int(params["mode"])
except: pass
try: pagina=int(params["pagina"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass
try : serieNome=urllib.unquote_plus(params["serieNome"])
except: pass
try : buildtipo=urllib.unquote_plus(params["buildtipo"])
except: pass
try : fanart=urllib.unquote_plus(params["fanart"])
except: pass
try : data_user=urllib.unquote_plus(params["data_user"])
except: pass




###############################################################################################################
#                                                   MODOS                                                     #
###############################################################################################################

if mode==None or url==None or len(url)<1: menu()
elif mode==1: listar_grupos(str(name),str(url),estilo,tipologia,tipo_user,servidor_user,fanart)
elif mode==2: listar_canais_url(str(name),str(url),estilo,tipologia,tipo_user,servidor_user,fanart,data_user)
elif mode==4: buildLiveit(buildtipo)
elif mode==3: listar_grupos_adultos(str(url),str(senha),estilo,tipologia,tipo_user,servidor_user,fanart)
elif mode==10: minhaConta(str(name),estilo)
elif mode==20: listamenusseries(str(name),str(url),estilo,tipologia,tipo_user,servidor_user,iconimage,fanart)
elif mode==21: listamenusfilmes(str(name),str(url),estilo,tipologia,tipo_user,servidor_user,iconimage,fanart)
elif mode==24: listamenusanimes(str(name),str(url),estilo,tipologia,tipo_user,servidor_user,iconimage,fanart)
#elif mode==22: menuSeries()
#elif mode==23: menuFilmes()
elif mode==31: programacao_canal(idCanal)
elif mode==105: play_mult_canal(url, iconimage, name)
elif mode==106: play_canal(url, iconimage, name)
elif mode==110: minhaConta2()
elif mode==111: filmes(url, pagina)
elif mode==123: series(url)
elif mode==118: getGeneros(url)
elif mode==119: getYears(url)
elif mode==120: pesquisa(url,servidor_user)
elif mode==121: anos(url)
elif mode==122: categorias(url)
elif mode==113: player(name, url, iconimage, temporada, episodio, serieNome)
elif mode==114: getSeasons(url)
elif mode==115: getEpisodes(url)
elif mode==117: download(url, name, temporada, episodio, serieNome)
elif mode==1000: abrirDefinincoes()
elif mode==2000: abrirNada()
elif mode==3000: abrirDefinincoesMesmo()
elif mode==3333: abrim3u(url,data_user)
elif mode==3334: PlayUrl(name,url,iconimage)
elif mode==4000: minhaContabuild()
elif mode==5000: CLEARCACHE()
elif mode==6000: PURGEPACKAGES()
elif mode==7000: loginPesquisa()
elif mode==8000: buildLiveit(url)


if mode==None or url==None or len(url)<1:
	xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False)
else:
	if mode !=7000 and  mode !=120 and  mode !=3333: xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False)
	else: xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=True)