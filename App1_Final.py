import streamlit as st
import pandas as pd
import plotly.express as px
import io
import unicodedata

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CSS
# ==============================================================================
st.set_page_config(
    page_title="App1_Final: Matriz de Transportes",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    /* Estilo das Notificações */
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
    div[data-baseweb="notification"] svg {
        color: #FFFFFF !important; 
        fill: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Matriz de Transportes: Evolução 2014-2023")

# ==============================================================================
# 2. METODOLOGIA
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

# ==============================================================================
# 3. DEFINIÇÕES GLOBAIS (VARIÁVEIS, CORES E DADOS)
# ==============================================================================

def normalizar_para_ordenacao(texto):
    """Normaliza texto para ordenação alfabética correta (remove acentos)."""
    if isinstance(texto, str):
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()
    return ""

# Cores dos Países
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

# Lista Principal de Países
PAISES_PRINCIPAIS = sorted([
    'Alemanha', 'Bélgica', 'Brasil', 'Canadá', 'China', 
    'Dinamarca', 'EUA', 'França', 'Hungria', 'Rússia'
], key=normalizar_para_ordenacao)

# Dados CSV 1: Percentuais (String Longa)
DATA_REAL_CSV = """Pais,Combined measure,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023
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

# Dados CSV 2: TKM Absoluto (String Longa)
DATA_TKM_ABSOLUTO = """Pais,Modal,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023
Alemanha,Ferroviário,111.9,115.0,135.1,124.3,128.4,126.5,101.5,119.8,123.1,126.9
Alemanha,Rodoviário,424.4,434.8,445.4,452.5,460.2,461.8,435.0,464.1,456.3,448.4
Alemanha,Aquaviário,58.9,55.7,53.9,54.3,47.0,50.5,43.5,46.7,42.3,40.6
Bélgica,Ferroviário,7.1,7.1,7.0,6.7,7.2,7.8,7.6,8.5,8.6,8.3
Bélgica,Rodoviário,46.7,46.6,46.8,44.5,44.5,49.4,50.9,55.4,53.3,55.1
Bélgica,Aquaviário,10.2,9.6,9.3,9.5,7.0,7.3,7.2,8.3,7.8,7.6
Dinamarca,Ferroviário,2.4,2.5,2.6,2.8,3.0,3.1,3.0,3.2,2.7,3.0
Dinamarca,Rodoviário,16.1,16.6,17.3,17.7,18.1,17.7,16.8,17.2,15.7,17.0
Dinamarca,Aquaviário,2.4,2.3,2.1,2.0,1.9,1.9,1.7,1.6,1.4,1.6
França,Ferroviário,34.4,40.3,38.6,37.9,36.4,36.3,33.0,38.2,36.7,29.4
França,Rodoviário,275.0,278.0,288.0,296.0,303.0,308.0,296.0,315.0,303.0,284.0
França,Aquaviário,9.2,9.5,9.4,7.9,7.6,8.5,7.4,7.6,6.9,6.1
Hungria,Ferroviário,17.5,17.0,16.8,19.9,16.3,15.8,15.3,15.4,14.8,12.6
Hungria,Rodoviário,35.6,37.4,38.8,38.1,41.7,40.6,34.5,40.5,38.7,35.9
Hungria,Aquaviário,3.1,3.1,3.2,3.0,2.5,3.2,2.6,2.6,2.0,1.6
Rússia,Ferroviário,2301.0,2306.0,2344.0,2493.0,2596.0,2601.0,2544.0,2639.0,2638.0,2636.0
Rússia,Rodoviário,247.7,233.5,248.4,255.3,260.5,274.4,271.6,295.9,312.5,362.3
Rússia,Aquaviário,114.5,114.1,108.0,120.5,103.6,107.4,105.1,115.9,113.4,124.9
EUA,Ferroviário,2701.0,2540.0,2321.0,2453.0,2526.0,2365.0,2102.0,2219.0,2190.0,2132.0
EUA,Rodoviário,2856.0,2900.0,3021.0,3310.0,3230.0,3285.0,3205.0,3159.0,3111.0,3334.0
EUA,Aquaviário,890.0,864.0,848.0,884.0,891.0,829.0,786.0,804.0,799.0,767.0
Canadá,Ferroviário,395.0,401.0,390.0,415.0,442.0,445.0,432.0,431.0,452.0,452.0
Canadá,Rodoviário,247.8,244.5,247.3,260.3,273.7,276.7,273.6,279.3,276.6,276.6
Canadá,Aquaviário,203.0,209.5,212.4,219.1,209.0,213.2,215.5,214.6,209.1,209.1
Brasil ,Ferroviário,335.0,335.0,335.0,375.0,375.0,375.0,375.0,375.0,375.0,375.0
Brasil ,Rodoviário,1450.0,1450.0,1450.0,1405.0,1405.0,1405.0,1405.0,1405.0,1405.0,1405.0
Brasil ,Aquaviário,246.0,246.0,246.0,314.0,314.0,314.0,314.0,314.0,314.0,314.0
China,Ferroviário,2753.0,2375.0,2379.0,2696.0,2882.0,3018.0,3051.0,3323.0,3594.0,3648.0
China,Rodoviário,6139.9,5790.1,6083.7,6682.2,7115.6,5958.6,6023.3,6884.9,6894.2,7392.0
China,Aquaviário,9218.9,9170.6,9697.6,9878.9,9878.3,10369.5,10609.6,11511.0,12115.6,12984.0
Bulgária,Ferroviário,4.7,5.2,4.8,5.8,6.4,7.2,6.6,7.4,9.8,8.6
Bulgária,Rodoviário,14.3,15.9,15.6,17.5,18.5,15.9,16.2,21.3,26.0,28.4
Bulgária,Aquaviário,7.0,7.9,7.6,7.7,8.1,10.9,9.2,9.3,7.1,8.1
Croácia,Ferroviário,2.1,2.2,2.3,2.7,2.9,3.5,3.5,3.7,4.3,4.0
Croácia,Rodoviário,7.6,8.4,8.8,9.2,9.9,10.0,9.5,10.8,11.5,12.9
Croácia,Aquaviário,0.7,0.9,0.9,0.9,0.7,1.0,1.0,1.0,0.7,0.6
Luxemburgo,Ferroviário,0.56,0.63,0.59,0.6,0.69,0.57,0.52,0.51,0.47,0.53
Luxemburgo,Rodoviário,7.87,7.56,7.94,7.66,7.17,7.06,6.64,6.75,6.47,6.17
Luxemburgo,Aquaviário,0.77,0.71,0.56,0.55,0.64,0.67,0.64,0.63,0.56,0.5
Holanda,Ferroviário,7.0,7.4,7.4,7.6,8.1,8.1,7.6,8.2,8.5,8.1
Holanda,Rodoviário,57.3,59.0,61.2,62.2,63.2,65.1,64.4,66.6,67.5,67.1
Holanda,Aquaviário,53.7,53.5,53.3,55.1,52.7,52.8,50.0,53.2,53.0,51.8
Áustria,Ferroviário,21.5,21.4,21.8,22.3,22.8,22.6,20.3,22.5,23.0,21.7
Áustria,Rodoviário,41.2,42.7,44.1,45.6,47.7,48.5,46.2,51.0,51.8,51.1
Áustria,Aquaviário,2.3,1.8,2.0,2.1,1.5,1.8,1.6,1.5,1.3,1.3
Romênia,Ferroviário,12.7,14.2,14.5,15.7,15.9,15.5,15.5,16.4,17.9,17.3
Romênia,Rodoviário,17.1,17.1,19.3,22.0,24.3,26.1,27.3,32.3,37.8,38.7
Romênia,Aquaviário,12.2,13.7,14.1,14.2,14.9,16.4,17.2,16.2,14.3,16.1
Eslováquia,Ferroviário,12.4,12.1,11.8,11.6,11.7,11.0,9.4,11.6,10.6,10.3
Eslováquia,Rodoviário,18.3,19.9,21.0,22.2,23.1,23.2,22.4,23.3,23.4,22.8
Eslováquia,Aquaviário,1.3,1.1,1.3,1.3,1.1,1.3,1.1,1.2,0.9,0.9
Azerbaijão,Ferroviário,7.4,6.5,5.5,4.6,4.3,4.9,6.3,7.1,7.6,6.8
Azerbaijão,Rodoviário,14.5,16.2,16.8,16.2,16.1,16.5,11.3,12.7,12.4,12.5
Azerbaijão,Aquaviário,4.1,3.0,3.2,4.4,4.4,3.2,4.2,4.1,3.7,4.1
Sérvia,Ferroviário,3.56,3.9,3.38,3.51,3.18,2.6,2.66,2.35,2.48,2.14
Sérvia,Rodoviário,3.53,3.57,4.71,5.32,6.44,7.43,7.5,7.97,8.54,9.27
Sérvia,Aquaviário,0.91,1.04,1.01,0.77,0.58,0.66,0.54,1.48,1.38,1.49
Japão,Ferroviário,21.5,21.0,20.5,21.5,20.8,20.5,18.5,19.5,18.0,18.5
Japão,Rodoviário,215.4,216.3,215.5,215.8,219.5,220.4,211.1,216.6,199.5,209.5
Japão,Aquaviário,184.6,182.7,182.4,184.2,184.2,186.2,172.5,178.8,165.4,174.1
Austrália,Ferroviário,403.3,413.7,416.9,433.4,448.5,453.2,456.7,455.4,453.9,461.3
Austrália,Rodoviário,207.5,209.4,213.8,218.6,226.3,228.0,223.7,230.7,236.7,241.8
Austrália,Aquaviário,98.1,96.2,93.5,96.8,100.2,101.5,102.4,100.5,102.1,103.4
Coreia do Sul,Ferroviário,10.2,10.1,9.8,10.1,9.7,9.5,8.9,9.8,9.5,9.2
Coreia do Sul,Rodoviário,115.3,118.2,122.7,133.8,137.3,139.9,141.3,155.6,147.3,142.7
Coreia do Sul,Aquaviário,31.4,32.1,33.6,36.4,36.1,36.9,35.2,38.8,37.0,35.8
Colômbia,Ferroviário,24.4,24.1,25.9,27.2,26.0,23.8,17.1,18.0,19.2,19.5
Colômbia,Rodoviário,78.9,81.0,80.1,80.5,83.6,87.9,89.3,89.9,90.3,91.8
Colômbia,Aquaviário,1.8,1.8,2.8,3.0,3.0,2.9,2.5,2.8,2.9,3.0
Reino Unido,Ferroviário,21.8,18.9,17.2,17.2,16.9,16.2,14.2,16.7,16.8,16.1
Reino Unido,Rodoviário,144.5,148.4,158.0,161.3,161.6,159.6,142.6,167.0,172.8,165.6
Reino Unido,Aquaviário,28.7,27.7,26.9,26.4,25.5,24.2,23.2,25.3,26.4,25.3
Itália,Ferroviário,20.4,20.9,22.2,22.1,22.3,20.2,20.8,24.3,24.1,22.7
Itália,Rodoviário,117.8,116.8,112.6,119.7,124.9,138.0,133.2,145.0,151.1,145.2
Itália,Aquaviário,54.2,56.1,58.3,59.8,58.9,59.5,53.4,60.5,63.2,61.8
Espanha,Ferroviário,10.1,10.0,10.5,10.8,10.7,10.6,9.4,10.4,10.5,9.3
Espanha,Rodoviário,202.3,209.4,216.8,228.3,235.1,241.2,232.6,255.4,266.7,263.4
Espanha,Aquaviário,33.5,35.0,36.2,37.5,38.9,40.1,34.2,40.5,45.6,47.1
Vietnã,Ferroviário,4.2,3.8,3.2,3.6,4.0,3.7,3.2,3.8,4.5,3.7
Vietnã,Rodoviário,48.9,53.7,56.6,61.8,68.9,76.8,72.5,78.4,88.5,92.1
Vietnã,Aquaviário,163.8,171.9,177.7,201.1,221.4,238.5,232.0,225.2,234.4,228.9
Suécia,Ferroviário,20.4,21.3,21.5,21.8,22.5,21.7,20.6,21.9,21.1,19.7
Suécia,Rodoviário,48.2,49.5,50.6,51.9,53.2,53.8,51.6,56.1,57.4,51.7
Suécia,Aquaviário,31.5,30.8,30.1,31.2,30.5,29.8,27.6,26.4,27.9,26.3
Finlândia,Ferroviário,9.6,8.5,9.4,10.4,11.0,10.8,10.3,11.1,10.7,9.8
Finlândia,Rodoviário,37.5,38.2,40.8,42.3,41.5,42.1,41.2,41.8,42.9,40.1
Finlândia,Aquaviário,2.8,2.7,2.9,3.1,3.3,3.5,3.2,3.4,2.7,2.3
Argentina,Ferroviário,8.4,8.6,8.2,8.0,9.1,9.6,8.9,10.5,11.2,9.5
Argentina,Rodoviário,165.0,168.2,162.5,175.0,179.9,172.0,165.0,185.0,192.0,178.5
Argentina,Aquaviário,18.5,19.0,19.5,19.2,18.8,19.5,18.0,17.5,18.2,19.0
República Tcheca,Ferroviário,15.6,15.8,15.7,15.8,16.6,16.2,15.3,16.3,16.4,15.0
República Tcheca,Rodoviário,54.1,58.6,60.3,44.3,41.1,39.1,56.1,63.8,65.8,64.8
República Tcheca,Aquaviário,0.9,0.9,0.8,0.6,0.6,0.6,0.5,0.5,0.5,0.5
Polônia,Ferroviário,50.1,50.6,50.6,54.8,59.7,55.9,52.2,56.0,62.5,60.0
Polônia,Rodoviário,251.5,261.3,290.7,335.7,360.2,385.1,390.3,418.9,431.2,377.0
Polônia,Aquaviário,0.8,0.6,0.5,0.4,0.3,0.2,0.2,0.1,0.1,0.1
Mexico,Ferroviário,82.3,84.3,86.4,88.9,88.4,88.1,84.6,89.2,93.6,90.8
Mexico,Rodoviário,225.1,232.0,241.5,250.8,258.4,263.2,249.1,257.5,274.3,285.1
Mexico,Aquaviário,26.4,27.2,28.1,27.9,29.1,29.5,25.6,26.4,28.0,27.8
Turquia,Ferroviário,11.2,10.8,11.3,11.8,12.3,11.9,11.6,14.0,14.3,13.1
Turquia,Rodoviário,240.1,243.2,253.3,265.1,269.0,272.4,275.3,310.5,335.2,335.1
Turquia,Aquaviário,12.8,13.2,14.5,15.8,16.3,17.2,16.8,17.9,18.5,19.2
Chile,Ferroviário,8.9,9.1,9.5,9.8,10.2,9.7,10.1,9.9,9.5,8.8
Chile,Rodoviário,39.2,40.5,41.8,43.1,45.5,46.2,43.8,48.2,49.5,48.9
Chile,Aquaviário,16.8,17.5,18.2,19.0,19.8,18.9,17.5,18.4,19.1,18.7
Noruega,Ferroviário,3.7,3.8,3.9,4.0,4.1,4.0,4.0,4.2,4.0,3.6
Noruega,Rodoviário,20.9,21.3,22.1,23.2,23.8,23.9,24.1,25.6,25.2,24.9
Noruega,Aquaviário,15.2,14.8,15.6,16.2,17.0,16.5,15.9,16.8,17.2,17.7
"""

# ==============================================================================
# 3. CARREGAMENTO E PROCESSAMENTO DE DADOS
# ==============================================================================
@st.cache_data
def carregar_dados_completos():
    """Carrega, limpa e unifica os dados percentuais e iniciais."""
    
    # 1. Carregar CSV Percentuais
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
    
    df_real = df_melted.pivot_table(
        index=['Pais', 'Ano'], 
        columns='Combined measure', 
        values='Valor', 
        aggfunc='first'
    ).reset_index()
    
    # Função para corrigir valores pequenos (visualização)
    def fix_small_values(x):
        if pd.notnull(x) and 0 < x < 0.1: return 0.1
        return x

    for col in ['Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)']:
        if col in df_real.columns:
            # Multiplica por 100 se estiver em decimal (ratio <= 1.5)
            df_real[col] = df_real[col].apply(lambda x: x * 100 if pd.notnull(x) and x <= 1.5 else x)
            df_real[col] = df_real[col].apply(fix_small_values)
            df_real[col] = df_real[col].round(2)
    
    # 2. Criar DataFrame com dados iniciais (Benchmark)
    # A variável global DADOS_CENARIO_INICIAL já foi definida acima
    df_ini = pd.DataFrame(DADOS_CENARIO_INICIAL, columns=['Pais', 'Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)'])
    df_ini['Ano'] = 'Inicial'
            
    return pd.concat([df_ini, df_real], ignore_index=True)

df = carregar_dados_completos()

# ==============================================================================
# 4. CONTROLES E SIDEBAR
# ==============================================================================
if "slider_principal" not in st.session_state:
    st.session_state.slider_principal = "Inicial"

def atualizar_para_recente():
    st.session_state.slider_principal = "2023"

# Sidebar Configuration
st.sidebar.header("Configurações")

is_inicial = (st.session_state.slider_principal == "Inicial")

todos_os_paises = df['Pais'].unique().tolist()

# Lista de países disponíveis para adição (exclui os principais)
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

# Aviso de baixa porcentagem aquaviária
paises_com_aviso_aquaviario = ['Polônia', 'República Tcheca']
paises_aviso_ativos = [p for p in selecao_adicional if p in paises_com_aviso_aquaviario]

if paises_aviso_ativos:
    # --- CORREÇÃO DA SINTAXE F-STRING ---
    lista_nomes = ", ".join(paises_aviso_ativos)
    st.sidebar.warning(f"⚠️ **Atenção:** Países com baixa participação aquaviária (< 1%): {lista_nomes}")

# Lista final de países para exibir
paises_para_mostrar = sorted(
    PAISES_PRINCIPAIS + (selecao_adicional if not is_inicial else []), 
    key=normalizar_para_ordenacao
)

# ==============================================================================
# 5. LAYOUT PRINCIPAL (BOTÃO, SLIDER, GRÁFICO)
# ==============================================================================
st.divider()
st.info("""
💡 **Dicas de Navegação:**
1. Clique no nome do país na legenda (**abaixo do gráfico**) para **ocultá-lo ou visualizá-lo** (duplo clique isola).
2. Utilize o menu na **barra lateral (esquerda)** para adicionar outros países ao gráfico.
""")

col_btn, col_slider = st.columns([1, 4])
with col_btn:
    st.write("### Ação")
    st.button("🚀 Atualização mais Recente", on_click=atualizar_para_recente)

with col_slider:
    opcoes = ["Inicial"] + [str(y) for y in range(2014, 2024)]
    st.select_slider("Linha do Tempo:", options=opcoes, key="slider_principal")

# Filtragem de Dados para o Gráfico
df_plot = df[
    (df['Ano'].astype(str) == st.session_state.slider_principal) & 
    (df['Pais'].isin(paises_para_mostrar))
]

if not df_plot.empty:
    df_plot = df_plot.sort_values(by='Pais', key=lambda col: col.map(normalizar_para_ordenacao))
    df_plot['Tamanho_Visual'] = df_plot['Aquaviário (%)'].apply(lambda x: 1 if x < 1 else x)
    
    # Formatador de texto para tooltips
    def format_pct_text(x):
        if pd.isna(x): return "-"
        if x == int(x): return f"{int(x)}%"
        return f"{x:.2f}%"

    df_plot['Aquaviário_Texto'] = df_plot['Aquaviário (%)'].apply(format_pct_text)

    col_ano = st.columns([1])[0]
    st.markdown(f"### 📅 Ano Visualizado: {st.session_state.slider_principal}")

    fig = px.scatter(
        df_plot,
        x="Ferroviário (%)", 
        y="Rodoviário (%)", 
        size="Tamanho_Visual", 
        color="Pais", 
        text="Pais", 
        color_discrete_map=cores_paises, 
        title=f"<b>Cenário: {st.session_state.slider_principal}</b>", 
        size_max=60, 
        template="plotly_white",
        range_x=[-5, 105], 
        range_y=[-5, 105],
        category_orders={"Pais": paises_para_mostrar},
        hover_data=['Aquaviário_Texto', 'Ano']
    )
    
    fig.update_layout(
        xaxis=dict(title="<b>Eixo X:</b> Participação Ferroviária (%)", dtick=10),
        yaxis=dict(title="<b>Eixo Y:</b> Participação Rodoviária (%)", dtick=10),
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5, title_text=None),
        height=650,
        margin=dict(b=150),
        showlegend=True
    )
    
    fig.update_traces(
        textposition='top center', 
        marker=dict(line=dict(width=1, color='DarkSlateGrey'), opacity=0.9),
        hovertemplate="<b>%{text}</b> (%{customdata[1]})<br><br>🚂 Ferroviário: %{x}%<br>🚛 Rodoviário: %{y}%<br>🚢 Aquaviário: %{customdata[0]}<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption("**Legenda:** Eixo Y: Rodoviário | Eixo X: Ferroviário | Tamanho: Aquaviário")

    # Tabela de Percentuais
    st.divider()
    st.subheader(f"📋 Dados Detalhados (Percentuais): {st.session_state.slider_principal}")
    
    # Ordem das colunas: Ferroviário, Rodoviário, Aquaviário
    cols_to_show = ['Pais', 'Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)']
    st.dataframe(
        df_plot[cols_to_show].sort_values(by='Pais', key=lambda col: col.map(normalizar_para_ordenacao))
        .set_index('Pais')
        .style.format(format_pct_text), 
        use_container_width=True,
        height=(len(df_plot) * 35) + 38
    )

    # Análise de Variação
    st.divider()
    st.subheader("📈 Análise de Variação (Comparativo entre Anos)")
    
    anos_disponiveis = [str(y) for y in range(2014, 2024)]
    col_var1, col_var2 = st.columns(2)
    ano_a = col_var1.selectbox("Ano Inicial (Base):", anos_disponiveis, index=0, key="ano_a")
    ano_b = col_var2.selectbox("Ano Final (Comparação):", anos_disponiveis, index=len(anos_disponiveis)-1, key="ano_b")

    if ano_a and ano_b:
        if int(ano_b) < int(ano_a):
            st.error("⚠️ **Erro:** O Ano Final não pode ser anterior ao Ano Inicial.")
        else:
            # Seleção de colunas na ordem correta
            cols_variation = ['Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)']
            df_var = df[df['Pais'].isin(paises_para_mostrar)]
            df_a = df_var[df_var['Ano'].astype(str) == ano_a].set_index('Pais')[cols_variation]
            df_b = df_var[df_var['Ano'].astype(str) == ano_b].set_index('Pais')[cols_variation]
            
            df_diff = df_b - df_a
            df_diff = df_diff.dropna().sort_index(key=lambda col: col.map(normalizar_para_ordenacao))
            
            if not df_diff.empty:
                st.dataframe(
                    df_diff.style.format("{:+.2f} p.p."), 
                    use_container_width=True,
                    height=(len(df_diff) * 35) + 38
                )
            else:
                st.warning("Sem dados suficientes para comparação.")

    # ==============================================================================
    # 7. TABELA DE DADOS ABSOLUTOS (NOVA SEÇÃO DINÂMICA)
    # ==============================================================================
    st.divider()
    st.subheader("📋 Dados Absolutos: Toneladas-Quilômetro (bilhões)")

    # Exibição DIRETA (Sem st.expander, conforme solicitado)
    if st.session_state.slider_principal == "Inicial":
            st.warning("⚠️ Os dados absolutos (TKM) não estão disponíveis para o Cenário Inicial. Selecione um ano específico na linha do tempo para visualizar.")
    else:
        # Carregar dados TKM
        df_tkm = pd.read_csv(io.StringIO(DATA_TKM_ABSOLUTO))
        df_tkm.columns = df_tkm.columns.astype(str)
        df_tkm['Pais'] = df_tkm['Pais'].str.strip()
        
        if 'paises_para_mostrar' in locals():
            df_tkm = df_tkm[df_tkm['Pais'].isin(paises_para_mostrar)]
        
        ano_selecionado = str(st.session_state.slider_principal)
        
        if ano_selecionado in df_tkm.columns:
            # Pivot para formato Wide (1 linha por país, 3 colunas de modal)
            df_slice = df_tkm[['Pais', 'Modal', ano_selecionado]].copy()
            
            # Pivot table: Index=Pais, Columns=Modal, Values=Ano Selecionado
            df_pivot = df_slice.pivot(index='Pais', columns='Modal', values=ano_selecionado)
            
            # Forçar a ordem das colunas
            cols_order = ['Ferroviário', 'Rodoviário', 'Aquaviário']
            # Filtra apenas as que existem (caso algum dado falte, evita erro)
            cols_final = [c for c in cols_order if c in df_pivot.columns]
            df_pivot = df_pivot[cols_final]
            
            # Ordenar por país
            df_pivot = df_pivot.sort_index(key=lambda col: col.map(normalizar_para_ordenacao))

            st.markdown(f"Valores expressos em **bilhões de toneladas-quilômetro (tkm)** para o ano **{ano_selecionado}**.")
            
            # Exibir Tabela Formatada
            st.dataframe(
                df_pivot, 
                use_container_width=True,
                height=(len(df_pivot) * 35) + 38
            )
        else:
            st.error(f"Dados para o ano {ano_selecionado} não encontrados na base de TKM.")

else:
    st.warning("Nenhum dado encontrado para a seleção atual.")