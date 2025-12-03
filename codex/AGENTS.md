# SuiteScript Auditor

## Objetivo del producto

Aplicación **desktop corporativa** para auditar y documentar proyectos **NetSuite SuiteScript (2.x/2.1)** a partir de un **.zip** o un **repositorio local**, generando una carpeta **`/Docs`** (sin modificar los `.js`) con:

* **Auditoría** por archivo: riesgos/hotspots con **líneas exactas**, score **1–10** (1 crítico, 10 OK), recomendaciones accionables.
* **Documentación técnica externa** por archivo: entry points, funciones (incluye arrow functions), contratos compactos (inputs/outputs inferidos), side-effects, módulos `N/*`, dependencias y call graph simplificado.
* **Resumen global** del proyecto: ranking de archivos críticos, top hotspots, métricas (tokens/costo LLM), historial de ejecuciones.
* **Modo multi-proyecto** (cola de jobs) con progreso y costo LLM por job.
* **Publicación Git opcional**: crear rama `docs/audit-YYYYMMDD-HHMM`, commit/push de `/Docs` y (opcional) creación de PR.

La app trabaja en 2 capas:

1. **Determinista** (sin LLM): parsing, line-map, AST, reglas SuiteScript, detección de hotspots con líneas reales.
2. **LLM (OCI)** opcional: “multiexpertos” por tipo de script (`@NScriptType`) para explicación y recomendaciones, sin inventar líneas.

---

## Tecnologías y stack

* **uv** (gestor de paquetes Python) para añadir se usa uv add <nombre_de_paquete> ex. uv add flet
* **Python 3.11+**
* **Flet** (GUI desktop, empaquetable a `.exe`/`.app`)
* **Tree-sitter** (JavaScript) para AST + rangos exactos de línea/columna
* **LangChain** + **langchain-oci** para OCI GenAI (modelo texto: `openai.gpt-oss-120b` o equivalente habilitado)
* **Pydantic** para esquemas y validación estricta de salidas
* **keyring** para guardar credenciales (OCI y tokens Git) en el keychain del sistema
* **Git** vía subprocess o **GitPython** (subprocess recomendado por simplicidad/compatibilidad)
* **Jinja2** (opcional) para plantillas Markdown, o generar Markdown desde Python sin plantillas

---

## Diseño UI (corporativo)

Tema corporativo estilo “enterprise console”:

* **Primario**: Rojo corporativo (botones primarios, highlights, tags de severidad HIGH)
* **Base**: Blanco y grises suaves (fondos, cards, separadores)
* **Acento**: Azul (relación NetSuite: chips, enlaces, estados “running”, iconografía informativa)
* Tipografía: sans (system), tamaño base 13–14, títulos 18–22
* Layout consistente: **App Shell** fijo en todas las vistas:

  * Header superior (logo + nombre app + acciones)
  * Sidebar izquierda (navegación)
  * Breadcrumb bajo el header (contexto)
  * Main content con cards y tablas
  * Inspector derecho “opcional” para detalles del ítem seleccionado

### Componentes visuales estándar

* **Cards** con sombra suave, borde 1px gris claro, radius 8
* **Tags**: HIGH (rojo), MED (ámbar), LOW (azul/gris)
* **Score badge** 1–10 (color gradient: 1–3 rojo; 4–6 ámbar; 7–10 verde/azul suave)
* **Tablas** con líneas finas, filtro y búsqueda siempre visibles cuando aplique
* **Code viewer** monoespaciado, numeración de líneas, highlight de rangos

---

## Navegación (rutas/vistas) y secuencia

Vistas con secuencia coherente usando el App Shell:

1. **Processing Center** (Home)
2. **New Analysis** (Setup)
3. **Run Log** (Progreso del job)
4. **Results** (Dashboard del proyecto)
5. **File Review** (Detalle por archivo con tabs Audit/Snippets/Summary/Dependencies)
6. **Docs Browser** (Navegador de documentación generada)
7. **Settings** (OCI/Git/Límites/Preferencias)
8. **History** (Historial de ejecuciones y comparación básica)

Modal:

* **Publish to Git** (invocable desde Results y File Review)

---

## Vista 1 — Processing Center (multi-proyecto + costo LLM)

**Propósito**: dashboard principal, cola de jobs, estado general, costos.

### Elementos obligatorios

* Header:

  * “SuiteScript Auditor”
  * Botones: `New Analysis` (primario rojo), `Settings`, `Help`
* Sidebar activo: Processing Center
* Cards superiores:

  * Total Jobs
  * Running
  * Completed
  * Failed
  * **LLM Cost Today** (USD)
* Tabla central de Jobs (orden: Running > Pending > Completed > Failed):

  * Project Name
  * Source (ZIP/Repo)
  * Status (Pending/Running/Completed/Failed/Canceled)
  * Progress %
  * Stage actual (Preparing/Parsing/Rules/LLM/Writing/Packaging)
  * Current file
  * Files processed / total
  * Elapsed
  * ETA
  * **LLM Cost (job)** USD
* Panel derecho (inspector) al seleccionar un job:

  * Modelo LLM usado
  * Tokens input/output, total
  * Cost breakdown
  * Predicción costo final
  * Toggle: “Limit cost per job” + input máximo USD
* Acciones por job:

  * `Open Run Log` (si Running)
  * `Open Results` (si Completed)
  * `Export Docs.zip` (si Completed)
  * `Cancel` (si Pending/Running)
  * `Retry` (si Failed)

---

## Vista 2 — New Analysis (Setup ZIP/Repo)

**Propósito**: crear un job con configuración.

### Elementos obligatorios a considerar

* Tabs: `ZIP` / `Local Repository`
* ZIP:

  * botón “Choose ZIP”
  * campo readonly path
* Repo:

  * botón “Choose Folder”
  * campo readonly folder path
* Project name (input)
* Output options:

  * checkbox `Generate /Docs/audit` (default ON)
  * checkbox `Generate /Docs/summary` (default ON)
  * checkbox `Include .md` (default ON)
* LLM:

  * dropdown `LLM Mode`: OFF / ON (OCI)
  * dropdown `Quality Tier`: Economic / Normal / Strict
  * Toggle `MoE multiexpert` (default ON cuando LLM ON)
* SuiteScript:

  * switch `Strict SuiteScript mode` (default ON)
  * switch `Prioritize transaction safety` (default ON)
  * switch `Exclude minified` (default ON)
* Panel derecho “Output Preview”:

  * muestra estructura final `Docs/…`
* Botón primario rojo: `Start Analysis`
* Validaciones UI:

  * sin source => deshabilitado
  * sin nombre => deshabilitado

---

## Vista 3 — Run Log (Progreso + logs + costo acumulado)

**Propósito**: seguimiento detallado de 1 job.

### Elementos obligatorios

* Header: proyecto + status
* Progress bar global (0–100)
* Stepper con etapas:

  1. Preparing workspace
  2. Discovering files
  3. Parsing (line map + AST)
  4. Static checks (SuiteScript rules)
  5. LLM Analysis (OCI / MoE) (cuando aplique)
  6. Generating Docs
  7. Packaging results
* Cards:

  * Current file
  * Hotspots detected (count)
  * Files processed / total
  * LLM Cost so far (USD)
* Log console:

  * scroll
  * filtro por nivel (info/warn/error)
  * botón copy logs
* Botones:

  * `Cancel Job`
  * `Back to Processing Center`
  * `Open Results` (solo al completar)

---

## Vista 4 — Results (Dashboard del proyecto)

**Propósito**: resumen ejecutivo + navegación por archivos.

### Elementos obligatorios

* Cards superiores:

  * Overall Score (1–10)
  * Critical files (score <=3)
  * High severity hotspots
  * Total files analyzed
* Sección “Top 10 Hotspots” (tabla):

  * Severity tag
  * File
  * Line range
  * Issue title
  * Score impact
  * Click => abre File Review en el hotspot seleccionado
* Panel de archivos:

  * Lado izquierdo: file explorer (árbol) con search + filtros:

    * ScriptType
    * Score threshold (slider)
    * Only HIGH toggle
    * Modules filter (N/search, N/record…)
  * Lado derecho: summary del archivo seleccionado:

    * score + breakdown
    * entry points y líneas
    * top 3 hotspots
    * botones: `Open File Review`, `Open Docs (Summary)`
* Barra de acciones:

  * `Export Docs.zip` (primario)
  * `Export index.json`
  * `Open Docs folder`
  * `Publish to Git` (secundario)

---

## Vista 5 — File Review (detalle: Audit + Snippets + Summary + Dependencies)

**Propósito**: vista unificada; no separar “auditoría” y “documentación” en apps distintas.

### Estructura

* Header interno:

  * File name
  * Script type
  * Score
  * Breadcrumb: Results > File Review > filename
* Tabs obligatorios:

  1. **Audit**
  2. **Snippets**
  3. **Summary**
  4. **Dependencies**

#### Tab Audit

* Card “File Summary”

  * NApiVersion, NScriptType, ModuleScope
  * Entry points
  * Modules N/*
  * Metrics: LOC, functions count, avg nesting, record/search/http counts
* Lista de Hotspots (cards):

  * Severity tag + Score 1–10 del hotspot
  * Title
  * Location: `startLine-endLine` + symbol
  * Evidence snippet (monospace, con line numbers)
  * Recommendation (bullets)
  * Verified flag (true/false)
* Botones:

  * `Export file.audit.json`
  * `Copy recommendation`
  * `Open in editor` (opcional: abrir archivo local)

#### Tab Snippets

* Code viewer monoespaciado:

  * numeración absoluta
  * highlight de rangos por hotspot
  * selector de hotspot para saltar al rango
* Acciones:

  * `Copy snippet`
  * `Copy line range`

#### Tab Summary (documentación externa tipo “JSDoc liviano”)

* Sección Entry Points (cards): nombre, líneas, rol
* Sección Functions:

  * agrupar por “Exported / Internal”
  * detectar y etiquetar: `Function Declaration`, `Arrow Function`, `Method`
  * cada función: signature, lines, role, inputs/outputs guess, side-effects, deps
  * “Sample usage” mini snippet opcional
* Acciones:

  * `Download .md`
  * `Download .summary.json`

#### Tab Dependencies

* Tabla imports:

  * specifier, resolved path, confidence
* Call graph simplificado:

  * lista “A -> B”
  * (opcional) mini-diagrama (texto)
* “Risky dependencies” (si un módulo crítico es usado en loops, etc.)

---

## Vista 6 — Docs Browser (navegación por documentación)

**Propósito**: explorar documentación generada en `/Docs/summary/**` sin entrar al analysis.

### Elementos

* File tree de Docs (solo summary por defecto)
* Panel principal render md
* Selector “Audit/Summary” para cambiar carpeta rápidamente
* Búsqueda global por función (index)
* Botón `Open File Review` si el proyecto está cargado

---

## Vista 7 — Settings (OCI + Git + límites + estilo)

**Secciones**

* OCI:

  * Region/Endpoint
  * Model name
  * Auth method (config file / instance principal / token)
  * Test connection button
* LLM limits:

  * Max cost per job
  * Max tokens per file
  * Tier presets (Economic/Normal/Strict)
* Git:

  * Provider
  * Default remote
  * Token storage status (keyring)
  * Test push permissions
* UI:

  * Theme (Light)
  * Primary color (Red), accent (Blue)
  * Font size

---

## Vista 8 — History (runs anteriores)

* Lista de runs por proyecto (timestamp, status, overall score)
* Comparación simple run-to-run:

  * delta de overall
  * nuevos hotspots HIGH
  * files más degradados
* Export histórico

---

## Modal — Publish to Git

Invocable desde Results y File Review.

### Campos

* Repository Path (readonly / picker si el análisis provino de ZIP)
* Detected Remote URL (editable)
* Base Branch (default `main`)
* New Branch Name (default `docs/audit-YYYYMMDD-HHMM`)
* Commit message (default `docs(audit): update Docs for <project>`)
* Checkboxes:

  * Include `/Docs/audit`
  * Include `/Docs/summary`
* Toggles:

  * `Push changes`
  * `Create Pull Request automatically`

    * si ON: PR title, PR desc, target branch
* Botones:

  * Publish (primario rojo)
  * Cancel

---

## Estructura del repositorio (código organizado por capas)

```
suitescript_auditor/
  app.py                          # entrypoint Flet (routing + shell)
  ui/
    shell.py                       # header/sidebar/breadcrumb standard
    views/
      processing_center.py
      new_analysis.py
      run_log.py
      results.py
      file_review.py
      docs_browser.py
      settings.py
      history.py
    components/
      cards.py
      tables.py
      code_viewer.py
      badges.py
      dialogs.py                   # publish to git modal, confirm dialogs
    theme/
      tokens.py                    # colores, spacing, fonts
      oracle_like_style.py         # estilos reutilizables

  core/
    jobs/
      models.py                    # Job, JobStatus, Stage enums
      runner.py                    # ejecuta pipeline en background thread/async
      queue.py                     # cola multi job, pausar/cancelar
      cost_tracker.py              # tokens y costo
    io/
      zip_handler.py               # unzip seguro, zip-slip prevention
      workspace.py                 # workspaces temporales, cleanup
      discovery.py                 # find js files, ignore patterns
      hashing.py                   # sha256
    parsing/
      line_map.py                  # offset <-> line mapping
      ast_js.py                    # tree-sitter parse, nodes, symbols
      suitescript_header.py        # detect NApiVersion/NScriptType
      module_resolver.py           # resolve define([...]) paths
      symbol_index.py              # function index per file
    rules/
      base.py                      # Rule interface
      suitescript/
        userevent_rules.py
        suitelet_rules.py
        clientscript_rules.py
        mapreduce_rules.py
        security_rules.py
        governance_rules.py
        data_integrity_rules.py
      scoring.py                   # 1–10 scoring aggregator
      verifier.py                  # verify evidence exists at line ranges
    llm/
      oci_client.py                # langchain-oci integration
      router.py                    # select experts per file
      dossier.py                   # build file dossier JSON (determinista)
      experts/
        base_expert.py
        expert_userevent.py
        expert_suitelet.py
        expert_clientscript.py
        expert_mapreduce.py
        expert_security.py
      orchestrator.py              # merges expert outputs, builds final
      prompts/
        system.md
        userevent.md
        suitelet.md
        clientscript.md
        mapreduce.md
        security.md
      schemas/
        expert_output.schema.json  # pydantic mirrored
        file_audit.schema.json
        file_summary.schema.json
    docs/
      writer.py                    # writes Docs/ structure
      markdown.py                  # markdown generation
      index_builder.py             # Docs/index.json + index.md
      templates/
        audit_file.md.j2
        summary_file.md.j2
        index.md.j2
    git/
      publish.py                   # create branch, commit, push
      providers.py                 # github/gitlab optional
    config/
      defaults.py
      loader.py                    # .auditorrc.json support
      secure_store.py              # keyring wrappers

  tests/
    fixtures/
    test_rules.py
    test_parser_line_map.py
    test_dossier.py
    test_docs_writer.py
```

---

## “File Dossier” (entrada estándar a expertos MoE)

Archivo JSON construido por `core/llm/dossier.py`, determinista, por archivo:

* `file_meta`: path, hash, loc
* `suitescript_meta`: NApiVersion, NScriptType, ModuleScope
* `modules`: lista `N/*` + alias variable
* `entry_points`: nombre + startLine/endLine + signature
* `symbols`: funciones internas/exportadas, arrow functions incluidas
* `imports_local`: define specifiers + resolved paths
* `hotspots_static`: issues detectados por reglas con líneas exactas
* `snippets`: lista de fragmentos numerados:

  * `snippet_id`
  * `startLine/endLine`
  * `text_numbered` (cada línea `124| ...`)
  * `hotspot_refs` (qué hotspots cubre)
* `metrics`: counts de APIs (record/search/http/file/log), nesting, loops
* `project_context`: info mínima (nombre proyecto, settings tier, cost limit)

Los expertos solo pueden generar issues citando:

* `snippet_id` + `line_range` + evidencia textual presente en el snippet.

---

## Salidas (formatos exactos en `/Docs`)

Estructura espejo de proyecto:

```
Docs/
  audit/<path>/X.js.audit.json
  audit/<path>/X.js.audit.md
  summary/<path>/X.js.summary.json
  summary/<path>/X.js.summary.md
  index.json
  index.md
  artifacts/
    Docs.zip
```

### `X.js.audit.json` (Pydantic schema estricto)

Campos obligatorios:

* `path`, `hash`, `scriptType`, `apiVersion`
* `score_1_10`: overall, risk, clean_code, quality, flexibility
* `hotspots[]`:

  * `severity` (HIGH/MED/LOW)
  * `score_1_10` (impacto local)
  * `title`
  * `location`: startLine, endLine, symbol
  * `snippet_id`
  * `evidence_excerpt` (máx 20–40 líneas numeradas)
  * `recommendations[]` (bullets)
  * `verified` (bool)
* `netsuite_specific[]` (gobernanza, contabilidad, idempotencia, seguridad)
* `fix_plan[]` top 3–7 acciones ordenadas por prioridad

### `X.js.summary.json`

* `path`, `hash`, `scriptType`, `apiVersion`
* `overview` (1–3 líneas)
* `entry_points[]` (name, signature, lines, role)
* `functions[]`:

  * `name`, `kind` (declaration/arrow/method)
  * `signature`
  * `lines`
  * `role`
  * `inputs[]` (name, type_guess, required)
  * `outputs` (type_guess)
  * `side_effects[]` (record/search/http/file/log/ui)
  * `dependencies[]` (calls to internal functions + N/* usage)
* `modules_used[]`
* `call_graph_lite[]` (from,to)

### `Docs/index.json`

* `project`: name, source, run_id, timestamp
* `settings`: llm_mode, tier, strict, limits
* `summary_scores`: overall + breakdown
* `counts`: files, critical_files, hotspots_high/med/low
* `ranking_files[]`: path, score_overall, hotspots_high, scriptType
* `top_hotspots[]`: global top 10 con links a file json
* `llm_usage`: tokens_in/out, cost_total, cost_by_file
* `artifacts`: paths to Docs.zip, index.md

---

## Reglas deterministas SuiteScript (mínimo viable + priorizadas)

Implementar al menos:

* **Governance**

  * `search.run().each` dentro de loops
  * `record.load/save` repetidos en loops
  * paginado inexistente
* **Data Integrity**

  * `ignoreMandatoryFields: true` sin justificación
  * `enableSourcing: true` sin control
  * `catch` vacío / sin log
* **Seguridad**

  * `https.request` a URL sin allowlist
  * secretos hardcode (tokens/keys)
  * `eval` / `new Function`
* **Riesgo contable/negocio**

  * cambios a transacciones clave y campos sensibles
  * afterSubmit que reescribe transacciones sin idempotencia
* **ClientScript**

  * validaciones frágiles, loops costosos en UI, dependencias globales
* **MapReduce**

  * idempotencia (reintentos), manejo de errores en summarize, dedupe ausente

Cada regla produce un hotspot con `startLine/endLine` y evidencia verificable.

---

## MoE multiexpertos (prompts por tipo)

Experts disponibles:

* `expert_clientscript`
* `expert_userevent`
* `expert_suitelet`
* `expert_mapreduce`
* `expert_security` (cross-cutting)

Routing determinista:

* si `@NScriptType == ClientScript` => clientscript + (security si hay señales)
* si `UserEvent` => userevent + (security si hay señales)
* si `Suitelet` => suitelet + (security si hay señales)
* si `MapReduce` => mapreduce + (security si hay señales)
* fallback => security + generic_suitescript_expert

### Restricciones de prompt (para evitar alucinaciones)

* Output exclusivamente JSON válido según schema.
* Prohibido inventar líneas: solo usar `snippet_id` y rangos presentes.
* Si falta contexto: `needs_context: true` y pedir rangos concretos (máx 1 retry).

---

## Separación de código: UI vs Core vs LLM vs Prompts

* UI solo controla navegación, render, selección de archivos/hotspots y muestra coste.
* Core genera dossier, aplica reglas, construye Docs, valida outputs.
* LLM layer recibe dossier+snippets y retorna JSON validado.
* Prompts son archivos `.md` versionados en `core/llm/prompts/`.

---

## Gestión de credenciales (desktop)

* OCI:

  * Preferir método seguro empresarial (config local + keyring)
  * Guardar en keychain con `keyring` (nunca en archivos planos del proyecto analizado)
* Git token (si PR automático):

  * keyring
  * indicar claramente en Settings si está presente/no presente
* Log sanitization:

  * nunca imprimir credenciales
  * si se detectan secretos en código, en evidencia mostrar `***REDACTED***`

---

## Empaquetado desktop

* Build a `.exe`:

  * incluir tree-sitter grammars y dependencias
  * asegurar permisos de lectura/escritura en workspace/Docs
* Workspace:

  * por job: carpeta temporal con ID único
  * cleanup garantizado en cancel/finish

---

## Requisitos de funcionamiento (aceptación)

* Al analizar un ZIP o repo:

  * se crea un Job en Processing Center
  * se genera `/Docs` completo sin tocar fuentes
  * cada hotspot tiene rangos reales de líneas + evidence snippet numerado
  * score 1–10 consistente y explicable
  * costo LLM visible por job y global
* El usuario puede:

  * ver resultados globales
  * entrar a File Review y navegar hotspots/snippets
  * exportar Docs.zip
  * publicar docs a rama Git sin modificar main automáticamente

---

## Detalle exacto “qué aparece en cada pantallazo” (para el agente de IA)

* Todas las pantallas: header + sidebar + breadcrumb + main cards + estilo rojo/blanco/azul consistente.
* Processing Center: cards métricas + tabla jobs + panel derecho costs + acciones.
* New Analysis: tabs ZIP/repo + configuración + panel preview + botón rojo Start.
* Run Log: progress bar + stepper + cards current file/hotspots/cost + logs + botones cancel/results.
* Results: cards score + file tree filtros + detalle archivo + top hotspots + botones export/publish.
* File Review: tabs audit/snippets/summary/deps + hotspot cards con evidencia numerada + code viewer highlight + summary functions cards + deps list/graph.
* Docs Browser: tree docs + render md + search + jump a File Review.
* Settings: OCI config/test + cost limits + git config/test + theme.
* Publish modal: repo/branch/commit/push/pr fields + Publish/Cancel.
