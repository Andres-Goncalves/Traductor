from PIL import Image, ImageTk, ImageGrab, ImageFont
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import scrolledtext 
import math
from ctypes import windll, wintypes, byref
import re

##################################################################################################################
# Algorítmo arcano que determina la altura de la barra de tareas en pixeles de forma mágica, por favor, no tocar #
##################################################################################################################

SPI_GETWORKAREA = 0x0030

desktopWorkingArea = wintypes.RECT()

_ = windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, byref(desktopWorkingArea), 0)

left = desktopWorkingArea.left
top = desktopWorkingArea.top
right = desktopWorkingArea.right
bottom = desktopWorkingArea.bottom

tsx,tsy = windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)
ts = tsy - (top + bottom)

##################################################################################################################
##################################################################################################################
##################################################################################################################

class Ventana(tk.Tk):
    def __init__(self, *args, **kwargs):
        #super()
        tk.Tk.__init__(self, *args, **kwargs)
        
        #Establece el nombre de la ventana (que no se espera sea mostrado en ninguna parte, pero se añade por si acaso)
        self.title("Traductor")

        #Establece la posición y tamaño inicial de la ventana
        self.x=int(self.winfo_screenwidth()/2-self.w/2)
        self.y=int(self.winfo_screenheight()/2-self.h/2)
        self.w=520
        self.h=520

        #Establece los valores iniciales del modo ventana
        self.windowed = True
        self.windowed_x = self.x
        self.windowed_y = self.y
        self.windowed_size_width = self.w
        self.windowed_size_height = self.h

        #Elimina la barra del título
        self.overrideredirect(True)

        self.movx = None
        self.movy = None

        #Seleciona un color arbitrario para establecerlo como tranparencia
        self.transparencia = "grey81"

        #Establece el atributo de transparencia al color selecionado
        self.attributes("-transparentcolor", self.transparencia)

        #aplica el color selecionado al fondo de la ventana
        self.config(bg=self.transparencia)

        #Realiza una busqueda recursiva para identificar todas las pantallas conectadas, sus pociciones y resoluciones
        self.pantallas = []
        self.detectar_pantallas(self.pantallas)

        #Crea un marco de color blanco que permite sujetar la ventana y moverla por la pantalla
        self.grip = tk.Frame(self, bg='white')
        self.grip.pack(fill=tk.BOTH, expand=True)

        #Enlaza los eventos de "presionar click izquierdo", "mover mouse mientras se mantiene el click izquierdo" y "soltar click izquierdo" a sus respectivas funciones
        self.grip.bind("<ButtonPress-1>", self.start_move)
        self.grip.bind("<ButtonRelease-1>", self.stop_move)
        self.grip.bind("<B1-Motion>", self.do_move)








        self.wm_attributes("-topmost", 1)
        self.bind("<Configure>", self.on_resize)
        #Fin de la inicialización de la ventana

    #Realiza los ajustes necesarios cada vez que ocurre un cambio en la ventana
    def on_resize(self, e):
    #print(e)
    #print(e.widget)
    #print(root)
        if e.widget == self:
            #print("pass")
            #canvas.config(width=e.width-20, height=e.height-20)
            self.canvas.config(width=e.width-20, height=e.height-42)

            #Transcripción
            frame_transcripcion.config(width=e.width-20, height=e.height-20)
            salir_transcripcion.place(x=e.width-20-20, y=2)
            Label_idioma_origen.place(x=int((e.width-20)/4), y=20, anchor="center")
            Label_idioma_destino.place(x=int((e.width-20)/4*3), y=20, anchor="center")
            text_area_idioma_origen.place(x=20, y=40, width = int((e.width-20)/2-20-10), height = e.height-20-40-20)
            text_area_idioma_destino.place(x=int((e.width-20)/2)+10, y=40, width = int((e.width-20)/2-10-20), height = e.height-20-40-20)
            
            #Esquina base
            salir.place(x=e.width-12-19, y=12)
            boton_maximizar.place(x=e.width-12-19-19, y=12)
            boton_configuracion.place(x=e.width-12-19-19-23, y=12)

            #Menu Configuración
            Menu_Configuracion_Frame.config(width=e.width-20, height=e.height-20)
            salir_Menu_Configuracion_Frame.place(x=e.width-20-20, y=2)
            Label_Menu_Configuracion.place(x=int(e.width/2), y=40)
            Label_idioma_app_select.place(x=int(e.width/2)-5, y=100)
            idioma_elegido_app.place(x=int(e.width/2)+5, y=100)
            Cancelar_Menu_Configuracion_Frame.place(x=int(e.width/2)-30, y=e.height-80)
            Guardar_Menu_Configuracion_Frame.place(x=int(e.width/2)+30, y=e.height-80)
            #print(windowed_size_width, windowed_size_height)
            global windowed, windowed_size_width, windowed_size_height

            if windowed == True:
                windowed_size_width = e.width
                windowed_size_height = e.height
                #print(windowed_size_width, windowed_size_height)


    def BotonMinMax(self):
        global windowed, windowed_size_width, windowed_size_height, windowed_x, windowed_y

        if windowed:
            windowed_x, windowed_y = root.winfo_rootx(), root.winfo_rooty()
            windowed = False
            root.state('zoomed')
            w, h, x, y = root.winfo_width(), root.winfo_height()-ts, root.winfo_rootx(), root.winfo_rooty()
            root.state('normal')
            root.geometry("%dx%d+%d+%d" % (w, h, x, y))
        else:
            windowed = True
            root.geometry("%dx%d+%d+%d" % (int(windowed_size_width), int(windowed_size_height), int(windowed_x), int(windowed_y)))
            root.update()


    def Maximizar(self):
        global windowed, pantallas

        if windowed == True:
            for p in pantallas:
                #print(p)
                if root.winfo_pointerx() >= p[2] and root.winfo_pointerx() <= p[2]+p[0]-1:
                    if root.winfo_pointery() >= p[3] and root.winfo_pointery() <= p[3]+p[1]-1:
                        if root.winfo_pointery() <= p[3]+2:
                            windowed = False
                            root.state('zoomed')
                            w, h, x, y = root.winfo_width(), root.winfo_height()-ts, root.winfo_rootx(), root.winfo_rooty()
                            root.state('normal')
                            root.geometry("%dx%d+%d+%d" % (w, h, x, y))
                            break

    def Minimizar(self):
        global movx, movy, windowed, windowed_size_width, windowed_size_height

        if windowed == False:
            mw, mh, mx, my = root.winfo_width(), root.winfo_height(), root.winfo_rootx(), root.winfo_rooty()
            x, y = root.winfo_pointerx(), root.winfo_pointery()
            windowed = True
            #print(windowed_size_width, windowed_size_height)
            root.geometry("%dx%d+%d+%d" % (int(windowed_size_width), int(windowed_size_height),int(x-windowed_size_width*(x-mx)/mw),int(y-windowed_size_height*(y-my)/mh)))
            root.update()
            #print(x, y)
            #print(mw, mh, mx, my)
            #print(root.winfo_width(), root.winfo_height(), root.winfo_rootx(), root.winfo_rooty())


            movx = int(root.winfo_width()*(x-mx)/mw)
            movy = int(root.winfo_height()*(y-my)/mh)


            # screen_width = root.winfo_screenwidth()
            # screen_height = root.winfo_screenheight()
            # print(screen_width, screen_height)

            # root.geometry("%dx%d+%d+%d" % (screen_width, screen_height,0,0))


            # Max_abs_x = root.winfo_pointerx() - root.winfo_rootx()
            # Max_abs_y = root.winfo_pointery() - root.winfo_rooty()
            # Max_width = root.winfo_width()
            # Max_height= root.winfo_height()
            # Max_x = root.winfo_rootx()
            # Max_y = root.winfo_rooty()

            # New_width = windowed_size_width
            # New_height = windowed_size_height
            # New_x = 0


            # root.geometry("%dx%d+%d+%d" % (screen_width, screen_height,x,y))

    def start_move(self, event):
        global movx, movy, windowed
        #print(event)
        movx = event.x
        movy = event.y
        #print(movx, movy)
        Minimizar()
        #print(movx, movy)

    def stop_move(self, event):
        global movx, movy, windowed, windowed_x, windowed_y
        movx = None
        movy = None
        #print(movx, movy)
        Maximizar()
        if windowed:
            windowed_x, windowed_y = root.winfo_rootx(), root.winfo_rooty()

    def do_move(self, event):
        #print(root.winfo_screenwidth())
        #print(f'x = {root.winfo_pointerx()} y = {root.winfo_pointery()}')
        # if root.winfo_pointerx()-700> root.winfo_screenwidth():
        #     #root.state("zoomed")
        #     print(f'x = {root.winfo_pointerx()} y = {root.winfo_pointery()}')
        #     screen_width = root.winfo_screenwidth()
        #     screen_height = root.winfo_screenheight()
        #     print(screen_width, screen_height)
        global movx, movy
        #print(event)
        #print(movx, movy)
        deltax = event.x - movx
        deltay = event.y - movy
        ax = root.winfo_x() + deltax
        ay = root.winfo_y() + deltay
        root.geometry(f"+{ax}+{ay}")

    #función recursiva para identificar todas las pantallas conectadas, sus pociciones y resoluciones
    def detectar_pantallas(self, p):
        
        #gurada los parametros de la primera pantalla
        principal = (self.winfo_screenwidth(), self.winfo_screenheight(), 0, 0)
        p.append(principal)
        px = []
        px.append(0)
        py = []
        py.append(0)

        self.detectar_pantalla_rec(self, self.winfo_screenwidth(), self.winfo_screenheight(), 0, 0, px, py, p)

        print(p) #

        #w=520
        #h=520
        #x=int(root.winfo_screenwidth()/2-w/2)
        #y=int(root.winfo_screenheight()/2-w/2)
        self.geometry(f'{self.w}x{self.h}+{self.x}+{self.y}')
        self.update()



    def detectar_pantalla_rec(self, ow, oh, ox, oy, px, py, p):

        Monitor_minimo = (800,600)

        #x_iter = math.ceil(int(p[0][0])/Monitor_minimo[0])
        #y_iter = math.ceil(int(p[0][1])/Monitor_minimo[1])

        x_iter = math.ceil(ow/Monitor_minimo[0])
        y_iter = math.ceil(oh/Monitor_minimo[1])

        #print(x_iter, y_iter)

        #minUnitX = (int(p[0][0])/x_iter)/2
        #minUnitY = (int(p[0][1])/y_iter)/2

        minUnitX = (ow/x_iter)/2
        minUnitY = (oh/y_iter)/2

        #print(minUnitX,minUnitY)

        for ix in range(x_iter+2):
            pos_x = -minUnitX + minUnitX*2*ix
            #print(pos_x)
            #detectar_pantallas_h(p, px, py, pos_x, minUnitY)
            self.detectar_pantallas_h(self, ow, oh, ox, oy, p, px, py, pos_x, minUnitY)

        for iy in range(y_iter):
            pos_y = -minUnitY + minUnitY*2*(iy+1)
            #print(pos_y)
            #detectar_pantallas_v(p, px, py, minUnitX, pos_y)
            self.detectar_pantallas_v(self, ow, oh, ox, oy, p, px, py, minUnitX, pos_y)



    def detectar_pantallas_h(self, ow, oh, ox, oy, p, px, py, x, y):

        #print(ox+x, oy-y)
        root.geometry(f"+{int(ox+x)}+{int(oy-y)}")
        root.update()
        root.state("zoomed")
        if (root.winfo_rootx() not in px) or (root.winfo_rooty() not in py):
            p.append((root.winfo_width(),root.winfo_height(),root.winfo_rootx(),root.winfo_rooty()))
            px.append(root.winfo_rootx())
            py.append(root.winfo_rooty())
            detectar_pantalla_rec(root.winfo_width(), root.winfo_height(), root.winfo_rootx(), root.winfo_rooty(), px, py, p)
        root.state("normal")

        #print(ox+x, oy+y)
        root.geometry(f"+{int(ox+x)}+{int(oh+y)}")
        root.update()
        root.state("zoomed")
        if (root.winfo_rootx() not in px) or (root.winfo_rooty() not in py):
            p.append((root.winfo_width(),root.winfo_height(),root.winfo_rootx(),root.winfo_rooty()))
            px.append(root.winfo_rootx())
            py.append(root.winfo_rooty())
            detectar_pantalla_rec(root.winfo_width(), root.winfo_height(), root.winfo_rootx(), root.winfo_rooty(), px, py, p)
        root.state("normal")



    def detectar_pantallas_v(self, ow, oh, ox, oy, p, px, py, x, y):

        #print(ox-x, oy+y)
        root.geometry(f"+{int(ox-x)}+{int(oy+y)}")
        root.update()
        root.state("zoomed")
        if (root.winfo_rootx() not in px) or (root.winfo_rooty() not in py):
            p.append((root.winfo_width(),root.winfo_height(),root.winfo_rootx(),root.winfo_rooty()))
            px.append(root.winfo_rootx())
            py.append(root.winfo_rooty())
            detectar_pantalla_rec(root.winfo_width(), root.winfo_height(), root.winfo_rootx(), root.winfo_rooty(), px, py, p)
        root.state("normal")

        #print(ow+x, oy+y)
        root.geometry(f"+{int(ow+x)}+{int(oy+y)}")
        root.update()
        root.state("zoomed")
        if (root.winfo_rootx() not in px) or (root.winfo_rooty() not in py):
            p.append((root.winfo_width(),root.winfo_height(),root.winfo_rootx(),root.winfo_rooty()))
            px.append(root.winfo_rootx())
            py.append(root.winfo_rooty())
            detectar_pantalla_rec(root.winfo_width(), root.winfo_height(), root.winfo_rootx(), root.winfo_rooty(), px, py, p)
        root.state("normal")

