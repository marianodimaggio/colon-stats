# Cómo crear el repo

## 1. Crear el repositorio vacío en GitHub

En github.com, botón New repository.

- Nombre: `colon-stats`
- Visibilidad: **privado** conviene, al menos al principio
- **No** tildar "Add a README", "Add .gitignore" ni licencia: ya vienen en el paquete

## 2. Subir el contenido

Descomprimir `colon-stats.zip`, entrar a la carpeta y:

```bash
cd colon-stats
git init
git add .
git commit -m "Kit de estadísticas de Colón: temporada 2026 completa"
git branch -M main
git remote add origin https://github.com/<usuario>/colon-stats.git
git push -u origin main
```

## 3. Probar que funciona

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdir datos
# copiar ahí matches.csv, players.csv y tabla.csv
python3 fecha.py 36 --matches datos/matches.csv --players datos/players.csv \
    --tabla datos/tabla.csv --vs 35
```

Tiene que dejar en `salida/` las trece placas, el HTML y el PDF de la fecha 36.
Si eso sale igual que lo publicado, el repo quedó bien.

## 4. De acá en adelante

Cada fecha:

```bash
git pull
# bajar los CSV a datos/
python3 fecha.py 37 ... --solo-calculo     # mirar los números
cp config/fechas/_plantilla.json config/fechas/f37.json
# completar f37.json
python3 fecha.py 37 ...                     # generar todo
git add config/fechas/f37.json
git commit -m "Fecha 37"
git push
```

Lo único que se versiona de cada fecha es el JSON de configuración, que pesa unos
pocos KB. Los CSV de entrada y las imágenes de salida quedan fuera por el `.gitignore`,
porque se pueden regenerar.

---

# Publicar la página de métricas

El repo trae `docs/index.html`, una página que explica qué mide cada estadística.
Para que quede online gratis con GitHub Pages:

1. En el repo, **Settings → Pages**
2. En *Source*, elegir **Deploy from a branch**
3. Branch: `main`, carpeta: **`/docs`**
4. Save

A los dos minutos queda en `https://<usuario>.github.io/colon-stats/`.

Ojo: GitHub Pages solo funciona con repos públicos, salvo que tengas plan pago. Si
querés el código privado y la página pública, la alternativa es un repo aparte solo
para la web, o subir ese HTML a Netlify como hiciste con el simulador.

Antes de publicar, cambiar en `docs/index.html` el link que dice
`https://github.com/` por la URL real del repo.
