# TensorFlow con GPU en Windows usando WSL2

Configuración completa de **TensorFlow** para detectar y utilizar GPU **NVIDIA** en Windows 11/10 mediante **WSL2 (Ubuntu)**, con integración profesional en **VS Code** y **Jupyter Notebooks**.

## Tabla de Contenidos

- [Requisitos del Sistema](#requisitos-del-sistema)
- [1. Verificar GPU en WSL](#1-verificar-gpu-en-wsl)
- [2. Preparar Entorno Python](#2-preparar-entorno-python)
- [3. Instalar TensorFlow con CUDA](#3-instalar-tensorflow-con-cuda)
- [4. Configurar el Proyecto](#4-configurar-el-proyecto)
- [5. Integración con VS Code y Jupyter](#5-integración-con-vs-code-y-jupyter)
- [Apéndice A: Solución de Problemas](#apéndice-a-solución-de-problemas)
- [Apéndice B: Referencia Rápida de Comandos](#apéndice-b-referencia-rápida-de-comandos)

---

## Requisitos del Sistema

### Hardware
- **GPU NVIDIA** compatible con CUDA (RTX, GTX, A-series, etc.)
- **RAM**: Mínimo 8GB (16GB recomendado)

### Software
- **Windows 10/11** con WSL2 habilitado
- **Driver NVIDIA** instalado en Windows con soporte para CUDA en WSL2
- **Ubuntu 20.04 LTS o superior** instalado en WSL2
- **Python 3.8+**

> ⚠️ **Nota Crítica**: Con CUDA en WSL2, **solamente se instala el driver de Windows**. **NO** se instalan drivers Linux dentro de WSL. El driver de Windows es transparente a través de la capa CUDA.

---

## 1. Verificar GPU en WSL

Abre una terminal de Ubuntu (WSL2) y verifica que el driver és accesible:

```bash
nvidia-smi
```

**Salida esperada**: Información del driver NVIDIA y lista de GPUs disponibles.

```
Tue Feb 14 12:34:56 2026
+-------------------------+----------------------+
| NVIDIA-SMI 999.99       Driver Version: 999.99 |
+-------------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        |
| 0   NVIDIA GeForce RTX 3080    Off  | 00:1F.0     |
+-------------------------+----------------------+
```

Si `nvidia-smi` no funciona, consulta [Apéndice A](#gpu-no-detectada-en-wsl).

---

## 2. Preparar Entorno Python

### 2.1 Actualizar Paquetes del Sistema

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip
```

### 2.2 Crear Entorno Virtual Dedicado

```bash
python3 -m venv ~/tf
source ~/tf/bin/activate
```

### 2.3 Actualizar pip

```bash
pip install --upgrade pip
```

Verifica que estés usando la versión correcta:

```bash
which python
python --version
```

---

## 3. Instalar TensorFlow con CUDA

### 3.1 Instalar TensorFlow con Soporte GPU

```bash
pip install "tensorflow[and-cuda]"
```

Este comando instala:
- TensorFlow 2.x (última versión compatible)
- CUDA 12.x
- cuDNN
- Todas las dependencias necesarias

### 3.2 Verificar Detección de GPU

```bash
python -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__); print('GPUs detected:', tf.config.list_physical_devices('GPU'))"
```

**Salida esperada**:
```
TensorFlow version: 2.15.0
GPUs detected: [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
```

> ✅ Si ves la GPU listada, la configuración de CUDA es correcta.

---

## 4. Configurar el Proyecto

### 4.1 Crear Estructura de Directorios

```bash
mkdir -p ~/proyectos
```

### 4.2 Mover el Proyecto a Sistema Linux

```bash
# Copiar desde Windows (a través de /mnt/c)
cp -r /mnt/c/Users/usuario/Pictures/Proyecto_imagen_ia ~/proyectos/

# Navegar al proyecto
cd ~/proyectos/Proyecto_imagen_ia
```

### 4.3 Activar Entorno Virtual al Entrar

Asegúrate de siempre activar el entorno antes de trabajar:

```bash
source ~/tf/bin/activate
```

---

## 5. Integración con VS Code y Jupyter

### 5.1 Instalar Jupyter Kernel

Con el entorno activado, instala ipykernel y jupyter:

```bash
source ~/tf/bin/activate
python -m pip install -U ipykernel jupyter
```

### 5.2 Crear Kernel Dedicado "TF GPU"

```bash
python -m ipykernel install --user --name tf-gpu --display-name "Python (WSL TF GPU)"
```

Verifica que el kernel esté registrado:

```bash
jupyter kernelspec list
```

**Salida esperada**:
```
Available kernels:
  python3      /usr/share/jupyter/kernels/python3
  tf-gpu       /home/ismael/.local/share/jupyter/kernels/tf-gpu
```

### 5.3 Usar en VS Code

1. Abre VS Code desde la carpeta del proyecto:

   ```bash
   cd ~/proyectos/Proyecto_imagen_ia
   code .
   ```

2. En cualquier Notebook (`.ipynb`), haz clic en el selector de kernel (esquina superior derecha)

3. Selecciona **"Python (WSL TF GPU)"**

4. Verifica que GPU está disponible ejecutando esta celda:
   ```python
   import tensorflow as tf
   print("TensorFlow version:", tf.__version__)
   print("GPUs disponibles:", tf.config.list_physical_devices('GPU'))
   ```

---

## Apéndice A: Solución de Problemas

### GPU No Detectada en WSL

**Síntoma**: `nvidia-smi` no funciona o no reconoce la GPU.

**Soluciones**:

1. Verifica que WSL2 está habilitado:
   ```powershell
   wsl -l -v
   ```
   Confirma que tu distribución tenga versión 2.

2. Reinstala el driver NVIDIA en Windows asegurándote de marcar la opción "CUDA support for WSL2"

3. Reinicia WSL:
   ```bash
   wsl --shutdown
   ```
   Luego abre una nueva terminal.

---

### TensorFlow No Detecta GPU

**Síntoma**: `tf.config.list_physical_devices('GPU')` devuelve lista vacía.

**Soluciones**:

1. Verifica que `nvidia-smi` funciona en WSL:
   ```bash
   nvidia-smi
   ```

2. Confirma que usas el Python del venv correcto:
   ```bash
   source ~/tf/bin/activate
   which python
   python --version
   pip show tensorflow
   ```

3. Reinstala TensorFlow:
   ```bash
   pip install --upgrade "tensorflow[and-cuda]"
   ```

4. Si persiste, limpia el caché y reinstala:
   ```bash
   pip uninstall tensorflow --yes
   python -m pip cache purge
   pip install "tensorflow[and-cuda]"
   ```

---

### Kernel Incorrecto en VS Code

**Síntoma**: VS Code muestra otro kernel o Python incorrectos.

**Solución**:

Recrea el kernel desde el venv:

```bash
source ~/tf/bin/activate
python -m pip install -U ipykernel jupyter
python -m ipykernel install --user --name tf-gpu --display-name "Python (WSL TF GPU)" --force
jupyter kernelspec list
```

Recarga VS Code (`Ctrl+Shift+P` > "Reload Window")

---

## Apéndice B: Referencia Rápida de Comandos

### Setup Inicial (Primera vez)
```bash
# Verificar GPU
nvidia-smi

# Actualizar sistema
sudo apt update && sudo apt install -y python3-venv python3-pip

# Crear y activar venv
python3 -m venv ~/tf
source ~/tf/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar TensorFlow
pip install "tensorflow[and-cuda]"

# Verificar GPU en TensorFlow
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### Configurar Jupyter Kernel
```bash
source ~/tf/bin/activate
python -m pip install -U ipykernel jupyter
python -m ipykernel install --user --name tf-gpu --display-name "Python (WSL TF GPU)"
jupyter kernelspec list
```

### Workflow Típico
```bash
# Iniciar sesión
cd ~/proyectos/Proyecto_imagen_ia
source ~/tf/bin/activate

# Lanzar VS Code
code .

# O usar Jupyter directamente
jupyter notebook
```

---

## Notas Adicionales

- **Persistencia de Activación**: Para que el venv se active automáticamente al abrir una terminal en este proyecto, considera agregar `source ~/tf/bin/activate` a tu `.bashrc` o crear un script de inicio.

- **Multigpu**: Si tienes múltiples GPUs, TensorFlow las detectará automáticamente. Consulta la [documentación oficial de TensorFlow](https://www.tensorflow.org/guide/gpu) para control granular.

- **Versiones Específicas**: Si necesitas versiones específicas de CUDA o cuDNN, instala manualmente antes de TensorFlow o especifica la versión en pip.

---

**Última actualización**: Febrero 2026
