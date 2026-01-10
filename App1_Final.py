import streamlit as st
import pandas as pd
import plotly.express as px
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
    }
    
    /* Texto das métricas */
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---

def normalizar_para_ordenacao(texto):
    """Remove acentos para ordenação correta."""
    if not isinstance(texto, str):
        return str(texto)
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

@st.cache_data
def carregar_dados_excel():
    """
    Carrega os dados atualizados (Origem: Base%_Final_App1.xlsx).
    Dados consolidados e embutidos para garantir integridade.
    """
    # Dicionário com os dados exatos do Excel fornecido (Paises Principais + Extras)
    data = {
        'Pais': ['Alemanha']*10 + ['Argentina']*10 + ['Austrália']*10 + ['Azerbaijão']*10 + ['Belgica']*10 + ['Brasil ']*10 + ['Bulgária']*10 + ['Canadá']*10 + ['Chile']*10 + ['China']*10 + ['Colômbia']*10 + ['Coreia do Sul']*10 + ['Croácia']*10 + ['Dinamarca']*10 + ['EUA']*10 + ['Eslováquia']*10 + ['Espanha']*10 + ['Finlândia']*10 + ['França']*10 + ['Holanda']*10 + ['Hungria']*10 + ['Itália']*10 + ['Japão']*10 + ['Luxemburgo']*10 + ['Mexico']*10 + ['Noruega']*10 + ['Polônia']*10 + ['Reino Unido']*10 + ['República Tcheca']*10 + ['Romênia']*10 + ['Russia']*10 + ['Suécia']*10 + ['Sérvia']*10 + ['Turquia']*10 + ['Vietnã']*10 + ['Áustria']*10,
        'Ano': [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023] * 36,
        'Rodoviário (%)': [
            # Alemanha
            71.30, 71.81, 70.21, 71.70, 72.40, 72.29, 75.00, 73.60, 73.40, 72.80,
            # Argentina
            85.98, 85.90, 85.44, 86.55, 86.57, 85.53, 85.98, 86.85, 86.72, 86.23,
            # Austrália
            29.27, 29.11, 29.52, 29.19, 29.20, 29.13, 28.58, 29.33, 29.86, 29.98,
            # Azerbaijão
            55.77, 63.04, 65.88, 64.29, 64.92, 67.07, 51.83, 53.14, 52.32, 53.42,
            # Belgica
            72.97, 73.62, 74.17, 73.31, 75.81, 76.59, 77.47, 76.73, 76.47, 77.61,
            # Brasil
            71.39, 71.39, 71.39, 67.10, 67.10, 67.10, 67.10, 67.10, 67.10, 67.10,
            # Bulgária
            55.00, 54.83, 55.71, 56.45, 56.06, 46.76, 50.62, 56.05, 60.61, 62.97,
            # Canadá
            29.30, 28.60, 29.10, 29.10, 29.60, 29.60, 29.70, 30.20, 29.50, 29.50,
            # Chile
            60.40, 60.36, 60.14, 59.94, 60.26, 61.76, 61.34, 63.01, 63.38, 64.01,
            # China
            33.90, 33.40, 33.50, 34.70, 35.80, 30.80, 30.60, 31.70, 30.50, 30.77,
            # Colômbia
            75.07, 75.77, 73.62, 72.72, 74.25, 76.70, 82.00, 81.21, 80.34, 80.31,
            # Coreia do Sul
            73.49, 73.69, 73.87, 74.21, 74.99, 75.09, 76.21, 76.20, 76.01, 76.03,
            # Croácia
            73.08, 73.04, 73.33, 71.88, 73.33, 68.97, 67.86, 69.68, 69.70, 73.71,
            # Dinamarca
            77.03, 77.57, 78.64, 78.67, 78.70, 77.97, 78.14, 78.18, 79.29, 78.70,
            # EUA
            44.30, 46.00, 48.80, 49.80, 48.59, 50.70, 52.60, 51.10, 51.00, 53.49,
            # Eslováquia
            57.19, 60.12, 61.58, 63.25, 64.35, 65.35, 68.09, 64.54, 67.05, 67.06,
            # Espanha
            82.27, 82.31, 82.28, 82.54, 82.58, 82.63, 84.21, 83.38, 82.62, 82.36,
            # Finlândia
            75.15, 77.33, 76.84, 75.81, 74.37, 74.65, 75.32, 74.25, 76.20, 76.82,
            # França
            86.32, 84.81, 85.71, 86.60, 87.32, 87.30, 87.99, 87.31, 87.42, 88.89,
            # Holanda
            48.56, 49.21, 50.21, 49.80, 50.97, 51.67, 52.79, 52.03, 52.33, 52.83,
            # Hungria
            63.35, 65.04, 65.99, 62.46, 68.93, 68.12, 65.84, 69.23, 69.73, 71.66,
            # Itália
            61.23, 60.27, 58.31, 59.38, 60.60, 63.39, 64.22, 63.10, 63.38, 63.21,
            # Japão
            51.10, 51.50, 51.51, 51.20, 51.71, 51.60, 52.50, 52.21, 52.10, 52.10,
            # Luxemburgo
            85.54, 84.94, 87.35, 86.95, 84.35, 85.06, 85.13, 85.55, 86.27, 85.69,
            # Mexico
            67.44, 67.54, 67.84, 68.23, 68.74, 69.12, 69.33, 69.02, 69.29, 70.62,
            # Noruega
            52.51, 53.38, 53.13, 53.46, 53.01, 53.83, 54.77, 54.94, 54.31, 53.90,
            # Polônia
            83.17, 83.62, 85.05, 85.88, 85.72, 87.28, 88.16, 88.19, 87.32, 86.25,
            # Reino Unido
            74.10, 76.10, 78.18, 78.72, 79.22, 79.80, 79.22, 79.90, 80.00, 80.00,
            # República Tcheca
            76.63, 77.82, 78.52, 72.98, 70.50, 69.95, 78.03, 79.16, 79.56, 80.70,
            # Romênia
            40.71, 38.00, 40.29, 42.39, 44.10, 45.00, 45.50, 49.77, 54.00, 53.68,
            # Russia
            9.30, 8.80, 9.20, 8.90, 8.80, 9.20, 9.30, 9.70, 10.20, 11.60,
            # Suécia
            48.15, 48.72, 49.51, 49.48, 50.09, 51.09, 51.70, 53.74, 53.95, 52.92,
            # Sérvia
            44.13, 41.95, 51.76, 55.42, 63.14, 69.50, 70.09, 67.54, 68.87, 71.86,
            # Turquia
            90.91, 91.02, 90.76, 90.57, 90.39, 90.35, 90.65, 90.68, 91.09, 91.21,
            # Vietnã
            22.54, 23.41, 23.83, 23.19, 23.41, 24.08, 23.56, 25.50, 27.03, 28.36,
            # Áustria
            63.38, 64.80, 64.95, 65.14, 66.25, 66.53, 67.84, 68.00, 68.07, 68.96
        ],
        'Ferroviário (%)': [
            # Alemanha
            18.80, 18.99, 21.30, 19.70, 20.20, 19.80, 17.50, 19.00, 19.80, 20.60,
            # Argentina
            4.38, 4.39, 4.31, 3.96, 4.38, 4.77, 4.64, 4.93, 5.06, 4.59,
            # Austrália
            56.89, 57.51, 57.57, 57.88, 57.87, 57.90, 58.34, 57.89, 57.26, 57.20,
            # Azerbaijão
            28.46, 25.29, 21.57, 18.25, 17.34, 19.92, 28.90, 29.71, 32.07, 29.06,
            # Belgica
            11.09, 11.22, 11.09, 11.04, 12.27, 12.09, 11.57, 11.77, 12.34, 11.69,
            # Brasil
            16.49, 16.49, 16.49, 17.91, 17.91, 17.91, 17.91, 17.91, 17.91, 17.91,
            # Bulgária
            18.08, 17.93, 17.14, 18.71, 19.39, 21.18, 20.63, 19.47, 22.84, 19.07,
            # Canadá
            46.70, 46.90, 45.90, 46.40, 47.80, 47.60, 46.90, 46.60, 48.20, 48.20,
            # Chile
            13.71, 13.56, 13.67, 13.63, 13.51, 12.97, 14.15, 12.94, 12.16, 11.52,
            # China
            15.20, 13.70, 13.10, 14.00, 14.50, 15.60, 15.50, 15.30, 15.90, 15.18,
            # Colômbia
            23.22, 22.54, 23.81, 24.57, 23.09, 20.77, 15.70, 16.26, 17.08, 17.06,
            # Coreia do Sul
            6.50, 6.30, 5.90, 5.60, 5.30, 5.10, 4.80, 4.80, 4.90, 4.90,
            # Croácia
            20.19, 19.13, 19.17, 21.09, 21.48, 24.14, 25.00, 23.87, 26.06, 22.86,
            # Dinamarca
            11.48, 11.68, 11.82, 12.44, 13.04, 13.66, 13.95, 14.55, 13.64, 13.89,
            # EUA
            41.90, 40.29, 37.50, 36.90, 38.00, 36.50, 34.50, 35.89, 35.90, 34.21,
            # Eslováquia
            38.75, 36.56, 34.60, 33.05, 32.59, 30.99, 28.57, 32.13, 30.37, 30.29,
            # Espanha
            4.11, 3.93, 3.98, 3.90, 3.76, 3.63, 3.40, 3.40, 3.25, 2.91,
            # Finlândia
            19.24, 17.21, 17.70, 18.64, 19.71, 19.15, 18.83, 19.72, 19.01, 18.77,
            # França
            10.80, 12.29, 11.49, 11.09, 10.49, 10.29, 9.81, 10.59, 10.59, 9.20,
            # Holanda
            5.93, 6.17, 6.07, 6.08, 6.53, 6.43, 6.23, 6.41, 6.59, 6.38,
            # Hungria
            31.14, 29.57, 28.57, 32.62, 26.94, 26.51, 29.20, 26.32, 26.67, 25.15,
            # Itália
            10.60, 10.78, 11.50, 10.96, 10.82, 9.28, 10.03, 10.57, 10.11, 9.88,
            # Japão
            5.10, 5.00, 4.90, 5.10, 4.90, 4.80, 4.60, 4.70, 4.70, 4.60,
            # Luxemburgo
            6.09, 7.08, 6.49, 6.81, 8.12, 6.87, 6.67, 6.46, 6.27, 7.36,
            # Mexico
            24.66, 24.54, 24.27, 24.18, 23.52, 23.14, 23.55, 23.91, 23.64, 22.49,
            # Noruega
            9.30, 9.52, 9.38, 9.22, 9.13, 9.01, 9.09, 9.01, 8.62, 7.79,
            # Polônia
            16.57, 16.19, 14.80, 14.02, 14.21, 12.67, 11.79, 11.79, 12.66, 13.73,
            # Reino Unido
            11.18, 9.69, 8.51, 8.39, 8.28, 8.10, 7.89, 7.99, 7.78, 7.78,
            # República Tcheca
            22.10, 20.98, 20.44, 26.03, 28.47, 28.98, 21.28, 20.22, 19.83, 18.68,
            # Romênia
            30.24, 31.56, 30.27, 30.25, 28.86, 26.72, 25.83, 25.27, 25.57, 23.99,
            # Russia
            86.40, 86.90, 86.80, 86.90, 87.70, 87.20, 87.10, 86.50, 86.10, 84.40,
            # Suécia
            20.38, 20.96, 21.04, 20.78, 21.19, 20.61, 20.64, 20.98, 19.83, 20.16,
            # Sérvia
            44.50, 45.83, 37.14, 36.56, 31.18, 24.32, 24.86, 19.92, 20.00, 16.59,
            # Turquia
            4.24, 4.04, 4.05, 4.03, 4.13, 3.95, 3.82, 4.09, 3.89, 3.57,
            # Vietnã
            1.94, 1.66, 1.35, 1.35, 1.36, 1.16, 1.04, 1.24, 1.37, 1.14,
            # Áustria
            33.08, 32.47, 32.11, 31.86, 31.67, 31.00, 29.81, 30.00, 30.22, 29.28
        ],
        'Aquaviário (%)': [
            # Alemanha
            9.90, 9.20, 8.50, 8.60, 7.39, 7.91, 7.50, 7.41, 6.80, 6.59,
            # Argentina
            9.64, 9.70, 10.25, 9.50, 9.05, 9.70, 9.38, 8.22, 8.22, 9.18,
            # Austrália
            13.84, 13.37, 12.91, 12.93, 12.93, 12.97, 13.08, 12.78, 12.88, 12.82,
            # Azerbaijão
            15.77, 11.67, 12.55, 17.46, 17.74, 13.01, 19.27, 17.15, 15.61, 17.52,
            # Belgica
            15.94, 15.17, 14.74, 15.65, 11.93, 11.32, 10.96, 11.50, 11.19, 10.70,
            # Brasil
            12.11, 12.11, 12.11, 15.00, 15.00, 15.00, 15.00, 15.00, 15.00, 15.00,
            # Bulgária
            26.92, 27.24, 27.14, 24.84, 24.55, 32.06, 28.75, 24.47, 16.55, 17.96,
            # Canadá
            24.00, 24.50, 25.00, 24.50, 22.60, 22.80, 23.40, 23.20, 22.30, 22.30,
            # Chile
            25.89, 26.08, 26.19, 26.43, 26.23, 25.27, 24.51, 24.05, 24.46, 24.48,
            # China
            50.90, 52.90, 53.40, 51.30, 49.70, 53.60, 53.90, 53.00, 53.60, 54.05,
            # Colômbia
            1.71, 1.68, 2.57, 2.71, 2.66, 2.53, 2.30, 2.53, 2.58, 2.62,
            # Coreia do Sul
            20.01, 20.01, 20.23, 20.19, 19.72, 19.81, 18.99, 19.00, 19.09, 19.07,
            # Croácia
            6.73, 7.83, 7.50, 7.03, 5.19, 6.90, 7.14, 6.45, 4.24, 3.43,
            # Dinamarca
            11.48, 10.75, 9.55, 8.89, 8.26, 8.37, 7.91, 7.27, 7.07, 7.41,
            # EUA
            13.80, 13.71, 13.70, 13.30, 13.40, 12.80, 12.90, 13.01, 13.10, 12.31,
            # Eslováquia
            4.06, 3.32, 3.81, 3.70, 3.06, 3.66, 3.34, 3.32, 2.58, 2.65,
            # Espanha
            13.62, 13.76, 13.74, 13.56, 13.66, 13.74, 12.38, 13.22, 14.13, 14.73,
            # Finlândia
            5.61, 5.47, 5.46, 5.56, 5.91, 6.21, 5.85, 6.04, 4.80, 4.41,
            # França
            2.89, 2.90, 2.80, 2.31, 2.19, 2.41, 2.20, 2.11, 1.99, 1.91,
            # Holanda
            45.51, 44.62, 43.72, 44.12, 42.50, 41.90, 40.98, 41.56, 41.09, 40.79,
            # Hungria
            5.52, 5.39, 5.44, 4.92, 4.13, 5.37, 4.96, 4.44, 3.60, 3.19,
            # Itália
            28.17, 28.95, 30.19, 29.66, 28.58, 27.33, 25.75, 26.33, 26.51, 26.90,
            # Japão
            43.80, 43.50, 43.59, 43.70, 43.39, 43.60, 42.90, 43.09, 43.20, 43.30,
            # Luxemburgo
            8.37, 7.98, 6.16, 6.24, 7.53, 8.07, 8.21, 7.98, 7.47, 6.94,
            # Mexico
            7.91, 7.92, 7.89, 7.59, 7.74, 7.75, 7.12, 7.08, 7.07, 6.89,
            # Noruega
            38.19, 37.09, 37.50, 37.33, 37.86, 37.16, 36.14, 36.05, 37.07, 38.31,
            # Polônia
            0.26, 0.19, 0.15, 0.10, 0.07, 0.05, 0.05, 0.02, 0.02, 0.02,
            # Reino Unido
            14.72, 14.21, 13.31, 12.88, 12.50, 12.10, 12.89, 12.11, 12.22, 12.22,
            # República Tcheca
            1.27, 1.20, 1.04, 0.99, 1.03, 1.07, 0.70, 0.62, 0.60, 0.62,
            # Romênia
            29.05, 30.44, 29.44, 27.36, 27.04, 28.28, 28.67, 24.96, 20.43, 22.33,
            # Russia
            4.30, 4.30, 4.00, 4.20, 3.50, 3.60, 3.60, 3.80, 3.70, 4.00,
            # Suécia
            31.47, 30.31, 29.45, 29.74, 28.72, 28.30, 27.66, 25.29, 26.22, 26.92,
            # Sérvia
            11.38, 12.22, 11.10, 8.02, 5.69, 6.17, 5.05, 12.54, 11.13, 11.55,
            # Turquia
            4.85, 4.94, 5.20, 5.40, 5.48, 5.70, 5.53, 5.23, 5.03, 5.23,
            # Vietnã
            75.52, 74.93, 74.82, 75.46, 75.23, 74.76, 75.40, 73.26, 71.59, 70.50,
            # Áustria
            3.54, 2.73, 2.95, 3.00, 2.08, 2.47, 2.35, 2.00, 1.71, 1.75
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Assegurar formato correto
    df['Ano'] = df['Ano'].astype(int)
    
    return df

# --- CARREGAMENTO DOS DADOS ---
df = carregar_dados_excel()

if df.empty:
    st.stop() # Para a execução se não houver dados

# --- SIDEBAR (Barra Lateral) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # 1. Seleção de Países
    lista_paises = sorted(df['Pais'].unique(), key=normalizar_para_ordenacao)
    
    # Tenta selecionar 'Brasil' e 'China' por padrão se existirem, senão seleciona os 2 primeiros
    padrao = [p for p in ['Brasil ', 'China', 'EUA'] if p in lista_paises]
    if not padrao:
        padrao = lista_paises[:2]
        
    paises_selecionados = st.multiselect(
        "Selecione os Países:",
        options=lista_paises,
        default=padrao
    )
    
    st.markdown("---")
    
    # 2. Seleção de Anos (Slider ou Selectbox)
    anos_disponiveis = sorted(df['Ano'].unique())
    
    col_ano1, col_ano2 = st.columns(2)
    with col_ano1:
        ano_a = st.selectbox("Ano Inicial (A)", options=anos_disponiveis, index=0)
    with col_ano2:
        ano_b = st.selectbox("Ano Final (B)", options=anos_disponiveis, index=len(anos_disponiveis)-1)

    st.markdown("---")
    # Botão de Atualizar (Opcional, pois o Streamlit atualiza auto, mas o usuário pediu estilo botão verde)
    btn_atualizar = st.button("Atualizar Análise")

# --- CORPO PRINCIPAL ---

st.title("📊 Análise Comparativa da Matriz de Transportes")
st.markdown(f"**Comparativo entre {ano_a} e {ano_b}**")

if not paises_selecionados:
    st.warning("⚠️ Por favor, selecione pelo menos um país na barra lateral.")
else:
    # Validação dos Anos
    if int(ano_b) < int(ano_a):
        st.error("⚠️ **Erro:** O Ano Final não pode ser anterior ao Ano Inicial. Por favor, ajuste a seleção.")
    else:
        # Filtrar DataFrame
        df_var = df[df['Pais'].isin(paises_selecionados)].copy()
        
        # Criar DataFrames específicos para Ano A e Ano B
        df_a = df_var[df_var['Ano'] == int(ano_a)].set_index('Pais')[['Rodoviário (%)', 'Ferroviário (%)', 'Aquaviário (%)']]
        df_b = df_var[df_var['Ano'] == int(ano_b)].set_index('Pais')[['Rodoviário (%)', 'Ferroviário (%)', 'Aquaviário (%)']]
        
        # Reindexar para garantir que temos todos os países selecionados (mesmo se faltar dado em um ano)
        df_a = df_a.reindex(paises_selecionados).fillna(0)
        df_b = df_b.reindex(paises_selecionados).fillna(0)

        # Calcular Diferença (B - A)
        df_diff = df_b - df_a
        
        # --- EXIBIÇÃO: TABELA DE VARIAÇÃO ---
        st.subheader(f"📈 Variação da Matriz ({ano_a} ➝ {ano_b})")
        st.markdown("*Valores em pontos percentuais (p.p.)*")
        
        # Ordenar tabela
        df_diff_sorted = df_diff.sort_index(key=lambda col: col.map(normalizar_para_ordenacao))
        
        # Estilização da Tabela (Cores condicionais)
        def colorir_valor(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'grey'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df_diff_sorted.style.format("{:+.2f} p.p.").applymap(colorir_valor),
            use_container_width=True
        )
        
        st.markdown("---")

        # --- EXIBIÇÃO: GRÁFICOS ---
        st.subheader("📊 Visualização Gráfica")

        # Preparar dados para o gráfico (Formato Longo para Plotly)
        # Queremos mostrar as barras lado a lado: Ano A vs Ano B para cada país e modal
        
        # Filtrar apenas anos A e B
        df_chart = df_var[df_var['Ano'].isin([int(ano_a), int(ano_b)])].copy()
        
        # Melt para o gráfico
        df_chart_long = df_chart.melt(
            id_vars=['Pais', 'Ano'], 
            value_vars=['Rodoviário (%)', 'Ferroviário (%)', 'Aquaviário (%)'],
            var_name='Modal', 
            value_name='Participação (%)'
        )
        
        # Gráfico Interativo
        fig = px.bar(
            df_chart_long,
            x="Pais",
            y="Participação (%)",
            color="Modal",
            pattern_shape="Ano", # Diferenciar ano por textura ou usar faceting
            barmode="group",
            facet_col="Modal", # Separar por modal para facilitar comparação
            title=f"Comparativo de Modais por País ({ano_a} vs {ano_b})",
            height=500,
            category_orders={"Ano": [int(ano_a), int(ano_b)]}
        )
        
        fig.update_layout(title_x=0.5)
        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)

        # --- DADOS BRUTOS (Expander) ---
        with st.expander("📂 Ver Dados Brutos (Valores em % do Total)"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Dados de {ano_a}**")
                st.dataframe(df_a.style.format("{:.2f}%"), use_container_width=True)
            with col2:
                st.markdown(f"**Dados de {ano_b}**")
                st.dataframe(df_b.style.format("{:.2f}%"), use_container_width=True)