import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px

st.set_page_config(page_title="Matriz de Transportes (OCDE)", layout="wide")

# --- FUNÇÃO: CARREGAR DADOS ANUAIS GLOBAIS ---
@st.cache_data(ttl=3600) # Cache por 1 hora
def carregar_dados_anuais():
    """
    Busca dados anuais de indicadores de transporte do ITF/OCDE.
    Foca na participação percentual (% share) dos modais no transporte terrestre total.
    """
    # URL para indicadores anuais do ITF (International Transport Forum)
    # Pedimos dados a partir de 2015 para não ficar muito pesado
    url = "https://sdmx.oecd.org/public/rest/data/OECD.ITF,DF_ITF_INDICATORS,1.0/.?startPeriod=2015"
    
    headers = {'Accept': 'application/vnd.sdmx.data+csv; file=true'}
    
    with st.spinner('Conectando à base de dados global da OCDE... (Isso pode levar alguns segundos)'):
        try:
            response = requests.get(url, headers=headers, timeout=60)
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text))
                return df
            else:
                st.error(f"Erro na API da OCDE: Código {response.status_code}")
                return pd.DataFrame()
        except Exception as e:
            st.error(f"Não foi possível conectar à OCDE. Erro: {e}")
            return pd.DataFrame()

# --- FUNÇÃO: PROCESSAR OS DADOS PARA O GRÁFICO ---
def processar_matriz_para_ano(df_bruto, ano_selecionado):
    if df_bruto.empty:
        return pd.DataFrame()

    # 1. Filtrar pelo ano escolhido e transformar a coluna de tempo em número
    df_ano = df_bruto[df_bruto['TIME_PERIOD'] == int(ano_selecionado)].copy()

    # --- PARTE CRÍTICA: IDENTIFICAR OS INDICADORES CORRETOS ---
    # A base da OCDE tem milhares de indicadores. Precisamos achar os que
    # representam a % de participação de cada modal.
    # Baseado na documentação do ITF, procuramos termos como "share" e os modais.

    # Mapeamento aproximado dos nomes dos indicadores (pode variar ligeiramente na base)
    # Vamos procurar por strings que indiquem a participação percentual (%) no transporte interior
    
    # Criar máscaras booleanas para encontrar os indicadores
    mask_road = df_ano['INDICATOR'].str.contains('road', case=False, na=False) & df_ano['INDICATOR'].str.contains('share', case=False, na=False)
    mask_rail = df_ano['INDICATOR'].str.contains('rail', case=False, na=False) & df_ano['INDICATOR'].str.contains('share', case=False, na=False)
    # Para aquaviário, procuramos "inland waterways"
    mask_water = df_ano['INDICATOR'].str.contains('water', case=False, na=False) & df_ano['INDICATOR'].str.contains('share', case=False, na=False)

    # 2. Criar sub-tabelas para cada modal
    df_road = df_ano[mask_road][['REF_AREA', 'OBS_VALUE']].rename(columns={'OBS_VALUE': 'Rodoviário (%)'})
    df_rail = df_ano[mask_rail][['REF_AREA', 'OBS_VALUE']].rename(columns={'OBS_VALUE': 'Ferroviário (%)'})
    df_water = df_ano[mask_water][['REF_AREA', 'OBS_VALUE']].rename(columns={'OBS_VALUE': 'Aquaviário (%)'})

    # 3. Juntar tudo numa única tabela (Pivot)
    # Começamos com Rodoviário e juntamos os outros baseados no país (REF_AREA)
    df_final = pd.merge(df_road, df_rail, on='REF_AREA', how='outer')
    df_final = pd.merge(df_final, df_water, on='REF_AREA', how='outer')

    # 4. Limpeza Final
    # Remover países que não tem dados de Rodoviário nem Ferroviário (não dá pra plotar no X/Y)
    df_final = df_final.dropna(subset=['Rodoviário (%)', 'Ferroviário (%)'], how='all')
    
    # Preencher Aquaviário com 0 se for nulo (para o tamanho da bolha não quebrar)
    df_final['Aquaviário (%)'] = df_final['Aquaviário (%)'].fillna(0)
    
    # Renomear a coluna de país
    df_final.rename(columns={'REF_AREA': 'País'}, inplace=True)

    return df_final


# --- INTERFACE DO APLICATIVO ---

st.title("📊 Matriz de Transportes: Comparativo Internacional")
st.markdown("Visualização estrutural semelhante ao modelo solicitado (Eixo X, Y e Tamanho da Bolha).")

# 1. Carregar dados brutos
df_global = carregar_dados_anuais()

if not df_global.empty:
    # Descobrir anos disponíveis
    anos_disponiveis = sorted(df_global['TIME_PERIOD'].unique(), reverse=True)
    
    # Barra lateral para escolher o ano
    with st.sidebar:
        st.header("Configurações")
        # Pega o ano mais recente como padrão (geralmente tem mais dados completos)
        ano_padrao = anos_disponiveis[1] if len(anos_disponiveis) > 1 else anos_disponiveis[0]
        ano_escolhido = st.selectbox("Selecione o Ano de Referência:", anos_disponiveis, index=anos_disponiveis.index(ano_padrao))
        st.info(f"Visualizando dados de: {ano_escolhido}. Dados de anos muito recentes podem estar incompletos para alguns países.")

    # 2. Processar dados para o ano escolhido
    df_plot = processar_matriz_para_ano(df_global, ano_escolhido)

    if not df_plot.empty:
        # 3. FILTRO DE PAÍSES
        todos_paises = sorted(df_plot['País'].unique())
        # Tentar pré-selecionar os países da imagem de exemplo
        sugestao = ['BRA', 'CHN', 'RUS', 'USA', 'DEU', 'FRA', 'DNK', 'HUN', 'BEL', 'CAN']
        pre_selecionados = [p for p in sugestao if p in todos_paises]
        
        paises_filtro = st.multiselect(
            "Filtre os Países para o gráfico:", 
            options=todos_paises,
            default=pre_selecionados if pre_selecionados else todos_paises[:5]
        )
        
        # Aplicar filtro
        if paises_filtro:
            df_filtrado = df_plot[df_plot['País'].isin(paises_filtro)]

            # --- 4. O GRÁFICO DE BOLHAS (REPRODUÇÃO DA IMAGEM) ---
            fig = px.scatter(
                df_filtrado,
                x="Ferroviário (%)",
                y="Rodoviário (%)",
                size="Aquaviário (%)", # O tamanho da bolha é o hidroviário
                text="País", # Rótulo da bolha
                hover_name="País",
                title=f"Matriz Modal em {ano_escolhido} (Tamanho da bolha = % Aquaviário)",
                # Definir limites fixos para os eixos (0 a 100%) para ficar igual à imagem
                range_x=[-2, 102],
                range_y=[-2, 102],
                size_max=60, # Ajuste visual do tamanho máximo das bolhas
                template="plotly_white"
            )
            
            # Melhorar a posição dos rótulos dos países
            fig.update_traces(textposition='top center')
            
            # Adicionar linhas de grade e nomes dos eixos
            fig.update_layout(
                xaxis_title="Ferroviário (%)",
                yaxis_title="Rodoviário (%)",
                showlegend=False # Não precisa de legenda pois o texto já diz o país
            )

            st.plotly_chart(fig, use_container_width=True)

            # Mostrar tabela de dados
            with st.expander("Ver dados da tabela"):
                st.dataframe(df_filtrado.set_index('País').style.format("{:.1f}%"))

        else:
            st.warning("Selecione pelo menos um país na caixa acima.")
    else:
        st.error(f"Não foram encontrados dados de 'share' modal suficientes para o ano de {ano_escolhido}.")