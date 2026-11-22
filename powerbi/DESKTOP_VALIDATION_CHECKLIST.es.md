# CASE-03: validación pendiente en Power BI Desktop

**Estado: pendiente.** El dashboard de Streamlit es el entregable interactivo principal. Este documento no equivale a un PBIX generado o comprobado.

## Modelo recomendado

Importar por separado `outputs/monthly.csv`, `outputs/merchandise_abc_summary.csv`, `outputs/rfm_segment_summary.csv`, `outputs/classification_bridge.csv`, `outputs/validated_affinity_shortlist.csv` y `outputs/merchandise_action_shortlist.csv`.

Estas tablas tienen granularidades distintas. **No crear relaciones artificiales entre agregados.** Usar hechos desconectados en páginas separadas o un modelo semántico explícito, con medidas y filtros comprobados.

## Valores que deben conciliarse

| Control | Resultado |
| --- | ---: |
| Ventas positivas | £20,972,594.55 |
| Mercancía candidata | £20,107,712.07 |
| Conceptos separados por reglas | £861,682.50 |
| Revisión de clasificación | £3,199.98 |
| Códigos de mercancía candidata | 4,875 |
| Pares que pasan el filtro temporal completo | 2,662 |
| Pares en la lista priorizada | 100 |

La última distinción es importante: contar filas en `validated_affinity_shortlist.csv` da 100, no los 2,662 pares aprobados en la evaluación completa.

## Criterios de aceptación

- [ ] Abrir el PBIX en Power BI Desktop y actualizar todas las tablas sin errores de ruta.
- [ ] Comprobar tipos, claves y granularidad de cada tabla; no mezclar conteos de facturas con líneas.
- [ ] Comparar cifras y filtros contra la tabla anterior y el dashboard Streamlit.
- [ ] Comprobar formato GBP, orden temporal de meses y aviso de meses parciales.
- [ ] Etiquetar mercancía como candidata y RFM como descripción histórica; no mostrar margen ni inventario inexistentes.
- [ ] Revisar la licencia y que no se exporten identificadores de clientes o datos brutos.
- [ ] Guardar el `.pbix`, hacer capturas y registrar versión y resultado de la prueba.

**Hasta que se completen estos controles, no ofrecer el archivo como evidencia de Power BI validado.**
