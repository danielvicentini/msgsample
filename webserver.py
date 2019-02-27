
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json 
import os
import requests
from webexteamssdk import WebexTeamsAPI



# CHAT BOT v3.0.0
# Integracao Cisco Operations Insights & Webex Teams & CMX
# (c) 2019 
# Flavio Correa
# Joao Peixoto
# Sergio Polizer
# Daniel Vicentini



#########################################################
## VAR FIXAS

# infobot
api = WebexTeamsAPI(access_token='YTk3NDY2NzMtYTUwZC00MzRjLTgwMDAtMWE0YmYxMmJkN2FmYjg0ZDhmZmMtYTM1')

# Webhook
webhook_url="https://webexteamsmsg.herokuapp.com"
webhook_name="chatops"
botmail="infobot@sparkbot.io"

#########################################################
## FUNCOES


def CriaWebhook(webhook_name,webhook_url):

	# Cria Webhook para receber msg via POST
    # Avisa Teams para gerar hooks para mensagems criadas somente

    api.webhooks.create(webhook_name,webhook_url,"messages","created")

    return


def webexME():
	# detalhes sobre mim
	data = api.people.me()
	return data

def WebexRoomCreate(name):

	# Cria Sala Webex e retorna ID da sala, name aqui e' o nome da Sala
	api.rooms.create(name)

	# Encontra roomID da sala para devolver
	novasala = getwebexRoomID(name)

	return novasala

def WebexRoomDel(id):

	#Remove sala Webex,id aqui e' roomID 
	api.rooms.delete(id)

	return

def WebexIncUser(sala,mail):

	#Inclui usuario como membro da sala, criando sala caso nao exista
    # Descobri roomID da sala (sala e' o nome completo ou parte dela)
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
    # O parametro sala e' todo ou parte do nome da sala procurada
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
	
    # msgID é o parametro resgatado do corpo do webhook
	# Retorna lista com o [0]texto da mensagem informada [1]ID da sala e [2]email da pessoa
	mensagem=api.messages.get(msgID)
				
	return mensagem.text,mensagem.roomId,mensagem.personEmail

def webexmsgRoom(sala,msg):

	# Manda msg para 1 sala especifica, procurando salas onde estou (usando partes do nome informado em sala)
	rooms=api.rooms.list()
	salawebex = None

	salawebex = getwebexRoomID(sala)
			
	# mandando uma mensagem para a Sala caso encontrada:
	if salawebex != None:
		api.messages.create(salawebex,None,None,msg)

	return

def webexmsgRoomviaID(sala,msg):

	# Manda msg para 1 sala especifica informada via sala=roomID, 
	api.messages.create(sala,None,None,msg)

	return

def webexmsgAll(msg):
	# mensagem em todas as salas que estou
	#
	rooms=api.rooms.list()

	for room in rooms:
		api.messages.create(room.id,None,None,msg)
	
	return


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
	#if textosearch == "tudo":
	#	textosearch = ""
    # Tudo não rola por causa do limite do Webex teams de caracteres DV

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

def webextalk(msg_id):

    # Camada de interação com o usuário conversando com o BOT

    # chama funcao para resgatar detalhes da mensagem (via id)
    dados = getwebexMsg(msg_id)
    # armazena o texto da msg enviada pelo usuario 
    # box e' o que o user escreveu
    box=dados[0]
    # armazena o id sala usada para devolver para mesma
    idsala=dados[1]
    # armazena email de quem enviou - nao utilizado ainda
    usermail=dados[2]

    # Para o caso de nenhum pedido coberto aqui
    msg="Nao entendi seu pedido"
    
    # Splita para encontrar detalhes dos parametros
    sp=box.split(" ")
    box=sp[0]

    # chamadas de acordo com os parametros
    if box == "help":
        msg="Chatops Teams 1.0\nComandos disponiveis:\nhelp: esta ajuda\nprocura <item>: Procurar Asset\n"
        msg=msg+str("userid <email>: Identifica ID do usuario\nroomid <nome da sala>: Identifica ID da sala\nsalas: lista salas que pertenco\nexit: sai")
            
    # chama funcao para procurar OPI somente se ouver 2 parametros
    if box == "procura" and len(sp)>1:
        asset=sp[1]
        msg = procura(asset)
            
    # chamada funcao se houver no minimo 2 parametros
    if box == "userid" and len(sp)>1:
        email=sp[1]
        msg = str("ID da user: " +str(email)+": "+str(getwebexUserID(email)))
        
    # chamada funcao se houver no minimo 2 parametros
    if box == "roomid" and len(sp)>1:
            sala=sp[1]
            msg = str("ID da sala: " +str(sala)+": "+str(getwebexRoomID(sala)))

    if box =="salas":
        msg = webexRoomsList()
        
    # apos montagem da resposta em msg, envia a respectiva sala teams:
    webexmsgRoomviaID(idsala,msg)

# RASCUNHOS ANTERIORES
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




#########################################################
## LOGICA COMECA AQUI


# inicia programa


# Site

# Cria webhook para receber POSTs
CriaWebhook(webhook_name,webhook_url)


# http server
class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    # POST valida se o que chega sem dados via o Webhook
    # do POST e' que se chama a rotina de respnder ao usuario

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

        # Daniel Vicentini
        # Aciona bot caso webhook seja identificado e mensagem postada nao seja do proprio bot
        content=json.loads(post_data.decode('utf-8'))
        if content['name']==webhook_name and content['data']['personEmail']!=botmail:
            
            # identifica id da mensagem
            msg_id=(content['data']['id'])
            # executa a logica conforme o pedido (interacao)
            webextalk(msg_id)


def run(server_class=HTTPServer, handler_class=S, port=int(os.getenv('PORT',8080))):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
        
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')



"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:	
        run()