import time   							# Uso de delay 

#DH/DAH	= Direccion horaria / antihoraria
#EHA	= Eje hacia arriba

#Cada paso recorre 1.8° -> 200 * 1.8° = 360°ca

## Segun casos de prueba
#  Posicion inicial a Posicion 1 = -90° + -45° = -135°/1.8° = 75 pasos DAH EHA
#  Posicion inicial a Posicion 2 = 		  -45° = -45°/1.8° 	= 25 pasos DAH EHA
#  Posicion inicial a Posicion 3 = 		   45° =  45°/1.8° 	= 25 pasos  DH EHA
#  Posicion inicial a Posicion 4 =  90° +  45° =  135°/1.8° = 75 pasos  DH EHA

nPasos		 = 0            						# Número de pasos del motor. 
microPausa 	 = 0.025 # 0.015        				# Pausa por paso en segundos.   tiempo minimo, 0.005
tiempoMuerto = 0.6	 # 0.35							# Tiempo muerto para evitar perdida de pasos al cambiar de direccion de giro
finCarrera1  = True									# Estado de sensor de fin de carrera.

#Funcion para posicionar/reposicionar el sistema en la posicion inicial

def reposicionar (GPIO, pinFinCarrera1, pinDir, pinPaso):

		finCarrera1 = GPIO.input(pinFinCarrera1)
		if (finCarrera1 == True):						# Si finCarrera1 no esta presionado
			GPIO.output(pinDir, 1)          			# Direccion 1, DAH EHA - giramos en sentido antihorario hasta ser presionado
			
			while (finCarrera1 == True):
				GPIO.output(pinPaso, True)
				time.sleep(microPausa)
				GPIO.output(pinPaso, False)
				time.sleep(microPausa)
				finCarrera1 = GPIO.input(pinFinCarrera1)# Si se presiona el sensor, frena el motor
			
			time.sleep(tiempoMuerto)
											
		GPIO.output(pinDir, 0)          			# Direccion 0, DH EHA - Cambiamos direccion de giro
		nPasos = 100								# 100 pasos de 1.8° recorre 180° (Giramos hacia el extremo derecho).
		for x in range(0,nPasos):
			GPIO.output(pinPaso, True)
			time.sleep(microPausa)
			GPIO.output(pinPaso, False)
			time.sleep(microPausa)
			
		time.sleep(tiempoMuerto)
		print("Reposicion")

# Funcion para posicionar el sistema en la posicion del sensor PIR activado 

def posicionar (GPIO,posicionPIR, pinDir, pinPaso):

	if (posicionPIR == 1): 								# pInit a P1 y a pInit
		nPasos = 75
		GPIO.output(pinDir, 1)          				# Direccion 1, DAH EHA
		for x in range(0,nPasos):
			GPIO.output(pinPaso, True)
			time.sleep(microPausa)
			GPIO.output(pinPaso, False)
			time.sleep(microPausa)

	elif (posicionPIR == 2):							# pInit a P2 y a pInit	
		nPasos = 25
		GPIO.output(pinDir, 1)          				# Direccion 1, DAH EHA
		for x in range(0,nPasos):
			GPIO.output(pinPaso, True)
			time.sleep(microPausa)
			GPIO.output(pinPaso, False)
			time.sleep(microPausa)

	elif (posicionPIR == 3): 							# pInit a P3 y a pInit
		nPasos = 25
		GPIO.output(pinDir,0)           				# Direccion 0, DH EHA
		for x in range(0,nPasos):
			GPIO.output(pinPaso, True)
			time.sleep(microPausa)
			GPIO.output(pinPaso, False)
			time.sleep(microPausa)

	elif (posicionPIR == 4):							# pInit a P4 y a pInit
		nPasos = 75
		GPIO.output(pinDir,0)           				# Direccion 0, DH EHA
		for x in range(0,nPasos):
			GPIO.output(pinPaso, True)
			time.sleep(microPausa)
			GPIO.output(pinPaso, False)
			time.sleep(microPausa)
	
	time.sleep(tiempoMuerto)							# Tiempo muerto para evitar perdida de pasos al cambiar de direccion de giro y para que la camara no vibre al tomar fotos

# Funcion para retornar desde la posicion del sensor PIR activado a la posicion inicial. 

def retornoPosInit(GPIO, posicionPIR, pinDir, pinPaso):

	if (posicionPIR == 1): 								# pInit a P1 y a pInit
		nPasos = 75                    	
		GPIO.output(pinDir,0)           				# Direccion 0, DH EHA
		for x in range(0,nPasos):
			GPIO.output(pinPaso, True)
			time.sleep(microPausa)
			GPIO.output(pinPaso, False)
			time.sleep(microPausa)

	elif (posicionPIR == 2):							# pInit a P2 y a pInit	
		nPasos = 25     	
		GPIO.output(pinDir,0)           				# Direccion 0, DH EHA
		for x in range(0,nPasos):
			GPIO.output(pinPaso, True)
			time.sleep(microPausa)
			GPIO.output(pinPaso, False)
			time.sleep(microPausa)

	elif (posicionPIR == 3): 							# pInit a P3 y a pInit
		nPasos = 25
		GPIO.output(pinDir, 1)          				# Direccion 1, DAH EHA
		for x in range(0,nPasos):
			GPIO.output(pinPaso, True)
			time.sleep(microPausa)
			GPIO.output(pinPaso, False)
			time.sleep(microPausa)

	elif (posicionPIR == 4):							# pInit a P4 y a pInit
		nPasos = 75
		GPIO.output(pinDir, 1)          				# Direccion 1, DAH EHA
		for x in range(0,nPasos):
			GPIO.output(pinPaso, True)
			time.sleep(microPausa)
			GPIO.output(pinPaso, False)
			time.sleep(microPausa) 

	time.sleep(tiempoMuerto)
