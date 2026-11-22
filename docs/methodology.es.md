# Metodología y definiciones

## Fuente y reglas sobre transacciones

La fuente es Online Retail II (UCI), con dos hojas originales de Excel y 1,067,371 líneas. La ingesta distingue ventas positivas, cancelaciones, importes cero, precios negativos y excepciones sin eliminar silenciosamente líneas repetidas. Los archivos `outputs/metrics.json`, `outputs/quality_summary.csv`, `outputs/monthly.csv` y `outputs/classification_bridge.csv` permiten conciliar los resultados agregados.

El neto analítico se define como **ventas positivas menos valor de cancelaciones**, sin vincular cada devolución a su venta original. No es un cierre contable ni permite calcular utilidad neta o margen de contribución.

## Mercancía candidata y ABC

Se aplican reglas sobre códigos y descripciones para separar posibles productos de mercancía, conceptos de servicio y ajustes, conservando excepciones para revisión. `outputs/merchandise_candidate_abc.csv` clasifica **4,875 códigos** por ventas positivas. La clase A reúne 1,035 códigos y aproximadamente el 80 % de esas ventas. No es un catálogo maestro validado ni una clasificación por margen.

## Clientes

Los grupos RFM describen compras históricas positivas de clientes identificados. Se considera recurrente al cliente con al menos dos facturas distintas de mercancía candidata; cumplen la condición 4,234 de 5,852 compradores identificados de mercancía. Algunas métricas usan un universo más amplio de clientes con ventas positivas, de modo que sus denominadores no deben mezclarse. Las ventas de compradores no identificados se muestran por separado.

## Afinidad y evaluación temporal

Los 100 artículos de mayor venta se seleccionaron utilizando **solo el entrenamiento**. Cada factura se asignó a un periodo según su primera línea positiva de mercancía candidata. El corte es el **1 de junio de 2011**; se analizaron 27,810 facturas de entrenamiento y 11,706 de evaluación posterior. Un par pasa el filtro si aparece conjuntamente al menos en 30 facturas de entrenamiento y 20 de evaluación, con lift mínimo de 1.5 en ambos periodos. **2,662 pares** cumplen las condiciones entre 4,363 que superaban la frecuencia mínima de entrenamiento. El filtro no corrige comparaciones múltiples ni demuestra efectos causales de promociones.

## Decisiones y experimentos

Las listas de revisión convierten recurrencia, concentración y compras conjuntas en hipótesis de trabajo. Antes de actuar deben revisarse catálogo, márgenes, costos, inventario, elegibilidad y una prueba con asignación aleatoria a tratamiento y control. Un lift elevado no representa utilidad incremental demostrada.

## Reproducción del paquete público

`python validate_release.py` ejecuta 13 conciliaciones de resultados agregados y `python -m pytest -q` ejecuta pruebas con datos sintéticos y controles de publicación. Para reproducir el pipeline completo hay que descargar el Excel original de dos hojas y preparar el esquema esperado por los programas de `src/`. El paquete público excluye facturas originales y registros individuales de clientes.
