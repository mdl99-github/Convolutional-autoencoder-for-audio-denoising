from scipy.io import wavfile
from os import path
import random
import numpy as np


def normalizar(train, train_noisy, test, test_noisy):
    m = 10000000
    M = -10000000

    for i in range(0, len(train)):
        train_noisy[i] = train_noisy[i]*0.1
        train[i] = train[i]*0.1
    for i in range(0, len(test)):
        test_noisy[i] = test_noisy[i]*0.1
        test[i] = test[i]*0.1

    for i in range(0, len(train)):
        M1 = max(train_noisy[i])
        M2 = max(train[i])
        M3 = max(M1, M2)
        M = max(M3, M)
        
        m1 = min(train_noisy[i])
        m2 = min(train[i])
        m3 = min(m1, m2)
        m = min(m3, m)
    for i in range(0, len(test)):
        M1 = max(test_noisy[i])
        M2 = max(test[i])
        M3 = max(M1, M2)
        M = max(M3, M)
        
        m1 = min(test_noisy[i])
        m2 = min(test[i])
        m3 = min(m1, m2)
        m = min(m3, m)
        
    for i in range(0, len(train)):
        train_noisy[i] = (train_noisy[i] - m)/(M - m)
        train[i] = (train[i] - m)/(M - m)
    for i in range(0, len(test)):
        test_noisy[i] = (test_noisy[i] - m)/(M - m)
        test[i] = (test[i] - m)/(M - m)

    train = np.array(train)
    test = np.array(test)
    train_noisy = np.array(train_noisy)
    test_noisy = np.array(test_noisy)

    return train, train_noisy, test, test_noisy, m, M

def add_noise(datos, ruido, snrb, snrc, energia_datos): 
    largo = len(ruido)
    largo_datos = len(datos)

    blanco = np.random.normal(0, 0.1, len(datos))
    energia_deseada = energia_datos/10**(snrb/10)
    factor = energia_deseada/0.1

    datos = datos + blanco*factor

    energia_datos_avg = energia_datos/largo_datos
    ruido = ruido*0.1
    energia_ruido_avg = sum(ruido**2)/largo

    energia_deseada = energia_datos_avg/10**(snrc/10)
    factor = energia_deseada/energia_ruido_avg

    inicio = random.randint(0, largo-50)

    for i in range(inicio, largo-50 ):
        if ruido[i] != 0:
            inicio = i
            break

    pos = random.randint(0, largo_datos-50)
    datos[pos:pos+50] = datos[pos:pos+50] + factor*ruido[inicio:inicio+50]

    return datos


def load_data(n, snrb, snrc, t):
    codigo = "1"
    formato = ".wav"
    carpeta = "data_limpia/"
    cargados = 0
    clean = []
    noisy = []
    fs, ruido = wavfile.read("ruido.wav")
    end_flag = False

    while codigo != "10000" and end_flag == False:
        nombre = carpeta + codigo + formato
        if path.exists(nombre) == False:
            codigo = str(int(codigo) + 1)
            continue
        fs, data = wavfile.read(nombre)
        energia = sum(data**2)
        largo_total = len(data)
        largo_seg = int(fs*t)
        start = 0
        end = largo_seg
        while end <= largo_total and end_flag == False:
            clean.append(data[start:end])
            noisy.append(clean[-1].copy())
            start += largo_seg
            end +=largo_seg
            cargados += 1
            noisy[-1] = add_noise(noisy[-1], ruido, snrb, snrc, energia)
            if cargados == n:
                end_flag = True
        codigo = str(int(codigo) + 1)
        if end_flag:
            break

    return clean, noisy

def deteccion(s, sensibilidad):
    ubicaciones = []
    i = 0

    while i < len(s)-1:
        if abs(s[i+1])/(abs(s[i]) + abs(s[i+1])) >= sensibilidad:
            ubicaciones.append(i)
            i = i + 25
            continue
        i = i + 1
    return ubicaciones
