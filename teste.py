# ==============================================================================
# SISTEMA DE CADASTRO RÁPIDO, PRESTADORES, SUBLOCATÁRIOS E GERENTES DE LOJA
# Autor: Raphael Santos
# Propriedade Intelectual e Desenvolvimento: Raphael Santos
# Licença: Uso Exclusivo Autorizado - Proibida Replicação ou Alteração sem Autorização
# Data de Criação: Set/2026
# ==============================================================================

import datetime
import random
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Configuração visual da página (DEVE SER A PRIMEIRA INSTRUÇÃO STREAMLIT)
st.set_page_config(page_title="Sistema de Cadastro e Gestão", layout="wide")

# 2. Customização CSS e Rodapé de Autoria
st.markdown(
    """
    <style>
    /* Fundo principal da aplicação */
    .stApp { 
        background-color: #341539 !important; 
    }

    /* BARRA LATERAL (SIDEBAR) - Cor cinza igual às caixas de texto */
    [data-testid="stSidebar"] {
        background-color: #262730 !important;
        border-right: 1px solid rgba(255, 216, 15, 0.2) !important;
    }

    /* Títulos e Rótulos principais */
    h1, h2, h3, label, [data-testid="stMarkdownContainer"] p { 
        color: #FFD80F !important; 
        font-weight: bold !important; 
    }

    /* CAIXAS DE INSERÇÃO DE TEXTO (INPUTS) - Fundo Cinza Escuro */
    div[data-baseweb="input"] > div { 
        background-color: #262730 !important; 
        border: 1px solid rgba(255, 216, 15, 0.3) !important;
        border-radius: 8px !important; 
    }
    div[data-baseweb="input"] input { 
        color: #FFFFFF !important; 
        font-weight: normal !important;
    }

    /* BOTÕES E FORMULÁRIOS PADRÃO */
    [data-testid="stForm"] { border: none !important; padding: 0 !important; }
    
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button { 
        background-color: #FFD80F !important; 
        color: #000000 !important; 
        border-radius: 8px !important; 
        border: none !important; 
        padding: 10px 24px !important; 
        font-weight: bold !important; 
    }
    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { 
        background-color: #7B2CBF !important; 
        color: #FFFFFF !important; 
    }
    
    /* BOTÃO SECRETO INVISÍVEL NA SIDEBAR */
    div.element-container:has(#secret-btn-marker) + div.element-container button {
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        box-shadow: none !important;
        height: 30px !important;
        width: 100% !important;
        padding: 0 !important;
        margin-top: 20px !important;
        cursor: default !important;
    }
    div.element-container:has(#secret-btn-marker) + div.element-container button:hover {
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
    }

    /* ==================================================================
       MENU LATERAL PERSONALIZADO EM BLOCOS/BOTÕES ROXOS
       ================================================================== */
    div[data-testid="stSidebar"] div[data-testid="stRadioButton"] > div[role="radiogroup"] {
        gap: 10px !important;
    }

    /* Esconde a bolinha do Radio Button */
    div[data-testid="stSidebar"] div[data-testid="stRadioButton"] div[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }

    /* Formatação dos botões no menu */
    div[data-testid="stSidebar"] div[data-testid="stRadioButton"] label {
        background-color: #341539 !important; /* Roxo principal */
        border: 1px solid rgba(255, 216, 15, 0.3) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }

    /* Texto amarelo dos botões */
    div[data-testid="stSidebar"] div[data-testid="stRadioButton"] label p {
        color: #FFD80F !important;
        font-weight: bold !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        text-align: center !important;
        margin: 0 !important;
    }

    /* Efeito Hover ao passar o mouse */
    div[data-testid="stSidebar"] div[data-testid="stRadioButton"] label:hover {
        background-color: #4A1E52 !important;
        border-color: #FFD80F !important;
    }

    /* Item Ativo/Selecionado */
    div[data-testid="stSidebar"] div[data-testid="stRadioButton"] [aria-checked="true"] {
        background-color: #341539 !important;
        border: 2px solid #FFD80F !important;
        box-shadow: 0px 0px 8px rgba(255, 216, 15, 0.4) !important;
    }

    /* SLIDER DE AVALIAÇÃO (Barra Amarela) */
    div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] ~ div,
    div[data-testid="stSlider"] [data-baseweb="slider"] div[style*="background-color"],
    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {
        background: #FFD80F !important;
        background-color: #FFD80F !important;
    }

    /* Puxador / Bolinha do Slider */
    div[data-testid="stSlider"] [role="slider"] {
        background-color: #FFD80F !important;
        border-color: #FFD80F !important;
        box-shadow: 0px 0px 6px rgba(255, 216, 15, 0.9) !important;
    }

    /* Rótulos e Números do Slider */
    div[data-testid="stSlider"] [data-testid="stTickBar"] div,
    div[data-testid="stSlider"] div,
    div[data-testid="stSlider"] p {
        color: #FFD80F !important;
    }

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

# --- CARREGAMENTO SEGURO DE USUÁRIOS ---
try:
    dados_secrets = st.secrets["USUARIOS"]
    USUARIOS = {k.strip().lower(): v for k, v in dados_secrets.items()}
except Exception:
    USUARIOS = {"admin": {"senha": "1234", "nivel": "Admin"}}

# --- PERSISTÊNCIA DE SESSÃO VIA URL ---
query_params = st.query_params

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"] and "user" in query_params:
    usuario_url = query_params["user"].strip().lower()
    if usuario_url in USUARIOS:
        st.session_state["autenticado"] = True
        st.session_state["usuario_logado"] = usuario_url.title()
        st.session_state["nivel_acesso"] = USUARIOS[usuario_url]["nivel"]

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
                st.query_params["user"] = usuario_limpo
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")

    st.stop()

# --- CONEXÃO COM O GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
url_planilha = st.secrets["connections"]["gsheets"]["spreadsheet"]

# --- CONTROLE DA ABA SECRETA ---
if "aba_secreta_desbloqueada" not in st.session_state:
    st.session_state["aba_secreta_desbloqueada"] = False

# --- MENU LATERAL ---
st.sidebar.title("Menu do Sistema")
st.sidebar.write(f"Usuário: **{st.session_state.get('usuario_logado')}**")
st.sidebar.write(f"Perfil: **{st.session_state.get('nivel_acesso')}**")

if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False
    st.session_state.pop("usuario_logado", None)
    st.session_state.pop("nivel_acesso", None)
    st.session_state["aba_secreta_desbloqueada"] = False
    st.query_params.clear()
    st.rerun()

st.sidebar.divider()

# Lista dinâmica de abas
opcoes_menu = ["Cadastro Rápido", "Controle de Prestadores", "Sublocatários", "Controle Gerentes de Loja"]
if st.session_state["aba_secreta_desbloqueada"]:
    opcoes_menu.append("🎮 Sala Secreta: Jogo da Forca")

aba_selecionada = st.sidebar.radio("Navegação", opcoes_menu)

# BOTÃO INVISÍVEL NA SIDEBAR
st.sidebar.markdown('<span id="secret-btn-marker"></span>', unsafe_allow_html=True)
if st.sidebar.button(" ", key="btn_secreto"):
    st.session_state["aba_secreta_desbloqueada"] = not st.session_state["aba_secreta_desbloqueada"]
    st.rerun()

nivel = st.session_state.get("nivel_acesso")

# --- ABA 1: CADASTRO RÁPIDO ---
if aba_selecionada == "Cadastro Rápido":
    st.title("Cadastro Rápido de Dados")

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
                try:
                    df_existente = conn.read(spreadsheet=url_planilha, worksheet="Cadastro Rápido", ttl=0)

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

                    df_atualizado = pd.concat([df_existente, novo_dado], ignore_index=True)
                    conn.update(spreadsheet=url_planilha, worksheet="Cadastro Rápido", data=df_atualizado)

                    st.success("Dados salvos com sucesso no Google Sheets!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na planilha: {err}")
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Cadastros")

    try:
        df = conn.read(spreadsheet=url_planilha, worksheet="Cadastro Rápido", ttl=0)
        
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
                    conn.update(spreadsheet=url_planilha, worksheet="Cadastro Rápido", data=df_atualizado)
                    st.success("Registro(s) removido(s) com sucesso!")
                    st.rerun()
        else:
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.info("Nenhum dado cadastrado ou erro ao conectar com a guia 'Cadastro Rápido'.")

# --- ABA 2: CONTROLE DE PRESTADORES ---
elif aba_selecionada == "Controle de Prestadores":
    st.title("Controle de Prestadores de Serviço")

    if nivel in ["Editor", "Admin"]:
        with st.form("form_prestadores", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                p_regiao = st.text_input("Região")
                p_nome = st.text_input("Prestador de Serviço")
                p_servicos = st.text_input("Serviços")
                p_tel = st.text_input("Telefone (Apenas números, 11 dígitos)")

            with col2:
                p_email = st.text_input("E-mail")
                p_avaliacao = st.slider("Avaliação de 0 a 5", min_value=0, max_value=5, value=5)
                p_prazo = st.text_input("Prazo pag.")
                p_nf = st.text_input("NF.")

            btn_salvar_p = st.form_submit_button("Cadastrar Prestador")

        if btn_salvar_p:
            campos_obrigatorios = [p_regiao, p_nome, p_servicos, p_tel, p_email, p_prazo, p_nf]
            if any(c.strip() == "" for c in campos_obrigatorios):
                st.error("Por favor, preencha todos os campos do formulário!")
            elif not p_tel.strip().isdigit() or len(p_tel.strip()) != 11:
                st.error("O campo 'Telefone' deve conter exatamente 11 dígitos numéricos!")
            else:
                try:
                    df_prestadores = conn.read(spreadsheet=url_planilha, worksheet="Controle de Prestadores", ttl=0)

                    novo_prestador = pd.DataFrame(
                        [
                            {
                                "Região": p_regiao,
                                "Prestador de Serviço": p_nome,
                                "Serviços": p_servicos,
                                "Telefone": str(p_tel),
                                "E-mail": p_email,
                                "Avaliação de 0 a 5": int(p_avaliacao),
                                "Prazo pag.": p_prazo,
                                "NF.": p_nf,
                                "Cadastrado Por": st.session_state["usuario_logado"],
                            }
                        ]
                    )

                    df_p_atualizado = pd.concat([df_prestadores, novo_prestador], ignore_index=True)
                    conn.update(spreadsheet=url_planilha, worksheet="Controle de Prestadores", data=df_p_atualizado)

                    st.success("Prestador cadastrado com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Controle de Prestadores': {err}")
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Prestadores")

    try:
        df_p = conn.read(spreadsheet=url_planilha, worksheet="Controle de Prestadores", ttl=0)
        
        if nivel == "Admin" and not df_p.empty:
            st.info("Selecione as linhas que deseja remover e clique no botão abaixo.")
            
            df_p_editor = df_p.copy()
            df_p_editor.insert(0, "Excluir", False)
            
            tabela_p_editavel = st.data_editor(
                df_p_editor,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )
            
            linhas_p_remover = tabela_p_editavel[tabela_p_editavel["Excluir"] == True]
            
            if not linhas_p_remover.empty:
                if st.button("Confirmar Exclusão dos Prestadores Selecionados"):
                    df_p_atualizado = tabela_p_editavel[tabela_p_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Controle de Prestadores", data=df_p_atualizado)
                    st.success("Prestador(es) removido(s) com sucesso!")
                    st.rerun()
        else:
            st.dataframe(df_p, use_container_width=True)

    except Exception as e:
        st.info("Nenhum prestador cadastrado ou a guia 'Controle de Prestadores' ainda não foi criada no Google Sheets.")

# --- ABA 3: SUBLOCATÁRIOS ---
elif aba_selecionada == "Sublocatários":
    st.title("Controle de Sublocatários")

    if nivel in ["Editor", "Admin"]:
        with st.form("form_sublocatarios", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                sub_loja = st.text_input("Loja")
                sub_endereco = st.text_input("Endereço")
                sub_nome = st.text_input("Nome completo")
                sub_tel = st.text_input("Telefone (Apenas números, 11 dígitos)")
                sub_rep = st.text_input("Nome do representante legal")
                sub_email = st.text_input("E-mail")
                sub_data_inicio = st.date_input("Data de inicio", value=datetime.date.today(), format="DD/MM/YYYY")

            with col2:
                sub_data_fim = st.date_input("Data de encerramento", value=datetime.date.today(), format="DD/MM/YYYY")
                sub_tipo_espaco = st.text_input("Tipo de espaço")
                sub_metragem_num = st.number_input("Metragem ocupada (m²)", min_value=0.0, step=1.0, format="%.2f")
                sub_energia = st.text_input("Demanda de energia")
                sub_pontos = st.text_input("Pontos de consumo")
                sub_segmento = st.text_input("Segmento")
                sub_horario = st.text_input("Horário de funcionamento")

            btn_salvar_sub = st.form_submit_button("Cadastrar Sublocatário")

        if btn_salvar_sub:
            campos_texto = [
                sub_loja, sub_endereco, sub_nome, sub_tel, sub_rep,
                sub_email, sub_tipo_espaco, sub_energia, sub_pontos,
                sub_segmento, sub_horario
            ]

            if any(c.strip() == "" for c in campos_texto):
                st.error("Por favor, preencha todos os campos do formulário!")
            elif not sub_tel.strip().isdigit() or len(sub_tel.strip()) != 11:
                st.error("O campo 'Telefone' deve conter exatamente 11 dígitos numéricos!")
            elif sub_metragem_num <= 0:
                st.error("A 'Metragem ocupada' deve ser maior que zero!")
            else:
                try:
                    df_sub = conn.read(spreadsheet=url_planilha, worksheet="Sublocatários", ttl=0)

                    metragem_formatada = f"{sub_metragem_num:g} m²"
                    data_ini_str = sub_data_inicio.strftime("%d/%m/%Y")
                    data_fim_str = sub_data_fim.strftime("%d/%m/%Y")

                    novo_sublocatario = pd.DataFrame(
                        [
                            {
                                "Loja": sub_loja,
                                "Endereço": sub_endereco,
                                "Nome completo": sub_nome,
                                "Telefone": str(sub_tel),
                                "Nome do representante legal": sub_rep,
                                "E-mail": sub_email,
                                "Data de inicio": data_ini_str,
                                "Data de encerramento": data_fim_str,
                                "Tipo de espaço": sub_tipo_espaco,
                                "Metragem ocupada": metragem_formatada,
                                "Demanda de energia": sub_energia,
                                "Pontos de consumo": sub_pontos,
                                "Segmento": sub_segmento,
                                "Horário de funcionamento": sub_horario,
                                "Cadastrado Por": st.session_state["usuario_logado"],
                            }
                        ]
                    )

                    df_sub_atualizado = pd.concat([df_sub, novo_sublocatario], ignore_index=True)
                    conn.update(spreadsheet=url_planilha, worksheet="Sublocatários", data=df_sub_atualizado)

                    st.success("Sublocatário cadastrado com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Sublocatários': {err}")
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Sublocatários")

    try:
        df_s = conn.read(spreadsheet=url_planilha, worksheet="Sublocatários", ttl=0)

        if nivel == "Admin" and not df_s.empty:
            st.info("Selecione as linhas que deseja remover e clique no botão abaixo.")

            df_s_editor = df_s.copy()
            df_s_editor.insert(0, "Excluir", False)

            tabela_s_editavel = st.data_editor(
                df_s_editor,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )

            linhas_s_remover = tabela_s_editavel[tabela_s_editavel["Excluir"] == True]

            if not linhas_s_remover.empty:
                if st.button("Confirmar Exclusão dos Sublocatários Selecionados"):
                    df_s_atualizado = tabela_s_editavel[tabela_s_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Sublocatários", data=df_s_atualizado)
                    st.success("Sublocatário(s) removido(s) com sucesso!")
                    st.rerun()
        else:
            st.dataframe(df_s, use_container_width=True)

    except Exception as e:
        st.info("Nenhum sublocatário cadastrado ou a guia 'Sublocatários' ainda não foi criada no Google Sheets.")

# --- ABA 4: CONTROLE GERENTES DE LOJA ---
elif aba_selecionada == "Controle Gerentes de Loja":
    st.title("Controle Gerentes de Loja")

    if nivel in ["Editor", "Admin"]:
        with st.form("form_gerentes", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                g_loja = st.text_input("Loja")
                g_nome = st.text_input("Nome")
                g_tel = st.text_input("Telefone (Apenas números, 11 dígitos)")

            with col2:
                g_email = st.text_input("E-mail")
                g_cargo = st.text_input("Cargo")

            btn_salvar_g = st.form_submit_button("Cadastrar Gerente")

        if btn_salvar_g:
            campos_gerente = [g_loja, g_nome, g_tel, g_email, g_cargo]

            if any(c.strip() == "" for c in campos_gerente):
                st.error("Por favor, preencha todos os campos do formulário!")
            elif not g_tel.strip().isdigit() or len(g_tel.strip()) != 11:
                st.error("O campo 'Telefone' deve conter exatamente 11 dígitos numéricos!")
            else:
                try:
                    df_gerentes = conn.read(spreadsheet=url_planilha, worksheet="Controle Gerentes de Loja", ttl=0)

                    novo_gerente = pd.DataFrame(
                        [
                            {
                                "Loja": g_loja,
                                "Nome": g_nome,
                                "Telefone": str(g_tel),
                                "E-mail": g_email,
                                "Cargo": g_cargo,
                                "Cadastrado Por": st.session_state["usuario_logado"],
                            }
                        ]
                    )

                    df_g_atualizado = pd.concat([df_gerentes, novo_gerente], ignore_index=True)
                    conn.update(spreadsheet=url_planilha, worksheet="Controle Gerentes de Loja", data=df_g_atualizado)

                    st.success("Gerente cadastrado com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Controle Gerentes de Loja': {err}")
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Gerentes de Loja")

    try:
        df_g = conn.read(spreadsheet=url_planilha, worksheet="Controle Gerentes de Loja", ttl=0)

        if nivel == "Admin" and not df_g.empty:
            st.info("Selecione as linhas que deseja remover e clique no botão abaixo.")

            df_g_editor = df_g.copy()
            df_g_editor.insert(0, "Excluir", False)

            tabela_g_editavel = st.data_editor(
                df_g_editor,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )

            linhas_g_remover = tabela_g_editavel[tabela_g_editavel["Excluir"] == True]

            if not linhas_g_remover.empty:
                if st.button("Confirmar Exclusão dos Gerentes Selecionados"):
                    df_g_atualizado = tabela_g_editavel[tabela_g_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Controle Gerentes de Loja", data=df_g_atualizado)
                    st.success("Gerente(s) removido(s) com sucesso!")
                    st.rerun()
        else:
            st.dataframe(df_g, use_container_width=True)

    except Exception as e:
        st.info("Nenhum gerente cadastrado ou a guia 'Controle Gerentes de Loja' ainda não foi criada no Google Sheets.")

# --- ABA SECRETA: JOGO DA FORCA ---
elif aba_selecionada == "🎮 Sala Secreta: Jogo da Forca":
    st.title("🕵️‍♂️ Área Secreta - Jogo da Forca")
    st.write("Parabéns por encontrar o modo secreto! Descanse um pouco e jogue uma partida.")

    # Lista de Palavras secretas
    PALAVRAS_FORCA = ["STREAMLIT", "PYTHON", "GERENTE", "SUBLOCATARIO", "PRESTADOR", "CADASTRO", "SISTEMA", "LOJA", "CONTRATO"]

    # Inicialização das variáveis do jogo
    if "palavra_secreta" not in st.session_state:
        st.session_state["palavra_secreta"] = random.choice(PALAVRAS_FORCA)
        st.session_state["letras_chutadas"] = []
        st.session_state["tentativas_restantes"] = 6

    def reiniciar_jogo():
        st.session_state["palavra_secreta"] = random.choice(PALAVRAS_FORCA)
        st.session_state["letras_chutadas"] = []
        st.session_state["tentativas_restantes"] = 6

    # Estágios da Forca em ASCII
    ESTAGIOS_FORCA = [
        """
           +---+
           |   |
               |
               |
               |
               |
         =========""",
        """
           +---+
           |   |
           O   |
               |
               |
               |
         =========""",
        """
           +---+
           |   |
           O   |
           |   |
               |
               |
         =========""",
        """
           +---+
           |   |
           O   |
          /|   |
               |
               |
         =========""",
        """
           +---+
           |   |
           O   |
          /|\\  |
               |
               |
         =========""",
        """
           +---+
           |   |
           O   |
          /|\\  |
          /    |
               |
         =========""",
        """
           +---+
           |   |
           O   |
          /|\\  |
          / \\  |
               |
         ========="""
    ]

    col_jogo1, col_jogo2 = st.columns([1, 1])

    with col_jogo1:
        erros = 6 - st.session_state["tentativas_restantes"]
        st.code(ESTAGIOS_FORCA[erros], language="text")

    with col_jogo2:
        # Mostra a palavra oculta
        palavra_exibida = "".join([letra if letra in st.session_state["letras_chutadas"] else " _ " for letra in st.session_state["palavra_secreta"]])
        st.subheader(f"Palavra: {palavra_exibida}")
        st.write(f"Tentativas restantes: **{st.session_state['tentativas_restantes']}**")
        st.write(f"Letras já tentadas: {', '.join(st.session_state['letras_chutadas'])}")

        # Verificação de vitória ou derrota
        ganhou = all(letra in st.session_state["letras_chutadas"] for letra in st.session_state["palavra_secreta"])
        perdeu = st.session_state["tentativas_restantes"] <= 0

        if not ganhou and not perdeu:
            with st.form("form_forca", clear_on_submit=True):
                chute = st.text_input("Digite uma letra:", max_chars=1).upper()
                btn_chutar = st.form_submit_button("Tentar Letra")

                if btn_chutar and chute:
                    if not chute.isalpha():
                        st.warning("Por favor, digite apenas letras!")
                    elif chute in st.session_state["letras_chutadas"]:
                        st.info("Você já tentou essa letra.")
                    else:
                        st.session_state["letras_chutadas"].append(chute)
                        if chute not in st.session_state["palavra_secreta"]:
                            st.session_state["tentativas_restantes"] -= 1
                        st.rerun()

        if ganhou:
            st.balloons()
            st.success("🎉 Parabéns, você venceu!")
            if st.button("Jogar Novamente"):
                reiniciar_jogo()
                st.rerun()

        if perdeu:
            st.error(f"☠️ Fim de jogo! A palavra era: **{st.session_state['palavra_secreta']}**")
            if st.button("Tentar Novamente"):
                reiniciar_jogo()
                st.rerun()
