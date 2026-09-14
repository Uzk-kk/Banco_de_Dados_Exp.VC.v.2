# ==============================================================================
# SISTEMA DE CADASTRO RÁPIDO, PRESTADORES, SUBLOCATÁRIOS E GERENTES DE LOJA
# Autor: Raphael Santos
# Propriedade Intelectual e Desenvolvimento: Raphael Santos
# Licença: Uso Exclusivo Autorizado - Proibida Replicação ou Alteração sem Autorização
# Data de Criação: Set/2026
# ==============================================================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import random
import re

# 1. Configuração da página e Estilo Amarelo/Roxo em Tema Escuro
st.set_page_config(page_title="Sistema de Cadastro e Gestão", layout="wide", page_icon="⚙️")

st.markdown("""
<style>
    /* Fundo geral escuro */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    
    /* Sidebar tema escuro */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
        border-right: 1px solid #333333;
    }

    /* Títulos em Amarelo */
    h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #FFD80F !important;
    }

    /* Botão Principal em Roxo com Texto Amarelo */
    .stButton>button {
        background-color: #341539 !important;
        color: #FFD80F !important;
        border: 1px solid #FFD80F !important;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #FFD80F !important;
        color: #341539 !important;
        border: 1px solid #341539 !important;
        box-shadow: 0 0 10px rgba(255, 216, 15, 0.5);
    }

    /* Inputs e Caixas de Texto com Borda Roxa */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #262626 !important;
        color: #FFFFFF !important;
        border: 1px solid #341539 !important;
        border-radius: 6px;
    }

    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border: 1px solid #FFD80F !important;
        box-shadow: 0 0 5px rgba(255, 216, 15, 0.5);
    }

    /* Labels dos campos */
    label {
        color: #E0E0E0 !important;
    }

    /* Estilização de Métricas / Cards */
    [data-testid="stMetricValue"] {
        color: #FFD80F !important;
    }

    /* Abas em tema personalizado */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1E1E1E;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #E0E0E0;
    }

    .stTabs [aria-selected="true"] {
        background-color: #341539 !important;
        color: #FFD80F !important;
        border-radius: 6px;
    }

    /* Tabela / Data Editor */
    [data-testid="stDataFrame"] {
        background-color: #1E1E1E;
        border-radius: 8px;
    }

    /* Botão "Invisível" do Easter Egg */
    .easter-egg-btn {
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        height: 15px !important;
        padding: 0 !important;
        min-height: 0px !important;
        cursor: default;
    }
    .easter-egg-btn:hover {
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper: Validação de E-mail via RegEx (Melhoria 1)
def e_email_valido(email: str) -> bool:
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(padrao, email.strip()))

# Helper: Formatação e Sanitização do Telefone (Melhoria 3)
def formatar_telefone(telefone: str) -> str:
    numeros = re.sub(r"\D", "", str(telefone))
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    return telefone.strip()

# 2. Conexão com Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro ao conectar com Google Sheets. Verifique suas configurações de Secrets.")

def carregar_dados():
    try:
        df = conn.read(ttl=0)
        df = df.dropna(how="all")
        # Garante a existência das colunas necessárias
        colunas_obrigatorias = ['ID', 'NOME', 'SETOR', 'CARGO', 'TELEFONE', 'EMAIL']
        for col in colunas_obrigatorias:
            if col not in df.columns:
                df[col] = ""
        # Converte ID para int se possível
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.warning("Não foi possível carregar a planilha ou ela está vazia. Criando estrutura inicial.")
        return pd.DataFrame(columns=['ID', 'NOME', 'SETOR', 'CARGO', 'TELEFONE', 'EMAIL'])

def salvar_dados(df):
    try:
        conn.update(data=df)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")
        return False

# Base de Dados Simulada de Usuários e Perfis
try:
    dados_secrets = st.secrets["USUARIOS"]
    USUARIOS = {k.strip().lower(): v for k, v in dados_secrets.items()}
except Exception:
    USUARIOS = {
        "admin": {"senha": "123", "nivel": "Admin"},
        "editor": {"senha": "123", "nivel": "Editor"},
        "leitor": {"senha": "123", "nivel": "Leitor"}
    }

# Gerenciamento de Sessão com Parâmetros de URL
query_params = st.query_params

if 'autenticado' not in st.session_state:
    if 'user' in query_params:
        usuario_url = query_params['user'].lower()
        if usuario_url in USUARIOS:
            st.session_state['autenticado'] = True
            st.session_state['usuario'] = usuario_url
            st.session_state['nivel'] = USUARIOS[usuario_url]['nivel']
        else:
            st.session_state['autenticado'] = False
    else:
        st.session_state['autenticado'] = False

if 'easter_egg' not in st.session_state:
    st.session_state['easter_egg'] = False

# 3. Tela de Login
if not st.session_state['autenticado']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔒 Login do Sistema</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Digite suas credenciais para continuar</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario_input = st.text_input("Usuário").strip().lower()
            senha_input = st.text_input("Senha", type="password").strip()
            btn_login = st.form_submit_button("Entrar", use_container_width=True)
            
            if btn_login:
                if usuario_input in USUARIOS and USUARIOS[usuario_input]['senha'] == senha_input:
                    st.session_state['autenticado'] = True
                    st.session_state['usuario'] = usuario_input
                    st.session_state['nivel'] = USUARIOS[usuario_input]['nivel']
                    st.query_params['user'] = usuario_input
                    st.success("Login realizado com sucesso!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

# 4. Sistema Principal (Pós-Login)
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 Usuário: `{st.session_state['usuario'].capitalize()}`")
        st.markdown(f"**Nível de Acesso:** `{st.session_state['nivel']}`")
        st.divider()

        if st.button("🚪 Sair / Logout", use_container_width=True):
            st.session_state['autenticado'] = False
            st.session_state['usuario'] = None
            st.session_state['nivel'] = None
            st.session_state['easter_egg'] = False
            st.query_params.clear()
            st.rerun()

        st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
        
        # Botão Invisível do Easter Egg
        if st.button(" ", key="secret_btn", help=None):
            st.session_state['easter_egg'] = not st.session_state['easter_egg']
            st.rerun()

    # Aplicação de CSS ao botão invisível
    st.markdown("""
        <script>
            const btn = window.parent.document.querySelector('button[kind="secondary"]:has(div:contains(" "))');
            if (btn) {
                btn.classList.add('easter-egg-btn');
            }
        </script>
    """, unsafe_allow_html=True)

    # Conteúdo do Easter Egg
    if st.session_state['easter_egg']:
        st.title("🕹️ Modo Secreto: Jogo da Forca!")
        st.markdown("Você descobriu a página secreta. Divirta-se jogando Forca com palavras do mundo Python/Tech!")

        palavras = ["PYTHON", "STREAMLIT", "DADOS", "DESENVOLVEDOR", "DATABASE", "SISTEMA", "PROGRAMACAO"]
        
        if 'palavra_secreta' not in st.session_state or st.button("🔄 Novo Jogo"):
            st.session_state['palavra_secreta'] = random.choice(palavras)
            st.session_state['letras_chutadas'] = []
            st.session_state['tentativas'] = 6

        palavra = st.session_state['palavra_secreta']
        letras = st.session_state['letras_chutadas']
        
        exibicao = "".join([letra if letra in letras else " _ " for letra in palavra])
        
        st.markdown(f"### Palavra: `{exibicao}`")
        st.write(f"❤️ Tentativas restantes: **{st.session_state['tentativas']}**")
        st.write(f"📝 Letras testadas: {', '.join(letras)}")

        if st.session_state['tentativas'] > 0 and "_" in exibicao:
            col_input, col_btn = st.columns([2, 1])
            with col_input:
                chute = st.text_input("Digite uma letra:", max_chars=1, key="input_forca").upper()
            with col_btn:
                st.write("<br>", unsafe_allow_html=True)
                if st.button("Tentar") and chute:
                    if chute in letras:
                        st.warning("Você já tentou essa letra!")
                    else:
                        st.session_state['letras_chutadas'].append(chute)
                        if chute not in palavra:
                            st.session_state['tentativas'] -= 1
                        st.rerun()

        if "_" not in exibicao:
            st.balloons()
            st.success("🎉 Parabéns! Você venceu o Jogo da Forca!")
        elif st.session_state['tentativas'] <= 0:
            st.error(f"💥 Fim de jogo! A palavra era: **{palavra}**")

        st.divider()

    # Aplicação Normal
    st.title("⚙️ Sistema de Cadastro e Gestão de Colaboradores")

    df_dados = carregar_dados()

    # Criação das Abas com base no Perfil
    abas = ["📋 Visualizar / Listar", "➕ Novo Cadastro"]
    if st.session_state['nivel'] in ["Editor", "Admin"]:
        abas.append("✏️ Editar Registro")
    if st.session_state['nivel'] == "Admin":
        abas.append("❌ Excluir Registro")

    guias = st.tabs(abas)

    # --- ABA 1: VISUALIZAR / LISTAR ---
    with guias[0]:
        st.subheader("Registros Cadastrados")
        
        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_nome = st.text_input("Filtrar por Nome:")
        with col_f2:
            setores_unicos = ["Todos"] + list(df_dados['SETOR'].dropna().unique())
            filtro_setor = st.selectbox("Filtrar por Setor:", setores_unicos)

        df_filtrado = df_dados.copy()
        if filtro_nome:
            df_filtrado = df_filtrado[df_filtrado['NOME'].astype(str).str.contains(filtro_nome, case=False, na=False)]
        if filtro_setor != "Todos":
            df_filtrado = df_filtrado[df_filtrado['SETOR'] == filtro_setor]

        st.dataframe(df_filtrado, use_container_width=True)
        st.caption(f"Total de registros exibidos: {len(df_filtrado)}")

    # --- ABA 2: NOVO CADASTRO ---
    with guias[1]:
        st.subheader("Formulário de Novo Cadastro")
        
        if st.session_state['nivel'] == "Leitor":
            st.warning("⚠️ Seu perfil de **Leitor** não permite adicionar novos cadastros.")
        else:
            with st.form("form_novo_cadastro", clear_on_submit=True):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    novo_nome = st.text_input("Nome Completo *")
                    novo_setor = st.text_input("Setor *")
                    novo_cargo = st.text_input("Cargo *")
                with col_c2:
                    novo_tel = st.text_input("Telefone (ex: 11999999999) *")
                    novo_email = st.text_input("E-mail *")

                btn_cadastrar = st.form_submit_button("Salvar Cadastro")

                if btn_cadastrar:
                    numeros_tel = re.sub(r"\D", "", novo_tel)
                    
                    if not (novo_nome and novo_setor and novo_cargo and novo_tel and novo_email):
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    elif len(numeros_tel) != 11:
                        st.error("O telefone deve conter exatamente 11 dígitos (DDD + Número).")
                    elif not e_email_valido(novo_email):
                        st.error("Por favor, insira um endereço de e-mail válido (exemplo: usuario@dominio.com).")
                    else:
                        proximo_id = 1 if df_dados.empty else int(df_dados['ID'].max()) + 1
                        tel_formatado = formatar_telefone(novo_tel)
                        
                        novo_registro = pd.DataFrame([{
                            'ID': proximo_id,
                            'NOME': novo_nome.strip(),
                            'SETOR': novo_setor.strip(),
                            'CARGO': novo_cargo.strip(),
                            'TELEFONE': tel_formatado,
                            'EMAIL': novo_email.strip()
                        }])

                        df_atualizado = pd.concat([df_dados, novo_registro], ignore_index=True)
                        if salvar_dados(df_atualizado):
                            st.success(f"Cadastro de **{novo_nome}** realizado com sucesso!")
                            time.sleep(1)
                            st.rerun()

    # --- ABA 3: EDITAR REGISTRO ---
    if st.session_state['nivel'] in ["Editor", "Admin"]:
        with guias[2]:
            st.subheader("Editar Registro Existente")
            if df_dados.empty:
                st.info("Nenhum registro encontrado para editar.")
            else:
                opcoes_id = df_dados['ID'].tolist()
                id_selecionado = st.selectbox("Selecione o ID do registro:", opcoes_id)
                
                dados_id = df_dados[df_dados['ID'] == id_selecionado].iloc[0]

                with st.form("form_editar_cadastro"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        edit_nome = st.text_input("Nome Completo", value=str(dados_id['NOME']))
                        edit_setor = st.text_input("Setor", value=str(dados_id['SETOR']))
                        edit_cargo = st.text_input("Cargo", value=str(dados_id['CARGO']))
                    with col_e2:
                        edit_tel = st.text_input("Telefone", value=str(dados_id['TELEFONE']))
                        edit_email = st.text_input("E-mail", value=str(dados_id['EMAIL']))

                    btn_atualizar = st.form_submit_button("Atualizar Registro")

                    if btn_atualizar:
                        numeros_tel = re.sub(r"\D", "", edit_tel)
                        
                        if not (edit_nome and edit_setor and edit_cargo and edit_tel and edit_email):
                            st.error("Todos os campos devem estar preenchidos.")
                        elif len(numeros_tel) != 11:
                            st.error("O telefone deve conter exatamente 11 dígitos (DDD + Número).")
                        elif not e_email_valido(edit_email):
                            st.error("Por favor, insira um endereço de e-mail válido (exemplo: usuario@dominio.com).")
                        else:
                            tel_formatado = formatar_telefone(edit_tel)
                            
                            idx = df_dados[df_dados['ID'] == id_selecionado].index[0]
                            df_dados.loc[idx, 'NOME'] = edit_nome.strip()
                            df_dados.loc[idx, 'SETOR'] = edit_setor.strip()
                            df_dados.loc[idx, 'CARGO'] = edit_cargo.strip()
                            df_dados.loc[idx, 'TELEFONE'] = tel_formatado
                            df_dados.loc[idx, 'EMAIL'] = edit_email.strip()

                            if salvar_dados(df_dados):
                                st.success("Registro atualizado com sucesso!")
                                time.sleep(1)
                                st.rerun()

    # --- ABA 4: EXCLUIR REGISTRO ---
    if st.session_state['nivel'] == "Admin":
        with guias[3]:
            st.subheader("Excluir Registros")
            st.warning("⚠️ **Atenção:** Selecione os registros na tabela abaixo e confirme a exclusão.")

            # Exibe a tabela com caixa de seleção de exclusão
            df_excluir = df_dados.copy()
            df_excluir.insert(0, "Excluir", False)

            edited_df = st.data_editor(
                df_excluir,
                column_config={"Excluir": st.column_config.CheckboxColumn("Excluir", default=False)},
                disabled=['ID', 'NOME', 'SETOR', 'CARGO', 'TELEFONE', 'EMAIL'],
                hide_index=True,
                use_container_width=True
            )

            registros_para_excluir = edited_df[edited_df['Excluir'] == True]

            if not registros_para_excluir.empty:
                st.error(f"Você selecionou {len(registros_para_excluir)} registro(s) para exclusão.")
                if st.button("🔴 Confirmar Exclusão Definitiva"):
                    ids_manter = edited_df[edited_df['Excluir'] == False]['ID'].tolist()
                    df_final = df_dados[df_dados['ID'].isin(ids_manter)]
                    
                    if salvar_dados(df_final):
                        st.success("Registros excluídos com sucesso!")
                        time.sleep(1)
                        st.rerun()
