##Sistema de Detección de Manipulación en Imágenes Digitales

Este proyecto implementa un sistema capaz de detectar posibles manipulaciones en imágenes digitales mediante análisis automatizados.
El objetivo es identificar alteraciones como clonación de regiones, inconsistencias en compresión JPEG, modificaciones de metadatos EXIF y artefactos visuales que evidencien fraude o edición digital.

##Descripción General

El sistema analiza una imagen sospechosa utilizando diversas técnicas de procesamiento digital.
Cada módulo de análisis opera de forma independiente y aporta evidencia al resultado final, permitiendo generar un reporte completo con:

Zonas sospechosas marcadas visualmente.

Inconsistencias detectadas durante los análisis.

Un nivel estimado de confianza sobre la posible manipulación.

##Funcionalidades Principales

- Carga y análisis automático de imágenes sospechosas

- Detección de clonación mediante comparación de bloques

- Evaluación de compresión con ELA y patrones JPEG

- Verificación de metadatos EXIF (modelo de cámara, software, fechas)

- Generación de un reporte completo:

-Imagen con zonas resaltadas

-Informe textual con descripción técnica de hallazgos

-Nivel de confianza de manipulación

## Tecnologías Utilizadas

-Python 3.10+

-OpenCV – Procesamiento y análisis de imágenes

-NumPy – Operaciones numéricas y manejo de matrices

-Pillow (PIL) – Análisis de compresión JPEG y ELA

-piexif – Lectura y validación de metadatos EXIF

## Arquitectura y Diseño (POO)

El proyecto está desarrollado siguiendo un enfoque modular basado en Programación Orientada a Objetos (POO). Cada componente del análisis se implementa como una clase especializada, permitiendo escalabilidad y fácil mantenimiento.

 Clases Principales
 ImageForgeryDetector

Clase central del sistema:

Carga la imagen

Ejecuta los módulos de análisis

Consolida los resultados

Analizadores especializados

(Heredan de una clase base BaseAnalyzer)

CloningAnalyzer
Detecta clonación mediante segmentación en bloques y comparación por distancia.

CompressionAnalyzer
Analiza niveles de compresión y genera ELA para identificar zonas editadas.

MetadataAnalyzer
Extrae y valida metadatos EXIF, detectando posibles inconsistencias.

ReportGenerator

Genera:

Imagen con resaltado de zonas sospechosas

Reporte textual con resultados detallados

##Ejemplo de Uso

from detector import ImageForgeryDetector

detector = ImageForgeryDetector("imagen_sospechosa.jpg")

results = detector.run_analysis()

detector.generate_report(results)

## Resultados Esperados

- Imagen procesada con regiones sospechosas marcadas

- Reporte detallado con:

-Evidencia encontrada por cada módulo

-Inconsistencias en estructura, compresión o metadatos

-Nivel de confianza general de manipulación

## Autores

Proyecto desarrollado por:

Mariana Morales

Florencia Ortiz Candeias
