from PIL import ImageGrab, ImageFont, Image, ImageTk
from libretranslatepy import LibreTranslateAPI
import tkinter as tk
from tkinter import scrolledtext 
import pytesseract
import os
import idiomas
import datetime
import datos

#Constantes especiales:
UMBRAL_DE_CONFIANZA = 10
PROFUNDIDAD_DE_BUSQUEDA_DE_PARRAFOS = 10
UMBRAL_DE_SUPERPOSICION_DE_PARRAFOS = 0.85

#Barra de progreso:
COLOR_BARRA_DE_PROGRASO = "lime green"
COLOR_BORDE_BARRA_DE_CARGA = "black"
TAM_TEXTO_BARRA_DE_PROGRESO = 16

#Checkpoints barra de progreso:
PROGRESO_CAPTURA_DE_DATOS = 0.01
PROGRESO_LIMPIA_DATOS_CAPTURADOS = 0.03
PROGRESO_REORGANIZANDO_LINEAS_INICIO = 0.05
PROGRESO_REORGANIZANDO_LINEAS_FIN = 0.3
PROGRESO_ELIMINANDO_DETECCIONES_ERRONEAS_INICIO = 0.31
PROGRESO_ELIMINANDO_DETECCIONES_ERRONEAS_FIN = 0.345
PROGRESO_RECALCULANDO_AREAS_DE_LINEAS_INICIO = 0.35
PROGRESO_RECALCULANDO_AREAS_DE_LINEAS_FIN = 0.355
PROGRESO_DETECTANDO_PARRAFOS_INICIO = 0.36
PROGRESO_DETECTANDO_PARRAFOS_FIN = 0.365
PROGRESO_AGRUPANDO_PARRAFOS_INICIO = 0.37
PROGRESO_AGRUPANDO_PARRAFOS_FIN = 0.375
PROGRESO_TRADUCIENDO_INICIO = 0.38
PROGRESO_TRADUCIENDO_FIN = 0.98
PROGRESO_DIBUJANDO = 0.99

#Debug
DEBUG_BORDES = False
DEBUG_LIMPIA_DATOS_CAPTURADOS = False
DEBUG_CALCULAR_POINTSIZE = False  
DEBUG_REORGANIZAR_LINEAS = False
DEBUG_FALSOS_POSITIVOS = False
DEBUG_AJUSTAR_LINEAS = False
DEBUG_COMBINAR_PARRAFOS = False

#Conexcion al servidor interno
LT = LibreTranslateAPI("http://127.0.0.1:50000")

#Establece la ruta del OCR
pytesseract.pytesseract.tesseract_cmd = os.environ["ProgramFiles"] + r'\Tesseract-OCR\tesseract'

class Traductor(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.create_image(kwargs.get('width'), kwargs.get('height'), image=ImageTk.PhotoImage(Image.new('RGBA', (kwargs.get('width'), kwargs.get('height')), (0, 0, 0, 0))))
        self.borde_canvas = self.create_rectangle(0, 0, kwargs.get('width')-1, kwargs.get('height')-1)
        self.ultima_actualizacion = datetime.datetime.now()
        self.rect1 = None
        self.rect2 = None
        self.rectfill1 = None
        self.rectfill2 = None
        self.descripcion_barra_de_carga = None
        self.permitir_barra_de_carga = False
        self.traduciendo = tk.BooleanVar()
        self.traduciendo.set(False)

        
    #Actualiza el borde del canvas
    def actualizar_borde(self, e):
        self.config(width=e.width-20, height=e.height-42)
        self.delete(self.borde_canvas)
        self.borde_canvas = self.create_rectangle(0, 0, e.width-20-1, e.height-42-1)

    #Limpia el canvas
    def limpiar(self):
        self.delete("all")
        self.borde_canvas = self.create_rectangle(0, 0, self.winfo_width()-1, self.winfo_height()-1)

    #Dibuja el texto que describe la tarea actual
    def dibujar_descripcion_barra_de_carga(self, texto: str):
        x = self.winfo_width()/2
        y = self.winfo_height()-60
        self.descripcion_barra_de_carga = [
            self.create_text(x+1, y+1, text=texto, font=f'arial {TAM_TEXTO_BARRA_DE_PROGRESO}', fill=COLOR_BORDE_BARRA_DE_CARGA, anchor="center"),
            self.create_text(x-1, y-1, text=texto, font=f'arial {TAM_TEXTO_BARRA_DE_PROGRESO}', fill=COLOR_BORDE_BARRA_DE_CARGA, anchor="center"),
            self.create_text(x+1, y-1, text=texto, font=f'arial {TAM_TEXTO_BARRA_DE_PROGRESO}', fill=COLOR_BORDE_BARRA_DE_CARGA, anchor="center"),
            self.create_text(x-1, y+1, text=texto, font=f'arial {TAM_TEXTO_BARRA_DE_PROGRESO}', fill=COLOR_BORDE_BARRA_DE_CARGA, anchor="center"),
            self.create_text(x, y, text=texto, font=f'arial {TAM_TEXTO_BARRA_DE_PROGRESO}', fill=COLOR_BARRA_DE_PROGRASO, anchor="center")
        ]

    #actualiza el texto
    def actualizar_descripcion_barra_de_carga(self, texto: str):
        self.eliminar_descripcion_barra_de_carga()
        self.dibujar_descripcion_barra_de_carga(texto)

    #elimina el texto
    def eliminar_descripcion_barra_de_carga(self):
        for capa in self.descripcion_barra_de_carga:
            self.delete(capa)

    #inicializala barra de progreso
    def iniciar_barra_de_progreso(self):
        self.rect2 = self.create_rectangle(self.winfo_width()/4, self.winfo_height()-40,self.winfo_width()*3/4, self.winfo_height()-20, outline =COLOR_BORDE_BARRA_DE_CARGA,width = 4)
        self.rect1 = self.create_rectangle(self.winfo_width()/4, self.winfo_height()-40,self.winfo_width()*3/4, self.winfo_height()-20, outline =COLOR_BARRA_DE_PROGRASO,width = 2)
        progreso = 0.01
        self.rectfill2 = self.create_rectangle(self.winfo_width()/4+5-1, self.winfo_height()-40+5-1,((self.winfo_width()*3/4-5+1)-(self.winfo_width()/4+5-1))*progreso+(self.winfo_width()/4+5-1),self.winfo_height()-20-5+1, fill="Black")
        self.rectfill1 = self.create_rectangle(self.winfo_width()/4+5, self.winfo_height()-40+5,((self.winfo_width()*3/4-5)-(self.winfo_width()/4+5))*progreso+(self.winfo_width()/4+5),self.winfo_height()-20-5, fill=COLOR_BARRA_DE_PROGRASO)
        self.dibujar_descripcion_barra_de_carga("Iniciando")
        self.permitir_barra_de_carga = True
        print("Progreso " + str(int(progreso*100)) + f"% Fase: Iniciando")

    #actualiza el progreso mostrado en la barra
    def actualizar_barra_de_progreso(self, progreso: float, fase: str):
        print("Progreso " + str(int(progreso*100)) + f"% Fase: "  + fase)
        if self.actualizar_checktime():
            if self.permitir_barra_de_carga:
                self.delete(self.rect2)
                self.delete(self.rect1)
                self.delete(self.rectfill1)
                self.delete(self.rectfill2)
                self.rect2 = self.create_rectangle(self.winfo_width()/4, self.winfo_height()-40,self.winfo_width()*3/4, self.winfo_height()-20, outline =COLOR_BORDE_BARRA_DE_CARGA,width = 4)
                self.rect1 = self.create_rectangle(self.winfo_width()/4, self.winfo_height()-40,self.winfo_width()*3/4, self.winfo_height()-20, outline =COLOR_BARRA_DE_PROGRASO,width = 2)
                self.rectfill2 = self.create_rectangle(self.winfo_width()/4+5-1, self.winfo_height()-40+5-1,((self.winfo_width()*3/4-5+1)-(self.winfo_width()/4+5-1))*progreso+(self.winfo_width()/4+5-1),self.winfo_height()-20-5+1, fill="Black")
                self.rectfill1 = self.create_rectangle(self.winfo_width()/4+5, self.winfo_height()-40+5,((self.winfo_width()*3/4-5)-(self.winfo_width()/4+5))*progreso+(self.winfo_width()/4+5),self.winfo_height()-20-5, fill=COLOR_BARRA_DE_PROGRASO)
                self.actualizar_descripcion_barra_de_carga(fase)
                self.update()

    #elimina la barra de carga
    def eliminar_barra_de_progreso(self):
        self.permitir_barra_de_carga = False
        self.delete(self.rect1)
        self.delete(self.rect2)
        self.delete(self.rectfill1)
        self.delete(self.rectfill2)
        self.eliminar_descripcion_barra_de_carga()
        self.update()

    #determina Si ha pasado suficiente tiempo antes de volver a actualizar la interfaz
    def actualizar_checktime(self):
        hora_actual = datetime.datetime.now()
        if self.ultima_actualizacion + datetime.timedelta(milliseconds=200) < hora_actual:
            self.ultima_actualizacion = hora_actual
            return True
        return False

    #Verifica si las palabras detectada complen con el humbral minimo de confianza
    def umbral(self, c):
        if float(c) < UMBRAL_DE_CONFIANZA:
            return False
        return True

    #Dibuja exto en el canvas en la posición deseada
    def texto_resaltado(self, texto: str, x: int, y: int, tam: int):
        self.create_text(x+1, y+1, text=texto, font=f'arial {tam}', fill="grey80", anchor="nw")
        self.create_text(x-1, y-1, text=texto, font=f'arial {tam}', fill="grey80", anchor="nw")
        self.create_text(x+1, y-1, text=texto, font=f'arial {tam}', fill="grey80", anchor="nw")
        self.create_text(x-1, y+1, text=texto, font=f'arial {tam}', fill="grey80", anchor="nw")
        self.create_text(x, y, text=texto, font=f'arial {tam}', fill="black", anchor="nw")
    
    #Muestra los bordes de las líneas y palabras mientras se procesan, función debug
    def mostrar_bordes(self, escala:float, lineas_extraidas: list[datos.Linea]):
        for linea in lineas_extraidas:
            self.create_rectangle((linea.x0)/escala, (linea.y0)/escala, (linea.x1)/escala, (linea.y1)/escala, outline ="red",width = 2)

            for p in linea.palabras_linea_original:
                self.create_rectangle((p.x0)/escala, (p.y0)/escala, (p.x1)/escala, (p.y1)/escala, outline ="blue",width = 1)
                self.texto_resaltado(p.Palabra_original, (p.x0)/escala, (p.y0)/escala, int((p.tamaño_letras)/escala))

    #Para es string de datos recibido del OCR a una estructura de datos más fácil de manipular
    def separar_resultado_OCR_en_lineas(self, resultado_OCR: str):

        #separa el str en líneas y luego en columnas, entonces elimina el primer y último elemento
        lineas = resultado_OCR.split("\n")
        cajas = []
        for linea in lineas:
            aux = linea.split("\t")
            cajas.append(aux)
        cajas.pop(0)
        cajas.pop()
        
        #Agrupa las palabras en líneas según corresponda y transcribe el str a una estructura ordenada
        Lineas: list[datos.Linea] = []
        for c in cajas:
            if c[0] == '4':
                Lineas.append(datos.Linea(x0=int(c[6]), y0=int(c[7]), x1=int(c[6])+int(c[8]), y1=int(c[7])+int(c[9]), parrafo_original=int(c[3]), identificador_de_division=-1))
            elif c[0] == '5':
                if self.umbral(c[10]):
                    Lineas[-1].palabras_linea_original.append(datos.Palabra(x0=int(c[6]), y0=int(c[7]), x1=int(c[6])+int(c[8]), y1=int(c[7])+int(c[9]), confianza=float(c[10]), Palabra_original=c[11]))
        
        return Lineas
    
    #Elimina palabras compuestas unicamente por espacios en blanco y las líneas que no contengan palabras
    def eliminar_lineas_y_palabras_vacias(self, lineas_extraidas: list[datos.Linea]):
        eliminar_linea = []
        for i_linea, linea in enumerate(lineas_extraidas):

            eliminar = []
            for i_palabra in range(len(linea.palabras_linea_original)):
                if linea.palabras_linea_original[i_palabra].Palabra_original.isspace():
                    eliminar.append(i_palabra)
                    continue

            for e in reversed(eliminar):
                if DEBUG_LIMPIA_DATOS_CAPTURADOS: 
                    print(linea.palabras_linea_original[e])
                linea.palabras_linea_original.pop(e)
                
            if linea.palabras_linea_original == []:
                eliminar_linea.append(i_linea)
                continue
            
            if (linea.x1 - linea.x0) < (linea.y1 - linea.y0) * 1.8:
                eliminar_linea.append(i_linea)
                continue
                
            if len(linea.palabras_linea_original) == 1:
                if len(linea.palabras_linea_original[0].Palabra_original) <= 2:
                    eliminar_linea.append(i_linea)

        for e in reversed(eliminar_linea):
            if DEBUG_LIMPIA_DATOS_CAPTURADOS: 
                print(lineas_extraidas[e])
            lineas_extraidas.pop(e)

    #Elimina lineas sospechosas de ser falsos positivos
    def eliminar_falsos_positivos(self, lineas_extraidas: list[datos.Linea], idioma_app: str):
        eliminar_linea = []
        for i_linea, linea in enumerate(lineas_extraidas):

            self.actualizar_barra_de_progreso(PROGRESO_ELIMINANDO_DETECCIONES_ERRONEAS_INICIO + i_linea*(PROGRESO_ELIMINANDO_DETECCIONES_ERRONEAS_FIN-PROGRESO_ELIMINANDO_DETECCIONES_ERRONEAS_INICIO)/len(lineas_extraidas), idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__eliminando_detecciones_erroneas'] + " " + str(i_linea+1) + "/" + str(len(lineas_extraidas)))

            eliminar = []
            for i_palabra in range(len(linea.palabras_linea_original)):
                if linea.palabras_linea_original[i_palabra].tamaño_letras > 72:
                    eliminar.append(i_palabra)

            for e in reversed(eliminar):
                if DEBUG_FALSOS_POSITIVOS: 
                    print(linea.palabras_linea_original[e])
                linea.palabras_linea_original.pop(e)

            if linea.palabras_linea_original == []:
                eliminar_linea.append(i_linea)
                continue
                
            if len(linea.palabras_linea_original) == 1:
                if len(linea.palabras_linea_original[0].Palabra_original) <= 2:
                    eliminar_linea.append(i_linea)

        for e in reversed(eliminar_linea):
            if DEBUG_FALSOS_POSITIVOS: 
                print(lineas_extraidas[e])
            lineas_extraidas.pop(e)
    
    #Calcula el tamaño de latra de un texto dada su área y el texto contenido en dicha área
    def calcular_tamaño_de_letra(self, texto: str, ancho: int, alto_palabra: int, alto_linea: int, fuente_elegida: str = "arial"):
        max_font_size = 127
        min_font_size = 1
        alto_referencia = min(alto_palabra, alto_linea)

        while min_font_size <= max_font_size:
            punto_medio = (min_font_size + max_font_size) // 2
            fuente = ImageFont.truetype(fuente_elegida, punto_medio)

            ancho_fuente, alto_fuente = fuente.getbbox(texto)[0] + fuente.getbbox(texto)[2], fuente.getbbox(texto)[1] + fuente.getbbox(texto)[3]

            if (alto_fuente <= alto_referencia) and ((alto_fuente * ancho_fuente) <= (alto_referencia * ancho)): # and ancho_fuente <= ancho:
                min_font_size = punto_medio + 1
            else:
                max_font_size = punto_medio - 1

        if DEBUG_CALCULAR_POINTSIZE:
            print(texto, alto_referencia, max_font_size)

        if max_font_size < 1:
            return 0
        else:
            return max_font_size
        
    #Hace su mejor esfuerzo por separar grupos que parescan contener dos líneas como si fueran una sola (version palabra)
    def reorganizar_lineas(self, escala: float, lineas_extraidas: list[datos.Linea], idioma_app: str):
        lineas_a_añadir: list[datos.Linea] = []
        for i_linea, linea in enumerate(lineas_extraidas):
            puntos_de_corte: list[int] = []
            for i, palabra in enumerate(linea.palabras_linea_original):
                palabra.tamaño_letras = self.calcular_tamaño_de_letra(texto=palabra.Palabra_original, ancho=palabra.x1-palabra.x0, alto_palabra=palabra.y1-palabra.y0, alto_linea=linea.y1-linea.y0)
                if i == 0:
                    continue
                else:
                    tamaño_letra_promedio = (linea.palabras_linea_original[i-1].tamaño_letras+palabra.tamaño_letras)/2

                    if ((palabra.x0 - linea.palabras_linea_original[i-1].x1) > (tamaño_letra_promedio * 1.5)) or (((palabra.x0 - linea.palabras_linea_original[i-1].x1) > (tamaño_letra_promedio * 1.2)) and (abs(linea.palabras_linea_original[i-1].tamaño_letras - palabra.tamaño_letras) > 5)):
                        if DEBUG_REORGANIZAR_LINEAS:
                            print([i.Palabra_original for i in linea.palabras_linea_original], i)
                        puntos_de_corte.append(i)
            
            linea.identificador_de_division = i_linea
            cortes = len(puntos_de_corte)
            if not (cortes == 0):
                for corte in reversed(puntos_de_corte):
                    linea_aux: datos.Linea = datos.Linea(x0=0, y0=linea.y0, x1=linea.x1, y1=linea.y1, parrafo_original=linea.parrafo_original, identificador_de_division=i_linea)
                    cortes -= 1
                    for i, palabra in reversed(list(enumerate(linea.palabras_linea_original))):
                        linea_aux.palabras_linea_original.insert(0, linea.palabras_linea_original.pop())
                        if i == corte:
                            if DEBUG_REORGANIZAR_LINEAS:
                                print(linea.palabras_linea_original[-1], palabra)
                            linea_aux.x0=linea_aux.palabras_linea_original[0].x0
                            linea.x1=linea.palabras_linea_original[-1].x1
                            break

                    lineas_a_añadir.append(linea_aux)
            if DEBUG_BORDES:
                self.delete("all")
                self.mostrar_bordes(escala, lineas_extraidas)

            self.actualizar_barra_de_progreso(PROGRESO_REORGANIZANDO_LINEAS_INICIO + i_linea*(PROGRESO_REORGANIZANDO_LINEAS_FIN-PROGRESO_REORGANIZANDO_LINEAS_INICIO)/len(lineas_extraidas), idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__reorganizando_lineas'] + " " + str(i_linea+1) + "/" + str(len(lineas_extraidas)))
            
        lineas_extraidas.extend(lineas_a_añadir)

    #Ajusta los valores de las líneas a unos más precisos con respecto a su contenido
    def ajustar_lineas(self, lineas_extraidas: list[datos.Linea], idioma_app: str):
        for i_linea, linea in enumerate(lineas_extraidas):
            texto_en_linea = ""
            miny = 100000
            maxy = 0
            y0_promedio = 0
            y1_promedio = 0
            tamaño_promedio = 0
            alto_promedio = 0

            for palabra in linea.palabras_linea_original:
                if palabra.y0 < miny:
                    miny = palabra.y0
                if palabra.y1 > maxy:
                    maxy = palabra.y1

                y0_promedio += palabra.y0
                y1_promedio += palabra.y1
                tamaño_promedio += palabra.tamaño_letras
                alto_promedio += (palabra.y1 - palabra.y0)
                texto_en_linea += (palabra.Palabra_original + " ")

            y0_promedio = y0_promedio / len(linea.palabras_linea_original)
            y1_promedio = y1_promedio / len(linea.palabras_linea_original)
            tamaño_promedio = tamaño_promedio / len(linea.palabras_linea_original)
            alto_promedio = alto_promedio / len(linea.palabras_linea_original)
            
            if DEBUG_AJUSTAR_LINEAS:
                print("tamaño", tamaño_promedio, "alto", alto_promedio, "alto_linea", linea.y1 - linea.y0, texto_en_linea.strip())

            linea.tamaño_letras = tamaño_promedio
            linea.linea_original = texto_en_linea.strip()
            linea.x0 = linea.palabras_linea_original[0].x0
            linea.x1 = linea.palabras_linea_original[-1].x1
            if y0_promedio > linea.y0:
                linea.y0 = max(linea.y0, miny)
            if y1_promedio < linea.y1:
                linea.y1 = min(linea.y1, maxy)

            self.actualizar_barra_de_progreso(PROGRESO_RECALCULANDO_AREAS_DE_LINEAS_INICIO + i_linea*(PROGRESO_RECALCULANDO_AREAS_DE_LINEAS_FIN-PROGRESO_RECALCULANDO_AREAS_DE_LINEAS_INICIO)/len(lineas_extraidas), idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__recalculando_areas_de_lineas'] + " " + str(i_linea+1) + "/" + str(len(lineas_extraidas)))
    
    #Agrupa las líneas en párrafos
    def detectar_parrafo(self, lineas_extraidas: list[datos.Linea], idioma_app: str):

        lineas_restantes = lineas_extraidas.copy()
        parrafos: list[datos.Parrafo] = []

        while len(lineas_restantes) > 0:
            linea_inicial = lineas_restantes.pop(0)
            parrafo = datos.Parrafo(x0=linea_inicial.x0, y0=linea_inicial.y0, x1=linea_inicial.x1, y1=linea_inicial.y1,tamaño_letras=linea_inicial.tamaño_letras)
            parrafo.lineas_parrafo_original.append(linea_inicial)

            if len(lineas_restantes) > 0:
                self.detectar_parrafo_comp(0, PROFUNDIDAD_DE_BUSQUEDA_DE_PARRAFOS, lineas_restantes, parrafo, 0, idioma_app)

            parrafos.append(parrafo)
            self.actualizar_barra_de_progreso(PROGRESO_DETECTANDO_PARRAFOS_INICIO + (len(lineas_extraidas) - len(lineas_restantes))*(PROGRESO_DETECTANDO_PARRAFOS_FIN-PROGRESO_DETECTANDO_PARRAFOS_INICIO)/len(lineas_extraidas), idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__detectando_parrafos'] + " " + str((len(lineas_extraidas) - len(lineas_restantes))) + "/" + str(len(lineas_extraidas)))
        
        return parrafos     

    #Función recursiva para el agrupador de parrafos
    def detectar_parrafo_comp(self, i:int , profundidad: int, lineas_restantes: list[datos.Linea], parrafo: datos.Parrafo, cont: int, idioma_app: str):

        t = 0
        if lineas_restantes[i].linea_original[0] == ' ':
            t = 1
            print("Como?")

        if not lineas_restantes[i].linea_original[t] in "#$%&*+-/<>@^_`|~": #(lineas[i][0][5][t].isupper() and not lineas[i][0][5][t+1].isupper()) and (not lineas[i][0][5][t] == '>') and (not lineas[i][0][5][t] == '+') and (not lineas[i][0][5][t] == '-'): 

            margen_tam = 3
            if parrafo.tamaño_letras >= lineas_restantes[i].tamaño_letras - margen_tam and parrafo.tamaño_letras <= lineas_restantes[i].tamaño_letras + margen_tam:
                margen_x = parrafo.tamaño_letras
                if parrafo.lineas_parrafo_original[-1].linea_original[t] == '>':
                    margen_x *= 2
                if parrafo.lineas_parrafo_original[-1].x0 >= lineas_restantes[i].x0 - margen_x and parrafo.lineas_parrafo_original[-1].x0 <= lineas_restantes[i].x0 + margen_x:
                    margen_y = parrafo.tamaño_letras *1.5
                    if lineas_restantes[i].y0 - parrafo.lineas_parrafo_original[-1].y1 < margen_y:

                        linea_a_añadir = lineas_restantes.pop(i)
                        parrafo.tamaño_letras = int((parrafo.tamaño_letras * len(parrafo.lineas_parrafo_original) + linea_a_añadir.tamaño_letras) / (len(parrafo.lineas_parrafo_original) + 1))
                        parrafo.y1 = linea_a_añadir.y1

                        if linea_a_añadir.x1 > parrafo.x1:
                            parrafo.x1 = linea_a_añadir.x1
                        parrafo.lineas_parrafo_original.append(linea_a_añadir)

                        if len(lineas_restantes) > i:
                            self.detectar_parrafo_comp(i, profundidad, lineas_restantes, parrafo, 0, idioma_app)

        if cont < profundidad:
            i += 1
            cont += 1
            if len(lineas_restantes) > i:
                self.detectar_parrafo_comp(i, profundidad, lineas_restantes, parrafo, cont, idioma_app)

    #Compruba si 2 parrafos se consideran superpuestos, 
    def parrafos_superpuestos(self, parrafo_aislado: datos.Parrafo, parrafo_a_comparar: datos.Parrafo):
        area_de_interseccion = max(0, 
            min(parrafo_aislado.x1, parrafo_a_comparar.x1) 
            - max(parrafo_aislado.x0, parrafo_a_comparar.x0)
            ) * max(0, 
            min(parrafo_aislado.y1, parrafo_a_comparar.y1) 
            - max(parrafo_aislado.y0, parrafo_a_comparar.y0)
            )
        
        porcentaje_de_interseccion_sobre_el_parrafo_aislado = area_de_interseccion / ((parrafo_aislado.x1 - parrafo_aislado.x0) * (parrafo_aislado.y1 - parrafo_aislado.y0))
        if porcentaje_de_interseccion_sobre_el_parrafo_aislado > UMBRAL_DE_SUPERPOSICION_DE_PARRAFOS:
            return True
        
        return False
    
    #Recorre todos los parrafos intentando determinar cuales deben combinarse
    def combinar_parrafos(self, parrafos: list[datos.Parrafo], idioma_app: str):
        i_parrafo = 0
        while i_parrafo < len(parrafos):
            if len(parrafos[i_parrafo].lineas_parrafo_original) == 1:
                j_parrafo = 0
                while j_parrafo < len(parrafos):
                    if j_parrafo == i_parrafo:
                        j_parrafo += 1
                        continue
                    if self.parrafos_superpuestos(parrafos[i_parrafo], parrafos[j_parrafo]):
                        parrafo_a_integrar = parrafos.pop(i_parrafo)
                        parrafos[j_parrafo].tamaño_letras = (parrafos[j_parrafo].tamaño_letras * len(parrafos[j_parrafo].lineas_parrafo_original) + parrafo_a_integrar.tamaño_letras) / (len(parrafos[j_parrafo].lineas_parrafo_original) + 1)
                        if parrafos[j_parrafo].x0 > parrafo_a_integrar.x0:
                            parrafos[j_parrafo].x0 = parrafo_a_integrar.x0
                        if parrafos[j_parrafo].x1 < parrafo_a_integrar.x1:
                            parrafos[j_parrafo].x1 = parrafo_a_integrar.x1
                        if parrafos[j_parrafo].y0 > parrafo_a_integrar.y0:
                            parrafos[j_parrafo].y0 = parrafo_a_integrar.y0
                        if parrafos[j_parrafo].y1 < parrafo_a_integrar.y1:
                            parrafos[j_parrafo].y1 = parrafo_a_integrar.y1
                        
                        completado = False
                        for i_linea, linea in enumerate(parrafos[j_parrafo].lineas_parrafo_original):
                            if linea.identificador_de_division == parrafo_a_integrar.lineas_parrafo_original[0].identificador_de_division:
                                if linea.x0 < parrafo_a_integrar.lineas_parrafo_original[0].x0:
                                    parrafos[j_parrafo].lineas_parrafo_original.insert(i_linea + 1, parrafo_a_integrar.lineas_parrafo_original[0])
                                    if len(parrafos[j_parrafo].sub_parrafos) == 0:
                                        parrafos[j_parrafo].sub_parrafos.append(parrafos[j_parrafo].lineas_parrafo_original[:i_linea+1])
                                        parrafos[j_parrafo].sub_parrafos.append(parrafos[j_parrafo].lineas_parrafo_original[i_linea+1:])
                                    else:
                                        parrafos[j_parrafo].sub_parrafos.append(parrafos[j_parrafo].lineas_parrafo_original[i_linea+1:])
                                else:
                                    parrafos[j_parrafo].lineas_parrafo_original.insert(i_linea, parrafo_a_integrar.lineas_parrafo_original[0])
                                    if len(parrafos[j_parrafo].sub_parrafos) == 0:
                                        parrafos[j_parrafo].sub_parrafos.append(parrafos[j_parrafo].lineas_parrafo_original[:i_linea+1])
                                        parrafos[j_parrafo].sub_parrafos.append(parrafos[j_parrafo].lineas_parrafo_original[i_linea+1:])
                                    else:
                                        parrafos[j_parrafo].sub_parrafos.append(parrafos[j_parrafo].lineas_parrafo_original[i_linea+1:])

                                completado = True
                                break
                        
                        if not completado and DEBUG_COMBINAR_PARRAFOS:
                            print("no completado")

                        i_parrafo -= 1  

                    j_parrafo += 1
            i_parrafo += 1
            
            self.actualizar_barra_de_progreso(PROGRESO_AGRUPANDO_PARRAFOS_INICIO + (i_parrafo) * (PROGRESO_AGRUPANDO_PARRAFOS_FIN - PROGRESO_AGRUPANDO_PARRAFOS_INICIO) / len(parrafos), idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__agrupando_parrafos'] + " " + str(i_parrafo) + "/" + str(len(parrafos)))
        
        for parrafo in parrafos:
            for i_linea, linea in enumerate(parrafo.lineas_parrafo_original):

                if i_linea == 0:
                    parrafo.parrafo_original.append(linea.linea_original + " ")
                    continue

                if linea.identificador_de_division == parrafo.lineas_parrafo_original[i_linea-1].identificador_de_division:
                    parrafo.parrafo_original[-1].strip()
                    parrafo.parrafo_original.append(linea.linea_original + ". ")
                    continue

                parrafo.parrafo_original[-1] += (linea.linea_original + " ")

            parrafo.parrafo_original[-1].strip()


    def traducir_parrafos(self, parrafos: list[datos.Parrafo], idioma_app: str, idioma_o: str, idioma_d: str):
        for i_parrafo, parrafo in enumerate(parrafos):
            for bloque in parrafo.parrafo_original:
                parrafo.parrafo_traducido.append(LT.translate(bloque, idioma_o, idioma_d))
            self.actualizar_barra_de_progreso(PROGRESO_TRADUCIENDO_INICIO + (i_parrafo + 1) * (PROGRESO_TRADUCIENDO_FIN - PROGRESO_TRADUCIENDO_INICIO) / len(parrafos), idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__traduciendo'] + " " + str(i_parrafo + 1) + "/" + str(len(parrafos)))
            
    def mostrar_traduccion(self, escala: float, parrafos: list[datos.Parrafo]):
        
        self.delete("all")
        for parrafo in parrafos:

            if len(parrafo.parrafo_traducido) > 1:
                for i_grupo, grupo in enumerate(parrafo.sub_parrafos):
                    self.balancear_texto_traducido(escala, parrafo, parrafo.parrafo_traducido[i_grupo], parrafo.parrafo_original[i_grupo], grupo)
            else: 
                self.balancear_texto_traducido(escala, parrafo, parrafo.parrafo_traducido[0], parrafo.parrafo_original[0], parrafo.lineas_parrafo_original)

    def balancear_texto_traducido(self, escala: float, parrafo: datos.Parrafo, bloque_de_texto_traducido: str, bloque_de_texto_original: str, lineas_a_balancear: list[datos.Linea]):

        espacio_disponible = 0
        for linea in lineas_a_balancear:
            espacio_disponible += (linea.x1 - linea.x0)

        parrafo.tamaño_letras = int(parrafo.tamaño_letras*1.05)
        texto_muy_largo = True

        while texto_muy_largo:

            fuente = ImageFont.truetype("arial", int(parrafo.tamaño_letras))
            largo_con_este_tamaño_de_letra = 0
            texto_muy_largo = False

            area_linea = fuente.getbbox(bloque_de_texto_traducido)
            largo_con_este_tamaño_de_letra += (area_linea[0] + area_linea[2])

            if largo_con_este_tamaño_de_letra / espacio_disponible > 0.9:
                parrafo.tamaño_letras = int(parrafo.tamaño_letras - 1)
                texto_muy_largo = True
                break

        proporcion = len(bloque_de_texto_traducido)/len(bloque_de_texto_original)
        texto_traducido = bloque_de_texto_traducido
        desviacion_acumulada = 0
        for i_linea, linea in enumerate(lineas_a_balancear):
            separador = 0
            
            i_aux = int(len(lineas_a_balancear[i_linea].linea_original) * proporcion)
            if i_linea == len(lineas_a_balancear) -1:
                linea.linea_traducida = texto_traducido
                break
            elif i_aux - desviacion_acumulada >= len(texto_traducido) or i_aux - desviacion_acumulada <= 0:
                linea.linea_traducida = texto_traducido
                break
            else:
                if texto_traducido[i_aux - desviacion_acumulada] == ' ':
                    separador = i_aux - desviacion_acumulada
                else:
                    desviacion = 0
                    fin_dercha = False
                    fin_izquierda = False
                    while True:
                        desviacion +=1
                        des_der = 0
                        if (i_aux - desviacion_acumulada + desviacion) < len(texto_traducido)-1:
                            if texto_traducido[i_aux - desviacion_acumulada + desviacion] == ' ':
                                separador = i_aux - desviacion_acumulada + desviacion
                                desviacion_acumulada += desviacion
                                break
                        else:
                            if not fin_dercha:
                                des_der = desviacion
                            fin_dercha = True

                        if (i_aux - desviacion_acumulada - desviacion) > 0:
                            if texto_traducido[i_aux - desviacion_acumulada - desviacion] == ' ':
                                separador = i_aux - desviacion_acumulada - desviacion
                                desviacion_acumulada -= desviacion
                                break
                        else:
                            fin_izquierda = True

                        if fin_dercha and  fin_izquierda:
                            desviacion_acumulada += des_der
                            break

                linea.linea_traducida = texto_traducido[:separador]
                texto_traducido = texto_traducido[separador:]

        
        for linea in lineas_a_balancear:
            self.create_rectangle((linea.x0-2)/escala, (linea.y0-2)/escala, (linea.x1+2)/escala, (linea.y1+2)/escala, outline ="black", fill="gray",width = 1)
            self.texto_resaltado(linea.linea_traducida, (linea.x0)/escala, (linea.y0)/escala, int((parrafo.tamaño_letras)/escala))
                
    def transcribir(self, parrafos: list[datos.Parrafo],  text_area_idioma_origen: scrolledtext.ScrolledText, text_area_idioma_destino: scrolledtext.ScrolledText):

        texto_original = ""
        texto_traducido = ""
        for parrafo in parrafos:
            for bloque in parrafo.parrafo_original:
                texto_original += bloque + ".  "
            for bloque in parrafo.parrafo_traducido:
                texto_traducido += bloque + ".  "
            texto_original += "\n\n"
            texto_traducido += "\n\n"

        text_area_idioma_origen.configure(state='normal')
        text_area_idioma_origen.delete("1.0","end")
        text_area_idioma_origen.insert('end', texto_original)
        text_area_idioma_origen.configure(state='disabled')
        text_area_idioma_destino.configure(state='normal')
        text_area_idioma_destino.delete("1.0","end")
        text_area_idioma_destino.insert('end', texto_traducido)
        text_area_idioma_destino.configure(state='disabled')

    def traducir(self, escala: int, text_area_idioma_origen: scrolledtext.ScrolledText, text_area_idioma_destino: scrolledtext.ScrolledText,  x: int, y: int, w: int, h: int, idioma_origen: str, idioma_destino: str, idioma_app: str):
        
        #Limpia el canvas antes de capturar la pantalla tras el 
        self.delete("all")
        self.update()

        #Captura la imagen
        archivo=ImageGrab.grab(bbox=(escala*(x+10),escala*(y+32),escala*(x+w-10),escala*(y+h-10)), include_layered_windows=False, all_screens=True)
        
        #Vuelve a dibujar el borde
        self.borde_canvas = self.create_rectangle(0, 0, self.winfo_width()-1, self.winfo_height()-1)
        self.update()

        #Inicia la barra de carga
        self.iniciar_barra_de_progreso()
        
        #Recupera los codigos de idioma para el OCR, idioma de origen e idioma objetivo
        idioma_OCR, idioma_o, idioma_d = idiomas.recuperar_codigos_de_idioma(idioma_app, idioma_origen, idioma_destino)

        #Barra de carga
        self.actualizar_barra_de_progreso(PROGRESO_CAPTURA_DE_DATOS, idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__captura_de_datos'])
        
        #Pasa la imagen al OCR
        respuesta_OCR = pytesseract.image_to_data(archivo, lang=idioma_OCR)

        

        #Organiza la información recuperada de la imagen
        lineas_extraidas: list[datos.Linea] = self.separar_resultado_OCR_en_lineas(respuesta_OCR)
        
        if DEBUG_BORDES:
            self.delete("all")
            self.mostrar_bordes(escala, lineas_extraidas)

        #Barra de carga
        self.actualizar_barra_de_progreso(PROGRESO_LIMPIA_DATOS_CAPTURADOS, idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__limpia_datos_capturados'])

        #Elimina palabras compuestas unicamente por espacios en blanco y las líneas que no contengan palabras
        self.eliminar_lineas_y_palabras_vacias(lineas_extraidas)

        #Barra de carga
        self.actualizar_barra_de_progreso(PROGRESO_REORGANIZANDO_LINEAS_INICIO, idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__reorganizando_lineas'] + " 0/" + str(len(lineas_extraidas)))
        
        #Hace su mejor esfuerzo por separar grupos que parescan contener dos líneas como si fueran una sola (version palabra)
        self.reorganizar_lineas(escala, lineas_extraidas, idioma_app)

        #Barra de carga
        self.actualizar_barra_de_progreso(PROGRESO_ELIMINANDO_DETECCIONES_ERRONEAS_INICIO, idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__eliminando_detecciones_erroneas'])

        #Elimina ruido visual
        self.eliminar_falsos_positivos(lineas_extraidas, idioma_app)

        #Barra de carga
        self.actualizar_barra_de_progreso(PROGRESO_RECALCULANDO_AREAS_DE_LINEAS_INICIO, idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__recalculando_areas_de_lineas'] + " 0/" + str(len(lineas_extraidas)))

        #Ajusta las lineas para hacerlas más precisas
        self.ajustar_lineas(lineas_extraidas, idioma_app)
        
        #Barra de carga
        self.actualizar_barra_de_progreso(PROGRESO_DETECTANDO_PARRAFOS_INICIO, idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__detectando_parrafos'] + " 0/" + str(len(lineas_extraidas)))

        #Agrupa las líneas en párrafos
        parrafos: list[datos.Parrafo] = self.detectar_parrafo(lineas_extraidas, idioma_app)

        #for p in parrafos:
            #self.create_rectangle(p.x0/escala-5,p.y0/escala-5,p.x1/escala+5,p.y1/escala+5, outline ="red",width = 2)
        
        #Barra de carga
        self.actualizar_barra_de_progreso(PROGRESO_AGRUPANDO_PARRAFOS_INICIO, idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__agrupando_parrafos'] + " 0/" + str(len(parrafos)))

        #combina parrafos con una superposición mayor al 85%
        self.combinar_parrafos(parrafos, idioma_app)

        #Barra de carga
        self.actualizar_barra_de_progreso(PROGRESO_TRADUCIENDO_INICIO, idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__traduciendo'] + " 0/" + str(len(parrafos)))

        #Traduce los párrafos
        self.traducir_parrafos(parrafos, idioma_app, idioma_o, idioma_d)

        #Barra de carga
        self.actualizar_barra_de_progreso(PROGRESO_DIBUJANDO, idiomas.INTERFAZ_DIC[idioma_app]['barra_de_progreso__dibujando'])

        #Calcula una diposición apropiada del texto traducido para que ocupe un espacio similar al original
        self.mostrar_traduccion(escala, parrafos)

        #Actualiza la pestaña de transcripciones
        self.transcribir(parrafos, text_area_idioma_origen, text_area_idioma_destino)

        #Cambia el estado del traductor
        self.traduciendo.set(False)

        #Elimina la barra de carga una ves terminada la tradución 
        self.eliminar_barra_de_progreso()