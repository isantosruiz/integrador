# Calculadora de integrales simbólicas

Aplicacion web en Python para calcular integrales simbólicas (indefinidas y definidas) con SymPy y mostrar el resultado en LaTeX.

## Estructura

- `api/index.py`: backend Flask con endpoint `/integrate`.
- `api/templates/index.html`: interfaz web con formulario y render LaTeX (MathJax).
- `requirements.txt`: dependencias.
- `vercel.json`: configuracion de despliegue para Vercel.

## Ejecutar localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run
```

Abre: `http://127.0.0.1:5000`

## Despliegue en Vercel

1. Sube este proyecto a un repositorio Git.
2. Importa el repositorio en Vercel.
3. Vercel detectara `vercel.json` y desplegara `api/index.py` como funcion Python.
