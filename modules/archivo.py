# -- coding: utf-8 --
"""
Created on 9/10/2024

@author: Paula Martínez Camarero y Andrés Estévez Ubierna
"""

#FUNCIONES MODULARIZADAS:

#Las librerias las vamos a ir importando según las vayamos necesitando

import pydicom as dcm
from pathlib import Path

def Load_Slices(foldername):
    '''
    Carga todos los archivos DICOM en una lista desde la carpeta especificada.

    Parámetros:

     foldername: 
         Ruta de la carpeta que contiene los archivos DICOM (.dcm) a cargar.

    Returns:

     lista:
         Lista donde cada elemento es un archivo DICOM cargado, con toda su información.
    '''
    
    lista = []
    
    # itera sobre todos los archivos DICOM en la ruta especificada que tengan extensión .dcm
    for i in Path(foldername).glob("*.dcm"):
        # muestra el nombre del archivo 
        print(f"Loading: {i}")  
        # lee y añade el archivo DICOM al final de la lista
        lista.append(dcm.dcmread(i))  
    
    return lista


import numpy as np
def CreaVolumen(imagenes):
    '''
    A partir de una lista de imágenes DICOM crea un volumen 3D, habiendolas convertido a la escala Hounsfield

    Parámetros:
    
     imagenes:
         Lista de objetos DICOM que contienen información de las imágenes (pixel_array, RescaleIntercept, RescaleSlope).

    Returns:
    
     volumen: 
         Volumen 3D de las imágenes convertidas a escala Hounsfield.
     volumen.shape:
         Dimensiones del volumen 3D.
     relacion_aspecto: 
         Relación de aspecto del volumen en las tres dimensiones.
     tamaño_voxel: 
         Tamaño del voxel en el espacio tridimensional.
    '''
    
    num_slices = len(imagenes)
    filas, columnas = imagenes[0].pixel_array.shape

    # inicializar el array 3D para almacenar el volumen
    volumen = np.zeros((num_slices, filas, columnas))

    # recorrer imágenes y convertirlas a la escala Hounsfield
    for i in range(num_slices):
        imagen = imagenes[i].pixel_array
        intercepto = imagenes[i].RescaleIntercept
        escala = imagenes[i].RescaleSlope
        
        # fórmula para convertir a unidades Hounsfield
        imagen = escala * imagen + intercepto
        volumen[i] = imagen

    # Obtener el tamaño del voxel
    pixel_spacing = imagenes[0].PixelSpacing
    slice_thickness = imagenes[0].SliceThickness
    tamaño_voxel = (slice_thickness, pixel_spacing[0], pixel_spacing[1])
        
    # calculamos la relación de aspecto
    relacion_aspecto = (
        slice_thickness / pixel_spacing[0], #axial
        pixel_spacing[0] / pixel_spacing[1], #sagital
        slice_thickness / pixel_spacing[1] #coronal
    )

    # devuelve el volumen, las dimensiones, la relación de aspecto y el tamaño del voxel
    return volumen, volumen.shape, relacion_aspecto, tamaño_voxel


def MetadataDT(imagenes):
    '''
    Extrae y organiza metadatos importantes de las imágenes DICOM, incluidos datos del paciente y detalles técnicos de la imagen.

    Parámetros:
    
     imagenes:
         Lista de objetos DICOM que contienen los metadatos de las imágenes, incluyendo información del paciente y    propiedades de la imagen.

    Returns:
    
     metadatos_imagen: dict
         Diccionario con los siguientes metadatos:
            - 'Nombre del sujeto': Nombre del paciente.
            - 'Edad del sujeto': Edad del paciente.
            - 'Sexo del sujeto': Sexo del paciente.
            - 'Tipo de imagen': Modalidad de la imagen (ej. CT, MR).
            - 'Fecha de adquisición': Fecha de adquisición de la imagen.
            - 'Modelo del tomógrafo': Modelo del equipo utilizado.
            - 'Espesor del corte': Grosor de cada corte en el volumen.
            - 'Tamaño voxel': Dimensiones del voxel (espesor del corte y espaciamiento de píxeles).
            - 'Tamaño imagen completa en voxeles': Dimensiones de la imagen en términos de filas y columnas.
            - 'Tamaño imagen completa en mm': Dimensiones de la imagen en milímetros.
    '''
    
    # seleccionamos la primera imagen para extraer metadatos, ya que los de todas las imagenes de una carpeta son los mismos y hemos elegido la primera por elegir una, para que no devuelva lo mismo muchas veces.
    i = imagenes[0]
    
    # extraemos cada uno de los datos solicitados
    nombre_sujeto = i.PatientName if hasattr(i, 'PatientName') else "No disponible"
    edad_sujeto = i.PatientAge if hasattr(i, 'PatientAge') else "No disponible"
    sexo_sujeto = i.PatientSex if hasattr(i, 'PatientSex') else "No disponible"
    tipo_imagen = i.Modality if hasattr(i, 'Modality') else "No disponible"
    fecha_adquisicion = i.AcquisitionDate if hasattr(i, 'AcquisitionDate') else "No disponible"
    modelo_tomografo = i.ManufacturerModelName if hasattr(i, 'ManufacturerModelName') else "No disponible"
    espesor_corte = i.SliceThickness if hasattr(i, 'SliceThickness') else "No disponible"

    # si está disponible calculamos el tamaño de voxel
    pixel_spacing = i.PixelSpacing if hasattr(i, 'PixelSpacing') else None
    slice_thickness = i.SliceThickness if hasattr(i, 'SliceThickness') else None
    tamaño_voxel = (slice_thickness, pixel_spacing[0], pixel_spacing[1]) if pixel_spacing and slice_thickness else "No disponible"

    # dimensiones de la imagen en voxeles
    tamaño_imagen_voxeles = (i.Rows, i.Columns) if hasattr(i, 'Rows') and hasattr(i, 'Columns') else "No disponible"
    # dimensiones de la imagen en mm
    tamaño_imagen_mm = (i.Rows * tamaño_voxel[0], i.Columns * tamaño_voxel[1]) if tamaño_voxel != "No disponible" and tamaño_imagen_voxeles != "No disponible" else "No disponible"
    
    # incluimos los metadatos en un diccionario
    metadatos_imagen = {
        'Nombre del sujeto': nombre_sujeto,
        'Edad del sujeto': edad_sujeto,
        'Sexo del sujeto': sexo_sujeto,
        'Tipo de imagen': tipo_imagen,
        'Fecha de adquisición': fecha_adquisicion,
        'Modelo del tomógrafo': modelo_tomografo,
        'Espesor del corte': espesor_corte,
        'Tamaño voxel': tamaño_voxel,
        'Tamaño imagen completa en voxeles': tamaño_imagen_voxeles,
        'Tamaño imagen completa en mm': tamaño_imagen_mm,
    }
    
    return metadatos_imagen






import numpy as np
import matplotlib.pyplot as plt

def MuestraVolumen(volumen, tamaño_imagen, aspecto_axial, aspecto_coronal, aspecto_sagital, titulo="Volumen"):
    '''
    Muestra vistas axial, coronal y sagital de un volumen 3D DICOM.
    '''
    corte_axial = tamaño_imagen[0] // 2  
    corte_coronal = tamaño_imagen[1] // 2  
    corte_sagital = tamaño_imagen[2] // 2  

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(titulo, fontsize=16)

    # Vista axial
    axes[0].imshow(volumen[corte_axial, :, :], cmap='gray', aspect=aspect_axial)
    axes[0].set_title('Vista Axial')

    # Vista coronal
    axes[1].imshow(volumen[:, corte_coronal, :], cmap='gray', aspect=aspect_coronal)
    axes[1].set_title('Vista Coronal')

    # Vista sagital
    axes[2].imshow(volumen[:, :, corte_sagital], cmap='gray', aspect=aspect_sagital)
    axes[2].set_title('Vista Sagital')

    plt.tight_layout()
    plt.show()


def segmentacion_hu(volumen, umbrales_hu):
    '''
    Segmenta un volumen 3D según los umbrales de Hounsfield Units.
    '''
    segmentaciones = {}
    for tejido, (hu_min, hu_max) in umbrales_hu.items():
        segmentaciones[tejido] = np.logical_and(volumen >= hu_min, volumen <= hu_max).astype(np.uint8)
    return segmentaciones


def MuestraSegmentaciones(volumen, tamaño_imagen, aspecto_axial, aspecto_coronal, aspecto_sagital, umbrales_hu):
    '''
    Realiza la segmentación y muestra las vistas axial, coronal y sagital para cada tejido.
    '''
    # Obtener segmentaciones
    segmentaciones = segmentacion_hu(volumen, umbrales_hu)

    # Mostrar el volumen original
    MuestraVolumen(volumen, tamaño_imagen, aspecto_axial, aspecto_coronal, aspecto_sagital, titulo="Volumen Original")

    # Mostrar cada segmento por tejido
    for tejido, segmentacion in segmentaciones.items():
        MuestraVolumen(segmentacion, tamaño_imagen, aspecto_axial, aspecto_coronal, aspecto_sagital, titulo=f"Segmentación: {tejido.capitalize()}")


# Definir los umbrales de HU específicos para cada tejido
umbrales_hu = {
    "aire": (-1000, -700),
    "grasa": (-120, -50),
    "tejido blando": (0, 60),
    "hueso esponjoso": (150, 300),
    "hueso compacto": (300, 1500)
}


#NUEVO DE OTSU:


def Segmentar_Otsu(volumen):
    '''
    Segmenta tejidos en un volumen 3D utilizando el umbral Otsu.

    Parámetros:
     volumen:
         Array 3D con valores de imagen a segmentar.

    Returns:
     volumen_segmentado:
         Array 3D con las máscaras segmentadas.
    '''
    # Inicializar un volumen para las máscaras segmentadas
    volumen_segmentado = np.zeros(volumen.shape)
    
    # Recorrer cada corte del volumen
    for i in range(volumen.shape[0]):
        # Obtener la imagen del corte actual
        imagen = volumen[i]
        
        # Calcular el umbral de Otsu
        umbral = threshold_otsu(imagen)
        
        # Aplicar el umbral para crear la máscara segmentada
        volumen_segmentado[i] = imagen > umbral
    
    return volumen_segmentado


def MuestraSegmentacionOtsu(volumen, tamaño_imagen, aspecto_axial, aspecto_coronal, aspecto_sagital):
    '''
    Realiza la segmentación mediante Otsu y muestra las vistas axial, coronal y sagital.

    Parámetros:
     volumen:
         Array 3D del volumen de imágenes.
     tamaño_imagen:
         Dimensiones del volumen (profundidad, altura, ancho).
     aspecto_axial:
         Relación de aspecto para la vista axial.
     aspecto_coronal:
         Relación de aspecto para la vista coronal.
     aspecto_sagital:
         Relación de aspecto para la vista sagital.
    '''
    # Obtener el volumen segmentado
    volumen_segmentado = Segmentar_Otsu(volumen)

    # Mostrar el volumen segmentado en las vistas axial, coronal y sagital
    MuestraVolumen(volumen_segmentado, tamaño_imagen, aspecto_axial, aspecto_coronal, aspecto_sagital, titulo="Segmentación Otsu")


import os
from skimage import io
import numpy as np

def guarda_segmentaciones_hu(segmentaciones, tipo_corte="axial", carpeta_salida="imagenes_hu"):
    """
    Guarda las imágenes de las segmentaciones en archivos .png en una carpeta especificada.
    
    Args:
        segmentaciones: Diccionario con las segmentaciones de cada tejido.
        tipo_corte: Tipo de corte ("axial", "coronal", "sagital").
        carpeta_salida: Ruta de la carpeta donde se guardarán las imágenes.
    """
    # creamos carpeta de salida si no existe
    os.makedirs(carpeta_salida)
    
    # guardar cada segmento como una imagen individual
    for tejido, segmentacion in segmentaciones.items():
        # Seleccionar el corte de acuerdo al tipo especificado
        if tipo_corte == "axial":
            imagen = segmentacion[segmentacion.shape[0] // 2, :, :]
        elif tipo_corte == "coronal":
            imagen = segmentacion[:, segmentacion.shape[1] // 2, :]
        elif tipo_corte == "sagital":
            imagen = segmentacion[:, :, segmentacion.shape[2] // 2]
        else:
            print("Tipo de corte no válido. Usa 'axial', 'coronal' o 'sagital'.")
        
        
    nombre_archivo = f"{tejido}_{tipo_corte}.png"
    ruta_completa = carpeta_salida + "/" + nombre_archivo
    
    # Guardar la imagen en formato PNG
    io.imsave(ruta_completa, imagen.astype(np.uint8) * 255)  # Convertir a escala de grises
    print(f"Imagen guardada: {ruta_completa}")




import os
from skimage import io
import numpy as np

def GuardaSegmentacionOtsu(volumen_segmentado, tipo_corte="axial", carpeta_salida="imagenes_otsu", nombre_base="segmentacion"):
    """
    Guarda la imagen de segmentación Otsu en formato PNG en la carpeta especificada.
    
    Args:
        volumen_segmentado: Volumen 3D segmentado.
        tipo_corte: Tipo de corte ('axial', 'coronal', 'sagital').
        carpeta_salida: Carpeta donde se guardará la imagen.
        nombre_base: Nombre base para el archivo de imagen.
    """
    os.makedirs(carpeta_salida)
    
    # definir el corte según el tipo especificado
    if tipo_corte == "axial":
        indice = volumen_segmentado.shape[0] // 2
        imagen = volumen_segmentado[indice, :, :]
    elif tipo_corte == "coronal":
        indice = volumen_segmentado.shape[1] // 2
        imagen = volumen_segmentado[:, indice, :]
    elif tipo_corte == "sagital":
        indice = volumen_segmentado.shape[2] // 2
        imagen = volumen_segmentado[:, :, indice]
    else:
        print("Tipo de corte no válido. Usa 'axial', 'coronal' o 'sagital'.")
       

    # generar el nombre completo del archivo
    nombre_archivo = f"{nombre_base}_{tipo_corte}.png"
    ruta_completa = carpeta_salida + "/" + nombre_archivo
    
    # Guardar la imagen en formato PNG
    io.imsave(ruta_completa, imagen.astype(np.uint8) * 255)
    print(f"Imagen guardada en: {ruta_completa}")