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

# --- ESTILIZAÇÃO CSS (CORRIGIDA E REFORÇADA) ---
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
    
    /* CORREÇÃO DAS CAIXAS DE DICA (st.info / st.warning) */
    /* Força fundo azul e LETRA BRANCA em todos os elementos internos */
    div[data-baseweb="notification"] {
        background-color: #00529B !important; 
        border-color: #00529B !important;
    }
    div[data-baseweb="notification"] div,
    div[data-baseweb="notification"] p,
    div[data-baseweb="notification"] li,
    div[data-baseweb="notification"] h1,
    div[data-baseweb="notification"] h2,
    div[data-baseweb="notification"] h3 {
        color: #FFFFFF !important; 
    }
    /* Ícone branco */
    div[data-baseweb="notification"] svg {
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

    **Fontes Oficiais dos Dados (Principais):**
    * **União Europeia:** Eurostat
    * **Brasil:** EPL / Ministério dos Transportes
    * **EUA:** Bureau of Transportation Statistics (BTS)
    * **China:** National Bureau of Statistics of China (NBSC)
    * **Rússia:** Rosstat
    * **Canadá:** Statistics Canada
    """)

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar_para_ordenacao(texto):
    if isinstance(texto, str):
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()
    return ""

# --- DEFINIÇÃO DE CORES ---
cores_paises = {
    # Principais
    'Alemanha': '#FFCE00', 
    'Bélgica': '#4B0082', # Roxo/Índigo
    'Brasil': '#009739', 
    'Canadá': '#FF0000', 
    'China': '#DAA520',   # Goldenrod
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

# --- DADOS REAIS (ALTA PRECISÃO) ---
DATA_REAL_CSV = """Pais,Combined measure,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023
Alemanha,Aquaviario -  Freight transport,0.099000,0.092000,0.085000,0.086000,0.074000,0.079000,0.075000,0.074000,0.068000,0.066000
Alemanha,Ferroviario - Freight transport,0.188000,0.190000,0.213000,0.197000,0.202000,0.198000,0.175000,0.190000,0.198000,0.206000
Alemanha,Rodoviario -  Freight transport,0.713000,0.718000,0.702000,0.717000,0.724000,0.723000,0.750000,0.736000,0.734000,0.728000
Argentina,Aquaviario -  Freight transport,0.079000,0.079000,0.079000,0.079000,0.078000,0.082000,0.082000,0.077000,0.075000,0.075000
Argentina,Ferroviario - Freight transport,0.039000,0.038000,0.039000,0.038000,0.041000,0.043000,0.043000,0.042000,0.042000,0.042000
Argentina,Rodoviario -  Freight transport,0.882000,0.883000,0.882000,0.883000,0.881000,0.875000,0.875000,0.881000,0.883000,0.883000
Austrália,Aquaviario -  Freight transport,0.152000,0.151000,0.150000,0.149000,0.151000,0.151000,0.148000,0.144000,0.144000,0.145000
Austrália,Ferroviario - Freight transport,0.560000,0.563000,0.567000,0.568000,0.566000,0.566000,0.569000,0.567000,0.563000,0.558000
Austrália,Rodoviario -  Freight transport,0.288000,0.286000,0.283000,0.283000,0.283000,0.283000,0.283000,0.289000,0.293000,0.297000
Azerbaijão,Aquaviario -  Freight transport,0.158574,0.117797,0.124257,0.174101,0.176500,0.128706,0.194481,0.173433,0.155287,0.174354
Azerbaijão,Ferroviario - Freight transport,0.283371,0.251988,0.214890,0.182526,0.173271,0.197897,0.286607,0.298082,0.320584,0.290002
Azerbaijão,Rodoviario -  Freight transport,0.558054,0.630214,0.660853,0.643372,0.650229,0.673396,0.518912,0.528485,0.524129,0.535644
Brasil,Aquaviario -  Freight transport,0.121000,0.121000,0.121000,0.150000,0.150000,0.150000,0.150000,0.150000,0.150000,0.150000
Brasil,Ferroviario - Freight transport,0.165000,0.165000,0.165000,0.179000,0.179000,0.179000,0.179000,0.179000,0.179000,0.179000
Brasil,Rodoviario -  Freight transport,0.714000,0.714000,0.714000,0.671000,0.671000,0.671000,0.671000,0.671000,0.671000,0.671000
Bulgária,Aquaviario -  Freight transport,0.269000,0.274000,0.273000,0.249000,0.245000,0.320000,0.288000,0.244000,0.166000,0.179000
Bulgária,Ferroviario - Freight transport,0.182000,0.179000,0.171000,0.186000,0.193000,0.212000,0.207000,0.196000,0.229000,0.191000
Bulgária,Rodoviario -  Freight transport,0.549000,0.547000,0.556000,0.565000,0.562000,0.468000,0.505000,0.560000,0.605000,0.630000
Bélgica,Aquaviario -  Freight transport,0.159000,0.152000,0.147000,0.156000,0.119000,0.113000,0.110000,0.115000,0.112000,0.107000
Bélgica,Ferroviario - Freight transport,0.111000,0.112000,0.111000,0.111000,0.123000,0.121000,0.116000,0.118000,0.123000,0.117000
Bélgica,Rodoviario -  Freight transport,0.730000,0.736000,0.742000,0.733000,0.758000,0.766000,0.774000,0.767000,0.765000,0.776000
Canadá,Aquaviario -  Freight transport,0.240000,0.245000,0.250000,0.245000,0.226000,0.228000,0.234000,0.232000,0.223000,0.223000
Canadá,Ferroviario - Freight transport,0.467000,0.469000,0.459000,0.464000,0.478000,0.476000,0.469000,0.466000,0.482000,0.482000
Canadá,Rodoviario -  Freight transport,0.293000,0.286000,0.291000,0.291000,0.296000,0.296000,0.297000,0.302000,0.295000,0.295000
Chile,Aquaviario -  Freight transport,0.143000,0.136000,0.133000,0.137000,0.137000,0.139000,0.142000,0.143000,0.142000,0.147000
Chile,Ferroviario - Freight transport,0.140000,0.136000,0.133000,0.132000,0.128000,0.128000,0.128000,0.112000,0.106000,0.085000
Chile,Rodoviario -  Freight transport,0.717000,0.728000,0.734000,0.731000,0.735000,0.733000,0.730000,0.745000,0.752000,0.768000
China,Aquaviario -  Freight transport,0.509000,0.529000,0.534000,0.513000,0.497000,0.536000,0.539000,0.530000,0.536000,0.541000
China,Ferroviario - Freight transport,0.152000,0.137000,0.131000,0.140000,0.145000,0.156000,0.155000,0.153000,0.159000,0.152000
China,Rodoviario -  Freight transport,0.339000,0.334000,0.335000,0.347000,0.358000,0.308000,0.306000,0.317000,0.305000,0.308000
Colômbia,Aquaviario -  Freight transport,0.017000,0.017000,0.026000,0.027000,0.027000,0.025000,0.023000,0.025000,0.026000,0.026000
Colômbia,Ferroviario - Freight transport,0.232000,0.225000,0.238000,0.246000,0.231000,0.208000,0.157000,0.163000,0.171000,0.171000
Colômbia,Rodoviario -  Freight transport,0.751000,0.758000,0.736000,0.727000,0.742000,0.767000,0.820000,0.812000,0.803000,0.803000
Coreia do Sul,Aquaviario -  Freight transport,0.200000,0.200000,0.202000,0.202000,0.197000,0.198000,0.190000,0.190000,0.191000,0.192000
Coreia do Sul,Ferroviario - Freight transport,0.065000,0.063000,0.059000,0.056000,0.053000,0.051000,0.048000,0.048000,0.049000,0.048000
Coreia do Sul,Rodoviario -  Freight transport,0.735000,0.737000,0.739000,0.742000,0.750000,0.751000,0.762000,0.762000,0.760000,0.760000
Croácia,Aquaviario -  Freight transport,0.069000,0.078000,0.074000,0.067000,0.053000,0.069000,0.070000,0.063000,0.044000,0.036000
Croácia,Ferroviario - Freight transport,0.204000,0.194000,0.191000,0.213000,0.215000,0.241000,0.253000,0.238000,0.258000,0.227000
Croácia,Rodoviario -  Freight transport,0.727000,0.728000,0.735000,0.720000,0.731000,0.690000,0.677000,0.699000,0.698000,0.737000
Dinamarca,Aquaviario -  Freight transport,0.115000,0.106000,0.098000,0.090000,0.081000,0.084000,0.076000,0.075000,0.072000,0.073000
Dinamarca,Ferroviario - Freight transport,0.115000,0.117000,0.117000,0.124000,0.131000,0.138000,0.141000,0.144000,0.136000,0.138000
Dinamarca,Rodoviario -  Freight transport,0.770000,0.777000,0.785000,0.786000,0.788000,0.778000,0.783000,0.781000,0.792000,0.789000
EUA,Aquaviario -  Freight transport,0.138000,0.137000,0.137000,0.133000,0.134000,0.128000,0.129000,0.130000,0.131000,0.123000
EUA,Ferroviario - Freight transport,0.419000,0.403000,0.375000,0.369000,0.380000,0.365000,0.345000,0.359000,0.359000,0.342000
EUA,Rodoviario -  Freight transport,0.443000,0.460000,0.488000,0.498000,0.486000,0.507000,0.526000,0.511000,0.510000,0.535000
Eslováquia,Aquaviario -  Freight transport,0.040000,0.032000,0.037000,0.036000,0.031000,0.036000,0.034000,0.033000,0.026000,0.026000
Eslováquia,Ferroviario - Freight transport,0.389000,0.366000,0.346000,0.330000,0.326000,0.310000,0.286000,0.321000,0.304000,0.304000
Eslováquia,Rodoviario -  Freight transport,0.571000,0.602000,0.617000,0.634000,0.643000,0.654000,0.680000,0.646000,0.670000,0.670000
Espanha,Aquaviario -  Freight transport,0.166000,0.162000,0.159000,0.161000,0.153000,0.152000,0.147000,0.144000,0.144000,0.145000
Espanha,Ferroviario - Freight transport,0.040000,0.039000,0.037000,0.036000,0.035000,0.034000,0.033000,0.033000,0.032000,0.032000
Espanha,Rodoviario -  Freight transport,0.794000,0.799000,0.804000,0.803000,0.812000,0.814000,0.820000,0.823000,0.824000,0.823000
Finlândia,Aquaviario -  Freight transport,0.069000,0.072000,0.073000,0.073000,0.067000,0.069000,0.066000,0.062000,0.061000,0.061000
Finlândia,Ferroviario - Freight transport,0.261000,0.253000,0.249000,0.256000,0.266000,0.260000,0.252000,0.254000,0.251000,0.251000
Finlândia,Rodoviario -  Freight transport,0.670000,0.675000,0.678000,0.671000,0.667000,0.671000,0.682000,0.684000,0.688000,0.688000
França,Aquaviario -  Freight transport,0.029000,0.029000,0.028000,0.023000,0.022000,0.024000,0.022000,0.021000,0.020000,0.019000
França,Ferroviario - Freight transport,0.108000,0.123000,0.115000,0.111000,0.105000,0.103000,0.098000,0.106000,0.106000,0.092000
França,Rodoviario -  Freight transport,0.863000,0.848000,0.857000,0.866000,0.873000,0.873000,0.880000,0.873000,0.874000,0.889000
Holanda,Aquaviario -  Freight transport,0.455000,0.446000,0.437000,0.441000,0.425000,0.419000,0.410000,0.416000,0.411000,0.408000
Holanda,Ferroviario - Freight transport,0.059000,0.062000,0.061000,0.061000,0.065000,0.064000,0.062000,0.064000,0.066000,0.064000
Holanda,Rodoviario -  Freight transport,0.486000,0.492000,0.502000,0.498000,0.510000,0.517000,0.528000,0.520000,0.523000,0.528000
Hungria,Aquaviario -  Freight transport,0.055000,0.054000,0.054000,0.049000,0.041000,0.053000,0.050000,0.044000,0.036000,0.032000
Hungria,Ferroviario - Freight transport,0.311000,0.295000,0.286000,0.326000,0.270000,0.265000,0.292000,0.264000,0.266000,0.252000
Hungria,Rodoviario -  Freight transport,0.634000,0.651000,0.660000,0.625000,0.689000,0.682000,0.658000,0.692000,0.698000,0.716000
Itália,Aquaviario -  Freight transport,0.413000,0.414000,0.415000,0.405000,0.393000,0.387000,0.390000,0.373000,0.373000,0.370000
Itália,Ferroviario - Freight transport,0.094000,0.097000,0.096000,0.096000,0.097000,0.093000,0.094000,0.097000,0.099000,0.096000
Itália,Rodoviario -  Freight transport,0.493000,0.489000,0.489000,0.499000,0.510000,0.520000,0.516000,0.530000,0.528000,0.534000
Japão,Aquaviario -  Freight transport,0.438000,0.435000,0.436000,0.437000,0.434000,0.436000,0.429000,0.431000,0.432000,0.433000
Japão,Ferroviario - Freight transport,0.051000,0.050000,0.049000,0.051000,0.049000,0.048000,0.046000,0.047000,0.047000,0.046000
Japão,Rodoviario -  Freight transport,0.511000,0.515000,0.515000,0.512000,0.517000,0.516000,0.525000,0.522000,0.521000,0.521000
Luxemburgo,Aquaviario -  Freight transport,0.084000,0.080000,0.062000,0.062000,0.075000,0.081000,0.082000,0.080000,0.075000,0.070000
Luxemburgo,Ferroviario - Freight transport,0.061000,0.071000,0.065000,0.068000,0.081000,0.069000,0.067000,0.065000,0.062000,0.073000
Luxemburgo,Rodoviario -  Freight transport,0.855000,0.849000,0.873000,0.870000,0.844000,0.850000,0.851000,0.855000,0.863000,0.857000
México,Aquaviario -  Freight transport,0.043000,0.043000,0.037000,0.043000,0.045000,0.044000,0.039000,0.036000,0.043000,0.042000
México,Ferroviario - Freight transport,0.258000,0.255000,0.247000,0.248000,0.242000,0.239000,0.245000,0.252000,0.252000,0.247000
México,Rodoviario -  Freight transport,0.699000,0.702000,0.716000,0.709000,0.713000,0.717000,0.716000,0.712000,0.705000,0.711000
Noruega,Aquaviario -  Freight transport,0.423000,0.429000,0.407000,0.430000,0.427000,0.422000,0.410000,0.399000,0.431000,0.422000
Noruega,Ferroviario - Freight transport,0.084000,0.084000,0.085000,0.084000,0.084000,0.085000,0.086000,0.086000,0.083000,0.045000
Noruega,Rodoviario -  Freight transport,0.493000,0.487000,0.508000,0.486000,0.489000,0.493000,0.504000,0.515000,0.486000,0.533000
Polônia,Aquaviario -  Freight transport,0.005371,0.002561,0.004256,0.002698,0.000836,0.000750,0.000636,0.000657,0.000689,0.000886
Polônia,Ferroviario - Freight transport,0.333063,0.320598,0.307271,0.295027,0.280771,0.262617,0.265961,0.277933,0.289908,0.290682
Polônia,Rodoviario -  Freight transport,0.661565,0.676841,0.688473,0.702275,0.718393,0.736634,0.733404,0.721409,0.709402,0.708432
Reino Unido,Aquaviario -  Freight transport,0.147000,0.142000,0.133000,0.129000,0.125000,0.121000,0.129000,0.121000,0.122000,0.122000
Reino Unido,Ferroviario - Freight transport,0.112000,0.097000,0.085000,0.084000,0.083000,0.081000,0.079000,0.080000,0.078000,0.078000
Reino Unido,Rodoviario -  Freight transport,0.741000,0.761000,0.782000,0.787000,0.792000,0.798000,0.792000,0.799000,0.800000,0.800000
República Tcheca,Aquaviario -  Freight transport,0.000389,0.000444,0.000548,0.000422,0.000392,0.000578,0.000252,0.000276,0.000249,0.000228
República Tcheca,Ferroviario - Freight transport,0.211611,0.206208,0.236744,0.263424,0.287276,0.292734,0.215111,0.203809,0.199161,0.188302
República Tcheca,Rodoviario -  Freight transport,0.788000,0.793348,0.762708,0.736154,0.712333,0.706688,0.784637,0.795915,0.800590,0.811470
Romênia,Aquaviario -  Freight transport,0.290000,0.304000,0.294000,0.274000,0.271000,0.282000,0.287000,0.250000,0.205000,0.223000
Romênia,Ferroviario - Freight transport,0.302000,0.316000,0.303000,0.302000,0.289000,0.268000,0.258000,0.253000,0.255000,0.240000
Romênia,Rodoviario -  Freight transport,0.408000,0.380000,0.403000,0.424000,0.441000,0.450000,0.455000,0.497000,0.540000,0.537000
Rússia,Aquaviario -  Freight transport,0.043000,0.043000,0.040000,0.042000,0.035000,0.036000,0.036000,0.038000,0.037000,0.040000
Rússia,Ferroviario - Freight transport,0.864000,0.869000,0.868000,0.869000,0.877000,0.872000,0.871000,0.865000,0.861000,0.844000
Rússia,Rodoviario -  Freight transport,0.093000,0.088000,0.092000,0.089000,0.088000,0.092000,0.093000,0.097000,0.102000,0.116000
Suécia,Aquaviario -  Freight transport,0.103000,0.105000,0.101000,0.102000,0.107000,0.110000,0.106000,0.104000,0.105000,0.107000
Suécia,Ferroviario - Freight transport,0.295000,0.296000,0.299000,0.301000,0.307000,0.300000,0.296000,0.305000,0.305000,0.304000
Suécia,Rodoviario -  Freight transport,0.602000,0.599000,0.600000,0.597000,0.586000,0.590000,0.598000,0.591000,0.590000,0.589000
Sérvia,Aquaviario -  Freight transport,0.113159,0.122052,0.111453,0.080559,0.056774,0.061772,0.050530,0.125659,0.111223,0.115292
Sérvia,Ferroviario - Freight transport,0.445508,0.458453,0.371231,0.365553,0.312221,0.243417,0.248393,0.199085,0.200021,0.165829
Sérvia,Rodoviario -  Freight transport,0.441332,0.419496,0.517316,0.553888,0.631005,0.694810,0.701078,0.675256,0.688756,0.718879
Turquia,Aquaviario -  Freight transport,0.033000,0.039000,0.042000,0.045000,0.043000,0.047000,0.048000,0.050000,0.053000,0.057000
Turquia,Ferroviario - Freight transport,0.039000,0.036000,0.037000,0.038000,0.041000,0.043000,0.047000,0.042000,0.045000,0.035000
Turquia,Rodoviario -  Freight transport,0.928000,0.925000,0.921000,0.917000,0.916000,0.910000,0.905000,0.908000,0.901000,0.908000
Vietnã,Aquaviario -  Freight transport,0.220000,0.218000,0.230000,0.237000,0.242000,0.247000,0.259000,0.263000,0.266000,0.266000
Vietnã,Ferroviario - Freight transport,0.021000,0.019000,0.016000,0.015000,0.015000,0.015000,0.013000,0.013000,0.013000,0.013000
Vietnã,Rodoviario -  Freight transport,0.759000,0.763000,0.754000,0.748000,0.743000,0.738000,0.728000,0.724000,0.721000,0.721000
Áustria,Aquaviario -  Freight transport,0.035000,0.028000,0.030000,0.030000,0.021000,0.025000,0.023000,0.020000,0.017000,0.017000
Áustria,Ferroviario - Freight transport,0.331000,0.325000,0.321000,0.319000,0.316000,0.310000,0.298000,0.300000,0.302000,0.293000
Áustria,Rodoviario -  Freight transport,0.634000,0.647000,0.649000,0.651000,0.663000,0.665000,0.679000,0.680000,0.681000,0.690000
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
    
    # FUNÇÃO DE CORREÇÃO PARA VALORES PEQUENOS (0% -> 0.1%)
    def fix_small_values(x):
        # Se o valor existe e é maior que 0 mas menor que 0.1%, arredonda para 0.1%
        if pd.notnull(x) and 0 < x < 0.1:
            return 0.1
        return x

    for col in ['Ferroviário (%)', 'Rodoviário (%)', 'Aquaviário (%)']:
        if col in df_real.columns:
            # Multiplica por 100 se estiver em decimal
            df_real[col] = df_real[col].apply(lambda x: x * 100 if pd.notnull(x) and x <= 1.5 else x)
            # Aplica a correção de 0.1%
            df_real[col] = df_real[col].apply(fix_small_values)
            # Arredonda para 1 casa decimal
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
    # ATUALIZADO CONFORME SOLICITAÇÃO (TEXTO E ACENTO)
    st.sidebar.warning(f"⚠️ **Atenção:** Para os países selecionados (**{lista_nomes}**), a participação do modal aquaviário é muito baixa (< 1%). Isso pode dificultar a visualização deste país no gráfico.")

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
    st.select_slider("Linha do Tempo:", options=opcoes, key="slider_principal")

# --- GRÁFICO ---
df_plot = df[
    (df['Ano'].astype(str) == st.session_state.slider_principal) & 
    (df['Pais'].isin(paises_para_mostrar))
]

if not df_plot.empty:
    df_plot = df_plot.sort_values(by='Pais', key=lambda col: col.map(normalizar_para_ordenacao))
    
    # [LÓGICA DE TAMANHO VISUAL]: Reduzi o tamanho mínimo de 2 para 1
    # Se valor < 1%, usa 1% para a bolinha não sumir, mas ficar bem pequena
    df_plot['Tamanho_Visual'] = df_plot['Aquaviário (%)'].apply(lambda x: 1 if x < 1 else x)

    st.divider()

    # EXPLICAÇÃO DOS EIXOS E DICAS (ATUALIZADO COM 2ª DICA)
    st.info("""
    💡 **Dicas de Navegação:**
    1. Clique no nome do país na legenda (à direita) para **ocultá-lo ou visualizá-lo** (duplo clique isola).
    2. Utilize o menu na **barra lateral (esquerda)** para adicionar outros países ao gráfico.
    """)

    st.markdown("""
    **Legenda do Gráfico:**
    * **Eixo Y (Vertical):** Participação do Modal **Rodoviário** (%)
    * **Eixo X (Horizontal):** Participação do Modal **Ferroviário** (%)
    * **Tamanho da Bolinha:** Participação do Modal **Aquaviário** (%)
    """)

    col_ano = st.columns([1])[0]
    col_ano.metric(label="Ano Visualizado", value=st.session_state.slider_principal)

    titulo_grafico = f"<b>Cenário: {st.session_state.slider_principal}</b>"
    
    fig = px.scatter(
        df_plot,
        x="Ferroviário (%)", 
        y="Rodoviário (%)", 
        size="Tamanho_Visual", # Usa tamanho visual (mínimo 1)
        color="Pais", 
        text="Pais", 
        color_discrete_map=cores_paises, 
        title=titulo_grafico, 
        size_max=60, 
        template="plotly_white",
        range_x=[-5, 105], 
        range_y=[-5, 105],
        category_orders={"Pais": paises_para_mostrar},
        # HOVER_DATA mostra o valor REAL, ignorando o tamanho visual
        hover_data={
            "Pais": False,
            "Tamanho_Visual": False,
            "Ferroviário (%)": ":.1f",
            "Rodoviário (%)": ":.1f",
            "Aquaviário (%)": ":.1f"
        }
    )
    
    # EIXOS E LEGENDAS MAIS CLAROS COM DTICK=10 E FONTE MAIOR NA LEGENDA
    fig.update_layout(
        xaxis=dict(title="<b>Eixo X:</b> Participação Ferroviária (%)", dtick=10),
        yaxis=dict(title="<b>Eixo Y:</b> Participação Rodoviária (%)", dtick=10),
        legend=dict(
            title_text="<b>Países (Clique para Filtrar)</b>",
            font=dict(size=16), # LEGENDA AUMENTADA
            itemsizing='constant'
        ),
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
                      "🚢 Aquaviário: %{customdata[2]}%<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --- NOVA TABELA DE DADOS ---
    st.divider()
    st.subheader(f"📋 Dados Detalhados: {st.session_state.slider_principal}")
    
    # CALCULO DINAMICO DA ALTURA PARA REMOVER SOBRAS
    # 35px por linha + 38px de cabeçalho
    altura_tabela = (len(df_plot) * 35) + 38

    # Selecionar e ordenar colunas para a tabela (SEM A COLUNA VISUAL)
    cols_to_show = ['Pais', 'Rodoviário (%)', 'Ferroviário (%)', 'Aquaviário (%)']
    st.dataframe(
        df_plot[cols_to_show].sort_values(by='Pais', key=lambda col: col.map(normalizar_para_ordenacao)).set_index('Pais'),
        use_container_width=True,
        height=altura_tabela # ALTURA DINÂMICA
    )

else:
    st.warning("Nenhum dado encontrado para a seleção atual.")