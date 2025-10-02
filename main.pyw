from ventana import Ventana
import subprocess
import os

#Inicia el servidor LibreTranslate en segundo plano y espera a que esté listo antes de proceder

os.environ["PYTHONUNBUFFERED"] = "1"

servidor_interno = subprocess.Popen('libretranslate --threads 4 --port 50000', stdout=subprocess.PIPE, text=True)

for p in servidor_interno.stdout:
    print(p)
    if "Running" in p:
        break

#Inicia la ventana

app = Ventana(servidor_interno)
app.mainloop()