# INSTRUCCIONES - Guia de Configuracion de OpenRig

## Requisitos Previos

### Software necesario

| Software | Version minima | Proposito |
|----------|---------------|-----------|
| Node.js | 18.x | Frontend (React) |
| Python | 3.11+ | Backend (FastAPI) |
| Blender | 4.0+ | Procesamiento 3D (headless) |
| Docker | 24.x (opcional) | Contenedores para despliegue |
| Docker Compose | 2.x (opcional) | Orquestacion de servicios |

---

## 1. Desarrollo Local (sin Docker)

### 1.1 Configurar el Backend

```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual de Python
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt

# Verificar que Blender esta instalado y accesible
blender --version
# Si no esta en el PATH, configurar la variable de entorno:
export BLENDER_PATH=/ruta/a/blender

# Iniciar el servidor de desarrollo
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

El backend estara disponible en `http://localhost:8000`.
La documentacion interactiva de la API esta en `http://localhost:8000/docs`.

#### Variables de entorno del backend

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `BLENDER_PATH` | `blender` | Ruta al ejecutable de Blender |
| `DATA_DIR` | `./data` | Directorio para archivos de datos |
| `MAX_UPLOAD_SIZE` | `52428800` (50MB) | Tamano maximo de upload en bytes |
| `CORS_ORIGINS` | `http://localhost:3000` | Origenes permitidos (separados por coma) |

### 1.2 Configurar el Frontend

```bash
# Navegar al directorio del frontend
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estara disponible en `http://localhost:3000`.
El proxy del dev server redirige automaticamente `/api/*` al backend en el puerto 8000.

#### Variables de entorno del frontend

Crear archivo `.env` en `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

> Nota: En modo desarrollo con `npm run dev`, el proxy de Vite maneja las peticiones al backend automaticamente, por lo que `VITE_API_URL` no es estrictamente necesario.

### 1.3 Ejecutar tests

```bash
# Tests del backend
cd backend
pip install pytest httpx
pytest tests/ -v

# Type check del frontend
cd frontend
npx tsc --noEmit

# Build de produccion del frontend
npm run build
```

---

## 2. Despliegue con Docker

### 2.1 Desarrollo con Docker

```bash
# Desde la raiz del proyecto
# Solo levanta el backend con Blender (el frontend se ejecuta con npm run dev)
docker-compose -f docker-compose.dev.yml up --build
```

Esto levanta:
- **Backend** en `http://localhost:8000` con hot-reload y Blender instalado

Luego en otra terminal:
```bash
cd frontend
npm run dev
```

### 2.2 Produccion con Docker Compose

```bash
# Construir y levantar todos los servicios
docker-compose up --build -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio especifico
docker-compose logs -f backend

# Detener servicios
docker-compose down
```

Esto levanta 3 servicios:
- **Frontend** (Nginx sirviendo la build de React) en el puerto 3000
- **Backend** (FastAPI + Blender) en el puerto 8000
- **Nginx** (reverse proxy) en el puerto 80

### 2.3 Estructura de servicios Docker

```
                    Puerto 80
                       |
                    [Nginx]
                    /      \
                  /          \
        [Frontend:3000]   [Backend:8000]
         (React SPA)      (FastAPI + Blender)
                              |
                         [/app/data]
                          (volumen)
```

---

## 3. Instalar Blender (Headless)

Blender es necesario para el procesamiento 3D (rigging, animaciones, export).

### 3.1 Linux (Ubuntu/Debian)

```bash
# Opcion 1: Desde snap
sudo snap install blender --classic

# Opcion 2: Descarga directa
BLENDER_VERSION=4.0.2
wget https://download.blender.org/release/Blender4.0/blender-${BLENDER_VERSION}-linux-x64.tar.xz
tar -xf blender-${BLENDER_VERSION}-linux-x64.tar.xz
sudo mv blender-${BLENDER_VERSION}-linux-x64 /opt/blender
sudo ln -s /opt/blender/blender /usr/local/bin/blender

# Verificar
blender --version
```

### 3.2 macOS

```bash
# Con Homebrew
brew install --cask blender

# Verificar
/Applications/Blender.app/Contents/MacOS/Blender --version

# Configurar variable de entorno si es necesario
export BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender
```

### 3.3 Windows

1. Descargar desde https://www.blender.org/download/
2. Instalar normalmente
3. Agregar al PATH: `C:\Program Files\Blender Foundation\Blender 4.0\`
4. O configurar `BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.0\blender.exe`

### 3.4 ARM64 (Oracle Cloud / Raspberry Pi)

```bash
BLENDER_VERSION=4.0.2
wget https://download.blender.org/release/Blender4.0/blender-${BLENDER_VERSION}-linux-arm64.tar.xz
tar -xf blender-${BLENDER_VERSION}-linux-arm64.tar.xz
sudo mv blender-${BLENDER_VERSION}-linux-arm64 /opt/blender
sudo ln -s /opt/blender/blender /usr/local/bin/blender
```

### 3.5 Verificar que Blender funciona headless

```bash
# Test basico
blender --background --python-expr "import bpy; print('Blender OK:', bpy.app.version_string)"

# Test de script
blender --background --python backend/blender_scripts/generate_preview.py -- --help
```

---

## 4. Poblar la Biblioteca de Animaciones

El sistema necesita archivos de animacion (BVH o FBX) en `backend/data/animations/`.

### 4.1 Estructura de carpetas

```
backend/data/animations/
  locomotion/        # Caminar, correr, saltar
  combat/            # Golpes, patadas, bloqueos
  social/            # Saludar, bailar, sentarse
  misc/              # Recoger objetos, empujar, etc.
```

### 4.2 Agregar una animacion

Para cada animacion necesitas:
1. **El archivo BVH o FBX** (ej: `walk_01.bvh`)
2. **Un archivo JSON de metadatos** con el mismo nombre (ej: `walk_01.json`)

Ejemplo de archivo de metadatos `walk_01.json`:
```json
{
  "id": "walk_01",
  "name": "Walk",
  "category": "locomotion",
  "duration_seconds": 1.0,
  "fps": 30,
  "loop": true,
  "root_motion": true,
  "tags": ["walk", "locomotion", "cycle"],
  "description": "Standard walk cycle, loops seamlessly"
}
```

### 4.3 Fuentes de animaciones gratuitas

| Fuente | URL | Formato | Licencia |
|--------|-----|---------|----------|
| CMU Motion Capture | http://mocap.cs.cmu.edu | BVH | Dominio publico |
| Bandai Namco Research | https://github.com/BandaiNamcoResearchInc | BVH | CC-BY-4.0 |
| Rokoko Free Pack | https://www.rokoko.com/free-mocap | FBX/BVH | Gratis (starter) |
| Mixamo | https://www.mixamo.com | FBX | Gratis (uso personal) |

### 4.4 Modo demo

Si no hay animaciones en disco, la API devuelve una lista de animaciones demo para que la interfaz funcione. Las animaciones demo no tienen archivos reales, pero permiten probar la interfaz completa.

---

## 5. Despliegue en Oracle Cloud (Free Tier)

### 5.1 Recursos del Free Tier

- 4 ARM OCPUs (Ampere A1)
- 24 GB RAM
- 200 GB Block Storage
- 10 TB/mes transferencia de datos

### 5.2 Crear la instancia

```bash
# Con OCI CLI
oci compute instance launch \
    --availability-domain "AD-1" \
    --compartment-id $COMPARTMENT_ID \
    --shape "VM.Standard.A1.Flex" \
    --shape-config '{"ocpus": 4, "memoryInGBs": 24}' \
    --image-id $UBUNTU_ARM_IMAGE_ID \
    --subnet-id $SUBNET_ID \
    --assign-public-ip true
```

### 5.3 Configurar la instancia

```bash
# Conectar por SSH
ssh ubuntu@<IP_PUBLICA>

# Instalar Docker
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
# Cerrar sesion y volver a entrar

# Clonar el repositorio
git clone <URL_DEL_REPO> openrig
cd openrig

# Construir y desplegar
docker compose up --build -d
```

### 5.4 Configurar el firewall

En la consola de Oracle Cloud:
1. Ir a Networking > Virtual Cloud Networks > tu VCN
2. Security Lists > Default Security List
3. Agregar Ingress Rules:
   - Puerto 80 (HTTP) desde 0.0.0.0/0
   - Puerto 443 (HTTPS) desde 0.0.0.0/0

En la instancia:
```bash
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

### 5.5 Configurar HTTPS con Let's Encrypt

```bash
# Instalar certbot
sudo apt install -y certbot

# Obtener certificado (detener nginx primero)
docker compose stop nginx
sudo certbot certonly --standalone -d tudominio.com
docker compose up -d nginx
```

Luego actualizar `nginx/nginx.conf` para usar los certificados SSL.

---

## 6. API Reference Rapida

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/upload` | Subir modelo 3D (multipart/form-data) |
| GET | `/api/models/{id}/preview.glb` | Descargar preview del modelo |
| POST | `/api/rig` | Procesar modelo con marcadores |
| GET | `/api/models/{id}/rigged.glb` | Descargar modelo riggeado |
| GET | `/api/animations` | Listar animaciones disponibles |
| POST | `/api/apply-animation` | Aplicar animacion a modelo |
| GET | `/api/models/{id}/animated/{anim}.glb` | Descargar modelo animado |
| POST | `/api/export` | Exportar modelo final (FBX/GLB) |
| GET | `/api/downloads/{filename}` | Descargar archivo exportado |
| GET | `/api/models/{id}/status` | Estado de procesamiento |

Documentacion interactiva completa: `http://localhost:8000/docs`

---

## 7. Estructura del Proyecto

```
AutoRiggerWebsite/
|-- frontend/                    # Aplicacion React + Three.js
|   |-- src/
|   |   |-- components/          # Componentes React
|   |   |   |-- Layout/          # Header, Sidebar, MainLayout
|   |   |   |-- Upload/          # Panel de carga de modelos
|   |   |   |-- Viewer/          # Visor 3D (Three.js)
|   |   |   |-- MarkerEditor/    # Editor de marcadores
|   |   |   |-- Animation/       # Biblioteca y reproductor
|   |   |   +-- Export/          # Panel de exportacion
|   |   |-- stores/              # Estado global (Zustand)
|   |   |-- services/            # Cliente API (Axios)
|   |   |-- types/               # Tipos TypeScript
|   |   +-- utils/               # Utilidades
|   |-- package.json
|   |-- vite.config.ts
|   +-- Dockerfile
|
|-- backend/                     # API FastAPI + Blender
|   |-- app/
|   |   |-- api/routes/          # Endpoints de la API
|   |   |-- services/            # Logica de negocio
|   |   |-- models/              # Schemas Pydantic
|   |   +-- utils/               # Utilidades
|   |-- blender_scripts/         # Scripts de Blender
|   |   |-- auto_rig.py          # Rigging automatico
|   |   |-- apply_animation.py   # Retargeting de animaciones
|   |   |-- export_model.py      # Exportacion multi-animacion
|   |   +-- generate_preview.py  # Conversion a GLB preview
|   |-- data/
|   |   |-- animations/          # Biblioteca de animaciones (BVH/FBX + JSON)
|   |   |-- uploads/             # Modelos subidos (temporal)
|   |   |-- processed/           # Modelos procesados (cache)
|   |   +-- exports/             # Archivos exportados (temporal)
|   |-- tests/
|   |-- requirements.txt
|   +-- Dockerfile
|
|-- docker-compose.yml           # Produccion (frontend + backend + nginx)
|-- docker-compose.dev.yml       # Desarrollo (solo backend con Docker)
|-- nginx/nginx.conf             # Configuracion de reverse proxy
|-- .gitignore
|-- CLAUDE.md                    # Especificacion del proyecto
+-- INSTRUCCIONES.md             # Este archivo
```

---

## 8. Flujo de Trabajo del Usuario

1. **Subir modelo** - El usuario arrastra un archivo OBJ/FBX/GLB al panel de carga
2. **Colocar marcadores** - El sistema pide al usuario que haga clic en 8 puntos anatomicos del modelo (menton, munecas, codos, rodillas, pelvis)
3. **Auto-Rig** - El backend procesa el modelo con Blender + Rigify usando los marcadores como guia
4. **Explorar animaciones** - El usuario navega la biblioteca de animaciones y las previsualiza
5. **Agregar animaciones** - El usuario selecciona las animaciones que quiere incluir
6. **Exportar** - El usuario elige formato (FBX/GLB) y descarga el modelo riggeado con animaciones

---

## 9. Solucion de Problemas

### El backend no inicia
- Verificar que Python 3.11+ esta instalado: `python3 --version`
- Verificar que las dependencias estan instaladas: `pip list | grep fastapi`
- Verificar los permisos del directorio data: `ls -la backend/data/`

### Blender no se encuentra
- Verificar la instalacion: `blender --version`
- Configurar la ruta: `export BLENDER_PATH=/ruta/completa/a/blender`
- En Docker, Blender se instala automaticamente

### El frontend no conecta con el backend
- Verificar que el backend esta corriendo en el puerto 8000
- Verificar la configuracion del proxy en `vite.config.ts`
- Comprobar CORS: la variable `CORS_ORIGINS` debe incluir `http://localhost:3000`

### Error "File too large"
- El limite por defecto es 50 MB
- Ajustar `MAX_UPLOAD_SIZE` en las variables de entorno
- En nginx, ajustar `client_max_body_size`

### Las animaciones no aparecen
- Verificar que hay archivos JSON en `backend/data/animations/*/`
- Si no hay archivos, la API devuelve datos demo automaticamente
- Para agregar animaciones reales, seguir la seccion 4 de este documento

### Docker no construye
- Verificar que Docker esta corriendo: `docker info`
- Limpiar cache: `docker system prune -a`
- Verificar espacio en disco: `df -h`
