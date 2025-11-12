##Sistema de Detección de Manipulación en Imágenes Digitales

## Descripción
Este proyecto desarrolla una herramienta capaz de detectar posibles manipulaciones en imágenes digitales mediante análisis automatizados.  
El sistema analiza metadatos, compresión, clonaciones y artefactos visuales para identificar zonas sospechosas.

## Funcionalidades
- Carga y análisis de imágenes sospechosas.  
- Detección de clonación por comparación de bloques.  
- Evaluación de compresión.
- Verificación de metadatos EXIF.  
- Generación de reporte visual y textual con nivel de confianza.

## Tecnologías Utilizadas
- Python 3.10+  
- OpenCV– Procesamiento de imágenes  
- NumPy*– Operaciones numéricas  
- Pillow (PIL) – Análisis de compresión JPEG  
- piexif– Lectura de metadatos EXIF  

## Arquitectura

El sistema sigue un enfoque de Programación Orientada a Objetos (POO) para mantener modularidad:

ImageForgeryDetector – Clase principal que gestiona el análisis.

CloningAnalyzer, CompressionAnalyzer, MetadataAnalyzer – Módulos de detección especializados.

ReportGenerator – Crea el reporte final con los resultados.

## Ejemplo de Uso
python
from detector import ImageForgeryDetector

detector = ImageForgeryDetector("imagen_sospechosa.jpg")

results = detector.run_analysis()

detector.generate_report(results)

## Resultados Esperados

-Imagen de salida con zonas manipuladas resaltadas.

-Reporte de texto con nivel de confianza e inconsistencias detectadas.

## Autores

Proyecto desarrollado por Mariana Morales y Florencia Ortiz Candeias
