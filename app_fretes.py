import streamlit as st
import pandas as pd
import requests
import io

# Configuração da página
st.set_page_config(page_title="Monitor OECD", layout="wide")

# --- 1. A FUNÇÃO DE "BACKEND" (O Motor) ---
# Usamos @st.cache_data para não baixar da internet toda vez que você clica num filtro.
# Ele baixa uma vez e guarda na memória.
@st.cache_data
def carregar_dados_oecd(periodo_inicio):
    url = "https://sdmx.oecd.org/public/rest/data/OECD.ITF,DSD_ST@DF_STFREIGHT,1.0/.Q......"
    
    params = {
        "startPeriod": periodo_inicio,
        "dimensionAtObservation": "AllDimensions"
    }
    
    headers = {'Accept': 'application/vnd.sdmx.data+csv; file=true'}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            return df
        else:
            st.error(f"Erro na API: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return pd.DataFrame()

# --- 2. O APLICATIVO (Frontend) ---

st.title("🚢 Painel de Fretes Internacionais (OCDE)")

# Barra lateral para configurações
with st.sidebar:
    st.header("Filtros")
    data_inicio = st.selectbox("Período de Início:", ["2023-Q1", "2023-Q4", "2024-Q1", "2024-Q2"])
    
    if st.button("Carregar/Atualizar Dados"):
        st.session_state['dados'] = carregar_dados_oecd(data_inicio)

# Verifica se os dados já foram carregados
if 'dados' in st.session_state:
    df = st.session_state['dados']
    
    # --- A MÁGICA DO FILTRO DE PAÍSES AQUI ---
    
    # 1. Descobrir quais países existem na tabela (Coluna REF_AREA)
    lista_paises = df['REF_AREA'].unique().tolist()
    lista_paises.sort() # Deixar em ordem alfabética
    
    # 2. Criar o componente de Multi-Seleção
    paises_selecionados = st.multiselect(
        "Selecione os Países para visualizar:",
        options=lista_paises,
        default=lista_paises[:3] # Já começa com os 3 primeiros marcados
    )
    
    # 3. Filtrar a tabela baseada na escolha
    # Se o usuário escolheu algo, filtramos. Se não, mostramos tudo (ou nada).
    if paises_selecionados:
        df_filtrado = df[df['REF_AREA'].isin(paises_selecionados)]
        
        # Mostrar métricas ou tabelas
        st.subheader(f"Dados filtrados: {', '.join(paises_selecionados)}")
        st.dataframe(df_filtrado, use_container_width=True)
        
        # Exemplo de Gráfico rápido (opcional)
        # Vamos pegar uma métrica comum, ex: Valor Observado (OBS_VALUE)
        st.bar_chart(df_filtrado, x="REF_AREA", y="OBS_VALUE", color="REF_AREA")
        
    else:
        st.warning("Por favor, selecione pelo menos um país acima.")
        
else:
    st.info("👈 Clique no botão na barra lateral para carregar os dados pela primeira vez.")