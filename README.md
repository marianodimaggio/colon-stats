# colon-stats

Generador de los hilos de estadísticas de Colón de Santa Fe para X
([@MarianoDiMaggio](https://x.com/MarianoDiMaggio)). Produce las placas 1080×1080,
los textos de los tuits, un HTML con botones para copiar y un PDF para compartir.

Un comando por fecha. El código no se toca: lo que cambia cada semana vive en
`config/fechas/fNN.json`.

---

## Puesta en marcha

```bash
git clone https://github.com/<usuario>/colon-stats.git
cd colon-stats
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## El flujo de cada fecha

**1. Bajar los datos.** Tres archivos a `datos/`:

| archivo | de dónde | qué trae |
|---|---|---|
| `matches.csv` | FootyStats, export *Matches* | partido por partido: goles, xG, remates |
| `players.csv` | FootyStats, export *Players* | xG y goles por jugador |
| `tabla.csv` | Promiedos | posiciones por zona |

`tabla.csv` necesita las columnas `tipo,zona,posicion,equipo,pts,jugados`, con
`tipo=tabla` en las filas de posiciones. El lector acepta además el formato de dos
archivos por zona y el combinado con separadores `ZONA A` / `ZONA B`.

**2. Mirar los números antes de escribir nada.**

```bash
python3 fecha.py 37 --matches datos/matches.csv --players datos/players.csv \
    --tabla datos/tabla.csv --solo-calculo
```

Imprime las ocho métricas con su puesto entre los 36 y el delta contra la fecha
anterior, más un control de GF/GC contra la tabla oficial. **Si GF o GC no coinciden
con la tabla, parar acá**: algo está mal en los datos de entrada.

**3. Completar la parte editorial.** Copiar `config/fechas/_plantilla.json` a
`fNN.json` y llenar portada, jugadores, rival y tuits con los números del paso 2.

**4. Generar todo.**

```bash
python3 fecha.py 37 --matches datos/matches.csv --players datos/players.csv \
    --tabla datos/tabla.csv
```

Deja en `salida/` las placas, el HTML y el PDF.

---

## Reglas de datos que no se negocian

Están acá porque cada una costó un error publicado o casi publicado.

**Cruzar GF y GC contra la tabla oficial antes de renderizar.** El paso 2 lo imprime.
Si no coincide, no se sigue.

**Los goles salen de la tabla, no del cálculo filtrado.** El filtro de dato imposible
(abajo) descarta partidos enteros, y con ellos sus goles. Para contar goles se usa
siempre la tabla oficial. *Esto nos hizo publicar que a Tristán Suárez le habían
hecho 15 goles cuando fueron 16.*

**Se descartan las filas donde el dato de evento se contradice a sí mismo:** remates
al arco negativos, goles convertidos con dos remates o menos, o goles mayores que
remates. Se aplica a los 36 equipos por igual para que los rankings sigan siendo
comparables. FootyStats trajo las fechas 4, 17, 29, 33, 34 y 36 con datos rotos.

**Definir la dirección de cada métrica.** En xGA, faltas y gambetas sufridas, menos es
mejor. Rankear todo de mayor a menor deja a Colón "36° en gambetas sufridas" cuando en
realidad es el mejor de la categoría.

**xG vs Real se calcula por partido**, nunca acumulado: `(GF − suma de xG) / PJ`.
Acumulado no se puede comparar entre fechas ni entre equipos con distinto PJ.

**Normalizar por minutos cuando se usan datos de SICS**, no por partidos: a varios
equipos les faltan fechas en ese export.

**Los goles de Lago salen de prensa.** FootyStats le reasignó un gol en julio y nunca
lo corrigió: acredita uno menos que la prensa y que SICS.

**El xG por jugador de FootyStats se reescribe entre exportaciones.** En un export le
bajó a Lago de 7,93 a 6,96 sin que jugara. El puesto individual es orientativo y así
hay que decirlo en el copy.

**El xG de FootyStats en esta categoría viene inflado alrededor de un 35%.** Si el
sesgo es parejo el ranking no se mueve, pero el valor absoluto está alto.

**Para predecir, el xG no sirve en esta liga.** La validación fuera de muestra del
[simulador](https://llave-reducido.netlify.app/) mostró que gana la variante que usa
solo goles. El xG se usa para describir, no para pronosticar.

---

## Reglas de diseño y de copy

**Nunca rojo con blanco**: es la combinación de Unión. Rojo, negro y dorado.
Sobre el panel rojo, solo texto dorado `#FFC533`.

**Nada de texto por debajo de 26px** en 1080×1080.

**Orden fijo del hilo**: portada, los 8 bloques en el orden de `config/bloques.json`,
xG individual, y último siempre el próximo rival. No se reordena.

**En el top 5, el número entre paréntesis es la posición en la tabla de puntos de esa
zona**, nunca el ranking de la métrica. Si Colón queda afuera del top 5, va en la
sexta fila con su puesto real vía `colon_rank`.

**Los tuits interpretan, no repiten** los números que ya están en la placa. Todos
cierran con `Sigue abajo 👇` antes de los hashtags, menos el último, que cierra con
una pregunta abierta. Español rioplatense, primera persona del plural, "el sabalero".

**Sin falso optimismo después de una derrota.** Y sin editorializar dentro de la placa:
la interpretación va en el texto.

---

## Estructura

```
fecha.py              el orquestador: hace todo
kit/                  el código, no se toca fecha a fecha
  colon_kit.py        motor de diseño (PIL): placas y portadas
  calc.py             calcula las 8 métricas y valida
  render.py           renderiza los 8 bloques
  html_reporte.py     HTML con copiar tuit y copiar imagen
  pdf_reporte.py      PDF para compartir
  placa_tramos.py     placa de evolución por tramos
  placas_modelo.py    placas del hilo de varianza
  identidad_sics.py   hilo de identidad de juego (datos SICS)
  varianza_reducido.py hilo de consistencia y Reducido
config/
  bloques.json        los 8 bloques: orden, etiquetas, dirección
  bloques_identidad.json  los 8 del hilo de identidad
  fechas/fNN.json     la parte editorial de cada fecha
assets/escudos/       los 36 escudos de la categoría
assets/fonts/         Bebas Neue y DM Mono
historico/            configs y tuits de las fechas ya publicadas
salida/               generado, no va al repo
```

## Piezas temáticas

Fuera del hilo semanal hay tres piezas con su propio formato y su propia portada:

- **Identidad de juego** (`kit/identidad_sics.py`): cómo juega el equipo, con datos de
  SICS. Duelos, gambetas, centros, pases al área.
- **Consistencia y Reducido** (`kit/varianza_reducido.py`): varianza del proceso contra
  varianza del resultado, y qué se puede anticipar en esta categoría.
- **Balance de temporada**: el hilo de cierre, con carátula propia.

## Pendiente

- Conseguir de SICS el detalle por partido de los 36 equipos y la columna de tiros a
  puerta, que hoy solo está en el PDF de Colón. Con eso las métricas de SICS pasan a
  ser series comparables fecha a fecha.
- Armar la proyección del cierre **cuando queden diez o doce fechas**, no cuatro: con
  catorce todavía es ruido y con cuatro llega tarde.
