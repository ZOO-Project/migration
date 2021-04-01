# -*- coding: utf-8 -*-
from Cheetah.Template import Template
import xmlrpclib,sys  
import zoo
server = xmlrpclib.ServerProxy("http://LOGIN:PASSWORD@SERVER/trac/login/xmlrpc",allow_none=True) 


defaultPage="Default"
defaultLang=""
wiki_prefix="ZooWebSite/2015"

def parseHTML(content):
	content1=server.wiki.getPageHTML(content).encode('utf-8')
	return content1.replace("</body></html>","").replace("<html><body>","").replace("/chrome/site/","/").replace("http://trac.geolabs.fr","").replace("js/","../js/").replace("styles.css","../styles.css")

def parse(content):
	try:
		return server.wiki.getPage(content).encode('utf-8').replace("</body></html>","").replace("<html><body>","").replace("/chrome/site/","/").replace("http://trac.geolabs.fr","")
	except:
		return "Not found"

def login(conf,inputs,outputs):
	if conf.has_key("senv") and conf["senv"].has_key("login"):
		conf["lenv"]["message"]="Vous etes deja connecte"
		return zoo.SERVICE_FAILED

	try:
		server=xmlrpclib.ServerProxy("http://"+inputs["login"]["value"]+":"+inputs["passwd"]["value"]+"@frog2013.foss4g.fr/login/xmlrpc")
		server.wiki.getPageHTML("WikiStart")
		conf["senv"]["login"]=inputs["login"]["value"]
		conf["senv"]["passwd"]=inputs["passwd"]["value"]
		conf["senv"]["isMeteoLib"]="false"
		conf["senv"]["isAdmin"]="true"
		outputs["Result"]["value"]="Utilisateur "+conf["senv"]["login"]+" authentifié"
		return zoo.SERVICE_SUCCEEDED
	except Exception as e:
		conf["lenv"]["message"]="Impossible de se connecter avec les informations fournies ("+str(e)+")."
		return zoo.SERVICE_FAILED

	
def logout(conf,inputs,outputs):
	if not(conf["senv"].has_key("login")):
		conf["lenv"]["message"]="Vous n'etes pas connecte"
		return zoo.SERVICE_FAILED
	else:
		outputs["Result"]["value"]="Utilisateur "+conf["senv"]["login"]+" deconnecte"
		conf["senv"].pop("login")
		conf["senv"].pop("passwd")
		conf["senv"].pop("isAdmin")
		try:
			conf["senv"].pop("isMeteoLib")
		except:
			pass
		return zoo.SERVICE_SUCCEEDED

def getCurrentServer(conf):
	if conf["senv"].has_key("login"):
		return xmlrpclib.ServerProxy("http://"+conf["senv"]["login"]+":"+conf["senv"]["passwd"]+"@SERVER/login/xmlrpc")
	else:
		return xmlrpclib.ServerProxy("http://LOGIN:PASSWORD@SERVER/login/xmlrpc")

def messageClub(conf,inputs,outputs):
	msgClub=server.wiki.getPage(wiki_prefix+"/fr/Templates/MessageClub")
	msg=Template(msgClub,searchList={"conf":conf,"inputs":inputs})
	if inputs.has_key("file"):
		inputs["file"]["value"]="<a href=\"http://geolabs.fr/tmp/data_tmp_1111"+conf["senv"]["MMID"]+"/"+inputs["file"]["value"].replace(" ","%20")+"\">fichier joint</a>"
	else:
		inputs["file"]={"value":""}
	#print >> sys.stderr,msg
	i=server.ticket.create(inputs["Subject"]["value"],"{{{\n#!html\n"+str(msg)+"\n}}}",{},True)# inputs["Message"]["value"]+" \n\n [http://meteolib.fr/tmp/data_tmp_1111"+conf["senv"]["MMID"]+"/"+inputs["file"]["value"].replace(" ","%20")+" fichier joint]");
	outputs["Result"]["value"]="Votre message a bien été envoyé, il a le numéro #"+str(i)+"."
	return zoo.SERVICE_SUCCEEDED

def getAttachment(conf,inputs,outputs):
	import base64,xmlrpclib
	tmpStr=server.wiki.getAttachment(inputs["file"]["value"])
	tmp=inputs["file"]["value"].split(".")
	file=open("/var/www/localhost/htdocs/dl/"+inputs["file"]["value"].replace(wiki_prefix+"/",""),"wb")
	file.write(tmpStr.data)
	file.close()
	file=open("/var/www/localhost/htdocs/dl/"+inputs["file"]["value"].replace(wiki_prefix+"/",""),"rb")
	outputs["Result"]["value"]=file.read()
	print >> sys.stderr,dir(file)
	import os
	s=os.stat("/tmp/demo")
	#outputs["Result"]["size"]=s.st_size
	print >> sys.stderr,s.st_size
	if tmp[1]=="pdf":
		outputs["Result"]["mimeType"]="application/pdf"
	if tmp[1]=="wmv":
		outputs["Result"]["mimeType"]="video/x-ms-wmv"
	if tmp[1]=="jpg":
		outputs["Result"]["mimeType"]="image/jpeg"
	outputs["Result"]["filename"]=inputs["file"]["value"].replace(wiki_prefix+"/","")
	return 3

def savePage(conf,inputs,outputs):
	llang=defaultLang
	value="{{{\n#!html\n"+inputs["content"]["value"]+"\n}}}"
	page=wiki_prefix+"/"+llang+"/Root/HTML/"+inputs["name"]["value"]
	#infov=server.wiki.getPageInfoVersion(page)
	#infov["comment"]="Mise en place depuis l'interface cliente."
	#infov["version"]+=1
	server0=getCurrentServer(conf)
	server0.wiki.putPage(page,value,{"action":"edit","comment": "Mise à jour depuis l'interface de saisie !MeteoLib."})
	return loadPageEdit(conf,inputs,outputs)

def loadPageEdit(conf,inputs,outputs):
	llang=defaultLang
	print >> sys.stderr,wiki_prefix+"/"+llang+"/"+inputs["name"]["value"]
	try:
		page=server.wiki.getPageHTML(wiki_prefix+"/"+llang+"/Root/HTML/"+inputs["name"]["value"]).replace("<html><body>","").replace("</body></html>","").encode('utf-8')
	except:
		page=""
	print >> sys.stderr,page
	outputs["Result"]["value"]=page
	return zoo.SERVICE_SUCCEEDED

def printTemplate(conf,inputs,outputs):
	import time
	if inputs["tmpl"]["value"]=="":
		inputs["tmpl"]["value"]="Accueil"
	tmpName=inputs["tmpl"]["value"].split('/')
	print >> sys.stderr,str(11)
        print >> sys.stderr,time.localtime()
	tmpName[0]=tmpName[0].replace("'","").replace('"','').replace('<','').replace('>','')
	try:
		if inputs.has_key("m") and inputs["m"]["value"]=="1":
			toto=parse(wiki_prefix+"/Mobile/Header").replace("[_title_]",tmpName[0])
		else:
			#try:
			#	toto=parse("WebSite/Headers/"+inputs["tmpl"]["value"]).replace("[_title_]",tmpName[0])
			#except:
			toto=parse(wiki_prefix+"/Headers/"+inputs["tmpl"]["value"]).replace("[_title_]",tmpName[0])
			if toto=="Not found":
				toto=parse(wiki_prefix+"/Header").replace("[_title_]",tmpName[0])
			toto=toto.replace("[_css_]","4219271310-widget_css_2_bundle.css")
	except:
		conf["senv"]["lang"]=defaultLang
		llang=defaultLang
		toto=parse(wiki_prefix+"/"+llang+"/Header").replace("[_title_]",tmpName[0])

  icons=None
	try:
		pages=server.wiki.getPage(wiki_prefix+"/Menu").encode('utf-8').split(',')
		#icons=server.wiki.getPage(wiki_prefix+"/MenuIcons").encode('utf-8').split(',')
	except:
		pages=[]
		#icons=[]
	if inputs.has_key("m") and inputs["m"]["value"]=="1":
		menuTmpl=server.wiki.getPage(wiki_prefix+"/Templates/Mobile/Menu")
	else:
		menuTmpl=server.wiki.getPage(wiki_prefix+"/Templates/Menu")

	menu=Template(menuTmpl,searchList={"conf":conf,"menuIcons": icons,"menuItems": pages,"inputs":inputs,"server": server})


	try:
		print >> sys.stderr,inputs["tmpl"]["value"]
		print >> sys.stderr,inputs["tmpl"]["value"]!="edit"
		tmp0=inputs["tmpl"]["value"].split("/")
		if inputs["tmpl"]["value"]!="edit" and tmp0[len(tmp0)-1]!="edit":
			if inputs.has_key("m") and inputs["m"]["value"]=="1":
				try:
					page=server.wiki.getPageHTML(wiki_prefix+"/Mobile/"+inputs["tmpl"]["value"]).replace("<html><body>","").replace("</body></html>","").encode('utf-8')
				except:
					page=server.wiki.getPageHTML(wiki_prefix+"/"+inputs["tmpl"]["value"]).replace("<html><body>","").replace("</body></html>","").encode('utf-8')
			else:
				page=server.wiki.getPageHTML(wiki_prefix+"/"+inputs["tmpl"]["value"]).replace("<html><body>","").replace("</body></html>","").encode('utf-8')
		else:
			ipages=server.wiki.getAllPages()
			ifpages=[]
			for i in ipages:
				if i.count("/Root/")>0:
					ifpages+=[i.encode("utf-8")]
			try:
				tpage0=server.wiki.getPage(wiki_prefix+"/Templates/Editor")
				page=str(Template(tpage0,searchList={"conf":conf,"pages":ifpages,"inputs":inputs}))
			except:
				page="Erreur"
				
	except Exception as e:
		print >> sys.stderr,e
		if inputs["tmpl"]["value"]=="Incident":
			tpage0=server.wiki.getPage(wiki_prefix+"/Templates/Incident")
			page=server.wiki.wikiToHtml(str(Template(tpage0,searchList={"conf":conf,"inputs":inputs}))).encode('utf-8').replace("<html><body>","").replace("</body></html>","")
		else:
			page="[_message_] <a href='/trac/wiki/"+wiki_prefix+"/"+inputs["tmpl"]["value"]+"'>"+wiki_prefix+"/"+inputs["tmpl"]["value"]+"</a> [_end_]"
        print >> sys.stderr,str(14)
        print >> sys.stderr,time.localtime()

	if inputs.has_key("m") and inputs["m"]["value"]=="1":
		tpage=server.wiki.getPage(wiki_prefix+"/Templates/Mobile/Page")
	else:
		tpage=server.wiki.getPage(wiki_prefix+"/Templates/Page").encode('utf-8')
	try:
		title=server.wiki.getPage(wiki_prefix+"/Titles/"+inputs["tmpl"]["value"]).encode('utf-8')

	except:
		title="Not found"
	footer=""
	footer=server.wiki.getPageHTML(wiki_prefix+"/Footer").replace("<html><body>","").replace("</body></html>","")
	reqf="select (select max(val) from suivi_previsions), datediff((select max(date_compt) from suivi_previsions),(select min(date_compt) from suivi_previsions))"

  titi=Template(tpage,searchList={"conf":conf,"pageTitle":title, "menu": menu,"content":page,"footer":"","inputs":inputs,"server":server})
  toto+=str(Template(tpage,searchList={"conf":conf,"pageTitle":title, "menu": menu,"content":page,"footer":"","inputs":inputs,"server":server}))
  try:
		script=server.wiki.getPage(wiki_prefix+"/Scripts/"+inputs["tmpl"]["value"]).encode('utf-8')
		#print >> sys.stderr,script
	except Exception as e:
		print >> sys.stderr,e
		script=server.wiki.getPage(wiki_prefix+"/Scripts/Default").encode('utf-8')
	if inputs["tmpl"]["value"]=="Références" or inputs["tmpl"]["value"]=="Références/NoWebGL":
		if conf.keys().count("senv") > 0:
			if inputs["tmpl"]["value"]!="Références/NoWebGL":
				conf["senv"]["refCount"]=str(int(conf["senv"]["refCount"])+1)
			conf["lenv"]["cookie"]="MMID="+conf["senv"]["MMID"]
			if int(conf["senv"]["refCount"])>0 and int(conf["senv"]["refCount"]) % 2 == 0:
				inputs["tmpl"]["value"]+="/1"
        print >> sys.stderr,str(19)
        print >> sys.stderr,time.localtime()
	
	if inputs.has_key("m") and inputs["m"]["value"]=="1":
		toto+=parse(wiki_prefix+"/Mobile/Footer")
	else:
		toto+=parse(wiki_prefix+"/Footer").replace("[_script_]",script)
    
	return toto
    
def wdisplay(conf,inputs,outputs):
	llang=defaultLang
	import os.path
	import time
	if conf.keys().count("senv") == 0 or inputs.keys().count("lang"):
		import time
		conf["senv"]={}
		conf["senv"]["MMID"]="MM"+str(time.time()).split(".")[0]
		conf["lenv"]["cookie"]="MMID="+conf["senv"]["MMID"]+"; path=/"
		conf["senv"]["refCount"]="0"
		if inputs.keys().count("lang"):
			conf["senv"]["lang"]=inputs["lang"]["value"]
		else:
			conf["senv"]["lang"]=defaultLang

	if inputs["tmpl"]["value"]=="":
		inputs["tmpl"]["value"]="Accueil"
	tmpName=inputs["tmpl"]["value"].split('/')
	tmpName[0]=tmpName[0].replace("'","").replace('"','').replace('<','').replace('>','')
	if len(tmpName)>=2:
		tmpName[1]=tmpName[1].replace("'","").replace('"','').replace('<','').replace('>','')
	iniName="_".join(tmpName)
	if os.path.isfile(conf["main"]["tmpPath"]+"/"+iniName+"_tmpl.html") and inputs.keys().count("force")==0:
		f=open(conf["main"]["tmpPath"]+"/"+iniName+"_tmpl.html","r")
		toto=f.read()
	else:
		toto=printTemplate(conf,inputs,outputs)
		f=open(conf["main"]["tmpPath"]+"/"+iniName+"_tmpl.html","w")
		f.write(toto)
		f.close()
	if inputs["tmpl"]["value"]=="atom.xml":
		outputs["Result"]["value"]=str(Template(tpage,searchList={"conf":conf,"pageTitle":title, "menu": menu,"content":page,"footer":"","inputs":inputs,"server":server}))
		outputs["Result"]["mimeType"]="text/xml"
	else:
		outputs["Result"]["value"]=toto
        print >> sys.stderr,str(20)
        print >> sys.stderr,time.localtime()
	return 3
 
