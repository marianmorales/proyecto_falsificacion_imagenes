## Sistema de Detección de Manipulación en Imágenes Digitales

Este proyecto implementa un sistema capaz de detectar posibles manipulaciones en imágenes digitales mediante análisis automatizados.
El objetivo es identificar alteraciones como clonación de regiones, inconsistencias en compresión JPEG, modificaciones de metadatos EXIF y artefactos visuales que evidencien fraude o edición digital.

## Descripción General

El sistema analiza una imagen sospechosa utilizando diversas técnicas de procesamiento digital.
Cada módulo de análisis opera de forma independiente y aporta evidencia al resultado final, permitiendo generar un reporte completo con:

- Zonas sospechosas marcadas visualmente.

- Inconsistencias detectadas durante los análisis.

- Un nivel estimado de confianza sobre la posible manipulación.

## Funcionalidades Principales

- Carga y análisis automático de imágenes sospechosas

- Detección de clonación mediante comparación de bloques

- Evaluación de compresión con ELA y patrones JPEG

- Verificación de metadatos EXIF (modelo de cámara, software, fechas)

- Generación de un reporte completo:

- Imagen con zonas resaltadas

- Informe textual con descripción técnica de hallazgos

- Nivel de confianza de manipulación

## Tecnologías Utilizadas

-Python 3.10+

-OpenCV – Procesamiento y análisis de imágenes

-NumPy – Operaciones numéricas y manejo de matrices

-Pillow (PIL) – Análisis de compresión JPEG y ELA

-piexif – Lectura y validación de metadatos EXIF

## Arquitectura y Diseño (POO)

El proyecto está construido bajo un enfoque modular y orientado a objetos (POO).
Cada responsabilidad del sistema se encapsula en una clase especializada, lo que facilita la escalabilidad, el mantenimiento y la extensibilidad del análisis forense digital.

Clases Principales

- ImageForgeryDetector (Clase central del sistema). Se encarga de:

Gestionar la carga de la imagen de entrada.

Ejecutar secuencialmente los módulos de análisis.

Integrar y normalizar los resultados de cada analizador.

Preparar los datos finales para la generación del reporte.

## Analizadores Especializados

(todas estas clases heredan de BaseAnalyzer)

- CloningAnalyzer

Detecta posibles clonaciones mediante segmentación en bloques.

Utiliza métricas de distancia (p. ej., euclidiana) para comparar regiones similares.

- CompressionAnalyzer

Evalúa la estructura de compresión JPEG.

Ejecuta Error Level Analysis (ELA) para identificar zonas con compresión inconsistente, típicas de ediciones locales.

- MetadataAnalyzer

Extrae los metadatos EXIF de la imagen.

Valida inconsistencias como fechas alteradas, modelo de cámara incorrecto o software sospechoso.

- ReportGenerator

Responsable de la creación del informe final:

Genera una imagen con las zonas sospechosas resaltadas.

Produce un reporte textual detallando evidencia, inconsistencias y nivel estimado de manipulación.

## Ejemplo de Uso

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
