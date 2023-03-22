from string import octdigits
import time 						# Importamos modulo de tiempo

# Funcion booleana que determina si se debe reposicionar el sistema (transcurrio 1 hora desde el inicio o desde el ultimo reposicionamiento)
# Retorno = 1 --> Si se requiere reposicionar
# Retorno = 0 --> No se requiere reposicionar

def transcurrio1Hora():
	aux = False 					

	## Toma de fecha y hora
	anio 	= time.strftime("%y")	# Numero de año 2 digitos
	mes 	= time.strftime("%m")	# Mes en numero
	dia 	= time.strftime("%d")	# Dia del mes en numero
	hora 	= time.strftime("%H")	# Formato 24H
	minuto 	= time.strftime("%M")
	segundo = time.strftime("%S")

	DDMMAA = (int(dia)*10000)+(int(mes)*100)+(int(anio)*1)
	HHMMSS = (int(hora)*10000)+(int(minuto)*100)+(int(segundo)*1)
	
	try: #Intentamos leer archivo con modo Read
		f = open("/home/fauna/Desktop/camaraTrampa/reposicionamiento.txt", "r")
		DDMMAAtxt = int(f.readline())
		HHMMSStxt = int(f.readline())
		f.close()
		
		# Si el dia es el mismo y la diferencia  es mayor o igual a 1 hora, reposiciona
		# Si el dia es distinto y la diferencia entre la hora guardada y la hora final del dia, sumado a la  hora transcurrida en el nuevo dia es mayor a 1 hora, se reposiciona.
		# Si transcurrieron mas de 1 dia, se reposiciona, sin importar diferencia horaria.
		
		if (((DDMMAA == DDMMAAtxt) and (HHMMSS -HHMMSStxt >= 10000)) or ((DDMMAA - DDMMAAtxt == 10000) and (235959 - HHMMSStxt + HHMMSS >= 10000)) or (DDMMAA - DDMMAAtxt > 10000)):
				f = open("/home/fauna/Desktop/camaraTrampa/reposicionamiento.txt", "w")
				f.write(dia+mes+anio + "\n" + hora+minuto+segundo)
				f.close()
				aux = True

	except FileNotFoundError: #Si no existe archivo, se crear y  se carga la fecha y hora actual en formato DDMMAA /n HHMMSS
		f = open("/home/fauna/Desktop/camaraTrampa/reposicionamiento.txt", "w")
		f.write(dia+mes+anio + "\n" + hora+minuto+segundo)
		f.close()

		# En este caso no se reposiciona debido a que es la primer ocurrencia ya que el archivo no existe.

	return aux

def nombreArc(ubicacion):
	##toma de fecha y hora
	anio    = time.strftime("%y")  	# Numero de año 2 digitos
	mes     = time.strftime("%m")  	# Mes en numero
	dia     = time.strftime("%d")  	# Dia del mes en numero
	hora    = time.strftime("%H") 	# Formato 24H
	minuto  = time.strftime("%M")
	segundo = time.strftime("%S")

	return ubicacion+dia+'_'+mes+'_'+anio+'-'+hora+'_'+minuto+'_'+segundo  # Nombre del archivo
