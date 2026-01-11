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
    
    /* CORREÇÃO DAS CAIXAS DE DICA */
    div[data-baseweb="notification"] {
        background-color: #00529B !important; 
        border-color: #00529B !important;
    }
    div[data-baseweb="notification"]:has(div[aria-label="Error"]) {
        background-color: #dc3545 !important;
        border-color: #dc3545 !important;
    }
    div[data-baseweb="notification"] div,
    div[data-baseweb="notification"] p,
    div[data-baseweb="notification"] li,
    div[data-baseweb="notification"] h1,
    div[data-baseweb="notification"] h2,
    div[data-baseweb="notification"] h3,
    div[data-baseweb="notification"] svg {
        color: #FFFFFF !important; 
        fill: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Matriz de Transportes: Evolução 2014-2023")

# ==============================================================================
# 1. METODOLOGIA (TOPO)
# ==============================================================================
with st.expander("📘 Metodologia e Fontes de Dados (Clique para abrir)"):
    st.markdown("""
    **Origem e Veracidade dos Dados:**
    Este painel é o resultado de uma **pesquisa detalhada** que compilou estatísticas oficiais de transporte de carga internacional.
    Todos os dados apresentados aqui são **reais** e foram extraídos diretamente de relatórios governamentais e institutos de estatística de cada país.

    **Período de Análise (2014-2023):**
    A série histórica apresentada encerra-se no ano de **2023**. Este corte foi estabelecido pois, no momento da realização desta pesquisa, 2023 era o ano mais recente com dados consolidados e auditados disponíveis nas fontes oficiais globais.

    **Métrica Utilizada:**
    A análise refere-se à divisão modal de transporte de carga (Modal Split) baseada na métrica de **toneladas-quilômetro (tkm)**. 
    Esta métrica multiplica a carga transportada (toneladas) pela distância percorrida (km), oferecendo a visão mais precisa do esforço logístico.

    **Fórmula do Cálculo:**
    $$
    \\text{Participação do Modal (\\%)} = \\left( \\frac{\\text{tkm do Modal}}{\\text{Total tkm (Rodoviário + Ferroviário + Aquaviário)}} \\right) \\times 100
    $$

    **Fontes Oficiais Consultadas:**
    * **União Europeia:** Eurostat
    * **Brasil:** EPL / Ministério dos Transportes
    * **EUA:** Bureau of Transportation Statistics (BTS)
    * **China:** National Bureau of Statistics of China (NBSC)
    * **Rússia:** Rosstat
    * **Canadá:** Statistics Canada
    """)

# --- FUNÇÕES E DADOS ---
def normalizar_para_ordenacao(texto):
    if isinstance(texto, str):
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()
    return ""

# DEFINIÇÃO DE CORES
cores_paises = {
    'Alemanha': '#FFCE00', 'Bélgica': '#4B0082', 'Brasil': '#009739', 
    'Canadá': '#FF0000', 'China': '#DAA520', 'Dinamarca': '#C8102E', 
    'EUA': '#002868', 'França': '#002395', 'Hungria': '#436F4D', 
    'Rússia': '#FF8C00', 'Argentina': '#d8ccdd', 'Austrália': '#2e8ec1', 
    'Áustria': '#944d33', 'Azerbaijão': '#5cefcb', 'Bulgária': '#e408c2', 
    'Colômbia': '#561827', 'Coreia do Sul': '#a0e6c9', 'Croácia': '#183c9e', 
    'Eslováquia': '#94152a', 'Espanha': '#ab7538', 'Finlândia': '#0f8d9f', 
    'Holanda': '#fa3d56', 'Itália': '#831a10', 'Japão': '#9e96e7', 
    'Luxemburgo': '#d0970b', 'Reino Unido': '#0792fa', 'Romênia': '#8e83b0', 
    'Sérvia': '#a3d636', 'Suécia': '#b7bb68', 'Vietnã': '#4a110b',
    'República Tcheca': '#11457e', 'Polônia': '#dc143c', 'México': '#006847',
    'Turquia': '#e30a17', 'Chile': '#0039a6', 'Noruega': '#ba0c2f'
}

PAISES_PRINCIPAIS = sorted([
    'Alemanha', 'Bélgica', 'Brasil', 'Canadá', 'China', 
    'Dinamarca', 'EUA', 'França', 'Hungria', 'Rússia'
], key=normalizar_para_ordenacao)

# DADOS INICIAIS E CSV
DADOS_CENARIO_INICIAL = [
    ('Alemanha', 17.5, 65.0, 17.5), ('Bélgica', 15.0, 75.0, 10.0), ('Brasil', 20.0, 67.5, 12.5),
    ('Canadá', 67.5, 22.5, 10.0), ('China', 40.0, 15.0, 45.0), ('Dinamarca', 12.5, 77.5, 10.0),
    ('EUA', 45.0, 35.0, 20.0), ('França', 20.0, 75.0, 5.0), ('Hungria', 30.0, 60.0, 10.0), ('Rússia', 60.0, 10.0, 30.0)
]
df_inicial = pd.DataFrame(DADOS_CENARIO_INICIAL, columns=['Pais', 'Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)'])
df_inicial['Ano'] = 'Inicial'

DATA_REAL_CSV = """
Pais,Combined measure,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023
Alemanha,Aquaviario -  Freight transport,0.098958,0.091990,0.084962,0.086040,0.073946,0.079054,0.075000,0.074056,0.068039,0.065920
Alemanha,Ferroviario - Freight transport,0.188004,0.189926,0.212957,0.196958,0.202014,0.198028,0.175000,0.189978,0.198005,0.206040
Alemanha,Rodoviario -  Freight transport,0.713038,0.718084,0.702081,0.717002,0.724040,0.722918,0.750000,0.735966,0.733955,0.728040
Argentina,Aquaviario -  Freight transport,0.096404,0.097038,0.102524,0.094955,0.090472,0.096967,0.093799,0.082160,0.082204,0.091787
Argentina,Ferroviario - Freight transport,0.043773,0.043922,0.043113,0.039565,0.043792,0.047737,0.046378,0.049296,0.050587,0.045894
Argentina,Rodoviario -  Freight transport,0.859823,0.859040,0.854364,0.865480,0.865736,0.855296,0.859823,0.868545,0.867209,0.862319
Austrália,Aquaviario -  Freight transport,0.138383,0.133741,0.129108,0.129274,0.129290,0.129679,0.130812,0.127765,0.128800,0.128208
Austrália,Ferroviario - Freight transport,0.568910,0.575142,0.575670,0.578793,0.578710,0.579021,0.583418,0.578947,0.572600,0.571978
Austrália,Rodoviario -  Freight transport,0.292707,0.291116,0.295222,0.291934,0.292000,0.291299,0.285769,0.293288,0.298600,0.299814
Azerbaijão,Aquaviario -  Freight transport,0.157692,0.116732,0.125490,0.174603,0.177419,0.130081,0.192661,0.171548,0.156118,0.175214
Azerbaijão,Ferroviario - Freight transport,0.284615,0.252918,0.215686,0.182540,0.173387,0.199187,0.288991,0.297071,0.320675,0.290598
Azerbaijão,Rodoviario -  Freight transport,0.557692,0.630350,0.658824,0.642857,0.649194,0.670732,0.518349,0.531381,0.523207,0.534188
Brasil,Aquaviario -  Freight transport,0.121123,0.121123,0.121123,0.149952,0.149952,0.149952,0.149952,0.149952,0.149952,0.149952
Brasil,Ferroviario - Freight transport,0.164943,0.164943,0.164943,0.179083,0.179083,0.179083,0.179083,0.179083,0.179083,0.179083
Brasil,Rodoviario -  Freight transport,0.713934,0.713934,0.713934,0.670965,0.670965,0.670965,0.670965,0.670965,0.670965,0.670965
Bulgária,Aquaviario -  Freight transport,0.269231,0.272414,0.271429,0.248387,0.245455,0.320588,0.287500,0.244737,0.165501,0.179601
Bulgária,Ferroviario - Freight transport,0.180769,0.179310,0.171429,0.187097,0.193939,0.211765,0.206250,0.194737,0.228438,0.190687
Bulgária,Rodoviario -  Freight transport,0.550000,0.548276,0.557143,0.564516,0.560606,0.467647,0.506250,0.560526,0.606061,0.629712
Bélgica,Aquaviario -  Freight transport,0.159375,0.151659,0.147385,0.156507,0.119250,0.113178,0.109589,0.114958,0.111908,0.107042
Bélgica,Ferroviario - Freight transport,0.110937,0.112164,0.110935,0.110379,0.122658,0.120930,0.115677,0.117729,0.123386,0.116901
Bélgica,Rodoviario -  Freight transport,0.729688,0.736177,0.741680,0.733114,0.758092,0.765891,0.774734,0.767313,0.764706,0.776056
Canadá,Aquaviario -  Freight transport,0.240009,0.245029,0.249971,0.244969,0.226019,0.228046,0.233959,0.232025,0.222992,0.222992
Canadá,Ferroviario - Freight transport,0.467013,0.469006,0.458986,0.463998,0.477993,0.475987,0.469004,0.465996,0.482031,0.482031
Canadá,Rodoviario -  Freight transport,0.292977,0.285965,0.291044,0.291033,0.295988,0.295967,0.297036,0.301979,0.294977,0.294977
Chile,Aquaviario -  Freight transport,0.258860,0.260805,0.261871,0.264256,0.262252,0.252674,0.245098,0.240523,0.244558,0.244764
Chile,Ferroviario - Freight transport,0.137134,0.135618,0.136691,0.136300,0.135099,0.129679,0.141457,0.129412,0.121639,0.115183
Chile,Rodoviario -  Freight transport,0.604006,0.603577,0.601439,0.599444,0.602649,0.617647,0.613445,0.630065,0.633803,0.640052
China,Aquaviario -  Freight transport,0.509000,0.529001,0.534000,0.513000,0.496999,0.536000,0.538999,0.529999,0.535998,0.540460
China,Ferroviario - Freight transport,0.152000,0.137001,0.131000,0.140000,0.145000,0.156000,0.155000,0.153000,0.159000,0.151848
China,Rodoviario -  Freight transport,0.339000,0.333999,0.335000,0.346999,0.358001,0.308000,0.306001,0.317000,0.305002,0.307692
Colômbia,Aquaviario -  Freight transport,0.017127,0.016838,0.025735,0.027100,0.026643,0.025305,0.022957,0.025294,0.025801,0.026247
Colômbia,Ferroviario - Freight transport,0.232160,0.225444,0.238051,0.245709,0.230906,0.207679,0.157025,0.162602,0.170819,0.170604
Colômbia,Rodoviario -  Freight transport,0.750714,0.757717,0.736213,0.727191,0.742451,0.767016,0.820018,0.812105,0.803381,0.803150
Coreia do Sul,Aquaviario -  Freight transport,0.200127,0.200125,0.202288,0.201886,0.197160,0.198068,0.189860,0.190010,0.190918,0.190730
Coreia do Sul,Ferroviario - Freight transport,0.065010,0.062968,0.059001,0.056018,0.052977,0.050993,0.048004,0.047992,0.049020,0.049014
Coreia do Sul,Rodoviario -  Freight transport,0.734863,0.736908,0.738712,0.742097,0.749863,0.750939,0.762136,0.761998,0.760062,0.760256
Croácia,Aquaviario -  Freight transport,0.067308,0.078261,0.075000,0.070312,0.051852,0.068966,0.071429,0.064516,0.042424,0.034286
Croácia,Ferroviario - Freight transport,0.201923,0.191304,0.191667,0.210938,0.214815,0.241379,0.250000,0.238710,0.260606,0.228571
Croácia,Rodoviario -  Freight transport,0.730769,0.730435,0.733333,0.718750,0.733333,0.689655,0.678571,0.696774,0.696970,0.737143
Dinamarca,Aquaviario -  Freight transport,0.114833,0.107477,0.095455,0.088889,0.082609,0.083700,0.079070,0.072727,0.070707,0.074074
Dinamarca,Ferroviario - Freight transport,0.114833,0.116822,0.118182,0.124444,0.130435,0.136564,0.139535,0.145455,0.136364,0.138889
Dinamarca,Rodoviario -  Freight transport,0.770335,0.775701,0.786364,0.786667,0.786957,0.779736,0.781395,0.781818,0.792929,0.787037
EUA,Aquaviario -  Freight transport,0.138049,0.137056,0.136995,0.132992,0.134045,0.127952,0.129000,0.130055,0.130984,0.123055
EUA,Ferroviario - Freight transport,0.418955,0.402919,0.374960,0.369039,0.380021,0.365025,0.344986,0.358945,0.359016,0.342050
EUA,Rodoviario -  Freight transport,0.442997,0.460025,0.488045,0.497969,0.485934,0.507023,0.526013,0.511000,0.510000,0.534895
Eslováquia,Aquaviario -  Freight transport,0.040625,0.033233,0.038123,0.037037,0.030641,0.036620,0.033435,0.033241,0.025788,0.026471
Eslováquia,Ferroviario - Freight transport,0.387500,0.365559,0.346041,0.330484,0.325905,0.309859,0.285714,0.321330,0.303725,0.302941
Eslováquia,Rodoviario -  Freight transport,0.571875,0.601208,0.615836,0.632479,0.643454,0.653521,0.680851,0.645429,0.670487,0.670588
Espanha,Aquaviario -  Freight transport,0.136234,0.137579,0.137381,0.135575,0.136635,0.137376,0.123823,0.132223,0.141264,0.147280
Espanha,Ferroviario - Freight transport,0.041074,0.039308,0.039848,0.039046,0.037583,0.036314,0.034033,0.033954,0.032528,0.029081
Espanha,Rodoviario -  Freight transport,0.822692,0.823113,0.822770,0.825380,0.825782,0.826310,0.842143,0.833823,0.826208,0.823640
Finlândia,Aquaviario -  Freight transport,0.056112,0.054656,0.054614,0.055556,0.059140,0.062057,0.058501,0.060391,0.047957,0.044061
Finlândia,Ferroviario - Freight transport,0.192385,0.172065,0.177024,0.186380,0.197133,0.191489,0.188300,0.197158,0.190053,0.187739
Finlândia,Rodoviario -  Freight transport,0.751503,0.773279,0.768362,0.758065,0.743728,0.746454,0.753199,0.742451,0.761989,0.768199
França,Aquaviario -  Freight transport,0.028876,0.028981,0.027976,0.023113,0.021902,0.024093,0.021998,0.021064,0.019908,0.019092
França,Ferroviario - Freight transport,0.107972,0.122941,0.114881,0.110884,0.104899,0.102891,0.098098,0.105876,0.105886,0.092019
França,Rodoviario -  Freight transport,0.863151,0.848078,0.857143,0.866004,0.873199,0.873016,0.879905,0.873060,0.874207,0.888889
Holanda,Aquaviario -  Freight transport,0.455085,0.446205,0.437244,0.441153,0.425000,0.419048,0.409836,0.415625,0.410853,0.407874
Holanda,Ferroviario - Freight transport,0.059322,0.061718,0.060705,0.060849,0.065323,0.064286,0.062295,0.064062,0.065891,0.063780
Holanda,Rodoviario -  Freight transport,0.485593,0.492077,0.502051,0.497998,0.509677,0.516667,0.527869,0.520312,0.523256,0.528346
Hungria,Aquaviario -  Freight transport,0.055160,0.053913,0.054422,0.049180,0.041322,0.053691,0.049618,0.044444,0.036036,0.031936
Hungria,Ferroviario - Freight transport,0.311388,0.295652,0.285714,0.326230,0.269421,0.265101,0.291985,0.263248,0.266667,0.251497
Hungria,Rodoviario -  Freight transport,0.633452,0.650435,0.659864,0.624590,0.689256,0.681208,0.658397,0.692308,0.697297,0.716567
Itália,Aquaviario -  Freight transport,0.281705,0.289474,0.301916,0.296627,0.285784,0.273312,0.257473,0.263272,0.265101,0.269047
Itália,Ferroviario - Freight transport,0.106029,0.107843,0.114966,0.109623,0.108200,0.092788,0.100289,0.105744,0.101091,0.098825
Itália,Rodoviario -  Freight transport,0.612266,0.602683,0.583118,0.593750,0.606016,0.633900,0.642237,0.630983,0.633809,0.632129
Japão,Aquaviario -  Freight transport,0.437960,0.435000,0.435946,0.437011,0.433922,0.435963,0.428998,0.430947,0.431967,0.432977
Japão,Ferroviario - Freight transport,0.051008,0.050000,0.048996,0.051008,0.048999,0.047998,0.046008,0.046999,0.047010,0.046008
Japão,Rodoviario -  Freight transport,0.511032,0.515000,0.515057,0.511981,0.517079,0.516038,0.524994,0.522054,0.521024,0.521015
Luxemburgo,Aquaviario -  Freight transport,0.083696,0.079775,0.061606,0.062429,0.075294,0.080723,0.082051,0.079848,0.074667,0.069444
Luxemburgo,Ferroviario - Freight transport,0.060870,0.070787,0.064906,0.068104,0.081176,0.068675,0.066667,0.064639,0.062667,0.073611
Luxemburgo,Rodoviario -  Freight transport,0.855435,0.849438,0.873487,0.869467,0.843529,0.850602,0.851282,0.855513,0.862667,0.856944
México,Aquaviario -  Freight transport,0.079089,0.079185,0.078933,0.075898,0.077414,0.077468,0.071250,0.070759,0.070725,0.068863
México,Ferroviario - Freight transport,0.246555,0.245415,0.242697,0.241839,0.235169,0.231355,0.235458,0.239078,0.236423,0.224919
México,Rodoviario -  Freight transport,0.674356,0.675400,0.678371,0.682263,0.687417,0.691176,0.693293,0.690163,0.692852,0.706217
Noruega,Aquaviario -  Freight transport,0.381910,0.370927,0.375000,0.373272,0.378619,0.371622,0.361364,0.360515,0.370690,0.383117
Noruega,Ferroviario - Freight transport,0.092965,0.095238,0.093750,0.092166,0.091314,0.090090,0.090909,0.090129,0.086207,0.077922
Noruega,Rodoviario -  Freight transport,0.525126,0.533835,0.531250,0.534562,0.530067,0.538288,0.547727,0.549356,0.543103,0.538961
Polônia,Aquaviario -  Freight transport,0.002646,0.001920,0.001463,0.001023,0.000714,0.000453,0.000452,0.000211,0.000203,0.000229
Polônia,Ferroviario - Freight transport,0.165675,0.161920,0.148040,0.140189,0.142075,0.126700,0.117913,0.117895,0.126569,0.137268
Polônia,Rodoviario -  Freight transport,0.831680,0.836160,0.850497,0.858787,0.857211,0.872847,0.881635,0.881895,0.873228,0.862503
Reino Unido,Aquaviario -  Freight transport,0.147179,0.142051,0.133102,0.128843,0.125000,0.121000,0.128889,0.121053,0.122222,0.122222
Reino Unido,Ferroviario - Freight transport,0.111795,0.096923,0.085106,0.083943,0.082843,0.081000,0.078889,0.079904,0.077778,0.077778
Reino Unido,Rodoviario -  Freight transport,0.741026,0.761026,0.781791,0.787213,0.792157,0.798000,0.792222,0.799043,0.800000,0.800000
República Tcheca,Aquaviario -  Freight transport,0.012748,0.011952,0.010417,0.009885,0.010292,0.010733,0.006954,0.006203,0.006046,0.006227
República Tcheca,Ferroviario - Freight transport,0.220963,0.209827,0.204427,0.260297,0.284734,0.289803,0.212796,0.202233,0.198307,0.186800
República Tcheca,Rodoviario -  Freight transport,0.766289,0.778220,0.785156,0.729819,0.704974,0.699463,0.780250,0.791563,0.795647,0.806974
Romênia,Aquaviario -  Freight transport,0.290476,0.304444,0.294363,0.273603,0.270417,0.282759,0.286667,0.249615,0.204286,0.223301
Romênia,Ferroviario - Freight transport,0.302381,0.315556,0.302714,0.302505,0.288566,0.267241,0.258333,0.252696,0.255714,0.239945
Romênia,Rodoviario -  Freight transport,0.407143,0.380000,0.402923,0.423892,0.441016,0.450000,0.455000,0.497689,0.540000,0.536755
Rússia,Aquaviario -  Freight transport,0.042993,0.042998,0.039994,0.042004,0.034999,0.036006,0.035985,0.037990,0.037012,0.039991
Rússia,Ferroviario - Freight transport,0.863998,0.869008,0.868020,0.869004,0.876997,0.871999,0.871024,0.865019,0.860994,0.844006
Rússia,Rodoviario -  Freight transport,0.093008,0.087994,0.091986,0.088992,0.088004,0.091994,0.092991,0.096991,0.101994,0.116003
Suécia,Aquaviario -  Freight transport,0.314685,0.303150,0.294521,0.297426,0.287194,0.283001,0.276553,0.252874,0.262218,0.269191
Suécia,Ferroviario - Freight transport,0.203796,0.209646,0.210372,0.207817,0.211864,0.206078,0.206413,0.209770,0.198308,0.201638
Suécia,Rodoviario -  Freight transport,0.481518,0.487205,0.495108,0.494757,0.500942,0.510921,0.517034,0.537356,0.539474,0.529171
Sérvia,Aquaviario -  Freight transport,0.113750,0.122209,0.110989,0.080208,0.056863,0.061740,0.050467,0.125424,0.111290,0.115504
Sérvia,Ferroviario - Freight transport,0.445000,0.458284,0.371429,0.365625,0.311765,0.243218,0.248598,0.199153,0.200000,0.165891
Sérvia,Rodoviario -  Freight transport,0.441250,0.419506,0.517582,0.554167,0.631373,0.695042,0.700935,0.675424,0.688710,0.718605
Turquia,Aquaviario -  Freight transport,0.048466,0.049401,0.051953,0.053980,0.054772,0.057048,0.055318,0.052278,0.050272,0.052259
Turquia,Ferroviario - Freight transport,0.042408,0.040419,0.040487,0.040314,0.041331,0.039469,0.038196,0.040888,0.038859,0.035656
Turquia,Rodoviario -  Freight transport,0.909125,0.910180,0.907560,0.905706,0.903898,0.903483,0.906487,0.906834,0.910870,0.912085
Vietnã,Aquaviario -  Freight transport,0.755187,0.749346,0.748211,0.754597,0.752294,0.747649,0.753981,0.732596,0.715944,0.704958
Vietnã,Ferroviario - Freight transport,0.019364,0.016565,0.013474,0.013508,0.013592,0.011599,0.010400,0.012362,0.013745,0.011395
Vietnã,Rodoviario -  Freight transport,0.225450,0.234089,0.238316,0.231895,0.234115,0.240752,0.235619,0.255042,0.270312,0.283646
Áustria,Aquaviario -  Freight transport,0.035385,0.027314,0.029455,0.030000,0.020833,0.024691,0.023495,0.020000,0.017083,0.017544
Áustria,Ferroviario - Freight transport,0.330769,0.324734,0.321060,0.318571,0.316667,0.310014,0.298091,0.300000,0.302234,0.292848
Áustria,Rodoviario -  Freight transport,0.633846,0.647951,0.649485,0.651429,0.662500,0.665295,0.678414,0.680000,0.680683,0.689609
"""

    with st.expander("📊 Clique aqui para abrir a Tabela de Dados Absolutos"):
        # Verificação se não está no Cenário Inicial
        if st.session_state.slider_principal == "Inicial":
             st.warning("⚠️ Os dados absolutos (TKM) não estão disponíveis para o Cenário Inicial (Dados de Benchmark). Selecione um ano específico na linha do tempo para visualizar.")
        else:
            # Carregar os dados da string
            df_tkm = pd.read_csv(io.StringIO(DATA_TKM_ABSOLUTO))
            
            # CORREÇÃO 1: Remover espaços extras nos nomes dos países (ex: "Brasil " -> "Brasil")
            df_tkm['Pais'] = df_tkm['Pais'].str.strip()
            
            # Filtrar pelos países selecionados no gráfico (se disponível)
            if 'paises_para_mostrar' in locals():
                df_tkm_filtrado = df_tkm[df_tkm['Pais'].isin(paises_para_mostrar)]
            else:
                df_tkm_filtrado = df_tkm
            
            # FILTRO DINÂMICO DE COLUNA (PAIS, MODAL, ANO_SELECIONADO)
            ano_selecionado = st.session_state.slider_principal
            cols_to_keep = ['Pais', 'Modal', ano_selecionado]
            
            # Selecionar apenas as colunas relevantes
            if ano_selecionado in df_tkm_filtrado.columns:
                df_final = df_tkm_filtrado[cols_to_keep]
            else:
                st.error(f"Dados para o ano {ano_selecionado} não encontrados na base de TKM.")
                df_final = pd.DataFrame() # Empty fallback

            if not df_final.empty:
                # CORREÇÃO 2: Ordenar alfabeticamente a tabela final
                df_final = df_final.sort_values(
                    by='Pais', 
                    key=lambda col: col.map(normalizar_para_ordenacao)
                )

                # Exibir tabela formatada
                st.markdown(f"Valores expressos em **bilhões de toneladas-quilômetro (tkm)** para o ano **{ano_selecionado}**.")
                st.dataframe(
                    df_final.set_index('Pais'), 
                    use_container_width=True,
                    height=(len(df_final) * 35) + 38 # Altura dinâmica
                )

else:
    st.warning("Nenhum dado encontrado para a seleção atual.")