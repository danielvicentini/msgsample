import requests
import json
from webexteamssdk import WebexTeamsAPI


# CHAT BOT v3.0.0
# Integracao Cisco Operations Insights & Webex Teams & CMX
# (c) 2019 
# Flavio Correa
# Joao Peixoto
# Sergio Polizer
# Daniel Vicentini

# infobot
api = WebexTeamsAPI(access_token='YTk3NDY2NzMtYTUwZC00MzRjLTgwMDAtMWE0YmYxMmJkN2FmYjg0ZDhmZmMtYTM1')

#########################################################
## FUNCOES


def CriaWebhook():

	# Cria Webhook para receber msg
	
	# Site
	webhook_url="https://enmg7zrdqz1p.x.pipedream.net/"
	
	api.webhooks.create("chatops", webhook_url,"messages","created")

	return

def webexME():
	# detalhes sobre mim
	data = api.people.me()
	return data

def WebexRoomCreate(name):

	# Cria Sala Webex e retorna ID da sala
	api.rooms.create(name)

	# Encontra ID da sala para devolver
	novasala = getwebexRoomID(name)

	return novasala

def WebexRoomDel(name):

	#Remove sala Webex
	api.rooms.delete(name)

	return

def WebexIncUser(sala,mail):

	#Inclui usuario como membro da sala, criando sala caso nao exista
	salaaincluir=getwebexRoomID(sala)

	# Cria sala caso esta nao exista
	if salaaincluir == None:
		salaaincluir = WebexRoomCreate(sala)

	useraincluir=getwebexUserID(mail)

	# inclui usuario caso id encontrado
	if useraincluir !=None:
			#executa a operacao
			api.memberships.create(salaaincluir,useraincluir)

	return

def webexUser(mail):
	# pesquisa ID do usuário e retorna MSG
	usuario = api.people.list(email=mail)
	user=None

	for inter in usuario:
		user = inter.id

	if user !=None:
		resultado = "Usuario "+str(mail)+" ID e' "+user
	else:
		resultado = "Nenhum Usuario encontrado para "+str(mail)

	return resultado

def getwebexUserID(mail):
	# pesquisa ID do usuário; retorna vazio se nao encontrado
	usuario = api.people.list(email=mail)
	user=None

	for x in usuario:
		user = x.id

	if user !=None:
		resultado = user
	
	return resultado


def webexRoomsList():
	# lista salas que pertenco
	rooms=api.rooms.list()
	resultado = ""

	for room in rooms:
		resultado = resultado + "Sala " + str(room.title) + " ID: " + str(room.id)+ "\n"

	return resultado



def getwebexRoomID(sala):

	# Retorna ID da Sala; retorna vazio se nao encontrado
	# Salas que pertenco
	rooms=api.rooms.list()
	salawebex = None

	# for para encontrar ID da sala determinada

	for room in rooms:
		if sala in room.title:
	  		salawebex = room
	  		break

			
	# mandando uma mensagem para a Sala caso encontrada:s
	if salawebex != None:
		resultado = (str(salawebex.id))
	else:
		resultado = salawebex
		
	return resultado

def getwebexMsg(msgID):
	
	# Retorna lista com o texto da mensagem informada, ID da sala e pessoa

	mensagem=api.messages.get(msgID)
				
	return mensagem.text,mensagem.roomId,mensagem.personEmail

def webexmsgRoom(sala,msg):

	# Manda msg para 1 sala especifica
	# salas onde estou
	rooms=api.rooms.list()
	salawebex = None

	salawebex = getwebexRoomID(sala)
			
	# mandando uma mensagem para a Sala caso encontrada:
	if salawebex != None:
		api.messages.create(salawebex,None,None,msg)

	return

def webexmsgAll(msg):
	# mensagem em todas as salas que estou
	#
	rooms=api.rooms.list()

	for room in rooms:
		api.messages.create(room.id,None,None,msg)
	
	return

#	def createroom(titulo,pessoa):




def procura(textosearch):
	# Faz uma pesquisa no Operation Insights

	# Parte 1 - pede Token para o OPI
	url = "https://opinsights.cisco.com/api/am/v1/auth/license/accesstoken"
	headers = {'Content-type': "application/json" , 'Authorization':'JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRJZCI6MjExLCJ0eXBlIjoiODQzMDc0YjAtMzIwYS0xMWU4LTg0YTctMzkzZWNiNTViY2Q5IiwidXNlck5hbWUiOiJmbGNvcnJlYUBjaXNjby5jb20iLCJpYXQiOjE1NTA4NjI5NTQsImp0aSI6IjQ2YjRiNTIwLTM2ZDYtMTFlOS04OTRmLTI3YTM3MDQ2NWExNCJ9.sNEnOPr45NXNRgx9AyEqU4x9xrt8ra-miRSX2rfH9K4'   }

	# response = valor HTTP (nao usado ainda) e conteudo e' o conteudo de fato, covertendo em json
	response = requests.request("GET", url, headers=headers)
	conteudo=json.loads(response.content)
	# resultado do token
	token='JWT ' + str(conteudo['token'])

	# Parte 2 - Consulta assets usando o Token
	url = "https://opinsights.cisco.com/api/am/v1/entities/access/assets"
	headers = {     'Content-type': "application/json" , 'Authorization': ''+token  }

	# response = valor HTTP (nao usado ainda) e conteudo e' o conteudo de fato, covertendo em json
	response = requests.request("GET", url, headers=headers)
	Jdata=json.loads(response.content)


	# Laco que Faz a pesquisa baseado no grupo do dispositivo da base acima

	# Permite procurar tudo caso esta keyword seja usada
	if textosearch == "tudo":
		textosearch = ""

	resultado = ""
	msg=""
	count = 0

	for items in Jdata:

		 
		if textosearch in str(items['tags'][0]['type']) or textosearch in str(items['category']['name']):
		
			# Caso encontrado monta a resposta
			msg=msg+str("----------------------------------------------------\n")
			msg=msg+str("local:"+str(items['site']['name'])+"\n")
			msg=msg+str("nome do asset:"+str(items['serial'])+"\n")
			#msg=msg+str("localizacao x:"+str(items['location']['x'])+" y: "+str(items['location']['y'])+"\n")
			msg=msg+str("estado: "+str(items['status'])+"\n")
			msg=msg+str("serial: "+str(items['tags'][0]['serial'])+"\n")
			msg=msg+str("tipo: "+str(items['tags'][0]['type'])+"\n")
			msg=msg+str("categoria: "+str(items['category']['name'])+"\n")

			count = count +1
		
		resultado = resultado + str(msg)

		
	resultado = resultado + "\n"+str(count)+" Assets Encontrados"	

	return resultado




#########################################################
#### CODIGO COMECA AQUI	

# Exemplos:
# Envia mensagem para a primeira sala que tiver o texto ASIC, e Texto e' a msg
# webexmsgRoom('ASIC','Texto')
#====
# Envia msg para todas as salas
# webexmsgAll ('Ola a todos')
#====
# user=webexME()
# webexmsgRoom('ASIC','ID:'+str(user.id))
#====
# pesquisa e apresenta no CMD
# msg  = procura('PACIEN')
# print (msg)
#====
# pesquisa pessoa
#webexmsgRoom('CHATOPS',webexUser('nhaca@nhaca.com'))
#====
# get pessoa e get sala retornas os IDs
#user = getwebexUserID('dvicenti@cisco.com')
#room = getwebexRoomID('CHATOPS')
#====
## Codigo exemplo de aviso, criando a sala e o usuario
#usuario = 'dvicenti@cisco.com'
#novasala = 'CHAT COM '+str(usuario)
#====
# Cria sala e inclui user
#WebexIncUser(novasala,usuario)
#webexmsgRoom(novasala,"Ola "+str(usuario))
#====
# exemplo de aviso
#webexmsgRoom(novasala,"Aviso: " + str(procura('MACA')+" fora de compliance"))
#====
# list salas que pertenco
# salas = webexRoomsList()
# print (salas)
#====
# Cria e deleta sala
#x=WebexRoomCreate("sala teste")
#print (x)
#z=getwebexRoomID("sala teste")
#WebexRoomDel(z)

### LOGICA DAQUI PARA BAIXO

CriaWebhook()

webexmsgAll("olá - teste webhook. Não vou responder nada ainda")