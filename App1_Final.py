import streamlit as st
import pandas as pd
import plotly.express as px
import io
import unicodedata

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="App1_Final: Matriz de Transportes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
<style>
    /* Estilo do Botão Verde */
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
    
    /* CORREÇÃO DA CAIXA DE DICA (st.info/warning) */
    .stAlert {
        background-color: #00529B !important; 
        color: white !important;
        border: 1px solid #00529B;
    }
    .stAlert p, .stAlert svg {
        color: #FFFFFF !important; 
        fill: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Matriz de Transportes: Evolução 2014-2023")

# --- METODOLOGIA ---
with st.expander("📘 Metodologia e Fontes de Dados (Clique para abrir)"):
    st.markdown("""
    **Como os dados foram obtidos?**
    Os dados apresentados referem-se à divisão modal de transporte de carga (Modal Split) baseada na métrica de **toneladas-quilômetro (tkm)**. 
    Esta métrica multiplica a carga transportada (toneladas) pela distância percorrida (km).

    **Fórmula do Cálculo:**
    $$
    \\text{Participação do Modal (\\%)} = \\left( \\frac{\\text{tkm do Modal}}{\\text{Total tkm (Rodoviário + Ferroviário + Aquaviário)}} \\right) \\times 100
    $$
    """)

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar_para_ordenacao(texto):
    if isinstance(texto, str):
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()
    return ""

# --- DEFINIÇÃO DE CORES (NOMES EM PT-BR) ---
cores_paises = {
    # Principais
    'Alemanha': '#FFCE00', 
    'Bélgica': '#4B0082', # Roxo índigo (Diferente da China)
    'Brasil': '#009739', 
    'Canadá': '#FF0000', 
    'China': '#DE2910', 
    'Dinamarca': '#C8102E', 
    'EUA': '#002868', 
    'França': '#002395', 
    'Hungria': '#436F4D', 
    'Rússia': '#FF8C00',
    # Adicionais Originais
    'Argentina': '#d8ccdd', 'Austrália': '#2e8ec1', 'Áustria': '#944d33', 
    'Azerbaijão': '#5cefcb', 'Bulgária': '#e408c2', 'Colômbia': '#561827', 
    'Coreia do Sul': '#a0e6c9', 'Croácia': '#183c9e', 'Eslováquia': '#94152a', 
    'Espanha': '#ab7538', 'Finlândia': '#0f8d9f', 'Holanda': '#fa3d56', 
    'Itália': '#831a10', 'Japão': '#9e96e7', 'Luxemburgo': '#d0970b', 
    'Reino Unido': '#0792fa', 'Romênia': '#8e83b0', 'Sérvia': '#a3d636', 
    'Suécia': '#b7bb68', 'Vietnã': '#4a110b',
    # Novos Adicionais
    'República Tcheca': '#11457e', 'Polônia': '#dc143c', 'México': '#006847',
    'Turquia': '#e30a17', 'Chile': '#0039a6', 'Noruega': '#ba0c2f'
}

PAISES_PRINCIPAIS = sorted([
    'Alemanha', 'Bélgica', 'Brasil', 'Canadá', 'China', 
    'Dinamarca', 'EUA', 'França', 'Hungria', 'Rússia'
], key=normalizar_para_ordenacao)

# --- DADOS INICIAIS ---
DADOS_CENARIO_INICIAL = [
    ('Alemanha', 17.5, 65.0, 17.5), ('Bélgica', 15.0, 75.0, 10.0), ('Brasil', 20.0, 67.5, 12.5),
    ('Canadá', 67.5, 22.5, 10.0), ('China', 40.0, 15.0, 45.0), ('Dinamarca', 12.5, 77.5, 10.0),
    ('EUA', 45.0, 35.0, 20.0), ('França', 20.0, 75.0, 5.0), ('Hungria', 30.0, 60.0, 10.0), ('Rússia', 60.0, 10.0, 30.0)
]
df_inicial = pd.DataFrame(DADOS_CENARIO_INICIAL, columns=['Pais', 'Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)'])
df_inicial['Ano'] = 'Inicial'

# --- DADOS REAIS (NOMES PADRONIZADOS COM ACENTO) ---
DATA_REAL_CSV = """Pais,Combined measure,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023
Alemanha,Ferroviario - Freight transport,0.188,0.19,0.213,0.197,0.202,0.198,0.175,0.19,0.198,0.206
Alemanha,Rodoviario -  Freight transport,0.713,0.718,0.702,0.717,0.724,0.723,0.75,0.736,0.734,0.728
Alemanha,Aquaviario -  Freight transport,0.099,0.092,0.085,0.086,0.074,0.079,0.075,0.074,0.068,0.066
Bélgica,Ferroviario - Freight transport,0.111,0.112,0.111,0.111,0.123,0.121,0.116,0.118,0.123,0.117
Bélgica,Rodoviario -  Freight transport,0.73,0.736,0.742,0.733,0.758,0.766,0.774,0.767,0.765,0.776
Bélgica,Aquaviario -  Freight transport,0.159,0.152,0.147,0.156,0.119,0.113,0.11,0.115,0.112,0.107
Dinamarca,Ferroviario - Freight transport,0.115,0.117,0.117,0.124,0.131,0.138,0.141,0.144,0.136,0.138
Dinamarca,Rodoviario -  Freight transport,0.77,0.777,0.785,0.786,0.788,0.778,0.783,0.781,0.792,0.789
Dinamarca,Aquaviario -  Freight transport,0.115,0.106,0.098,0.09,0.081,0.084,0.076,0.075,0.072,0.073
França,Ferroviario - Freight transport,0.108,0.123,0.115,0.111,0.105,0.103,0.098,0.106,0.106,0.092
França,Rodoviario -  Freight transport,0.863,0.848,0.857,0.866,0.873,0.873,0.88,0.873,0.874,0.889
França,Aquaviario -  Freight transport,0.029,0.029,0.028,0.023,0.022,0.024,0.022,0.021,0.02,0.019
Hungria,Ferroviario - Freight transport,0.311,0.295,0.286,0.326,0.27,0.265,0.292,0.264,0.266,0.252
Hungria,Rodoviario -  Freight transport,0.634,0.651,0.66,0.625,0.689,0.682,0.658,0.692,0.698,0.716
Hungria,Aquaviario -  Freight transport,0.055,0.054,0.054,0.049,0.041,0.053,0.05,0.044,0.036,0.032
Rússia,Ferroviario - Freight transport,0.864,0.869,0.868,0.869,0.877,0.872,0.871,0.865,0.861,0.844
Rússia,Rodoviario -  Freight transport,0.093,0.088,0.092,0.089,0.088,0.092,0.093,0.097,0.102,0.116
Rússia,Aquaviario -  Freight transport,0.043,0.043,0.04,0.042,0.035,0.036,0.036,0.038,0.037,0.04
EUA,Ferroviario - Freight transport,0.419,0.403,0.375,0.369,0.38,0.365,0.345,0.359,0.359,0.342
EUA,Rodoviario -  Freight transport,0.443,0.46,0.488,0.498,0.486,0.507,0.526,0.511,0.51,0.535
EUA,Aquaviario -  Freight transport,0.138,0.137,0.137,0.133,0.134,0.128,0.129,0.13,0.131,0.123
Canadá,Ferroviario - Freight transport,0.467,0.469,0.459,0.464,0.478,0.476,0.469,0.466,0.482,0.482
Canadá,Rodoviario -  Freight transport,0.293,0.286,0.291,0.291,0.296,0.296,0.297,0.302,0.295,0.295
Canadá,Aquaviario -  Freight transport,0.24,0.245,0.25,0.245,0.226,0.228,0.234,0.232,0.223,0.223
Brasil,Ferroviario - Freight transport,0.165,0.165,0.165,0.179,0.179,0.179,0.179,0.179,0.179,0.179
Brasil,Rodoviario -  Freight transport,0.714,0.714,0.714,0.671,0.671,0.671,0.671,0.671,0.671,0.671
Brasil,Aquaviario -  Freight transport,0.121,0.121,0.121,0.15,0.15,0.15,0.15,0.15,0.15,0.15
China,Ferroviario - Freight transport,0.152,0.137,0.131,0.14,0.145,0.156,0.155,0.153,0.159,0.152
China,Rodoviario -  Freight transport,0.339,0.334,0.335,0.347,0.358,0.308,0.306,0.317,0.305,0.308
China,Aquaviario -  Freight transport,0.509,0.529,0.534,0.513,0.497,0.536,0.539,0.53,0.536,0.541
Bulgária,Ferroviario - Freight transport,0.182,0.179,0.171,0.186,0.193,0.212,0.207,0.196,0.229,0.191
Bulgária,Rodoviario -  Freight transport,0.549,0.547,0.556,0.565,0.562,0.468,0.505,0.56,0.605,0.63
Bulgária,Aquaviario -  Freight transport,0.269,0.274,0.273,0.249,0.245,0.32,0.288,0.244,0.166,0.179
Croácia,Ferroviario - Freight transport,0.204,0.194,0.191,0.213,0.215,0.241,0.253,0.238,0.258,0.227
Croácia,Rodoviario -  Freight transport,0.727,0.728,0.735,0.72,0.731,0.69,0.677,0.699,0.698,0.737
Croácia,Aquaviario -  Freight transport,0.069,0.078,0.074,0.067,0.054,0.069,0.07,0.063,0.044,0.036
Luxemburgo,Ferroviario - Freight transport,0.061,0.071,0.065,0.068,0.081,0.069,0.068,0.065,0.062,0.073
Luxemburgo,Rodoviario -  Freight transport,0.855,0.849,0.873,0.87,0.844,0.85,0.851,0.855,0.863,0.857
Luxemburgo,Aquaviario -  Freight transport,0.084,0.08,0.062,0.062,0.075,0.081,0.081,0.08,0.075,0.07
Holanda,Ferroviario - Freight transport,0.059,0.062,0.061,0.061,0.065,0.064,0.062,0.064,0.066,0.064
Holanda,Rodoviario -  Freight transport,0.486,0.492,0.502,0.498,0.51,0.517,0.528,0.52,0.523,0.528
Holanda,Aquaviario -  Freight transport,0.455,0.446,0.437,0.441,0.425,0.419,0.41,0.416,0.411,0.408
Áustria,Ferroviario - Freight transport,0.331,0.326,0.321,0.319,0.316,0.31,0.298,0.3,0.303,0.293
Áustria,Rodoviario -  Freight transport,0.634,0.647,0.649,0.65,0.663,0.665,0.679,0.68,0.68,0.69
Áustria,Aquaviario -  Freight transport,0.035,0.027,0.03,0.031,0.021,0.025,0.023,0.02,0.017,0.017
Romênia,Ferroviario - Freight transport,0.302,0.316,0.304,0.302,0.289,0.268,0.258,0.253,0.255,0.24
Romênia,Rodoviario -  Freight transport,0.408,0.38,0.402,0.425,0.441,0.45,0.455,0.497,0.54,0.537
Romênia,Aquaviario -  Freight transport,0.29,0.304,0.294,0.273,0.27,0.282,0.287,0.25,0.205,0.223
Eslováquia,Ferroviario - Freight transport,0.389,0.366,0.346,0.33,0.326,0.31,0.286,0.322,0.304,0.304
Eslováquia,Rodoviario -  Freight transport,0.571,0.602,0.617,0.634,0.643,0.654,0.68,0.645,0.67,0.67
Eslováquia,Aquaviario -  Freight transport,0.04,0.032,0.037,0.036,0.031,0.036,0.034,0.033,0.026,0.026
Azerbaijão,Ferroviario - Freight transport,0.283,0.252,0.215,0.183,0.173,0.198,0.287,0.298,0.32,0.29
Azerbaijão,Rodoviario -  Freight transport,0.558,0.63,0.661,0.643,0.651,0.674,0.518,0.529,0.525,0.536
Azerbaijão,Aquaviario -  Freight transport,0.159,0.118,0.124,0.174,0.176,0.128,0.195,0.173,0.155,0.174
Sérvia,Ferroviario - Freight transport,0.446,0.459,0.372,0.366,0.313,0.244,0.249,0.2,0.201,0.166
Sérvia,Rodoviario -  Freight transport,0.441,0.419,0.517,0.553,0.631,0.695,0.701,0.675,0.688,0.719
Sérvia,Aquaviario -  Freight transport,0.113,0.122,0.111,0.081,0.056,0.061,0.05,0.125,0.111,0.115
Japão,Ferroviario - Freight transport,0.051,0.05,0.049,0.051,0.049,0.048,0.046,0.047,0.047,0.046
Japão,Rodoviario -  Freight transport,0.511,0.515,0.515,0.512,0.517,0.516,0.525,0.522,0.521,0.521
Japão,Aquaviario -  Freight transport,0.438,0.435,0.436,0.437,0.434,0.436,0.429,0.431,0.432,0.433
Austrália,Ferroviario - Freight transport,0.56,0.563,0.567,0.568,0.566,0.566,0.569,0.567,0.563,0.558
Austrália,Rodoviario -  Freight transport,0.288,0.286,0.283,0.283,0.283,0.283,0.283,0.289,0.293,0.297
Austrália,Aquaviario -  Freight transport,0.152,0.151,0.15,0.149,0.151,0.151,0.148,0.144,0.144,0.145
Coreia do Sul,Ferroviario - Freight transport,0.065,0.063,0.059,0.056,0.053,0.051,0.048,0.048,0.049,0.048
Coreia do Sul,Rodoviario -  Freight transport,0.735,0.737,0.739,0.742,0.75,0.751,0.762,0.762,0.76,0.76
Coreia do Sul,Aquaviario -  Freight transport,0.2,0.2,0.202,0.202,0.197,0.198,0.19,0.19,0.191,0.192
Colômbia,Ferroviario - Freight transport,0.232,0.225,0.238,0.246,0.231,0.208,0.157,0.163,0.171,0.171
Colômbia,Rodoviario -  Freight transport,0.751,0.758,0.736,0.727,0.742,0.767,0.82,0.812,0.803,0.803
Colômbia,Aquaviario -  Freight transport,0.017,0.017,0.026,0.027,0.027,0.025,0.023,0.025,0.026,0.026
Reino Unido,Ferroviario - Freight transport,0.112,0.097,0.085,0.084,0.083,0.081,0.079,0.08,0.078,0.078
Reino Unido,Rodoviario -  Freight transport,0.741,0.761,0.782,0.787,0.792,0.798,0.792,0.799,0.8,0.8
Reino Unido,Aquaviario -  Freight transport,0.147,0.142,0.133,0.129,0.125,0.121,0.129,0.121,0.122,0.122
Itália,Ferroviario - Freight transport,0.094,0.097,0.096,0.096,0.097,0.093,0.094,0.097,0.099,0.096
Itália,Rodoviario -  Freight transport,0.493,0.489,0.489,0.499,0.51,0.52,0.516,0.53,0.528,0.534
Itália,Aquaviario -  Freight transport,0.413,0.414,0.415,0.405,0.393,0.387,0.39,0.373,0.373,0.37
Espanha,Ferroviario - Freight transport,0.04,0.039,0.037,0.036,0.035,0.034,0.033,0.033,0.032,0.032
Espanha,Rodoviario -  Freight transport,0.794,0.799,0.804,0.803,0.812,0.814,0.82,0.823,0.824,0.823
Espanha,Aquaviario -  Freight transport,0.166,0.162,0.159,0.161,0.153,0.152,0.147,0.144,0.144,0.145
Vietnã,Ferroviario - Freight transport,0.021,0.019,0.016,0.015,0.015,0.015,0.013,0.013,0.013,0.013
Vietnã,Rodoviario -  Freight transport,0.759,0.763,0.754,0.748,0.743,0.738,0.728,0.724,0.721,0.721
Vietnã,Aquaviario -  Freight transport,0.22,0.218,0.23,0.237,0.242,0.247,0.259,0.263,0.266,0.266
Suécia,Ferroviario - Freight transport,0.295,0.296,0.299,0.301,0.307,0.3,0.296,0.305,0.305,0.304
Suécia,Rodoviario -  Freight transport,0.602,0.599,0.6,0.597,0.586,0.59,0.598,0.591,0.59,0.589
Suécia,Aquaviario -  Freight transport,0.103,0.105,0.101,0.102,0.107,0.11,0.106,0.104,0.105,0.107
Finlândia,Ferroviario - Freight transport,0.261,0.253,0.249,0.256,0.266,0.26,0.252,0.254,0.251,0.251
Finlândia,Rodoviario -  Freight transport,0.67,0.675,0.678,0.671,0.667,0.671,0.682,0.684,0.688,0.688
Finlândia,Aquaviario -  Freight transport,0.069,0.072,0.073,0.073,0.067,0.069,0.066,0.062,0.061,0.061
Argentina,Ferroviario - Freight transport,0.039,0.038,0.039,0.038,0.041,0.043,0.043,0.042,0.042,0.042
Argentina,Rodoviario -  Freight transport,0.882,0.883,0.882,0.883,0.881,0.875,0.875,0.881,0.883,0.883
Argentina,Aquaviario -  Freight transport,0.079,0.079,0.079,0.079,0.078,0.082,0.082,0.077,0.075,0.075
República Tcheca,Ferroviario - Freight transport,0.224,0.214,0.215,0.26,0.285,0.29,0.212,0.202,0.198,0.187
República Tcheca,Rodoviario -  Freight transport,0.77,0.779,0.776,0.73,0.706,0.699,0.781,0.791,0.796,0.808
República Tcheca,Aquaviario -  Freight transport,0.006,0.007,0.009,0.01,0.009,0.011,0.007,0.006,0.006,0.005
Polônia,Ferroviario - Freight transport,0.161,0.154,0.142,0.134,0.135,0.119,0.113,0.112,0.12,0.132
Polônia,Rodoviario -  Freight transport,0.831,0.841,0.85,0.864,0.867,0.875,0.875,0.88,0.867,0.866
Polônia,Aquaviario -  Freight transport,0.003,0.002,0.001,0.001,0.001,0.001,0.0,0.0,0.001,0.001
México,Ferroviario - Freight transport,0.275,0.272,0.26,0.262,0.254,0.251,0.261,0.268,0.267,0.258
México,Rodoviario -  Freight transport,0.745,0.748,0.753,0.748,0.749,0.752,0.761,0.758,0.748,0.742
México,Aquaviario -  Freight transport,0.046,0.045,0.038,0.046,0.047,0.046,0.041,0.038,0.046,0.044
Turquia,Ferroviario - Freight transport,0.039,0.036,0.037,0.038,0.041,0.043,0.047,0.042,0.045,0.035
Turquia,Rodoviario -  Freight transport,0.928,0.925,0.921,0.917,0.916,0.91,0.905,0.908,0.901,0.908
Turquia,Aquaviario -  Freight transport,0.033,0.039,0.042,0.045,0.043,0.047,0.048,0.05,0.054,0.057
Chile,Ferroviario - Freight transport,0.14,0.136,0.133,0.131,0.128,0.128,0.128,0.112,0.106,0.085
Chile,Rodoviario -  Freight transport,0.717,0.728,0.734,0.731,0.735,0.733,0.729,0.745,0.752,0.768
Chile,Aquaviario -  Freight transport,0.143,0.136,0.133,0.137,0.137,0.139,0.142,0.143,0.142,0.147
Noruega,Ferroviario - Freight transport,0.084,0.084,0.085,0.084,0.084,0.085,0.086,0.086,0.082,0.045
Noruega,Rodoviario -  Freight transport,0.493,0.487,0.508,0.486,0.489,0.493,0.504,0.515,0.486,0.533
Noruega,Aquaviario -  Freight transport,0.423,0.429,0.407,0.431,0.427,0.422,0.41,0.399,0.431,0.422
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
            # Multiplica por 100 se estiver em decimal (menor que 1.5)
            df_real[col] = df_real[col].apply(lambda x: x * 100 if pd.notnull(x) and x <= 1.5 else x)
            df_real[col] = df_real[col].round(1)
            
    return pd.concat([df_inicial, df_real], ignore_index=True)

df = carregar_dados_completos()

# --- CONTROLE DE ESTADO ---
if "slider_principal" not in st.session_state:
    st.session_state.slider_principal = "Inicial"

def atualizar_para_recente():
    st.session_state.slider_principal = "2023"

# --- INTERFACE ---
st.sidebar.header("Configurações")

# LOGICA DE BLOQUEIO NO CENARIO INICIAL
is_inicial = (st.session_state.slider_principal == "Inicial")

todos_os_paises = df['Pais'].unique().tolist()
paises_adicionais_disponiveis = sorted(
    [p for p in todos_os_paises if p not in PAISES_PRINCIPAIS],
    key=normalizar_para_ordenacao
)

if is_inicial:
    st.sidebar.warning("🔒 **Nota:** A adição de países extras só está disponível para a série histórica (2014-2023).")

selecao_adicional = st.sidebar.multiselect(
    "Adicionar Outros Países:", 
    options=paises_adicionais_disponiveis,
    default=[], 
    disabled=is_inicial
)

# --- AVISO DE BAIXA PORCENTAGEM AQUAVIÁRIA ---
paises_com_aviso_aquaviario = ['Polônia', 'República Tcheca']
paises_aviso_ativos = [p for p in selecao_adicional if p in paises_com_aviso_aquaviario]

if paises_aviso_ativos:
    lista_nomes = ", ".join(paises_aviso_ativos)
    st.sidebar.warning(f"⚠️ **Atenção:** Para os países selecionados (**{lista_nomes}**), a participação do modal aquaviário é muito baixa (< 1%). Isso pode dificultar a visualização desta categoria no gráfico.")

paises_para_mostrar = sorted(
    PAISES_PRINCIPAIS + (selecao_adicional if not is_inicial else []), 
    key=normalizar_para_ordenacao
)

# Layout Principal
col_btn, col_slider = st.columns([1, 4])
with col_btn:
    st.write("### Ação")
    st.button("🚀 Atualização mais Recente", on_click=atualizar_para_recente)

with col_slider:
    opcoes = ["Inicial"] + [str(y) for y in range(2014, 2024)]
    # CORREÇÃO CRUCIAL: USAR APENAS 'KEY' PARA LIGAÇÃO COM O ESTADO
    st.select_slider("Linha do Tempo:", options=opcoes, key="slider_principal")

# --- GRÁFICO ---
df_plot = df[
    (df['Ano'].astype(str) == st.session_state.slider_principal) & 
    (df['Pais'].isin(paises_para_mostrar))
]

if not df_plot.empty:
    df_plot = df_plot.sort_values(by='Pais', key=lambda col: col.map(normalizar_para_ordenacao))

st.divider()

# EXPLICAÇÃO DOS EIXOS E DICA
st.markdown("""
**Legenda do Gráfico:**
* **Eixo Y (Vertical):** Participação do Modal **Rodoviário** (%)
* **Eixo X (Horizontal):** Participação do Modal **Ferroviário** (%)
* **Tamanho da Bolinha:** Participação do Modal **Aquaviário** (%)
""")

st.info("💡 **Dica:** Clique no nome do país na legenda (à direita) para **ocultá-lo ou visualizá-lo** e dê um **duplo clique** para isolá-lo.")

col_ano = st.columns([1])[0]
col_ano.metric(label="Ano Visualizado", value=st.session_state.slider_principal)

if not df_plot.empty:
    titulo_grafico = f"<b>Cenário: {st.session_state.slider_principal}</b>"
    
    fig = px.scatter(
        df_plot,
        x="Ferroviário (%)", 
        y="Rodoviário (%)", 
        size="Aquaviário (%)",
        color="Pais", 
        text="Pais", 
        color_discrete_map=cores_paises, 
        title=titulo_grafico, 
        size_max=60, 
        template="plotly_white",
        range_x=[-5, 105], 
        range_y=[-5, 105],
        category_orders={"Pais": paises_para_mostrar},
        hover_data={
            "Pais": False,
            "Ferroviário (%)": ":.1f",
            "Rodoviário (%)": ":.1f",
            "Aquaviário (%)": ":.1f"
        }
    )
    
    # EIXOS E LEGENDAS MAIS CLAROS
    fig.update_layout(
        xaxis_title="<b>Eixo X:</b> Participação Ferroviária (%)",
        yaxis_title="<b>Eixo Y:</b> Participação Rodoviária (%)",
        legend_title_text="<b>Países (Clique para Filtrar)</b>",
        height=650,
        showlegend=True,
        transition={'duration': 800, 'easing': 'cubic-in-out'}
    )
    
    fig.update_traces(
        textposition='top center', 
        marker=dict(line=dict(width=1, color='DarkSlateGrey'), opacity=0.9),
        hovertemplate="<b>%{text}</b><br><br>" +
                      "🚂 Ferroviário: %{x}%<br>" +
                      "🚛 Rodoviário: %{y}%<br>" +
                      "🚢 Aquaviário: %{marker.size}%<extra></extra>"
    )
    
    fig.add_shape(type="line", x0=0, y0=100, x1=100, y1=0, line=dict(color="LightGray", dash="dot"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --- NOVA TABELA DE DADOS ---
    st.divider()
    st.subheader(f"📋 Dados Detalhados: {st.session_state.slider_principal}")
    
    # Selecionar e ordenar colunas para a tabela
    cols_to_show = ['Pais', 'Rodoviário (%)', 'Ferroviário (%)', 'Aquaviário (%)']
    st.dataframe(
        df_plot[cols_to_show].sort_values(by='Pais', key=lambda col: col.map(normalizar_para_ordenacao)).set_index('Pais'),
        use_container_width=True
    )

else:
    st.warning("Nenhum dado encontrado para a seleção atual.")