# QUICKSTART

## Ejecutar

```powershell
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Abrir `http://127.0.0.1:8000/docs`.

## Pruebas rapidas

```bash
curl http://127.0.0.1:8000/users
curl http://127.0.0.1:8000/users/1
curl -X PATCH http://127.0.0.1:8000/users/1 -H "Content-Type: application/json" -d "{\"role\":\"support\"}"
curl -X DELETE http://127.0.0.1:8000/users/3
```

Para probar errores, usa `/users/999`, un correo repetido y `PATCH /users/1` con `{}`. Las colecciones contienen ejemplos adicionales.