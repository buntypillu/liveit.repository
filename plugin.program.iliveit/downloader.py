import xbmcgui
import urllib

__ALERTA__ = xbmcgui.Dialog().ok

def download(url, dest, dp = None):
    if not dp:
        dp = xbmcgui.DialogProgress()
        dp.create("Husham...Maintenance","Downloading & Copying File",' ', ' ')
    dp.update(0)
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
 
def _pbhook(numblocks, blocksize, filesize, url, dp):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled():
        __ALERTA__('Live!t TV', 'Cancelou a acao. Tente mais tarde.')
        dp.close()
