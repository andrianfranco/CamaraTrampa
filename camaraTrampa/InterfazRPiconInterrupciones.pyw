#########################################################################################################################################################################################
#   Interfaz gráfica y control de cámara trampa 
#   Andrian Franco
#   09/11/22
################################################################### Importacion de librerias ############################################################################################

#Librerias para Interfaz Grafica
import sys
from Interfaz.Interfaz_ui import  Ui_MainWindow, QtWidgets  # Interfaz creada con PyQt5 en Qt Designer.
from PyQt5.QtWidgets      import QApplication, QMainWindow  # todos los widgets de qt
from PyQt5.QtCore         import QDate, QTime               # Widgets de tiempo

# Librerias de Raspberry
import shutil                                               # Calculo de almacenamiento
import time
from time import sleep                                      # Uso de delay             
import RPi.GPIO as GPIO                                     # Pines GPIO de Raspberry Pi
from picamera import PiCamera                               # Camara de Raspberry pi   
import errno 		                                        # Constantes de valores asignados en caso de varias condiciones de error.

#Librerias propias
import Camara.captura         as cap                        # Camara indica el paquete(directorio) desde donde se extrae el modulo.
import Deteccion.deteccion    as det
import Posicion.posicion      as pos
import Posicion.tiempo        as time2	
import Interfaz.datosInterfaz as datos

# Librerias para operaciones con directorios
import os, sys, subprocess                                  # Explorador de archivos
import glob                                                 # conteo de elementos en directorio

# Librerias para imagen en tiempo real
from PyQt5.QtCore       import QThread, Qt                  # Uso de subprocesos que se ejecuten en paralelo al programa principal sin congelar la interfaz.
from PyQt5.QtGui        import QImage, QPixmap
from PyQt5.QtCore       import pyqtSignal

# Librerias para muestra de video en tiempo real 
import numpy as np
from PIL import Image
from numpy import asarray
from io import BytesIO

# Librerias para envio de gmail
from email.message import EmailMessage
import smtplib

# Librerias de tiempo 
import datetime as dt

###################################################################################### Declaracion de variables globales y locales (comentadas) ########################################################################################                                                                                                                                                                                     #

# Directorios
path_CyG              = "/home/fauna/Desktop/camaraTrampa/CyG"               # Path inicial de capturas y grabaciones
path_CyG_Diurnas      = "/home/fauna/Desktop/camaraTrampa/CyG/Diurnas"       # Path de capturas y grabaciones diurnas         
path_CyG_Nocturnas    = "/home/fauna/Desktop/camaraTrampa/CyG/Nocturnas"     # Path de capturas y grabaciones nocturnas
path_CyG_Aux          = path_CyG_Diurnas                                     # Path auxiliar para variar segun estado de iluminacion nocturna. Estado inicial = Capturas diurnas

pathReestablecimiento = "/home/fauna/Desktop/camaraTrampa/"   
pathAlmacenamiento    = "/media/fauna/"

# Datos envio de correo 
#remitente    = "faunaraspberrypi@gmail.com"             # Emails para aviso de almacenamiento lleno 
#destinatario = "julian.sabattini@fca.uner.edu.ar"
#mensaje      = "¡Almacenamiento proximo a llenarse!"    # Mensaje a enviar
#auxGmail     = False                                    # Variable para envio de email solo en la primer lectura de almacenamiento lleno

# Variables para interfaz
#resImagen = "8 MP - 16:9"                              # Resolucion de imagen y relacion de aspecto
#resVideo  = "1080p"                                    # Resolucion de video          
#cantCapturasDiurnasW      = 1                          # Cantidad de capturas y grabaciones en directorios
#cantGrabacionesDiurnasW   = 2
#cantCapturasNocturnasW    = 1
#cantGrabacionesNocturnasW = 1
#cantCapturas                           
#cantGrabaciones
#nombreArc  = 'imagen1.jpg'                             # Nombre de archivos para capturas y grabaciones
subproceso = False                                      # Estado de subproceso para cierre de aplicacion
ubicacionEquipo  = "Ubicacion predeterminada"           # Valor predeterminado para uso de leyenda sin seteo de ubicacion
estadoFechayhora = False                                # Bandera para determinar cambio de hora

# Variables de sistema de posicionamiento      
posicionPIR  = 0                                        # var. entera con valores 0/1/2/3/4, indica posicion segun disposicion de pirs, o 0 si no hay deteccion. 
#auxUltimaPos = 0                                       # variable auxiliar con ultima posicion sensada

# Variables para configuracion de camara
#isoDia   = 100                                         # En 0 elige de manera automatica el iso entre 100 y 800 de acuerdo de la luz.
#isoNoche = 600                                         # Iso maximo permitido.
#obturadorDia   = 500                                   # Velocidad maxima de obturacion en us para congelar movimiento de dia (Para congelar el movimiento obturadorDia < 5000 us)
#obturadorNoche = 300000                                # Velocidad maxima de obturacion en us para congelar movimiento de noche
#estadoIluminacion = False                              # False: Iluminacion desactivada - Dia / True: Iluminacion Activada - Noche
#estadoInicial     = True                               # Realiza lectura y cambia estado de iluminacion sin importar el valor anterior (auxUltimoVal)
#auxUltimoVal                                           # Variable auxiliar con ultimo estado de iluminacion nocturna

#Variables para captura de imagen y video
duracion = 1                                            # Duracion de video en segundos
rhi = 1920                                              # Resolucion horizontal de imagen
rvi = 3280                                              # Resolucion vertical   de imagen
rhv = 2464                                              # resolucion horizontal de video
rvv = 1080                                              # resolucion vertical   de video
fps = 0.2                                               # cuadros por segundo   de video
estadoLeyenda = False                                   # Variable para leyenda en imagen y video
nroCapturas = 1                                         # Variable para capturas multiples
#labelIluminacion = "D"                                 # Identificador para capturas y grabaciones: "D" para diurnas y "N" para nocturnas

############################################################# Declaración y configuracion de pines  #####################################################################
'''NO USAR PIN 3 y 5 como entradas '''

# Pines de iluminacion
pinHabilitacionLuz = 36
#pinGNDnano = 34
pinEstadoIluminacion = 32

# Pines de deteccion de movimiento 
pinPIR1 = 37
pinPIR2 = 35
pinPIR3 = 33
pinPIR4 = 31 

# Pines de motor paso a paso y fin de carrera
pinPaso 	       = 40                        # Pin Step o pas
pinDir 		       = 38                        # Pin DIR 
pinFinCarrera1     = 15                        # Pin fin de carrera 1 (Izquierdo)
#pin3v3FinCarrera1 = 17

pinSleep = 19

GPIO.setmode(GPIO.BOARD)                                # Usar la numeración de pines de la placa.
GPIO.setwarnings(False)                                 # Desactivamos avisos de puertos sin cerrar en el ultimo uso. 

# Configuracion de pines de iluminacion nocturna
GPIO.setup(pinHabilitacionLuz,GPIO.OUT)
GPIO.setup(pinEstadoIluminacion,GPIO.IN)

# deshabilitamos la iluminacion nocturna
GPIO.output(pinHabilitacionLuz, False)

# Configuracion de interrupcion en pin de estado de iluminacion con tiempo minimo entre llamados de 250ms.
GPIO.add_event_detect(pinEstadoIluminacion,GPIO.BOTH, bouncetime = 250)   # Paso de 0 a 1 y de 1 a 0 logico

# Configuracion de pines de deteccion de movimiento
GPIO.setup(pinPIR1,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pinPIR2,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pinPIR3,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pinPIR4,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)

# Configuracion de pines de motor para la posicion 
GPIO.setup(pinDir,GPIO.OUT)
GPIO.setup(pinPaso,GPIO.OUT)
GPIO.setup(pinFinCarrera1,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)

# Creamos objeto de cámara
camara = PiCamera() 
###################################################################################### Subproceso ###############################################################################################

class Worker1(QThread):                                 # Creamos clase Worker1, heredera de QThread
    ImageUpdate = pyqtSignal(QImage)                    # Señal emitida cuando se requiera que la clase Worker1 interactue con la clase MainWindow, pasando un objeto del tipo QImage al constuctor.
    
    def __init__(self,camRPi,treeWidget):
        QThread.__init__(self)
        self.cam = camRPi
        self.treeWidget = treeWidget      
          
    def run(self):                                      # Funcion de ejecucion
        self.ThreadActive = True                        # Bandera que indica estado del subproceso
        
        global pinPIR1, pinPIR2, pinPIR3, pinPIR4, pathAlmacenamiento, posicionPIR, pinDir, pinPaso, path_CyG_Diurnas, path_CyG_Nocturnas, path_CyG_Aux, rhi, rvi, rhv,rvv,fps, GPIO, CambioEstado ,pinEstadoIluminacion, nroCapturas, duracion, pinFinCarrera1, ubicacionEquipo, estadoLeyenda 

        # Variables locales
        auxUltimaPos = 0
        labelIluminacion = "D"
        auxGmail = False
        isoDia   = 100
        isoNoche = 800
        obturadorDia = 500
        obturadorNoche = 300000
        estadoIluminacion = False

        outputImg = np.zeros((256,144,3),np.uint8)
        
        # Asignamos path actual a path_CyH_Aux
        path_CyG_Aux = path_CyG_Diurnas

        # Rutina inicial para posicionar motor paso a paso.
        pos.reposicionar(GPIO,pinFinCarrera1, pinDir, pinPaso)
        
        # Configuracion de interrupcion en pines de deteccion de movimiento con tiempo minimo entre llamados de 1s para evitar rebotes de contacto (tiempo minimo grabacion de video + 1 segundo )
        GPIO.add_event_detect(pinPIR1,GPIO.FALLING, bouncetime = 15000)
        GPIO.add_event_detect(pinPIR2,GPIO.FALLING, bouncetime = 15000)
        GPIO.add_event_detect(pinPIR3,GPIO.FALLING, bouncetime = 15000)
        GPIO.add_event_detect(pinPIR4,GPIO.FALLING, bouncetime = 15000) 

        while self.ThreadActive:
            
            if GPIO.event_detected(pinEstadoIluminacion): # En el caso inicial estadoIluminacion = Falso (iluminacion apagada):
                                                          # Si se detecta cambio la iluminacion se enciende.
                                                          # si no se detecta, la iluminacion se mantiene apagada.
                estadoIluminacion = not estadoIluminacion
                CambioEstado = True
                
                if estadoIluminacion:
                    path_CyG_Aux = path_CyG_Nocturnas
                    labelIluminacion = "N"
                    
                else:
                    path_CyG_Aux = path_CyG_Diurnas
                    labelIluminacion = "D"
            
            if (estadoInicial or CambioEstado) and estadoIluminacion:                           # EstadoIluminacion = True --> Iluminacion encendida, se hizo de noche.
                cap.configuracionCamara(self.cam,estadoIluminacion, obturadorNoche, isoNoche,fps)
                CambioEstado = False
                estadoInicial = False
                sleep(2)                                                                        # Tiempo necesario para ajustar la ganancia del sensor y los tiempos de exposicion.

            elif (estadoInicial or CambioEstado) and (not estadoIluminacion):                   # EstadoIluminacion = False --> Iluminacion apagada, se hizo de dia.
                cap.configuracionCamara(self.cam,estadoIluminacion, obturadorDia, isoDia,fps)
                CambioEstado = False
                estadoInicial = False
                sleep(2)                                                                        # Tiempo necesario para ajustar la ganancia del sensor y los tiempos de exposicion.

            espacio = shutil.disk_usage(pathAlmacenamiento)
                
            # ¿Almacenamiento proximo a llenarse?    -->     No: Sigue normal  | Si: Retornar a la salida.                                     
            # Consideramos proximo a llenarse si el espacio ocupado es del 95% de la capacidad. 

            if ((espacio.used*100)/espacio.total) < 95:

                # Leemos si hubo un cambio de estado en las entradas de los sensores (Mediante interrupciones)
                posicionPIR = det.lecturaPIRs(GPIO,pinPIR1,pinPIR2,pinPIR3,pinPIR4)

                if posicionPIR != 0:
                    
                    # Iniciamos contador de tiempo
                    start = dt.datetime.now()

                    # Si en 1 segundos no se genera una nueva detección, ademas de la actual, se graba el video.
                    while (dt.datetime.now() - start).seconds < 5:
                        
                        if posicionPIR and posicionPIR != auxUltimaPos:
                            print("Posicion inicial: ", posicionPIR)
                                                  
                            # Posicionamos sistema y generamos nombre a asignar
                            pos.posicionar(GPIO,posicionPIR,pinDir,pinPaso)
                            nombreArc = time2.nombreArc(path_CyG_Aux)   
                            
                            # Realizamos las capturas necesarias en una misma posición 
                            for i in range(nroCapturas):
                                # Re contabilizamos cantidad de capturas y grabaciones
                                cantCapturas = len(glob.glob(path_CyG_Aux+"*.jpg"))
                                cap.captura(self.cam,rhi,rvi,nombreArc +"-("+ str(i+1) +")-"+labelIluminacion, estadoLeyenda, cantCapturas+1,ubicacionEquipo) 
                        
                            # Guardamos ultima posicion
                            auxUltimaPos = posicionPIR
                            
                        #Leemos si hubo un cambio de estado en las entradas de los sensores (Mediante interrupciones)
                        posicionPIR = det.lecturaPIRs(GPIO,pinPIR1,pinPIR2,pinPIR3,pinPIR4)

                        if posicionPIR and posicionPIR != auxUltimaPos:
                            start = dt.datetime.now()
                            #retornamos a posicion inicial
                            pos.retornoPosInit(GPIO,auxUltimaPos,pinDir,pinPaso) 
                            print("Reposicion: ", posicionPIR)

                    posicionPIR = auxUltimaPos
                    
                    # Una vez finalizada el seguimiento de objetivo y secuencia de imagenes, se graba el video. El nombre tomado sera el de la ultima secuencia de capturas.
                    cantGrabaciones = len(glob.glob(path_CyG_Aux+"*.h264"))
                    cap.grabacion(self.cam,duracion,rhv,rvv,fps,nombreArc+"-"+labelIluminacion, estadoLeyenda, cantGrabaciones+1,ubicacionEquipo) 
                    print("Grabacion de video")
                    pos.retornoPosInit(GPIO,posicionPIR,pinDir,pinPaso)
                    
                    # Actualizamos treeWidget de avistamientos
                    datos.addTopLevelRaiz(self.treeWidget,str(time.strftime("%d"))+"/"+str(time.strftime("%m"))+"/"+str(time.strftime("%Y")),str(time.strftime("%H"))+":"+str(time.strftime("%M"))+":"+str(time.strftime("%S")))

                    # Actualizamos cantidad de grabaciones y capturas
                    window.ui.twConfiguracionSeteada.topLevelItem(1).setText(1,str(len(glob.glob(path_CyG_Diurnas+"*.jpg"))))
                    window.ui.twConfiguracionSeteada.topLevelItem(2).setText(1,str(len(glob.glob(path_CyG_Diurnas+"*.h264"))))
                    window.ui.twConfiguracionSeteada.topLevelItem(3).setText(1,str(len(glob.glob(path_CyG_Nocturnas+"*.jpg"))))
                    window.ui.twConfiguracionSeteada.topLevelItem(4).setText(1,str(len(glob.glob(path_CyG_Nocturnas+"*.jpg"))))

                    self.reposicionar = time2.transcurrio1Hora()     
                    if self.reposicionar == True:
                        pos.reposicionar(GPIO,pinFinCarrera1, pinDir, pinPaso)
                    
                    posicionPIR = auxUltimaPos = 0
                    
            elif not auxGmail:
                    email = EmailMessage()
                    email["From"] = "faunaraspberrypi@gmail.com"
                    email["To"] = "julian.sabattini@fca.uner.edu.ar"
                    email["Subject"] = "Sistema de monitoreo de Fauna - Rasbperry Pi 3A+"
                    email.set_content("¡Almacenamiento proximo a llenarse!")
                    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
                    smtp.login("faunaraspberrypi@gmail.com", "yicfizilnxamrhtx")
                    smtp.sendmail("faunaraspberrypi@gmail.com", "julian.sabattini@fca.uner.edu.ar", email.as_string())
                    smtp.quit()

                    auxGmail = True
                    
            stream = BytesIO()
            self.cam.resolution = (rhv,rvv) #256,144    # Seteamos resolucion minima para transmision en vivo para aumentar velocidad de fotogramas por segundo.
            self.cam.capture(stream,'jpeg')
            stream.seek(0)
            imagen= Image.open(stream)
            outputImg = asarray(imagen)
            
            alto, ancho, canal = outputImg.shape
            bytesPorLinea = 3 * ancho                    
            ConvertToQTFormat = QImage(outputImg.data,ancho,alto,bytesPorLinea,QImage.Format_RGB888)
            Pic = ConvertToQTFormat.scaled(591,511, Qt.KeepAspectRatio) 
            self.ImageUpdate.emit(Pic)

    def stop(self):
        self.ThreadActive = False
        self.quit()
            
##################################################################### Clase de Ventana principal ################################################################################################

class MainWindow(QMainWindow):
    def __init__(self, parent=None):				    # Constructor.
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui=Ui_MainWindow()		                	# Invocamos Ventana principal (Interfaz.py)
        self.ui.setupUi(self)
        self.reestablecer()                             # Reestablecemos ultima configuración en caso de apagado inesperado del sistema. 
          
        ############################################################################# Captura de eventos #############################################################################
        # ComboBox y spinBox
        self.ui.cbResImagen.currentIndexChanged.connect(self.cambioConfig)    # Si cambia el estado del indice del Combo Box ResImagen,  se realizara la comprobacion para el encendido
        self.ui.cbResVideo.currentIndexChanged.connect(self.cambioConfig)     # Si cambia el estado del indice del Combo Box ResVideo,   se realizara la comprobacion para el encendido
        self.ui.sbDuracion.valueChanged.connect(self.cambioConfig)            # Si cambia el valor  del indice del Spin  Box sbDuracion, se realizara la comprobacion para el encendido
        self.ui.rbFechayhora.toggled.connect(self.fechayhora)
        self.ui.rbLeyenda.toggled.connect(self.leyenda)

        # Botones
        self.ui.pbCapturas.clicked.connect(self.capturas)                                                                         
        self.ui.pbEncender.clicked.connect(self.encender)
        self.ui.pbCerrar.clicked.connect(self.cerrar)
 
    #################################################################################### Funciones ######################################################################################   

    def leyenda(self):
        global estadoLeyenda
        if self.ui.rbLeyenda.isChecked():
            estadoLeyenda = True
        else:
            estadoLeyenda = False

    def fechayhora(self): 
        global estadoFechayhora  
        if self.ui.rbFechayhora.isChecked():
            self.ui.deFecha.setEnabled(True)
            self.ui.teHora.setEnabled(True)
            estadoFechayhora = True

        else:
            self.ui.deFecha.setEnabled(False)
            self.ui.teHora.setEnabled(False)

    # Funcion de reestablecimiento de configuracion en caso de apagado inesperado.
    def reestablecer(self): 
        global estadoLeyenda, ubicacionEquipo, pathReestablecimiento, estadoFechayhora
        if(datos.existeReestablecimiento(pathReestablecimiento)==True):
            self.ui.twConfiguracionSeteada.clear()
            auxIndexImg, auxIndexVid, auxIndexCapturas, duracionVid, estadoLeyenda, ubicacionEquipo, estadoFechayhora  = datos.reestablecerConfiguracion(pathReestablecimiento)
            self.ui.cbResImagen.setCurrentIndex(auxIndexImg)
            self.ui.cbResVideo.setCurrentIndex(auxIndexVid)
            self.ui.cbNroCapturas.setCurrentIndex(auxIndexCapturas)
            self.ui.sbDuracion.setValue(duracionVid)
            self.ui.rbLeyenda.setChecked(bool(estadoLeyenda))
            self.ui.leUbicacion.setText(ubicacionEquipo)

            if not bool(estadoFechayhora):
                self.encender()
            
            else: 
                self.ui.twConfiguracionSeteada.clear()
                self.ui.twAvistamientos.clear()
                self.ui.cbResImagen.setCurrentIndex(0)
                self.ui.cbResVideo.setCurrentIndex(0)
                self.ui.cbNroCapturas.setCurrentIndex(0)
                self.ui.sbDuracion.setValue(0)
                self.ui.rbLeyenda.setChecked(False)
                self.ui.leUbicacion.setText('')
                self.ui.rbFechayhora.setChecked(False)
                
                estadoFechayhora = False

                subprocess.run(["sudo", "systemctl", "start","systemd-timesyncd.service"])
                subprocess.run(["sudo", "timedatectl", "set-ntp","true"])

    # Comprobacion de cambios para activar boton encender
    def cambioConfig(self):
        if (self.ui.cbResImagen.currentText() != "" and self.ui.cbResVideo.currentText() != "" and int(self.ui.sbDuracion.value()) != 0):
            self.ui.pbEncender.setEnabled(True)
        else:
            self.ui.pbEncender.setEnabled(False)

    # Funcion de boton Capturas
    def capturas(self):
        global path_CyG
        if sys.platform == "win32":                     # Explorador de archivos para windows 
            os.startfile(path_CyG)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open" # Explorador de archivos para Linux o Mac
            subprocess.call([opener, path_CyG])

    # Funcion para conectar con la señal de activacion del subproceso
    def ImageUpdateSlot(self,Image):                            
        self.ui.lbVideo.setPixmap(QPixmap.fromImage(Image))

    # Funcion de boton encender
    def encender(self):                                                                             
        global camara, rhi, rvi, rhv, rvv, fps, duracion, path_CyG_Diurnas, path_CyG_Nocturnas, pathAlmacenamiento, estadoLeyenda, ubicacionEquipo, estadoFechayhora, nroCapturas, pathReestablecimiento
        
        # Escondemos boton encender ya que no se requiere
        self.ui.pbEncender.hide()
        
        # Deshabilitamos radioButtons de leyenda y configuracion de fecha y hora manual
        self.ui.rbLeyenda.setEnabled(False)
        self.ui.rbFechayhora.setEnabled(False)
        
        # Seteo manual de hora
        if estadoFechayhora:
            datos.cambioFechayHora(self.ui.deFecha,self.ui.teHora)

        # Tomamos resolucion de imagen y video configuradas y la duracion de este ultimo, la cantidad de capturas; y el estado de la leyenda y asignamos las resoluciones horizontales, verticales y fps correspondientes
        rhi, rvi, resImagen, indexImagen    = datos.getResImagen(self.ui.cbResImagen) 
        rhv, rvv, fps, resVideo, indexVideo = datos.getResVideo (self.ui.cbResVideo)     # Estas funciones retornan mas de 1 valor utilizando tuplas
        nroCapturas                         = datos.getCantCapturas(self.ui.cbNroCapturas)
        duracion                            = datos.getDuracion (self.ui.sbDuracion)
        estadoLeyenda                       = datos.getEstadoLeyenda(self.ui.rbLeyenda)
        ubicacionEquipo                     = datos.getUbicacionEquipo(self.ui.leUbicacion)
        estadoFechayhora                    = datos.getEstadoFechayHora(self.ui.rbFechayhora)

        # Guardamos configuracion en archivo de texto
        datos.setearConfiguracion(pathReestablecimiento,indexImagen,indexVideo,nroCapturas,duracion,estadoLeyenda, ubicacionEquipo, estadoFechayhora)

        # Seteamos fecha, hora, y configuracion establecida
        self.ui.deFecha.setDate(QDate(int(time.strftime("%Y")),int(time.strftime("%m")),int(time.strftime("%d")))) # Seteamos fecha de inicio en configuracion
        self.ui.teHora.setTime(QTime(int(time.strftime("%H")),int(time.strftime("%M")),int(time.strftime("%S"))))  # Seteamos hora  de inicio en configuracion

        # Consultamos dispositivo de almacenamiento USB
        paths = os.listdir(pathAlmacenamiento)
        cant = len(paths)

        # si existe un dispositivo de almacenamiento USB, cant = 1, sino cant = 0.
        if cant:
            pathAlmacenamiento  = "/media/fauna/"
            pathUSB=pathAlmacenamiento+paths[0]
        
        else:
            pathAlmacenamiento  = "/home/fauna/"
            pathUSB = pathAlmacenamiento + "Desktop/camaraTrampa"
            
        #Intentamos crear directorio CyG, si existe, no lo crea para evitar errores. 
        try:
            os.mkdir(pathUSB+'/CyG')
        except OSError as e:
            if e.errno !=errno.EEXIST:
                raise

        #Intentamos crear directorio Diurnas, si existe, no lo crea para evitar errores. 
        try:
            os.mkdir(pathUSB+'/CyG/'+'Diurnas')
        except OSError as e:
            if e.errno !=errno.EEXIST:
                raise

        #Intentamos crear directorio Nocturnas, si existe, no lo crea para evitar errores. 
        try:
            os.mkdir(pathUSB+'/CyG/'+'Nocturnas')
        except OSError as e:
            if e.errno !=errno.EEXIST:
                raise

        # asignamos path de capturas y grabaciones diurnas y nocturnas
        path_CyG_Diurnas    = pathUSB +'/CyG/Diurnas/'
        path_CyG_Nocturnas  = pathUSB +'/CyG/Nocturnas/'

        # Calculo de cantidad de archivos en directorio capturas y directorio grabaciones
        cantCapturasDiurnasW      = len(glob.glob(path_CyG_Diurnas+"*.jpg"))
        cantGrabacionesDiurnasW   = len(glob.glob(path_CyG_Diurnas+"*.h264"))
        cantCapturasNocturnasW    = len(glob.glob(path_CyG_Nocturnas+"*.jpg"))
        cantGrabacionesNocturnasW = len(glob.glob(path_CyG_Nocturnas+"*.h264"))

        # Tree Widget de configuracion seteada y Avistamientos      
        raiz1 = datos.addRaiz(self.ui.twConfiguracionSeteada,'Cámara','')

        datos.addRaiz(self.ui.twConfiguracionSeteada,'Cantidad de capturas diurnas'     ,str(cantCapturasDiurnasW)) # No asignamos retorno a ninguna variable porque no se requiere agregar hijos           
        datos.addRaiz(self.ui.twConfiguracionSeteada,'Cantidad de grabaciones diurnas'  ,str(cantGrabacionesDiurnasW))     
        datos.addRaiz(self.ui.twConfiguracionSeteada,'Cantidad de capturas nocturnas'   ,str(cantCapturasNocturnasW)) # No asignamos retorno a ninguna variable porque no se requiere agregar hijos           
        datos.addRaiz(self.ui.twConfiguracionSeteada,'Cantidad de grabaciones nocturnas',str(cantGrabacionesNocturnasW))     
                           
        # Agregamos hijos a raiz1
        datos.addHijo(raiz1,'Resolución imagen',resImagen)
        datos.addHijo(raiz1,'Resolución video',resVideo)
        datos.addHijo(raiz1,'Duración video',str(duracion))
        datos.addHijo(raiz1,'Capturas por deteccion',str(nroCapturas))
        datos.addHijo(raiz1,'Ubicacion', ubicacionEquipo)

        # Expandimos raices creadas
        self.ui.twConfiguracionSeteada.expandAll()
        self.ui.twAvistamientos.expandAll() 

        # Seteamos pin de habilitacion de iluminacion nocturna (Arduino Nano)
        GPIO.output(pinHabilitacionLuz, True)

        # Configuracion inicial de camara: Diurna
        cap.configInitCam(camara,rhi,rvi, 1000,0)

        sleep(2)                                        # Tiempo necesario para ajustar la ganancia del sensor y los tiempos de exposicion.

        # Creamos instancia de clase Worker1 para hacer un subproceso, la inciamos y actualizamos el video en tiempo real, en lbVideo
        self.Worker1 = Worker1(camara,self.ui.twAvistamientos)                               
        subproceso = True
        self.Worker1.start()                                   
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot) 

    # Funcion de boton cerrar
    def cerrar(self):
        global camara,subproceso, pinHabilitacionLuz
        if subproceso:
            # Finalizamos subproceso para video en vivo
            self.Worker1.stop()

        # Finalizamos el proceso de camaraTrampa
        GPIO.output(pinHabilitacionLuz, False)          # Deshabilitamos a Arduino Nano a encender iluminacion nocturna en caso de ser requerido
        if camara:
            camara.close()                          
        GPIO.cleanup()                                  # Cerramos los puertos para evitar errores y proteger RPI.
        
        # si existe archivo de reestablecimiento, se elimina ya que el sistema finalizo correctamente.
        if (datos.existeReestablecimiento(pathReestablecimiento)== True):   
            os.remove(pathReestablecimiento+"apagon.txt")
        
        subprocess.run(["sudo", "systemctl", "start","systemd-timesyncd.service"])
        subprocess.run(["sudo", "timedatectl", "set-ntp","true"])

    def closeEvent(self,event):
        global pinHabilitacionLuz
        GPIO.output(pinHabilitacionLuz, False)          # Deshabilitamos a Arduino Nano a encender iluminacion nocturna en caso de ser requerido
        
        subprocess.run(["sudo", "systemctl", "start","systemd-timesyncd.service"])
        subprocess.run(["sudo", "timedatectl", "set-ntp","true"])
###################################################################### Creacion de objeto de ventana principal ##################################################################################       

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())