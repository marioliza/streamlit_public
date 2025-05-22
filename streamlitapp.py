import streamlit as st
import pandas as pd
import plotly.express as px
import pandas as pd
import re

st.set_page_config(page_title="Dashboard General Experience", layout="wide")

st.title("Análisis General Chats Experience")

st.markdown("Este Dashboard muestra datos de una muestra entregada de conversaciones generadas entre los diferentes agentes y los buyers finales para las marcas: MLÉ','Savvy','twins and icons','nook and scent','nipskin'")


st.markdown('Se realiza lectura de 4 jsons entregados, posteriormente el procesamiento usando OpenaAi el cual servira como herramienta para identificar temas e intenciones')


st.markdown("---")
# Ejemplo de DataFrame
df = pd.read_parquet('chats_5.parquet')
df['order_internal_number'] = df["content"].apply(lambda x: re.findall(r"Orden Melonn:\s*(M\d+)", x)[0] if re.findall(r"Orden Melonn:\s*(M\d+)", x) else None)
incidencias = pd.read_parquet('incidencias.parquet')
df.drop(columns=['origen_mensaje','origen_mensaje_2','origen_mensaje_3','origen_mensaje_4','origen_mensaje_5','interaccion','interaccion_2'], inplace=True)

# ======== SECCIÓN 1 ========
st.markdown("## ✍️ Sección 1: Conversaciones por Día")

# Bloque de métricas y tabla
met1, met2, met3 = st.columns([1, 1,1])
with met1:
    st.metric("💬 Total de conversaciones", df.conversation_id.nunique())
with met2:
    st.metric("📨 Conversaciones con Mensaje Inicial", df[~df.marca.isna()].conversation_id.nunique())
with met3:
    st.metric("📨 Tasa Conversion con Mensaje Inicial", round(df[~df.marca.isna()].conversation_id.nunique() / df.conversation_id.nunique(),3 )* 100, "percent")

met4, met5, met6 = st.columns([1, 1, 1])

with met4:
    st.metric("📨 Total Interacciones", df[df['Si'] == 'Si'].conversation_id.nunique())
with met5:
    st.metric("📨 Total Interacciones con Bots", df[(df['bots'] == 'Si') & (df['Si'] == 'Si')].conversation_id.nunique())
with met6:
    st.metric("📨 Tasa Interacciones con Bots", round(df[(df['bots'] == 'Si') & (df['Si'] == 'Si')].conversation_id.nunique() / df[df['Si'] == 'Si'].conversation_id.nunique(),3 )* 100, "percent")


# Mostrar DataFrame completo (puedes poner un filtro aquí si quieres)
st.markdown("### 🧾 Vista de Datos")
st.dataframe(df, use_container_width=True)

# Convertir a datetime si aún no lo está
df['fecha'] = pd.to_datetime(df['fecha'])

# Agrupaciones
interacciones = df[df['Si'] == 'Si'] \
    .groupby(df['fecha'].dt.date)['conversation_id'] \
    .nunique().reset_index(name='interacciones')

mensajes_iniciales = df[df['mensaje_inicial'] == 'Si'] \
    .groupby(df['fecha'].dt.date)['conversation_id'] \
    .nunique().reset_index(name='mensajes_iniciales')

# Merge para gráfico
df_plot = pd.merge(interacciones, mensajes_iniciales, on='fecha', how='outer').fillna(0)

# Melt para gráfico largo
df_melt = df_plot.melt(id_vars='fecha',
                       value_vars=['interacciones', 'mensajes_iniciales'],
                       var_name='tipo', value_name='cantidad')

# Crear gráfico
fig = px.line(
    df_melt,
    x='fecha',
    y='cantidad',
    color='tipo',
    markers=True,
    title='📈 Interacciones vs. Mensajes Iniciales por Día'
)

fig.update_traces(
    mode='lines+markers+text',
    text=df_melt['cantidad'],
    textposition='top center'
)

fig.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Conversaciones Únicas",
    legend_title="Tipo",
    xaxis_tickangle=45,
    template='plotly_white'
)

# Mostrar gráfico
st.markdown("### 📊 Gráfico de Conversaciones por Día")
st.plotly_chart(fig, use_container_width=True)

# Comentario final
st.markdown("---")
st.markdown("### 🧠 Conclusión")
st.markdown("""
> Se puede evidenciar que a medida que existieron mensajes iniciales, hubo **mayor interacción por parte de los Buyers**.
""")



# ---------------------------------------------------------------------


# Título de sección
st.markdown("## 🌟 Sección 2: Visual de los mensajes con saludo estándar inicial")

# Bloque 1: métricas
met1, met2, met3,met4 = st.columns([1, 1, 1,1])

with met1:
    st.metric("🟢 Conversaciones con mensaje inicial e interacción",
              df[(~df.marca.isna()) & (df.Si == 'Si')].conversation_id.nunique())

with met2:
    interacciones = df[(~df.marca.isna()) & (df.Si == 'Si')].conversation_id.nunique()
    total = df[~df.marca.isna()].conversation_id.nunique()
    tasa = interacciones / total if total > 0 else 0
    st.metric("📊 Tasa de conversión (%)", f"{round(tasa * 100, 2)}%")

with met3:
    st.metric("🤖 Conversaciones con bots que generaron interacción",
              df[(~df.marca.isna()) & (df.Si == 'Si') & (df.bots == 'Si')].conversation_id.nunique())
with met4:
    df_ = df[(df['bots'] == 'Si') & (df['Si'] == 'Si') & (~df.marca.isna()) & (df.sender == 'USER')].groupby(
        'conversation_id').sender.value_counts().reset_index()
    df_[df_['count'] > 2].conversation_id.nunique()
    st.metric("Conversaciones con interraccion real", df[(~df.marca.isna()) & (df.Si == 'Si')].conversation_id.nunique() -(df[(~df.marca.isna()) & (df.Si == 'Si') & (df.bots == 'Si')].conversation_id.nunique()-df_[df_['count'] > 2].conversation_id.nunique()))


# Espaciado antes del gráfico
st.markdown("")

# Bloque 2: gráfico de barras
st.markdown("### 📊 Interacciones por tipo de Respuesta inicial (Automatico vs Humano)")

# Preparar datos
df['fecha'] = pd.to_datetime(df['fecha'])
df['Automatico'] = df['bots'].fillna('No')  # 'Si' o 'No'
resumen = df[(~df.marca.isna()) & (df.Si == 'Si')] \
    .groupby([df['fecha'].dt.date, 'Automatico'])['conversation_id'] \
    .nunique().reset_index()

resumen.columns = ['fecha', 'Automatico', 'n_conversaciones']

# Gráfico de barras agrupadas
fig_bar = px.bar(
    resumen,
    x='fecha',
    y='n_conversaciones',
    color='Automatico',
    barmode='group',
    labels={'n_conversaciones': 'Conversaciones', 'fecha': 'Fecha'},
)

fig_bar.update_layout(
    xaxis_tickangle=45,
    template='plotly_white',
    legend_title="Automatico"
)

st.plotly_chart(fig_bar, use_container_width=True)

# Observación
st.markdown("---")
st.markdown("### 🔍 Observación")
st.markdown("""
> A pesar de tratarse de mensajes automáticos o bots, estas conversaciones **lograron generar interacción real**.  
Esto sugiere que no necesariamente por tener respuesta automatica no generara o calificara el servicio.
""")


# ======== SECCIÓN 3 ========
st.markdown("## 😃 Sección 3: Calificaciones Satisfactorias")

# Validar columna
if 'content' in df.columns and 'marca' in df.columns:

    # Asegurar tipo fecha
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Conversaciones por nivel de satisfacción
    if 'satisfaccion' in df.columns:
        sat_group = df.groupby(['fecha', 'satisfaccion'])['conversation_id'].nunique().reset_index()
        sat_group.columns = ['fecha', 'satisfaccion', 'n_conversaciones']
    else:
        # alternativa si no hay columna explícita: usar 'content' == 'Excelente' como proxy
        sat_group = df[df['content'] == 'Excelente'] \
            .groupby([df['fecha'].dt.date])['conversation_id'].nunique().reset_index()
        sat_group['satisfaccion'] = 'Excelente'
        sat_group.rename(columns={'conversation_id': 'n_conversaciones', 'fecha': 'fecha'}, inplace=True)

    # Cálculos solicitados
    total_satis_con_mensaje_inicial = df[(df['content'] == 'Excelente') & (~df['marca'].isna())].conversation_id.nunique()
    total_satis_con_mensaje_bot = df[(df['content'] == 'Excelente') & (~df['marca'].isna()) & (df['bots'] == 'Si')].conversation_id.nunique()
    total_satis_sin_mensaje_inicial = df[(df['content'] == 'Excelente') & (df['marca'].isna())].conversation_id.nunique()

    met1, met2, met3 = st.columns(3)
    with met1:
        st.metric("✅ Respuestas 'Excelente' con mensaje inicial", total_satis_con_mensaje_inicial)
    with met2:
        st.metric("🤖 'Excelente' de bots con mensaje inicial", total_satis_con_mensaje_bot)
    with met3:
        st.metric("📨 'Excelente' sin mensaje inicial", total_satis_sin_mensaje_inicial)

    # Gráfico (usando proxy de 'content' == 'Excelente' si no hay columna 'satisfaccion')
    fig_satisfaccion = px.bar(
        sat_group,
        x='fecha',
        y='n_conversaciones',
        color='satisfaccion' if 'satisfaccion' in df.columns else None,
        title='📊 Conversaciones Satisfactorias por Fecha',
        labels={'n_conversaciones': 'Cantidad', 'fecha': 'Fecha'}
    )

    fig_satisfaccion.update_layout(template='plotly_white', xaxis_tickangle=45)
    st.plotly_chart(fig_satisfaccion, use_container_width=True)

    # Agrupación por marca
    satis_por_marca = df[
        (df['content'] == 'Excelente') &
        (~df['marca'].isna())
        ].groupby('marca')['conversation_id'].nunique().reset_index()

    satis_por_marca.columns = ['Marca', 'Conversaciones_Excelente']
    satis_por_marca = satis_por_marca.sort_values(by='Conversaciones_Excelente', ascending=False)

    # Mostrar tabla
    #st.dataframe(satis_por_marca, use_container_width=True)

    # Gráfico opcional
    fig_marca_satis = px.bar(
        satis_por_marca,
        x='Marca',
        y='Conversaciones_Excelente',
        title="🔝 Ranking de Marcas por Conversaciones Satisfactorias",
        text='Conversaciones_Excelente',
        labels={'Conversaciones_Excelente': 'N° de Conversaciones', 'Marca': 'Marca'}
    )

    fig_marca_satis.update_layout(template='plotly_white')
    fig_marca_satis.update_traces(textposition='outside')

    st.plotly_chart(fig_marca_satis, use_container_width=True)

    # Tabla: intenciones relacionadas con satisfacción
    st.markdown("### 📋 Conversaciones relacionadas con satisfacción (sin insatisfacción)")
    filtro_satisfaccion = df[
        df['intencion'].str.contains('satisfacción', case=False, na=False) &
        ~df['intencion'].str.contains('insatisfacción', case=False, na=False) &
        ~df['marca'].isna()
    ]

    tabla_satisfaccion = filtro_satisfaccion.groupby(
        ['conversation_id', 'marca', 'fecha', 'sender', 'content']
    ).size().reset_index(name='recuento')

    st.dataframe(tabla_satisfaccion, use_container_width=True)



else:
    st.warning("⚠️ Las columnas necesarias ('content', 'marca', 'intencion') no están disponibles.")


# ======== Métricas de Respuestas Insatisfactorias ========
st.markdown("## 😞 Respuestas Insatisfactorias: 'No me fue bien'")

# Cálculos
no_bien_con_marca = df[
    df['content'].str.contains('No me fue bien', case=False, na=False) &
    ~df['marca'].isna()
].conversation_id.nunique()

no_bien_con_marca_bot = df[
    df['content'].str.contains('No me fue bien', case=False, na=False) &
    ~df['marca'].isna() &
    (df['bots'] == 'Si')
].conversation_id.nunique()

no_bien_sin_marca = df[
    df['content'].str.contains('No me fue bien', case=False, na=False) &
    df['marca'].isna()
].conversation_id.nunique()

# Mostrar métricas
met1, met2, met3 = st.columns(3)

with met1:
    st.metric("❌ 'No me fue bien' con mensaje inicial", no_bien_con_marca)

with met2:
    st.metric("🤖 'No me fue bien' con bots", no_bien_con_marca_bot)

with met3:
    st.metric("📭 'No me fue bien' sin mensaje inicial", no_bien_sin_marca)

# Agrupar por marca y contar conversaciones únicas con esa respuesta
insatis_por_marca = df[
    df['content'].str.contains('No me fue bien', case=False, na=False) &
    (~df['marca'].isna())
].groupby('marca')['conversation_id'].nunique().reset_index()

insatis_por_marca.columns = ['Marca', 'Conversaciones_NoMeFueBien']
insatis_por_marca = insatis_por_marca.sort_values(by='Conversaciones_NoMeFueBien', ascending=False)

# Mostrar tabla
#st.dataframe(insatis_por_marca, use_container_width=True)

# Gráfico de barras
fig_marca_insatis = px.bar(
    insatis_por_marca,
    x='Marca',
    y='Conversaciones_NoMeFueBien',
    title="📉 Ranking de Marcas por Conversaciones Insatisfactorias",
    text='Conversaciones_NoMeFueBien',
    labels={'Conversaciones_NoMeFueBien': 'N° de Conversaciones', 'Marca': 'Marca'}
)

fig_marca_insatis.update_layout(template='plotly_white')
fig_marca_insatis.update_traces(textposition='outside')

st.plotly_chart(fig_marca_insatis, use_container_width=True)

# ======== Tabla de Intenciones de Insatisfacción ========
st.markdown("## 📋 Conversaciones con intención de Insatisfacción")

# Filtro de conversaciones insatisfactorias con marca
tabla_insatisfaccion = df[
    df['intencion'].str.contains('insatisfacción', case=False, na=False) &
    ~df['marca'].isna()
].groupby(['conversation_id', 'marca', 'fecha', 'sender', 'content']) \
 .size().reset_index(name='recuento')

# Mostrar la tabla
st.dataframe(tabla_insatisfaccion, use_container_width=True)


# ======== SECCIÓN 5: Análisis por Categoría de Conversación ========
st.markdown("## 🗂️ Sección 5: Análisis por Categoría Final")

# Mostrar tabla resumen de cantidad de conversaciones únicas por categoría
st.markdown("### 🔢 Conversaciones Únicas por Categoría")
df.loc[
    (~df['marca'].isna()) &
    (df['bots'] == 'No') &
    (df['categoria_final'].isna()) &
    (df['sender'] == 'USER') &
    (df['content'] != 'Excelente') &
    (df['content'] != 'No me fue bien'),
    'categoria_final'
] = 'Seguimiento y confirmación de ordenes'
conversaciones_por_categoria = df[(~df.marca.isnull()) & (df.bots == 'No') & (df.sender == 'USER') & (~df.categoria_final.isna())].groupby('categoria_final')['conversation_id'].nunique().reset_index()
conversaciones_por_categoria.columns = ['Categoría', 'Conversaciones']
conversaciones_por_categoria = conversaciones_por_categoria.sort_values(by='Conversaciones', ascending=False)

st.dataframe(conversaciones_por_categoria, use_container_width=True)

# Selector de categoría para filtrar intenciones
st.markdown("### 🎯 Análisis de Intenciones dentro de una Categoría")

categorias_disponibles = df['categoria_final'].dropna().unique()
categoria_seleccionada = st.selectbox("Selecciona una categoría para analizar", sorted(categorias_disponibles))

# Filtrar DataFrame
df_filtrado = df[(df['categoria_final'] == categoria_seleccionada) & (~df.marca.isna()) & (df.bots == 'No') & (df.sender == 'USER') ]

# Agrupar por intención
intenciones_por_categoria = df_filtrado.groupby(['categoria_final', 'intencion'])['conversation_id'].nunique().reset_index()
intenciones_por_categoria.columns = ['Categoría', 'Intención', 'Conversaciones']

# Mostrar tabla
st.dataframe(intenciones_por_categoria, use_container_width=True)
st.dataframe(df_filtrado[df_filtrado.sender == 'USER'][['conversation_id','sender','sender_id','content']], use_container_width=True)

with open("chats_no_bots.csv", "rb") as file:
    st.download_button(
        label="⬇️ Descargar CSV completo de conversaciones sin bots",
        data=file,
        file_name="chats_no_bots.csv",
        mime="text/csv"
    )


# Gráfico opcional
fig_intencion_cat = px.bar(
    intenciones_por_categoria,
    x='Intención',
    y='Conversaciones',
    title=f"📊 Intenciones dentro de la categoría: {categoria_seleccionada}",
    text='Conversaciones'
)
fig_intencion_cat.update_layout(template='plotly_white', xaxis_tickangle=45)
fig_intencion_cat.update_traces(textposition='outside')

#st.plotly_chart(fig_intencion_cat, use_container_width=True)
# Observación final
st.markdown("### 🔍 Observación")
st.markdown(f"""
> Esta sección permite explorar a fondo las **intenciones específicas dentro de cada categoría de conversación**. Estas categorizaciones se realizan del restante de conversaciones que no tuvieron interacciones directamente con un calificativo, lo que podriamos decir la carnita adicional para identificar que se pregunta por parte de los buyers  
> Al analizar la categoría **“{categoria_seleccionada}”**, puedes identificar cuáles son los temas más frecuentes abordados por los compradores.  
> Esta información es útil para **priorizar mejoras operativas, automatizar respuestas frecuentes** o entrenar mejor a los agentes según la categoría dominante.
""")


# Sección para filtrar incidencias desde feedback
st.markdown("## 🔍 Sección Final: Revisión de Incidencias según Feedback del Cliente")

# Paso 1: Selección de tipo de respuesta
opcion_feedback = st.selectbox(
    "Selecciona el tipo de respuesta para filtrar las órdenes",
    ["Excelente", "No me fue bien"]
)

# Paso 2: Filtrar df por contenido y obtener conversation_id
convs_feedback = df[df['content'].str.contains(opcion_feedback.strip(), case=False, na=False)]['conversation_id'].unique()

# Paso 3: Volver a filtrar df por conversation_id y extraer órdenes válidas
ordenes_validas = df[
    df['conversation_id'].isin(convs_feedback) &
    df['order_internal_number'].notna()
]['order_internal_number'].dropna().unique()

# Paso 4: Filtrar incidencias por esas órdenes
incidencias_filtradas = incidencias[
    incidencias['número_interno_orden'].isin(ordenes_validas)
]

# Mostrar resultados
st.markdown(f"### 📝 Incidencias relacionadas con conversaciones tipo: **{opcion_feedback}**")
if len(ordenes_validas) == 0:
    st.warning("⚠️ No se encontraron órdenes válidas asociadas a las conversaciones.")
elif incidencias_filtradas.empty:
    st.info("ℹ️ Se encontraron órdenes válidas, pero no hay incidencias relacionadas.")
else:
    st.dataframe(incidencias_filtradas, use_container_width=True)






st.markdown("---")
st.markdown("## 🧠 Conclusión General del Análisis")
st.markdown("""
Este analisis general da un vistazo inicial de lo que se puede llegar a encontrar dentro de la experiencia de usuarios bajo las conversaciones por chat, es importante seguir realizando mas entrenamientos en las clasificaciones y las siguientes recomendaciones:
1. Afinar el pipeline con LLM (Actualmente usado GPT-3.5-TURBO), primero por escalabilidad de costos y fine tunning del prompt
2. Validar casos especificos ya en manos de Maria para validar si hay alguna novedad con la base de datos trabajada
3. Seguir generando data y seguir genrando analisis mas especicos
        Por ejemplo: 
        - Porque no tenemos mensajes finales asi como los tenemos iniciales
        - En la mayoria de respuestas negativas la respuesta del agente fue casi " Que pena no hacerlo mejor" y se finalizaba la conversacion
        - Se evidencio que los mensajes sin saludo iniciales tuvieron menos probabilidad de responder a la calificacion
        - Mas alla de responder, podriamos generar mas respuestas intuitivas para el seguimiento de las ordenes? La mayoria de preguntas fueron acerca del estaoo del pedido pero dentro del saludo ya estaba el link (No seria mejor informar por cada fase, es decir . Reserado, En transporte y fuera en reparto y finalmente entregado?
4. Agregar infomracion de las ordenes dado que la podemos obtener dentro del saludo, esto para proximas iteraciones para mejorar este analisis.
                    
""")
