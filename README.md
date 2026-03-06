<h1 align="center">StyleMePal AI 🧥 - Tu asistente personal de armario virtual y generación de outfits</h1>

<img src="https://drive.google.com/uc?export=view&id=1Vcb--qa_OF1GnT2Izk4mvg9i7-vp9TKP">

**StyleMePal AI** es un proyecto innovador de Inteligencia Artificial enfocado en la moda. Esta aplicación resuelve el problema de "Cold Start" en la compatibilidad de moda permitiendo a los usuarios digitalizar su propio armario y generar *outfits* dinámicos basados en preferencias de estilo, condiciones climáticas y reglas taxonómicas.

> [Presentación del proyecto Canva]()
>
> [Presentación del proyecto PDF]()
>
> [Video explicatorio]()
> 
> [App desplegada](https://stylemepal.duckdns.org/)
>
> [Documentación]()

## Índice

1. [Descripción del proyecto](#1-descripción-del-proyecto)
2. [Visión y propósito](#2-visión-y-propósito)
3. [Características principales](#3-características-principales)
4. [Estructura del Proyecto](#4-estructura-del-proyecto)
5. [Tecnologías utilizadas](#5-tecnologías-principales)
6. [Arquitectura](#6-arquitectura)
7. [¿Cómo funciona nuestro sistema?](#7-cómo-funciona-nuestro-sistema)
8. [Obtención de los datos](#8-obtención-de-los-datos)
9. [Aplicación Web](#9-aplicación-web)
10. [Instalación y despliegue](#10-instalación-rápida-y-despliegue)
11. [Alcance del proyecto](#11-alcance-del-proyecto)
12. [Recursos utilizados](#12-recursos-utilizados)
13. [Autores](#13-autores-y-distribución-de-tareas)
14. [Citación y trabajo original](#14-citación-y-trabajo-original)
15. [Licencia](#15-licencia)

## 1. Descripción del proyecto

StyleMePal AI es un sistema generador de *outfits* basado en el dominio de "conjunto cerrado" (el armario personal del usuario). El sistema procesa imágenes de la ropa del usuario y las proyecta en un "Espacio de Estilo" latente, donde la proximidad geométrica equivale a la compatibilidad estilística.

A diferencia de los sistemas de recomendación comerciales que sugieren ropa para comprar, nuestra plataforma utiliza un modelo de Grafo Relacional (FashionRGCN) y Modelos de Lenguaje (LLM) para combinar prendas que el usuario **ya posee**, aplicando reglas categóricas estrictas (ej. un *top* se combina con *bottoms*, no con otros *tops*).

## 2. Visión y Propósito

El propósito de StyleMePal AI es terminar con la frustración diaria de "no saber qué ponerse". Nuestra visión es democratizar el acceso a un estilista personal mediante el uso de inteligencia artificial multimodal, ayudando a los usuarios a maximizar el uso de sus prendas existentes de manera creativa, coherente y adaptada al contexto del mundo real (clima y eventos).

## 3. Características Principales

- **Digitalización del Armario**: Sube fotos de tus prendas tomadas con tu teléfono.
- **Extracción de Metadatos Dinámicos**: Etiquetado *Zero-Shot* automático de estilo y clima usando FashionCLIP.
- **Generación Conversacional**: Pide *outfits* en lenguaje natural (ej. "Un conjunto para un concierto de verano en Madrid").
- **Motor de Reglas Taxonómicas**: Garantiza conjuntos lógicamente viables (Tops + Bottoms + Zapatos + Accesorios).
- **IA de Proximidad de Estilo**: Integración de redes neuronales de grafos (GNN) para asegurar que las prendas combinen visualmente.

## 4. Estructura del Proyecto

```
.
├── app/
│   ├── back/             # Lógica del servidor y API
│   └── front/            # Interfaz de usuario y cliente
├── data/                 # Conjuntos de datos y recursos de datos
├── docs/                 # Documentación del proyecto y artefactos
├── models/               # Modelos entrenados 
├── notebooks/            # Jupyter Notebooks para experimentación
├── reports/              # Reportes generados y análisis
├── tests/                # Jupyter Notebooks pruebas de los modelos
├── .dockerignore         # Archivos excluidos de Docker
├── .gitignore            # Archivos excluidos de Git
├── LICENSE               # Licencia del proyecto
├── README.md             # Documentación principal
└── docker-compose.yml    # Orquestación de contenedores Docker
```

## 5. Tecnologías Principales

- **Frontend**: Angular, TypeScript, Nginx (Proxy Inverso).
- **Backend**: Python, FastAPI.
- **Almacenamiento (Base de Datos Híbrida)**: PostgreSQL (datos relacionales) + extensión **pgvector** (búsqueda de similitud vectorial).
- **IA & Machine Learning**:
    - **FashionCLIP**: Para extracción de embeddings visual-semánticos (512 dimensiones) y metadatos dinámicos.
    - **FashionRGCN**: Red Neuronal Convolucional de Grafos Relacional para embeddings conscientes del tipo (Type-Aware Embeddings).
    - **CategoryClassifierNN**: Red neuronal para classificacion de categoria de prendas.
    - **Groq y ollama**: Para el razonamiento y extracción de filtros mediante lenguaje natural.
- **DevOps**: Docker, Docker Compose.

## 6. Arquitectura

<img src="https://drive.google.com/uc?export=view&id=104yn-aC_FW-YoN0b3DHvzrXy3VA85Zel">

## 7. ¿Cómo funciona nuestro sistema? 

La verdadera inteligencia de **StyleMePal AI** radica en su arquitectura desacoplada. Para garantizar rapidez y precisión, el motor del sistema se divide en dos flujos de trabajo principales, tal y como se ilustra en el diagrama:

### Flujo 1: Ingesta y Digitalización (De la cámara a la Base de Datos)
<img src="https://drive.google.com/uc?export=view&id=1xL_TLTmz9U07iPKfXk-lUH_sH81fpps4">

### Flujo 2: Inferencia y Recomendación (Del *Prompt* al *Outfit*)
<img src="https://drive.google.com/uc?export=view&id=1EX3Edu29V9NajjJCfNlC7r9ZZJzZchgg">

## 8. Obtención de los datos

Para optimizar el desarrollo y evitar la tediosa fase de limpieza de datos en crudo, el entrenamiento y la validación de nuestros modelos se basaron en dos datasets de la comunidad previamente refactorizados y estandarizados.

- [**Polyvore-Outfits**](https://huggingface.co/datasets/owj0421/polyvore-outfits): Utilizado para el entrenamiento del modelo **FashionRGCN**. Este dataset contiene grafos limpios de compatibilidad de moda, esenciales para aprender los pesos relacionales entre las 11 categorías distintas.
- [**Polyvore**](https://huggingface.co/datasets/owj0421/polyvore): Utilizado para entrenar y validar nuestro **Modelo de Clasificación de Categorías**. Proporciona imágenes limpias y categorizadas correctamente, eliminando el ruido de etiquetado (Label Noise).

Para más información, consulte los cuadernos en la carpeta `notebooks`.

### ⚙️ Procesamiento e Inferencia (El Modelo)

1. **Extracción de Características (Fase 1)**: FashionCLIP toma la imagen de la prenda y genera un vector de 512 dimensiones.
2. **Generación de Metadatos (Fase 2)**: Ese vector pasa por el modelo de classificacion de categoria para predecir la categoria y por tareas *Zero-Shot* de alineación texto-imagen para predecir si la prenda es casual, formal, de verano, invierno, etc.
3. **Proyección GNN (Fase 3)**: El vector entra al FashionRGCN actuando como un nodo aislado. La red aplica matrices de peso específicas por relación categórica y comprime el dato en un vector de estilo final de 128 dimensiones.
4. **Búsqueda Vectorial**: Usando la distancia L2 en `pgvector`, el sistema encuentra los vecinos más cercanos dentro del armario restringido del usuario.

## 9. Aplicación Web

La aplicación está dividida en módulos principales:

### **Login y registro**

<img src="https://drive.google.com/uc?export=view&id=1mjzQHrra7UfAdrzdhKLd-GT0_yTJH1s3">
<img src="https://drive.google.com/uc?export=view&id=16xuPste-f8u701opEdMVTqklcUk_QnZ0">

### **Armario Virtual (Virtual Wardrobe)**
Digitaliza y clasifica automáticamente las fotos de tu ropa para procesarlas y almacenarlas en tu inventario.
<img src="https://drive.google.com/uc?export=view&id=1wW8CYzv-UtXcN2NJY3qIE-_MzuD84ugY">

### **Interfaz Conversacional (Prompt Filter)**
Interactúa mediante texto natural para que la IA filtre tu ropa automáticamente según la ocasión y el clima.
<img src="https://drive.google.com/uc?export=view&id=1w2cBoy58QRB05TEko7ErbxFsxYcJGgkQ">

### **El Generador de Outfits**
Crea instantáneamente el conjunto perfecto calculando la compatibilidad de estilo entre tus prendas disponibles.
<img src="https://drive.google.com/uc?export=view&id=1EIUXBqL-UomABUxZ7w7PI0gd_0JCURH-">

### **Dashboard**
Panel principal para visualizar de un vistazo las estadísticas de tu armario y gestionar tus outfits generados.
<img src="https://drive.google.com/uc?export=view&id=1kYXwp6LIPvnfpYjkdvbLEJBBbNBJz1ez">

## 10. **Instalación Rápida y Despliegue**

Sigue estos pasos para clonar el repositorio y levantar los contenedores con Docker:

1. **Clona el repositorio:**
    ```Bash
    git clone https://github.com/TFM-OUTFIT-IA/stylemepal.git
    cd stylemepal-ai
    ```
    
2. **Levanta los contenedores con Docker:**
Asegúrate de tener Docker y Docker Compose instalados. La configuración de contenedores levantará Angular, FastAPI, PostgreSQL (con pgvector)
    
    ```Bash
    docker compose build
    docker compose up -d
    ```
    
3. **Accede a la aplicación:**
    - Frontend: `http://localhost:4200` 
    - Backend API: `http://localhost:8000/docs` para acceder a la especificación Swagger de FastAPI.

## 11. Alcance del Proyecto

StyleMePal AI demuestra la viabilidad de implementar sistemas de recomendación complejos en entornos de conjuntos cerrados. Abarca desde la ingesta de datos no estructurados (imágenes de cámaras móviles) hasta el despliegue completo de un pipeline de *Machine Learning* apoyado por bases de datos vectoriales y agente IA para el filtrado dinámico de metadatos.

## 12. Recursos utilizados
- [Paper: Learning Type-Aware Embeddings for Fashion Compatibility *(Vasileva et al., ECCV 2018)*](https://arxiv.org/pdf/1803.09196)
- [Polyvore-Outfits](https://huggingface.co/datasets/owj0421/polyvore-outfits)
- [Polyvore](https://huggingface.co/datasets/owj0421/polyvore)
- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [pgvector repo](https://github.com/pgvector/pgvector)
- [FashionCLIP repo](https://github.com/patrickjohncyh/fashion-clip)
- [Angular Framework](https://v17.angular.io/docs)
- [Gemini](https://gemini.google.com/app)
- [Claude](https://claude.ai/)


## 13. Autores y Distribución de tareas

Este proyecto ha sido desarrollado equitativamente por el siguiente equipo:

- **Ismael Sihammou Anahnah** - 33.33%
- **Juan Francisco Chacon Macias** - 33.33%
- **Ismael Guerrero Martin** - 33.33%

## 14. Citación y trabajo original

```
@misc{vasileva2018learningtypeawareembeddingsfashion,
      title={Learning Type-Aware Embeddings for Fashion Compatibility},
      author={Mariya I. Vasileva and Bryan A. Plummer and Krishna Dusad and Shreya Rajpal and Ranjitha Kumar and David Forsyth},
      year={2018},
      eprint={1803.09196},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={[https://arxiv.org/abs/1803.09196](https://arxiv.org/abs/1803.09196)},
}
```

## 15. Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

⭐ ¡Si te parece interesante nuestra solución al problema de compatibilidad de moda, no dudes en darnos una estrella en GitHub!