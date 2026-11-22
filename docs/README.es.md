# Inteligencia de ventas y clientes

**¿Cómo puede un equipo comercial utilizar sus transacciones para decidir qué productos y relaciones con clientes necesitan atención?**

[Español](README.es.md) | [English](../README.md) | [Metodología](methodology.es.md) | [Datos y limitaciones](data_provenance.md)

En este caso independiente analicé transacciones históricas reales de **Online Retail II**. Revisé la calidad de los registros, clasifiqué posibles productos de mercancía con reglas conservadoras, estudié patrones de compra y evalué asociaciones entre artículos en un periodo posterior. El objetivo es pasar de los datos a preguntas comerciales que puedan investigarse.

No es un proyecto para un cliente. La fuente no contiene costos de producto ni inventarios comprobados, por lo que no permite afirmar rentabilidad real, abandono de clientes ni efectos causales de promociones.

## Qué encontré

| Resultado histórico | Valor observado |
| --- | ---: |
| Líneas de transacciones en las dos hojas originales | **1,067,371** |
| Ventas positivas registradas en líneas clasificadas como ventas | **£20.97 millones** |
| Cancelaciones registradas por separado | **£1.53 millones** |
| Ventas clasificadas como posibles artículos de mercancía | **£20.11 millones** |
| Códigos candidatos a mercancía | **4,875** |
| Compradores identificados de mercancía candidata | **5,852** |
| Pares de artículos que superaron el filtro temporal exploratorio | **2,662** |

En la clasificación ABC de mercancía candidata, **1,035 códigos de clase A concentran aproximadamente el 80 % de sus ventas positivas**. Entre los **5,852** compradores identificados de mercancía candidata, **4,234** realizaron compras recurrentes. Otro resumen RFM señala **396** compradores de gasto alto y menor recencia que podrían revisarse, sin afirmar que abandonarán la tienda.

Para estudiar compras conjuntas, seleccioné 100 productos utilizando únicamente el periodo de entrenamiento. **2,662 pares** cumplieron condiciones mínimas de frecuencia y lift tanto en entrenamiento como en una evaluación posterior. Son hipótesis para investigar, no paquetes promocionales cuya rentabilidad esté demostrada.

## Para qué sirve

El caso ayuda a decidir qué clasificaciones de productos requieren verificación, dónde existen señales de concentración o recurrencia de compradores y qué combinaciones de artículos merecen una prueba controlada. Antes de intervenir sería necesario comprobar costos, disponibilidad, definiciones del catálogo y viabilidad comercial.

## Dashboard interactivo

La aplicación bilingüe de Streamlit se ejecuta desde `app.py`. Tiene seis secciones: panorama ejecutivo, clasificación ABC, clientes, afinidades de compra, revisión de productos y metodología.

[Abrir el dashboard de Streamlit](https://retail-sales-customer-intelligence-pyazdmafnsbevcbqpoxmud.streamlit.app/). La portada en español ya se comprobó visualmente con la captura proporcionada por el titular. Las demás pestañas y la interfaz inglesa cuentan con pruebas automáticas de carga, pero aún no con una revisión visual completa. `dashboard.py` corresponde al prototipo anterior v1.4; `app.py` es el archivo principal de publicación.

```bash
python -m pip install -r requirements.txt
python validate_release.py
python -m pytest -q
streamlit run app.py
```

El repositorio público contiene únicamente **resultados agregados** en `outputs/`. No incluye el Excel original, registros individuales de facturas ni identificadores de clientes. Los controles publicados permiten conciliar agregados, pero para reproducir toda la ingesta es necesario descargar por separado la fuente original. Consulta las [notas de datos y reproducción](data_provenance.md).

## Límites de interpretación

- Los **£20.97 millones** corresponden a valores positivos de líneas clasificadas como ventas, no a ingresos contables auditados. Las cancelaciones no están vinculadas a las operaciones originales y otros ajustes requieren revisión separada.
- La clasificación de mercancía candidata usa reglas sobre códigos y descripciones, sin cotejo contra un catálogo maestro.
- La clasificación ABC se basa en ventas positivas, no en utilidad. Los grupos de clientes describen compras históricas, no predicciones.
- El lift mide asociación de productos en una factura, no ventas incrementales causadas por una promoción. No se realizó un experimento comercial.
- La implementación de **Power BI Desktop no está validada**. Existen instrucciones de modelo agregado y medidas DAX preliminares en `powerbi/`, pero no un archivo `.pbix` certificado en esta publicación.

**Fuente:** Chen, D. (2012), *Online Retail II*, UCI Machine Learning Repository, [DOI: 10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D), licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). No se ha elegido una licencia de código abierto independiente para el código original del repositorio.

**Carlos Segura | CS Intelligence**
