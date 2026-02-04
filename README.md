# 🔍 Offert Hunt – Comparador de Precios

**Offert Hunt** es un proyecto de portafolio desarrollado en **Python, SQL y HTML** que permite buscar un artículo específico y comparar automáticamente los precios entre múltiples tiendas online para encontrar la **mejor oferta disponible**.

---

## 🚀 Características

- 🔎 Búsqueda de productos por nombre  
- 🕷️ Scraping de múltiples tiendas online  
- 📊 Comparación automática de precios  
- 🏷️ Identificación de la mejor oferta  
- 🧩 Arquitectura modular de scrapers  
- 💼 Proyecto orientado a portafolio técnico  

---

## 🛠️ Tecnologías Utilizadas

- Python  
- SQL  
- HTML  
- Requests / BeautifulSoup / Selenium  
- Base de datos para historial de precios  

---

## 📁 Estructura del Proyecto

```text
Team-404/
├── backend/
├── frontend/
├── logic/
├── notifications/
├── scraping/
└── .gitignore
```
---

## ⚙️ Instalación

Cloná el repositorio y entrá al directorio del proyecto:
```bash
git clone https://github.com/usuario/offert-hunt.git
cd offert-hunt
```
Instalá las dependencias necesarias:
```bash
pip install -r requirements.txt
```
## ▶️ Ejecución del Proyecto
🧪 Activar entorno virtual y levantar el backend
```bash
# Permitir la ejecución de scripts en PowerShell (solo una vez)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# Ingresar al backend
cd backend

# Levantar el servidor con Uvicorn
uvicorn main:app --reload
```
