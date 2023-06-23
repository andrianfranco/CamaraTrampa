# Lectura de estados de sensores PIR
# El funcionamiento presenta logica invertida por lo que se obtiene una deteccion cuando la entrada indica False.
#import RPi.GPIO as GPIO 

def lecturaPIRs(GPIO,pinPIR1,pinPIR2,pinPIR3,pinPIR4):
										
	if GPIO.event_detected(pinPIR1):    
		posicionPIR = 1

	elif GPIO.event_detected(pinPIR2):  
		posicionPIR = 2
	
	elif GPIO.event_detected(pinPIR3):  
		posicionPIR = 3
		
	elif GPIO.event_detected(pinPIR4):    
		posicionPIR = 4

	else:
		posicionPIR = 0
	
	return posicionPIR
