# ==============================================================================
# SISTEMA DE CADASTRO RÁPIDO DE DADOS
# Autor: Raphael Santos
# Propriedade Intelectual e Desenvolvimento: Raphael Santos
# Licença: Uso Exclusivo Autorizado - Proibida Replicação ou Alteração sem Autorização
# Data de Criação: Set/2026
# ==============================================================================

import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuração visual do tema e da página
st.set_page_config(page_title="Cadastro Rápido", layout="wide")

# --- CARREGAMENTO SEGURO DE USUÁRIOS ---
try:
    dados_secrets = st.secrets["USUARIOS"]
    USUARIOS = {k.strip().lower(): v for k, v in dados_secrets.items()}
except Exception:
    USUARIOS = {"admin": {"senha": "1234", "nivel": "Admin"}}

# Inicializa o estado de autenticação
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Customização CSS e Rodapé de Autoria
st.markdown(
    """
    <style>
    .stApp { background-color: #341539; }
    h1, h2, h3, p, label, .stMarkdown { color: #FFD80F !important; font-weight: bold !important; }
    div[data-baseweb="input"] > div { background-color: #FFD80F !important; border-radius: 8px !important; }
    div[data-baseweb="input"] input { color: #FFFFFF !important; }
    [data-testid="stForm"] { border: none !important; padding: 0 !important; }
    div.stButton > button { background-color: #FFD80F; color: #000000; border-radius: 8px; border: none; padding: 10px 24px; font-weight: bold; }
    div.stButton > button:hover { background-color: #7B2CBF; color: #FFFFFF; }
    
    /* Rodapé fixo de autoria */
    .footer-autoria {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #1E0A22;
        color: #FFD80F;
        text-align: center;
        padding: 8px 0;
        font-size: 12px;
        font-weight: bold;
        z-index: 9999;
        border-top: 1px solid #FFD80F;
    }
    </style>
    <div class="footer-autoria">
        Desenvolvido exclusivamente por Raphael Santos | © Todos os direitos reservados
    </div>
    """,
    unsafe_allow_html=True,
)

# --- TELA DE LOGIN ---
if not st.session_state["autenticado"]:
    st.title("Acesso Restrito")

    with st.form("form_login"):
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        btn_login = st.form_submit_button("Entrar")

        if btn_login:
            usuario_limpo = usuario_input.strip().lower()
            senha_limpa = senha_input.strip()

            if (
                usuario_limpo in USUARIOS
                and USUARIOS[usuario_limpo]["senha"] == senha_limpa
            ):
                st.session_state["autenticado"] = True
                st.session_state["usuario_logado"] = usuario_input.strip().title()
                st.session_state["nivel_acesso"] = USUARIOS[usuario_limpo]["nivel"]
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")

    st.stop()


# --- CONEXÃO COM O GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- MENU LATERAL (NAVEGAÇÃO ENTRE ABAS) ---
st.sidebar.title("Menu do Sistema")
st.sidebar.write(f"Usuário: **{st.session_state.get('usuario_logado')}**")
st.sidebar.write(f"Perfil: **{st.session_state.get('nivel_acesso')}**")

if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False
    st.session_state.pop("usuario_logado", None)
    st.session_state.pop("nivel_acesso", None)
    st.rerun()

st.sidebar.divider()

# Seleção de Abas
aba_selecionada = st.sidebar.radio(
    "Navegação",
    ["Cadastro Rápido", "Outra Planilha (Em Breve)"],
)

nivel = st.session_state.get("nivel_acesso")

# --- ABA 1: CADASTRO RÁPIDO ---
if aba_selecionada == "Cadastro Rápido":
    st.title("Cadastro Rápido de Dados")

    # --- FORMULÁRIO (Exibido apenas para Editor e Admin) ---
    if nivel in ["Editor", "Admin"]:
        with st.form("form_cadastro", clear_on_submit=True):
            campo1 = st.text_input("Loja")
            campo2 = st.text_input("Nome Completo")
            campo3 = st.text_input("Endereço")
            campo4 = st.text_input("Telefone (Apenas números, máximo 11 dígitos)")
            campo5 = st.text_input("E-mail")
            campo6 = st.text_input("Status")

            btn_salvar = st.form_submit_button("Salvar")

        if btn_salvar:
            campos = [campo1, campo2, campo3, campo4, campo5, campo6]
            if any(c.strip() == "" for c in campos):
                st.error("Por favor, preencha todos os campos antes de salvar!")

            elif not campo4.strip().isdigit():
                st.error("O campo 'Telefone' deve conter apenas números inteiros!")

            elif len(campo4.strip()) != 11:
                st.error("O telefone deve conter exatamente 11 dígitos (ex: DDD + Número)!")

            else:
                # Carrega os dados existentes do Google Sheets
                df_existente = conn.read(ttl=0)

                novo_dado = pd.DataFrame(
                    [
                        {
                            "Loja": campo1,
                            "Nome Completo": campo2,
                            "Endereço": campo3,
                            "Telefone": str(campo4),
                            "E-mail": campo5,
                            "Status": campo6,
                            "Cadastrado Por": st.session_state["usuario_logado"],
                        }
                    ]
                )

                # Consolida e atualiza a planilha
                df_atualizado = pd.concat([df_existente, novo_dado], ignore_index=True)
                conn.update(data=df_atualizado)

                st.success("Dados salvos com sucesso no Google Sheets!")
                st.rerun()

    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    # --- VISUALIZAÇÃO E EXCLUSÃO ---
    st.divider()
    st.subheader("Visualização do Banco de Dados")

    try:
        df = conn.read(ttl=0)
        
        if nivel == "Admin" and not df.empty:
            st.info("Selecione as linhas que deseja remover e clique no botão abaixo.")
            
            df_editor = df.copy()
            df_editor.insert(0, "Excluir", False)
            
            tabela_editavel = st.data_editor(
                df_editor,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )
            
            linhas_para_remover = tabela_editavel[tabela_editavel["Excluir"] == True]
            
            if not linhas_para_remover.empty:
                if st.button("Confirmar Exclusão dos Selecionados"):
                    df_atualizado = tabela_editavel[tabela_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(data=df_atualizado)
                    st.success("Registro(s) removido(s) com sucesso!")
                    st.rerun()
        else:
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.info("Nenhum dado cadastrado ou erro ao conectar com o Google Sheets.")

# --- ABA 2: ESPAÇO RESERVADO PARA EXPANSÃO FUTURA ---
elif aba_selecionada == "Outra Planilha (Em Breve)":
    st.title("Nova Aba em Desenvolvimento")
    st.info("Este espaço está reservado para a inclusão de novas planilhas e relatórios.")