from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
import subprocess

# BLOQUE DE FUNCIONES UTILIZADO PARA TOMA/CARGA DE DATOS Y CONFIGURACION DE INTERFAZ


# FUNCION UTILIZADA PARA TOMAR DATOS DE INTERFAZ

def getResImagen (widget):
    rhi=0
    rvi=0
    resImagen = "vacio"
    indexImg = 0

    if(widget.currentText() == "8 MP - 4:3"):
        rhi = 3280
        rvi = 2464
        resImagen = "8 MP - 4:3"
        indexImg = 1
    elif (widget.currentText() == "2 MP - 16:9"):
        rhi = 1920
        rvi = 1080
        resImagen = "2 MP - 16:9"
        indexImg = 2

    elif (widget.currentText() == "2 MP - 4:3"):
        rhi = 1640
        rvi = 1232
        resImagen = "2 MP - 4:3"
        indexImg = 3

    elif (widget.currentText() == "1.5 MP - 16:9"):
        rhi = 1640
        rvi = 922
        resImagen = "1.5 MP - 16:9"
        indexImg = 4

    elif (widget.currentText() == "0.9 MP - 16:9"):
        rhi = 1280
        rvi = 720
        resImagen = "0.9 MP - 16:9"
        indexImg = 5

    elif (widget.currentText() == "0.3 MP - 4:3"):
        rhi = 640
        rvi = 480
        resImagen = "0.3 MP - 4:3"
        indexImg = 6

    return rhi,rvi,resImagen, indexImg

def getResVideo (widget):
    rhv=0
    rvv=0
    fps = 0
    resVideo = "vacio"
    indexVideo = 0

    if(widget.currentText() == "1080p - 30fps"):
        rhv = 1920
        rvv = 1080
        fps = 30
        resVideo = "1080p - 30fps"
        indexVideo = 1

    elif(widget.currentText() == "720p - 60fps"):
        rhv = 1280
        rvv = 720
        fps = 60
        resVideo = "720p - 60fps"
        indexVideo = 2

    elif(widget.currentText() == "480p - 60fps"):
        rhv = 640
        rvv = 480
        fps = 60
        resVideo = "480p - 60fps"
        indexVideo = 3

    elif(widget.currentText() == "480p - 90fps"):
        rhv = 640
        rvv = 480
        fps = 90
        resVideo = "480p - 90fps"
        indexVideo = 4

    return rhv,rvv,fps,resVideo, indexVideo 

def getCantCapturas (widget):
    capturas = int(widget.currentText())
    return  capturas

def getDuracion (widget):
    duracion = widget.value()
    return duracion

def getEstadoLeyenda(widget):
    if widget.isChecked():
        leyenda = True
    else:
        leyenda = False
    return leyenda

def getUbicacionEquipo(widget):
    getUbicacionEquipo = widget.text()
    return getUbicacionEquipo

def getEstadoFechayHora(widget):
    if widget.isChecked():
        fechayhora = True
    else:
        fechayhora = False
    return fechayhora

def cambioFechayHora(widgetFecha,widgetHora):
    fecha   = widgetFecha.date().toString("dd-MM-yyyy")
    horario = widgetHora.time().toString("HH-mm-ss")

    dia  = fecha[:2]
    mes  = fecha[3:5]
    anio = fecha[6:]

    hora    = horario[:2]
    minuto  = horario[3:5]
    segundo = horario[6:]

    fechayhora = anio + "-" + mes + "-" + dia + " " + hora + ":" + minuto + ":" + segundo
    subprocess.run(["sudo", "systemctl", "stop","systemd-timesyncd.service"])
    subprocess.run(["sudo", "timedatectl", "set-ntp","false"])
    subprocess.run(["sudo", "timedatectl", "set-time",fechayhora])

# Funciones para agregar datos a Tree Widget
def addRaiz(widget,txtFila,txtColumna):
    raiz = QTreeWidgetItem(widget)
    raiz.setText(0,txtFila)
    raiz.setText(1,txtColumna)
    return raiz 
    
def addHijo(widget,txtFila,txtColumna):
    hijo = QTreeWidgetItem()
    hijo.setText(0,txtFila)
    hijo.setText(1,txtColumna)
    widget.addChild(hijo)

def addTopLevelRaiz(widget,txtFila,txtColumna):
    tlRaiz = QTreeWidgetItem()
    tlRaiz.setText(0,txtFila)
    tlRaiz.setText(1,txtColumna)
    widget.insertTopLevelItem(0,tlRaiz)

# FUNCIONES DE COMPROBACION DE CAMBIO DE ESTADO DE RESOLUCION IMAGEN, VIDEO Y DURACION

def CambioResImagen(resImagen,resVideo,duracion,pbEncender):
    if (resImagen.currentText() != "" and resVideo.currentText() != "" and int(duracion.value()) != 0):
        pbEncender.setEnabled(True)
    else:
        pbEncender.setEnabled(False)
def CambioResVideo(resImagen,resVideo,duracion,pbEncender):
    if (resImagen.currentText() != "" and resVideo.currentText() != "" and int(duracion.value()) != 0):
        pbEncender.setEnabled(True)
    else:
        pbEncender.setEnabled(False)
def CambioDuracion(resImagen,resVideo,duracion,pbEncender):
    if (resImagen.currentText() != "" and resVideo.currentText() != "" and int(duracion.value()) != 0):
        pbEncender.setEnabled(True)
    else:
        pbEncender.setEnabled(False)

# FUNCIONES UTILIZADAS EN CASO DE APAGADO INESPERADO.
def setearConfiguracion(rutaArchivo,indexImg,indexVid, indexCapturas,duracionV, leyenda, ubicacionEquipo, fechayhora):       # Una vez encendido el sistema se crea un registro con la configuracion actual.
	f = open(rutaArchivo+"apagon.txt", "w")
	f.write(str(indexImg) + "\n" + str(indexVid) + "\n" + str(indexCapturas) + "\n" + str(duracionV) + "\n" + str(leyenda)+ "\n" +  str(ubicacionEquipo)+ "\n" + str(fechayhora))
	f.close()

def reestablecerConfiguracion(rutaArchivo):             # En caso de apagon, se reestablecere la configuracion almacenada en el archivo de texto.
    
    f = open(rutaArchivo+"apagon.txt", "r")
    indexImg  = int(f.readline())
    indexVid  = int(f.readline())
    indexCapturas = int(f.readline())
    duracionV = int(f.readline())
    estadoLeyenda =bool(f.readline())
    ubicacionEquipo = str(f.readline())
    estadoFechayHora = bool(f.readline())

    f.close()
		
    return indexImg,indexVid,indexCapturas,duracionV,estadoLeyenda, ubicacionEquipo, estadoFechayHora

def existeReestablecimiento(rutaArchivo):
    aux = False                                         # Variable booleana que retorna existencia de archivo

    try: 
        f = open(rutaArchivo+"apagon.txt", "r")
        f.close()
        aux = True
    except FileNotFoundError:
        aux = False
    
    finally:
        return aux