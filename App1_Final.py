import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="App1_Final: Matriz de Transportes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS (BOTÃO VERDE) ---
st.markdown("""
<style>
    div.stButton > button:first-child {
        background-color: #28a745; 
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
        width: 100%;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #218838;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Matriz de Transportes: Evolução 2014-2023")

# ==============================================================================
# 1. DADOS DO CENÁRIO INICIAL (ATUALIZADOS CONFORME ÚLTIMA SOLICITAÇÃO)
# ==============================================================================
DADOS_CENARIO_INICIAL = [
    # Pais       | Ferr(X) | Rod(Y) | Aqua(Size)
    ('Alemanha',   17.5,     62.5,    20.0), # Atualizado
    ('Brasil',     20.0,     65.0,    15.0),
    ('França',     20.0,     75.0,     5.0),
    ('Belgica',    15.0,     70.0,    15.0), # Atualizado
    ('Dinamarca',  10.0,     80.0,    10.0),
    ('Hungria',    30.0,     60.0,    10.0),
    ('USA',        45.0,     35.0,    20.0),
    ('China',      40.0,     15.0,    45.0),
    ('Canada',     67.5,     22.5,    10.0),
    ('Russia',     60.0,     10.0,    30.0)
]

df_inicial = pd.DataFrame(DADOS_CENARIO_INICIAL, columns=['Pais', 'Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)'])
df_inicial['Ano'] = 'Inicial'

# ==============================================================================
# 2. DADOS REAIS (2014-2023) - EXTRAÍDOS DA SUA PLANILHA
# ==============================================================================
DATA_REAL_CSV = """Pais,Combined measure,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023
Alemanha,Aquaviario -  Freight transport,0.099,0.092,0.085,0.086,0.074,0.079,0.075,0.074,0.068,0.066
Alemanha,Ferroviario - Freight transport,0.188,0.19,0.213,0.197,0.202,0.198,0.175,0.19,0.198,0.206
Alemanha,Rodoviario -  Freight transport,0.713,0.718,0.702,0.717,0.724,0.723,0.75,0.736,0.734,0.728
Belgica,Aquaviario -  Freight transport,0.159,0.152,0.147,0.156,0.119,0.113,0.11,0.115,0.112,0.107
Belgica,Ferroviario - Freight transport,0.111,0.112,0.111,0.111,0.123,0.121,0.116,0.118,0.123,0.117
Belgica,Rodoviario -  Freight transport,0.73,0.736,0.742,0.733,0.758,0.766,0.774,0.767,0.765,0.776
Brasil,Aquaviario -  Freight transport,0.121,0.121,0.121,0.15,0.15,0.15,0.15,0.15,0.15,0.15
Brasil,Ferroviario - Freight transport,0.714,0.714,0.714,0.671,0.671,0.671,0.671,0.671,0.671,0.671
Brasil,Rodoviario -  Freight transport,0.165,0.165,0.165,0.179,0.179,0.179,0.179,0.179,0.179,0.179
Canada,Aquaviario -  Freight transport,0.24,0.245,0.25,0.245,0.226,0.228,0.234,0.232,0.223,0.223
Canada,Ferroviario - Freight transport,0.467,0.469,0.459,0.464,0.478,0.476,0.469,0.466,0.482,0.482
Canada,Rodoviario -  Freight transport,0.293,0.286,0.291,0.291,0.296,0.296,0.297,0.302,0.295,0.295
China,Aquaviario -  Freight transport,0.512,0.529,0.529,0.513,0.497,0.536,0.539,0.53,0.536,0.54
China,Ferroviario - Freight transport,0.152,0.137,0.132,0.14,0.145,0.156,0.155,0.153,0.159,0.152
China,Rodoviario -  Freight transport,0.336,0.334,0.339,0.347,0.358,0.308,0.306,0.317,0.305,0.308
Dinamarca,Aquaviario -  Freight transport,0.115,0.106,0.098,0.09,0.081,0.084,0.076,0.075,0.072,0.073
Dinamarca,Ferroviario - Freight transport,0.115,0.117,0.117,0.124,0.131,0.138,0.141,0.144,0.136,0.138
Dinamarca,Rodoviario -  Freight transport,0.77,0.777,0.785,0.786,0.788,0.778,0.783,0.781,0.792,0.789
França,Aquaviario -  Freight transport,0.029,0.029,0.028,0.023,0.022,0.024,0.022,0.021,0.02,0.019
França,Ferroviario - Freight transport,0.108,0.123,0.115,0.111,0.105,0.103,0.098,0.106,0.106,0.092
França,Rodoviario -  Freight transport,0.863,0.848,0.857,0.866,0.873,0.873,0.88,0.873,0.874,0.889
Hungria,Aquaviario -  Freight transport,0.055,0.054,0.054,0.049,0.041,0.053,0.05,0.044,0.036,0.032
Hungria,Ferroviario - Freight transport,0.311,0.295,0.286,0.326,0.27,0.265,0.292,0.264,0.266,0.252
Hungria,Rodoviario -  Freight transport,0.634,0.651,0.66,0.625,0.689,0.682,0.658,0.692,0.698,0.716
Russia,Aquaviario -  Freight transport,0.043,0.043,0.04,0.042,0.035,0.036,0.036,0.038,0.037,0.04
Russia,Ferroviario - Freight transport,0.864,0.869,0.868,0.869,0.877,0.872,0.871,0.865,0.861,0.844
Russia,Rodoviario -  Freight transport,0.093,0.088,0.092,0.089,0.088,0.092,0.093,0.097,0.102,0.116
USA,Aquaviario -  Freight transport,0.138,0.137,0.137,0.133,0.134,0.128,0.129,0.13,0.131,0.123
USA,Ferroviario - Freight transport,0.419,0.403,0.375,0.369,0.38,0.365,0.345,0.359,0.359,0.342
USA,Rodoviario -  Freight transport,0.443,0.46,0.488,0.498,0.486,0.507,0.526,0.511,0.51,0.535
"""

@st.cache_data
def carregar_dados_completos():
    df_real_raw = pd.read_csv(io.StringIO(DATA_REAL_CSV))
    df_melted = df_real_raw.melt(id_vars=['Pais', 'Combined measure'], var_name='Ano', value_name='Valor')
    modal_map = {
        'Ferroviario - Freight transport': 'Ferroviário (%)',
        'Rodoviario -  Freight transport': 'Rodoviário (%)',
        'Rodoviario - Freight transport': 'Rodoviário (%)',
        'Aquaviario -  Freight transport': 'Aquaviário (%)',
        'Aquaviario - Freight transport': 'Aquaviário (%)'
    }
    df_melted['Combined measure'] = df_melted['Combined measure'].map(modal_map).fillna(df_melted['Combined measure'])
    df_real = df_melted.pivot_table(index=['Pais', 'Ano'], columns='Combined measure', values='Valor', aggfunc='first').reset_index()
    
    for col in ['Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)']:
        if col in df_real.columns:
            df_real[col] = (df_real[col] * 100).round(1)
            
    df_final = pd.concat([df_inicial, df_real], ignore_index=True)
    return df_final

df = carregar_dados_completos()

# --- 3. CONTROLE DE ESTADO ---
if "slider_principal" not in st.session_state:
    st.session_state.slider_principal = "Inicial"

def atualizar_para_recente():
    st.session_state.slider_principal = "2023"

# --- 4. INTERFACE ---
col_btn, col_slider = st.columns([1, 4])

with col_btn:
    st.write("### Ação")
    st.button("🚀 Atualizar (2023)", on_click=atualizar_para_recente)

with col_slider:
    opcoes = ["Inicial"] + [str(y) for y in range(2014, 2024)]
    selecao = st.select_slider("Linha do Tempo:", options=opcoes, key="slider_principal")

# --- 5. GRÁFICO ---
if st.session_state.slider_principal == "Inicial":
    titulo = "Cenário Inicial (Dados de Referência)"
    df_plot = df[df['Ano'] == 'Inicial']
else:
    ano = st.session_state.slider_principal
    titulo = f"Matriz de Transportes ({ano})"
    df_plot = df[df['Ano'].astype(str) == str(ano)]

st.divider()

if not df_plot.empty:
    fig = px.scatter(
        df_plot,
        x="Ferroviário (%)", y="Rodoviário (%)", size="Aquaviário (%)",
        color="Pais", text="Pais", hover_name="Pais",
        title=titulo, size_max=60, template="plotly_white",
        range_x=[-5, 105], range_y=[-5, 105]
    )
    fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='DarkSlateGrey'), opacity=0.9))
    fig.update_layout(
        xaxis_title="<b>Porcentagem do Modal Ferroviário</b>",
        yaxis_title="<b>Modal Rodoviário</b>",
        height=650, showlegend=False,
        transition={'duration': 800, 'easing': 'cubic-in-out'}
    )
    fig.add_shape(type="line", x0=0, y0=100, x1=100, y1=0, line=dict(color="LightGray", dash="dot"))
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander(f"📋 Dados detalhados ({st.session_state.slider_principal})"):
        st.dataframe(df_plot.set_index('Pais')[['Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)']])