from ..plugin import Plugin
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import json, sys

import requests
session = requests.Session()

try:
    from resources.lib.util.common import *
except ImportError:
    from .resources.lib.util.common import *

addon_id = xbmcaddon.Addon().getAddonInfo('id')
default_icon = xbmcaddon.Addon(addon_id).getAddonInfo('icon')
default_fanart = xbmcaddon.Addon(addon_id).getAddonInfo('fanart')
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.344'
iStream_Agent = 'user-agent=' + USER_AGENT


class mpd_play_video(Plugin):
    name = "mpd video playback"
    priority = 10

    def play_video(self, item):
        if not '"link":' in str(item) : return False
        item = json.loads(item)
        link = item["link"]
        title = item["title"]
        thumbnail = item.get("thumbnail", default_icon)
        liz = xbmcgui.ListItem(title)
        liz.setInfo('video', {'Title': title})
        liz.setArt({'thumb': thumbnail, 'icon': thumbnail})   
        
        mpd_url = '' 
        
        if '===' in link :
            link_url = link.split("===")
            header_url = link_url[0].replace(
                                "is_hls://", "").replace(
                                "is_mpd_msready://", "").replace(
                                "is_mpd://", "").replace(
                                "is_mpd://", "")
                                
        elif  'X-forwarded-for' in link :
            xf_url = link.split("|X-forwarded-for=")
            # link = xf_url[0]
            header_url = xf_url[-1]
            if not header_url. startswith('http'): header_url = 'http://'+header_url
            
        else :
            header_url = link.replace(
                                "is_hls://", "").replace(
                                "is_msready://", "").replace(
                                "is_mpd://", "")
 
        headers1 = {'User-Agent': USER_AGENT ,
                               'Referer': header_url }   
 
        headers2 = {'User-Agent': USER_AGENT }        
 
        headers3= {'User-Agent': 'Mozilla' }        
 
        headers4 = {'User-Agent': 'iPad' }       
 
        headers5 = {'User-Agent': 'Apple-iPhone/701.341' }        
 
        try :
            headers_text = session.get(header_url).headers
            headers6 = {'User-Agent': USER_AGENT ,
                                   'Referer': str(headers_text) }             
        except :
            headers6 = headers1
            
        headers = headers1
        
        do_log(f'{self.name} - headers = \n' + str(headers) )  
        
        liz.setProperty('inputstream', 'inputstream.adaptive')            
        liz.setProperty('inputstream.adaptive.stream_headers', str(headers) )       
        # liz.setProperty('inputstream.adaptive.stream_headers', header_url)          
        # liz.setProperty('inputstream.adaptive.stream_headers', iStream_Agent)                                                                                                                      
        
        liz.setContentLookup(False)   
        
        # ok_helper = self.mpd_helper('mpd', 'com.widevine.alpha' )   
        # if ok_helper : do_log(f'{self.name} - ok_helper = ' + str(ok_helper))  
        
        if link :            
            if link.startswith("is_hls://"):
                mpd_url = link.replace("is_hls://", "")
                PROTOCOL = 'hls' 
                DRM = '' 
                MIMETYPE = 'application/vnd.apple.mpegurl' 
                
                liz.setProperty('inputstream.adaptive.manifest_type', PROTOCOL) # PROTOCOL
                liz.setMimeType(MIMETYPE) 
 
            elif link.startswith("is_msready://"):
                mpd_url = link.replace("is_msready://", "")
                PROTOCOL = 'ism' 
                DRM = '' 
                MIMETYPE = 'application/vnd.ms-sstr+xml' 

                liz.setProperty('inputstream.adaptive.manifest_type', PROTOCOL) # PROTOCOL
                liz.setMimeType(MIMETYPE) 
                                
            elif link.startswith("is_mpd://"):
                PROTOCOL = 'mpd' 
                DRM = 'com.widevine.alpha' 
                MIMETYPE = 'application/dash+xml' 
               
                try : 
                    mpd_split = link.split("===")
                    mpd_url = mpd_split[0].replace("is_mpd://", "")
                    license_key = mpd_split[1] # +'|User-Agent=' + USER_AGENT + '|R{SSM}|'    
                except :
                    mpd_url = link.replace("is_mpd://", "")              
                    # license_key = ''
                    # license_key = 'https://widevine-proxy.appspot.com/proxy'
                    # license_key = 'https://widevine-proxy.appspot.com/proxy' + '||R{SSM}|'
                    # license_key = 'https://widevine-proxy.appspot.com/proxy' + '||b{SSM}!b{SID}|'
                    # license_key = 'https://widevine-proxy.appspot.com/proxy|User-Agent=Mozilla|R{SSM}|'                  
                    license_key = 'https://widevine-proxy.appspot.com/proxy|User-Agent=' + USER_AGENT + '|R{SSM}|'    
                                        
                if license_key != '':
                    liz.setProperty('inputstream.adaptive.license_type', DRM) #DRM
                    liz.setProperty('inputstream.adaptive.license_key', license_key) 
                           
                liz.setProperty('inputstream.adaptive.manifest_type', PROTOCOL) # PROTOCOL     
                liz.setMimeType(MIMETYPE) 
          
            if mpd_url :         
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
                xbmc.Player().play(mpd_url, liz)   
                return True
    
        else:
        	return False 
        
    def mpd_helper(self, protocol, drm) :
        import inputstreamhelper
        is_helper = inputstreamhelper.Helper(protocol, drm)
        if not is_helper.check_inputstream():     
            return False
        else :  
            return True 
       