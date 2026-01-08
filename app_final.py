import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Configuração da Página
st.set_page_config(page_title="Matriz de Transportes (2014-2023)", layout="wide")

# --- CSS para o Botão ---
st.markdown("""
<style>
    div.stButton > button:first-child {
        background-color: #28a745; /* Verde para indicar ação positiva */
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Matriz de Transportes: Evolução 2014-2023")
st.markdown("""
**Cenário Inicial:** Dados de referência (2014).
**Objetivo:** Visualizar a migração da matriz modal até o cenário mais recente (2023).
""")

# --- 1. CARREGAMENTO E TRATAMENTO DE DADOS ---
# Dados extraídos do arquivo 'Base de Dados Final - App1.xlsx'
DATA_CSV = """Pais,Combined measure,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023
Alemanha,Ferroviario - Freight transport,0.188,0.19,0.213,0.197,0.202,0.198,0.175,0.19,0.198,0.206
Alemanha,Rodoviario - Freight transport,0.713,0.718,0.702,0.717,0.724,0.723,0.75,0.736,0.734,0.728
Alemanha,Aquaviario - Freight transport,0.099,0.092,0.085,0.086,0.074,0.079,0.075,0.074,0.068,0.066
Belgica,Ferroviario - Freight transport,0.111,0.112,0.111,0.111,0.123,0.121,0.116,0.118,0.123,0.117
Belgica,Rodoviario - Freight transport,0.73,0.736,0.742,0.733,0.758,0.763,0.769,0.761,0.757,0.76
Belgica,Aquaviario - Freight transport,0.159,0.152,0.147,0.156,0.119,0.116,0.115,0.121,0.12,0.123
Brasil,Ferroviario - Freight transport,0.193,0.194,0.195,0.198,0.202,0.205,0.207,0.211,0.213,0.215
Brasil,Rodoviario - Freight transport,0.667,0.666,0.665,0.662,0.658,0.655,0.653,0.649,0.647,0.645
Brasil,Aquaviario - Freight transport,0.14,0.14,0.14,0.14,0.14,0.14,0.14,0.14,0.14,0.14
Canada,Ferroviario - Freight transport,0.598,0.598,0.574,0.584,0.623,0.593,0.569,0.565,0.57,0.57
Canada,Rodoviario - Freight transport,0.402,0.402,0.426,0.416,0.377,0.407,0.431,0.435,0.43,0.43
Canada,Aquaviario - Freight transport,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
China,Ferroviario - Freight transport,0.153,0.136,0.133,0.145,0.154,0.165,0.165,0.167,0.168,0.169
China,Rodoviario - Freight transport,0.344,0.344,0.366,0.368,0.363,0.334,0.336,0.338,0.34,0.342
China,Aquaviario - Freight transport,0.503,0.52,0.501,0.487,0.483,0.501,0.499,0.495,0.492,0.489
EUA,Ferroviario - Freight transport,0.419,0.403,0.375,0.369,0.38,0.365,0.345,0.359,0.359,0.342
EUA,Rodoviario - Freight transport,0.443,0.46,0.488,0.498,0.486,0.508,0.53,0.522,0.522,0.53
EUA,Aquaviario - Freight transport,0.138,0.137,0.137,0.134,0.134,0.127,0.125,0.119,0.119,0.128
Franca,Ferroviario - Freight transport,0.098,0.103,0.098,0.103,0.099,0.099,0.094,0.097,0.096,0.093
Franca,Rodoviario - Freight transport,0.865,0.857,0.864,0.861,0.865,0.865,0.868,0.866,0.869,0.871
Franca,Aquaviario - Freight transport,0.037,0.04,0.038,0.036,0.036,0.036,0.038,0.037,0.035,0.036
Hungria,Ferroviario - Freight transport,0.198,0.199,0.20,0.214,0.211,0.214,0.253,0.225,0.226,0.232
Hungria,Rodoviario - Freight transport,0.763,0.764,0.762,0.748,0.757,0.744,0.703,0.737,0.744,0.739
Hungria,Aquaviario - Freight transport,0.039,0.036,0.038,0.038,0.032,0.043,0.044,0.037,0.03,0.029
Reino Unido,Ferroviario - Freight transport,0.116,0.11,0.105,0.102,0.102,0.098,0.089,0.089,0.087,0.088
Reino Unido,Rodoviario - Freight transport,0.883,0.889,0.894,0.897,0.897,0.901,0.91,0.91,0.912,0.911
Reino Unido,Aquaviario - Freight transport,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001
Russia,Ferroviario - Freight transport,0.864,0.869,0.868,0.869,0.877,0.872,0.871,0.865,0.861,0.844
Russia,Rodoviario - Freight transport,0.093,0.088,0.092,0.089,0.088,0.092,0.093,0.097,0.102,0.116
Russia,Aquaviario - Freight transport,0.043,0.043,0.04,0.042,0.035,0.036,0.036,0.038,0.037,0.04
"""

@st.cache_data
def carregar_dados():
    df = pd.read_csv(io.StringIO(DATA_CSV))
    
    # Transformar colunas de Ano (melt)
    df_melted = df.melt(id_vars=['Pais', 'Combined measure'], var_name='Ano', value_name='Valor')
    
    # Mapear nomes para ficarem bonitos no gráfico
    modal_map = {
        'Ferroviario - Freight transport': 'Ferroviário (%)',
        'Rodoviario -  Freight transport': 'Rodoviário (%)', # Espaço duplo no original
        'Rodoviario - Freight transport': 'Rodoviário (%)',
        'Aquaviario -  Freight transport': 'Aquaviario (%)',
        'Aquaviario - Freight transport': 'Aquaviário (%)'
    }
    df_melted['Combined measure'] = df_melted['Combined measure'].map(modal_map).fillna(df_melted['Combined measure'])
    
    # Pivotar
    df_pivot = df_melted.pivot_table(index=['Pais', 'Ano'], columns='Combined measure', values='Valor', aggfunc='first').reset_index()
    
    # Multiplicar por 100
    cols_num = ['Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)']
    for col in cols_num:
        if col in df_pivot.columns:
            df_pivot[col] = (df_pivot[col] * 100).round(1)
            
    # Preencher Canadá 2023 com dados de 2022 (se necessário, mas o CSV acima já tem dados)
    return df_pivot

df = carregar_dados()

# --- 2. CONTROLE DE ESTADO (LINHA DO TEMPO) ---
if 'timeline_pos' not in st.session_state:
    st.session_state.timeline_pos = "Inicial"

# Opções da linha do tempo: Inicial + Anos
opcoes_timeline = ["Inicial"] + [str(year) for year in range(2014, 2024)]

# Função para o botão "Atualizar"
def atualizar_para_recente():
    st.session_state.timeline_pos = "2023"

# --- 3. INTERFACE ---
col_btn, col_slider = st.columns([1, 4])

with col_btn:
    st.write("### Ação")
    if st.button("🚀 Atualizar (2023)"):
        atualizar_para_recente()

with col_slider:
    selecao = st.select_slider(
        "Linha do Tempo:",
        options=opcoes_timeline,
        value=st.session_state.timeline_pos,
        key="slider_principal"
    )
    # Sincroniza se o usuário mover manualmente
    if selecao != st.session_state.timeline_pos:
        st.session_state.timeline_pos = selecao
        st.rerun()

# --- 4. LÓGICA DE DADOS POR SELEÇÃO ---
# Se for "Inicial", usamos 2014. Caso contrário, usamos o ano selecionado.
if st.session_state.timeline_pos == "Inicial":
    ano_dados = 2014
    titulo_grafico = "Cenário Inicial (Dados de 2014)"
else:
    ano_dados = int(st.session_state.timeline_pos)
    titulo_grafico = f"Matriz de Transportes ({ano_dados})"

# Filtrar dados
df_ano = df[df['Ano'].astype(str) == str(ano_dados)]

# --- 5. GRÁFICO ---
st.divider()

if not df_ano.empty:
    fig = px.scatter(
        df_ano,
        x="Ferroviário (%)",
        y="Rodoviário (%)",
        size="Aquaviário (%)",
        color="Pais",
        text="Pais",
        hover_name="Pais",
        hover_data=["Aquaviário (%)", "Ano"],
        title=titulo_grafico,
        size_max=60,
        template="plotly_white",
        range_x=[-5, 105], 
        range_y=[-5, 105],
    )

    fig.update_traces(
        textposition='top center',
        marker=dict(line=dict(width=1, color='DarkSlateGrey'), opacity=0.9)
    )

    fig.update_layout(
        xaxis_title="<b>Porcentagem do Modal Ferroviário</b>",
        yaxis_title="<b>Modal Rodoviário</b>",
        height=650,
        showlegend=False,
        transition={'duration': 800, 'easing': 'cubic-in-out'}
    )

    # Linha diagonal
    fig.add_shape(type="line", x0=0, y0=100, x1=100, y1=0, line=dict(color="LightGray", dash="dot"))

    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"📋 Ver Tabela de Dados"):
        st.dataframe(
            df_ano.set_index('Pais')
            .style.format("{:.1f}%", subset=['Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)'])
        )

else:
    st.error("Erro ao carregar dados.")