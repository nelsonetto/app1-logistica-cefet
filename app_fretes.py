import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

st.set_page_config(page_title="Monitor OECD", layout="wide")

# --- FUNÇÃO DE CARREGAMENTO E LIMPEZA ---
@st.cache_data
def carregar_dados_oecd(periodo_inicio):
    # URL da API
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
            
            # --- LIMPEZA DOS DADOS (CORREÇÃO) ---
            # 1. Selecionar apenas as colunas que importam
            # REF_AREA = País/Área
            # TIME_PERIOD = Trimestre (ex: 2024-Q1)
            # OBS_VALUE = O número/valor
            # MEASURE = O tipo de medida (ex: Toneladas, Index) - importante para não misturar dados
            cols_desejadas = ['REF_AREA', 'TIME_PERIOD', 'OBS_VALUE', 'MEASURE']
            
            # Filtra apenas se as colunas existirem para evitar erro
            cols_finais = [c for c in cols_desejadas if c in df.columns]
            df_limpo = df[cols_finais].copy()
            
            # 2. Renomear para ficar bonito na tela
            df_limpo.rename(columns={
                'REF_AREA': 'País',
                'TIME_PERIOD': 'Trimestre',
                'OBS_VALUE': 'Valor',
                'MEASURE': 'Medida'
            }, inplace=True)
            
            return df_limpo
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# --- INTERFACE ---
st.title("📈 Evolução de Fretes (OCDE)")

# Carregamento Inicial
df = carregar_dados_oecd("2023-Q1")

if not df.empty:
    # --- FILTROS ---
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtro de País
        lista_paises = sorted(df['País'].unique())
        # Pré-selecionar alguns países padrão
        padrao = ['USA', 'BRA', 'DEU'] # Tenta pegar esses se existirem
        padrao_existente = [p for p in padrao if p in lista_paises]
        
        paises_selecionados = st.multiselect(
            "Selecione os Países:",
            options=lista_paises,
            default=padrao_existente if padrao_existente else lista_paises[:3]
        )

    with col2:
        # Filtro de Medida (Importante: as vezes a tabela tem Toneladas e Toneladas-KM misturado)
        lista_medidas = sorted(df['Medida'].unique())
        medida_selecionada = st.selectbox("Tipo de Medida:", lista_medidas)

    # --- APLICAÇÃO DOS FILTROS ---
    if paises_selecionados:
        # Filtra País E Filtra a Medida (para o gráfico não ficar maluco)
        df_filtrado = df[
            (df['País'].isin(paises_selecionados)) & 
            (df['Medida'] == medida_selecionada)
        ]
        
        # Ordenar por data para o gráfico não ficar riscado
        df_filtrado = df_filtrado.sort_values(by='Trimestre')

        # --- GRÁFICO CORRETO (LINHAS / TEMPO) ---
        if not df_filtrado.empty:
            fig = px.line(
                df_filtrado, 
                x="Trimestre", 
                y="Valor", 
                color="País", 
                markers=True,
                title=f"Evolução por Trimestre ({medida_selecionada})",
                template="plotly_white" # Visual limpo
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela Limpa abaixo
            with st.expander("Ver dados em tabela"):
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        else:
            st.warning("Sem dados para essa combinação.")
    else:
        st.info("Selecione pelo menos um país.")
else:
    st.error("Não foi possível carregar os dados da OCDE. Tente novamente mais tarde.")