from unittest.mock import CallableMixin
#from picamera import PiCamera
#from time import sleep
from fractions import Fraction
import time 											# Importamos modulo de tiempo
import datetime as dt
														# Como utilizaremos camara NoIR 8MP, no es necesario una configuracion nocturna y una diurna

import cv2
import numpy as np
from picamera import Color

def configInitCam(cam,rhi,rvi,obturadorDia,isoDia):                     
	cam.resolution = (rhi,rvi) 
	cam.framerate = 30
	cam.sensor_mode = 0
	cam.shutter_speed = obturadorDia	
	cam.video_stabilization = False
	cam.exposure_compensation = 0	            		# Compensacion de exposicion: -25 0 25  Valor normal = 0
	cam.exposure_mode='auto'			        		# Al usarlo en off se anula la configuracion del iso
	cam.iso = isoDia					        		# 0 = auto; 100 y 200 para mucha luz; 400 y 800 para poca luz               

	cam.rotation	= 90
	cam.sharpness	= 0		                    		# Nitidez: 	 -100 a 100		Valor normal = 0
	cam.contrast	= 0		                    		# Contraste: -100 a 100		Valor normal = 0
	cam.saturation	= 0		                    		# Color: 	 -100 a 100		Valor normal = 0     	// Para modo noche en -100 (greyscale)
	cam.brightness	= 50	                    		# Brillo: 	 	0 a 100		Valor normal = 50

def configuracionCamara(cam,estadoIluminacion,obturador, iso):
	
	cam.shutter_speed = obturador
	cam.iso = iso
	
	if estadoIluminacion:
		cam.saturation = -100
		cam.awb_mode = 'off'
		cam.awb_gains = 8
		cam.image_effect = 'denoise'

	else:
		cam.saturation = 0
		cam.awb_mode = 'auto'
		cam.image_effect = 'none'

def captura(cam,rhi,rvi,nombreArc, estadoLeyenda, cantCapturas,ubicacionEquipo):

	# Configuracion de camara para captura de imagen
	cam.resolution=(rhi,rvi)

	# Captura de imagen		
	cam.capture(nombreArc+'.jpg')
		
	# Agregamos leyenda
	if estadoLeyenda: 
		# Lectura de imagen con OpenCv
		img = cv2.imread(nombreArc+'.jpg')
		
		#Creamos barra negra para texto
		cv2.line(img, (0,int(rvi-rvi/98)),(rhi,int(rvi-rvi/98)),(0,0,0),int(rvi/16)) #Parametros: Imagen, punto inicial xy, punto final xy, color BGR, grosor de linea en pixeles
		
		# Creacion de etiqueta
		texto =  ubicacionEquipo + ' - ' + dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + ' - Captura Nro.' + str(cantCapturas) 	
		ubicacion = (40,int(rvi-rvi/61))
		font = cv2.FONT_HERSHEY_COMPLEX
		tamLetra = rvi/1642
		colorLetra = (255,255,255)
		grosorLetra = int(rvi/1232)
		
		# Escritura de imagen
		cv2.putText (img, texto, ubicacion, font, tamLetra, colorLetra, grosorLetra)
		
		#Guardamos imagen
		cv2.imwrite(nombreArc+'.jpg', img)
	
def grabacion(camara,duracion,rhv,rvv,fps,nombreArc, estadoLeyenda, cantGrabaciones, ubicacionEquipo): # Recprdar que grabacion de video no permite sensor_mode=3, ese se utiliza para el "Modo Noche" que programe.
	
	# Configuracion de camara para grabacion de video
	camara.resolution = (rhv,rvv)	
	camara.framerate = fps
	
	if estadoLeyenda:
			
		camara.annotate_background = Color("black")
		camara.annotate_text_size = 60
		
		# Grabacion de video 
		camara.annotate_text = ubicacionEquipo + ' - ' + dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + ' - Grabacion Nro.' + str(cantGrabaciones) 
		camara.start_recording(nombreArc+'.h264')
		
		start = dt.datetime.now()
		while (dt.datetime.now() - start).seconds < duracion:
			camara.annotate_text = 'Ubicacion 1 - ' + dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + ' - Grabacion Nro.' + str(cantGrabaciones) 
			camara.wait_recording(0.2) 
			
		camara.stop_recording() 
		camara.annotate_text = ' '
		camara.annotate_background = False
	
	else:
		camara.start_recording(nombreArc+'.h264')
		camara.wait_recording(duracion)
		camara.stop_recording()
		
# En la siguiente funcion se puede ajustar el tiempo de obturacion para tiempos mayores a 100000us, mejorando la cantidad de luz de la imagen pero no permite obtener movimiento congelado.
# Ademas se requiere un delay o tiempo muerto para ajustar la ganancia del sensor y los tiempos de exposicion lo cual nos haria perder el animal en movimiento.
def capturaNocturna (camara,rhi,rvi, nombrearc):																
	camara.resolution=(rhi,rvi) 
	camara.sensor_mode=3 								# Forzamos modo 3 de sensor para exposiciones largas
														# Modo 0 elige el modo de acuerdo a la resolucion y el framerate solicitado.
														# Modo 1 permite hasta   100000us (0.1s)
														# Modo 2 permite hasta   100000us (0.1s)
														# Modo 3 permite hasta  6000000us (6s)
														# Modo 4 permite hasta 	100000us (0.1s)
														# Modo 5 permite hasta 	33000us (0.033s)
														# Modo 6 permite hasta 	23000us (0.023s)
														# Modo 7 permite hasta 	16000us (0.016s)

	camara.framerate=Fraction(2,1)						# Seteamos un freamrate de 2 a 1/6 fps, y una velocidad de 
														# disparo de 0.1 a 6s con un iso de 800 para maxima ganancia
	camara.shutter_speed = 50000 						# Valor minimo visible = 100000 Valor maximo del modulo = 6000000
	camara.iso = 800
	
	#cam.awb_mode = 'off'								# Aumento de ganancia en modo off de ganancia de blancos. 
	#cam.awb_gains = 6									# Se obtiene una imagen mas clara pero violeta lo cual no nos sirve

	sleep(2)											# Tiempo necesario para ajustar la ganancia del sensor y los tiempos de exposicion.
	camara.capture(nombreArc+'.jpg')