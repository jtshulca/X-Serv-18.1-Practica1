#!/usr/bin/python3

import webapp
import csv
import urllib.parse


class contentApp(webapp.webApp):

    dicc_URL = {}
    dicc_short = {} 
    
    with open('csv') as fich:
        reader = csv.reader(fich)
        for row in reader:
            URL_corta = row[0]
            URL_larga = row[1]
            dicc_URL[URL_corta] = URL_larga
            dicc_short[URL_larga] = URL_corta

    def parse(self, request):
        try:
            metodo = request.split(' ',2)[0]
            recurso = request.split(' ',2)[1]
            try:
                cuerpo = request.split('\r\n\r\n')[1]
            except IndexError:
                cuerpo =""
        except IndexError:
            return None

        return(metodo, recurso, cuerpo)
        
	#Obtener las url almacenadas:
    def url_acortadas(self):
        lista = ""
        for url in self.dicc_URL:
            URL_corta = url
            URL_larga = self.dicc_URL[URL_corta]
            lista = lista + "<p><a href=" +  URL_larga + ">" + URL_larga + "</a>" \
                    " --> " + "<a href=" + URL_corta + ">" + URL_corta + "</a></p>"
        return lista

    def process(self, parsed):
        try:
            metodo, recurso, cuerpo = parsed
        except TypeError:
            httpCode = "HTTP/1.1 404 Not found"
            htmlBody = "<html><body>Not found</body></html>"
            return (httpCode, htmlBody)
        
        if metodo == "GET" and recurso == "/":
            info_incial = "<p><h2> Aplicacion web simple para acortar URLs</h2></p>"
            formulario = "<form method='POST' action=''><input type='text'" \
                           " name='url'><input type='submit' " \
                           "value='Acortar'></form></body></html>"

            if len(self.dicc_URL) == 0:
                info_lista_URLs = "<p>No hay URLs acortadas</p>"
                lista_URLs = ""
            else:
                info_lista_URLs = "<p><h2>URLs acortadas:</h2></p>"
                lista_URLs = self.url_acortadas()
                
            httpCode = "HTTP/1.1 200 OK"
            htmlBody = "<html><body>" + info_incial + formulario + info_lista_URLs + \
                        lista_URLs + "</body></html>"
                                                
        elif metodo == "POST" and recurso == "/":

            info_incial = "<p><h2> Aplicacion web simple para acortar URLs</h2></p>"
            url_body = cuerpo.split("=")[1]
			
			#Si no introducimos nada en el formulario
            if url_body == "":
                httpCode = "HTTP/1.1 400 Bad Request"
                htmlBody = "<html><body>Error. Debes introducir una url." \
                               "</body></html>"
            else:
                url_body = urllib.parse.unquote(url_body)

                if url_body.split("://")[0] != "http" and url_body.split("://")[0] != "https":
                    url_body = "http://" + url_body
				
                try: #Si ya tenemos acortada la URL
                    url_short = self.dicc_short[url_body]
                    ya_existe = "<p> Ya hemos acortado esa URL</p>"
                #Si no esta acortada la URL    
                except KeyError: 
                    if len(self.dicc_URL) == 0:
                        self.contador = 0
                    else:
                        self.contador = (len(self.dicc_URL)-1) + 1

                    url_short = "http://localhost:1234/" + str(self.contador)

                    # Añadimos y actualizamos el diccionario
                    self.dicc_URL[url_short] = url_body
                    self.dicc_short[url_body] = url_short
                    with open('csv', 'a') as fich:
                        escribir = csv.writer(fich)
                        escribir.writerow([url_short, url_body])
                    ya_existe = ""

                httpCode = "HTTP/1.1 200 OK"
                htmlBody = "<html><body>" + info_incial + \
                            "<p><h2>" + ya_existe + "</h2></p>" + \
                            "<p>URL: <a href=" + url_body + ">" + url_body + \
                            "</a> --> URL acortada: <a href=" + url_short + ">" + \
                            url_short + "</a></p></body></html>"

        elif metodo == "GET" and len(recurso) > 1:
            # Si ya tenemos algo en el diccionario
            try:
                recurso_num = int(recurso[1:])
            #Si no insertamos un numero 
            except ValueError:
                httpCode = "HTTP/1.1 404 Not Found"
                htmlBody = "<html><body><h1>Introduzca un numero</h1></body></html>"
                return (httpCode, htmlBody)

            URL_corta = "http://localhost:1234" + recurso
            try:
                URL_larga = self.dicc_URL[URL_corta]
            #Si el recurso que inserto no lo tenemos almacenado    
            except KeyError:
                httpCode = "HTTP/1.1 404 Not Found"
                htmlBody = "<html><body><h1>Recurso no disponible</h1></body></html>"
                return (httpCode, htmlBody)

            httpCode = "HTTP/1.1 302 Redirect"
            htmlBody = '<html><head><meta http-equiv="Refresh" content="3; url=' + \
    		 			URL_larga + '"/></head' + \
     					'<body>Redirigiendo a ' + URL_larga + ' en 3 segundos.</b></body></html>'
                        
        return (httpCode, htmlBody)

if __name__ == "__main__":
	testWebApp = contentApp("localhost", 1234)
