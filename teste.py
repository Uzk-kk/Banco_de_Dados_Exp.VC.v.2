# ==============================================================================
# SISTEMA DE CADASTRO RÁPIDO, PRESTADORES, SUBLOCATÁRIOS E GERENTES DE LOJA
# Autor: Raphael Santos
# Propriedade Intelectual e Desenvolvimento: Raphael Santos
# Licença: Uso Exclusivo Autorizado - Proibida Replicação ou Alteração sem Autorização
# Data de Criação: Set/2026
# Atualização de Segurança: Set/2026 (token de sessão, hash de senha, rate limiting)
# Atualização: Set/2026 (adição das páginas: Contas de Consumo, Controle de Acessos,
#              Senhas Concessionárias e Espaços Disponíveis)
# ==============================================================================

import datetime
import random
import secrets  # ADICIONADO: geração de tokens de sessão aleatórios e seguros
import hashlib  # ADICIONADO: hash de senhas (nunca mais salvar senha em texto puro)
import hmac     # ADICIONADO: comparação de senha em tempo constante (evita timing attack)
import time     # ADICIONADO: controle de tentativas de login (rate limiting)
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

    /* BOTÃO RADIO (Navegação no Menu Lateral - Seleção em Amarelo) */
    div[data-testid="stRadioButton"] label p {
        color: #FFD80F !important;
    }

    /* Radio Ativo - Círculo Externo e Preenchimento */
    div[data-testid="stRadioButton"] [aria-checked="true"] div:first-child,
    div[data-testid="stRadioButton"] [data-baseweb="radio"] input:checked + div {
        border-color: #FFD80F !important;
        background-color: #FFD80F !important;
    }

    /* Radio Ativo - Ponto Central Interno */
    div[data-testid="stRadioButton"] [aria-checked="true"] div:first-child > div,
    div[data-testid="stRadioButton"] [data-baseweb="radio"] input:checked + div > div {
        background-color: #262730 !important;
    }

    /* Radio Inativo - Apenas Borda Amarela */
    div[data-testid="stRadioButton"] [aria-checked="false"] div:first-child,
    div[data-testid="stRadioButton"] [data-baseweb="radio"] input:not(:checked) + div {
        border-color: #FFD80F !important;
        background-color: transparent !important;
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

# ==============================================================================
# BLOCO DE SEGURANÇA - AUTENTICAÇÃO E SESSÃO
# ==============================================================================
#
# COMO CONFIGURAR OS USUÁRIOS (st.secrets):
# No arquivo .streamlit/secrets.toml (local) OU em "Settings > Secrets" no painel
# do Streamlit Cloud, cadastre os usuários usando SENHA EM HASH, nunca em texto puro:
#
#   [USUARIOS.admin]
#   senha = "COLE_AQUI_O_HASH_GERADO"
#   nivel = "Admin"
#
# COMO GERAR O HASH DE UMA SENHA:
# Rode este trecho uma única vez (no terminal, num arquivo .py separado, ou até
# aqui mesmo comentando a linha st.stop() abaixo temporariamente) e copie o
# resultado para o secrets.toml:
#
#   import hashlib
#   print(hashlib.sha256("SUA_SENHA_AQUI".strip().encode("utf-8")).hexdigest())
#
# IMPORTANTE: como as senhas no secrets.toml agora precisam ser o HASH (e não
# mais a senha em texto puro), você precisa gerar o hash de cada senha existente
# e atualizar o secrets.toml antes de fazer login novamente.
# ==============================================================================


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash SHA-256 de uma senha em texto puro.
    Use esta função só para GERAR o valor que vai no secrets.toml.
    O app usa essa mesma função em tempo real para comparar com o hash salvo,
    então a senha digitada nunca é comparada em texto puro."""
    return hashlib.sha256(senha.strip().encode("utf-8")).hexdigest()


# --- CARREGAMENTO SEGURO DE USUÁRIOS ---
# IMPORTANTE: NÃO existe mais fallback com usuário/senha fixos (o antigo admin/1234
# foi removido). Se os secrets não estiverem configurados corretamente, o acesso
# fica bloqueado por completo — isso evita uma "porta dos fundos" esquecida em produção.
try:
    dados_secrets = st.secrets["USUARIOS"]
    USUARIOS = {k.strip().lower(): v for k, v in dados_secrets.items()}
    if not USUARIOS:
        raise ValueError("Nenhum usuário encontrado em st.secrets['USUARIOS'].")
    ERRO_CONFIGURACAO = None
except Exception as erro_config:
    USUARIOS = {}
    ERRO_CONFIGURACAO = str(erro_config)


# --- ARMAZENAMENTO DE SESSÕES (TOKENS) ---
# Os tokens de sessão ficam guardados em memória no servidor (nunca na URL como
# texto legível, nunca no navegador além do próprio token opaco).
# st.cache_resource faz esse dicionário ser compartilhado entre todos os usuários
# e sobreviver a "reruns" do Streamlit. Ele só é zerado se o servidor reiniciar
# (ex: você fez um novo commit no GitHub e o Streamlit Cloud reimplantou o app) —
# nesse caso, todo mundo simplesmente precisa logar de novo, o que é esperado.
@st.cache_resource
def obter_armazenamento_sessoes():
    return {}  # formato: { token: {"usuario": str, "nivel": str, "expira_em": timestamp} }


SESSOES = obter_armazenamento_sessoes()
DURACAO_SESSAO_SEGUNDOS = 8 * 60 * 60  # login fica válido por 8 horas


def criar_sessao(usuario: str, nivel: str) -> str:
    """Cria um token aleatório e opaco para a sessão (isso é o que vai na URL,
    nunca o nome do usuário)."""
    token = secrets.token_urlsafe(32)
    SESSOES[token] = {
        "usuario": usuario,
        "nivel": nivel,
        "expira_em": time.time() + DURACAO_SESSAO_SEGUNDOS,
    }
    return token


def validar_sessao(token: str):
    """Retorna (usuario, nivel) se o token existir e ainda for válido, senão None."""
    sessao = SESSOES.get(token)
    if not sessao:
        return None
    if time.time() > sessao["expira_em"]:
        SESSOES.pop(token, None)  # limpa sessão expirada da memória
        return None
    return sessao["usuario"], sessao["nivel"]


def encerrar_sessao(token: str):
    """Remove o token da memória do servidor (usado no logout)."""
    SESSOES.pop(token, None)


# --- PERSISTÊNCIA DE SESSÃO VIA URL (AGORA COM TOKEN, NÃO COM O NOME DO USUÁRIO) ---
query_params = st.query_params

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"] and "session" in query_params:
    token_url = query_params["session"]
    resultado_sessao = validar_sessao(token_url)
    if resultado_sessao:
        usuario_sessao, nivel_sessao = resultado_sessao
        st.session_state["autenticado"] = True
        st.session_state["usuario_logado"] = usuario_sessao.title()
        st.session_state["nivel_acesso"] = nivel_sessao
        st.session_state["session_token"] = token_url
    else:
        # Token inválido, expirado, ou o servidor reiniciou -> limpa a URL
        st.query_params.clear()


# --- CONTROLE DE TENTATIVAS DE LOGIN (RATE LIMITING BÁSICO) ---
# Evita força bruta simples: depois de MAX_TENTATIVAS erradas, bloqueia por um tempo.
MAX_TENTATIVAS = 5
BLOQUEIO_SEGUNDOS = 60

if "tentativas_login" not in st.session_state:
    st.session_state["tentativas_login"] = 0
if "bloqueado_ate" not in st.session_state:
    st.session_state["bloqueado_ate"] = 0


# --- TELA DE LOGIN ---
if not st.session_state["autenticado"]:
    st.title("Acesso Restrito")

    if ERRO_CONFIGURACAO:
        # SEM FALLBACK: se os secrets estiverem mal configurados, ninguém entra.
        st.error(
            "Erro de configuração: os usuários não foram carregados corretamente "
            "a partir de st.secrets['USUARIOS']. Verifique o arquivo de secrets "
            "no painel do Streamlit Cloud (ou o .streamlit/secrets.toml local).\n\n"
            f"Detalhe técnico: {ERRO_CONFIGURACAO}"
        )
        st.stop()

    agora = time.time()
    tempo_restante_bloqueio = st.session_state["bloqueado_ate"] - agora

    if tempo_restante_bloqueio > 0:
        st.error(
            f"Muitas tentativas incorretas. Tente novamente em "
            f"{int(tempo_restante_bloqueio)} segundos."
        )
        st.stop()

    with st.form("form_login"):
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        btn_login = st.form_submit_button("Entrar")

        if btn_login:
            usuario_limpo = usuario_input.strip().lower()
            senha_limpa = senha_input.strip()
            hash_senha_digitada = gerar_hash_senha(senha_limpa)

            usuario_existe = usuario_limpo in USUARIOS
            hash_esperado = USUARIOS.get(usuario_limpo, {}).get("senha", "")

            # hmac.compare_digest compara em tempo constante, para não vazar
            # informação (via tempo de resposta) sobre se o usuário existe ou não.
            senha_correta = hmac.compare_digest(hash_senha_digitada, hash_esperado)

            if usuario_existe and senha_correta:
                nivel_usuario = USUARIOS[usuario_limpo]["nivel"]
                token = criar_sessao(usuario_limpo, nivel_usuario)

                st.session_state["autenticado"] = True
                st.session_state["usuario_logado"] = usuario_input.strip().title()
                st.session_state["nivel_acesso"] = nivel_usuario
                st.session_state["session_token"] = token
                st.session_state["tentativas_login"] = 0  # zera o contador ao logar

                st.query_params["session"] = token  # só o token vai na URL
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.session_state["tentativas_login"] += 1
                if st.session_state["tentativas_login"] >= MAX_TENTATIVAS:
                    st.session_state["bloqueado_ate"] = time.time() + BLOQUEIO_SEGUNDOS
                    st.session_state["tentativas_login"] = 0
                    st.error(
                        f"Muitas tentativas incorretas. Acesso bloqueado por "
                        f"{BLOQUEIO_SEGUNDOS} segundos."
                    )
                else:
                    tentativas_restantes = MAX_TENTATIVAS - st.session_state["tentativas_login"]
                    st.error(
                        f"Usuário ou senha incorretos! "
                        f"({tentativas_restantes} tentativa(s) restante(s) antes do bloqueio)"
                    )

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
    # ATUALIZADO: agora também invalida o token de sessão no servidor,
    # não só limpa o estado local, para que o link antigo pare de funcionar.
    encerrar_sessao(st.session_state.get("session_token"))
    st.session_state["autenticado"] = False
    st.session_state.pop("usuario_logado", None)
    st.session_state.pop("nivel_acesso", None)
    st.session_state.pop("session_token", None)
    st.session_state["aba_secreta_desbloqueada"] = False
    st.query_params.clear()
    st.rerun()

st.sidebar.divider()

# Lista dinâmica de abas
# ATUALIZADO: adicionadas as 4 novas páginas mantendo a aba secreta sempre por último.
opcoes_menu = [
    "Cadastro Rápido",
    "Controle de Prestadores",
    "Sublocatários",
    "Controle Gerentes de Loja",
    "Contas de Consumo",
    "Controle de Acessos",
    "Senhas Concessionárias",
    "Espaços Disponíveis",
]
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

# ==============================================================================
# NOVA ABA 5: CONTAS DE CONSUMO
# ==============================================================================
elif aba_selecionada == "Contas de Consumo":
    st.title("Contas de Consumo")

    if nivel in ["Editor", "Admin"]:
        with st.form("form_contas_consumo", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                cc_loja = st.text_input("Loja")
                # UF: campo limitado a 2 caracteres; é convertido para MAIÚSCULO automaticamente.
                cc_uf = st.text_input("UF (2 letras, ex: SP)", max_chars=2)
                cc_status = st.text_input("Status")
                cc_num_fornecimento = st.text_input("Número do fornecimento")
                cc_concessionaria_energia = st.text_input("Concessionária energia")
                cc_concessionaria_agua = st.text_input("Concessionária água")
                cc_instalacao_energia = st.text_input("Número de instalação energia")
                cc_instalacao_agua = st.text_input("Número de instalação água")

            with col2:
                cc_telefone = st.text_input("Telefone (Apenas números, 11 dígitos)")
                cc_documento_titular = st.text_input("Documento do titular")
                cc_protocolo_energia = st.text_input("Protocolo energia")
                cc_protocolo_agua = st.text_input("Protocolo água")
                cc_nome = st.text_input("Nome")
                cc_cpf_cnpj = st.text_input("CPF/CNPJ (Apenas números)")
                cc_email = st.text_input("E-mail")

            btn_salvar_cc = st.form_submit_button("Cadastrar Conta de Consumo")

        if btn_salvar_cc:
            # Lista de todos os campos obrigatórios (todos devem ser preenchidos)
            campos_cc = [
                cc_loja, cc_uf, cc_status, cc_num_fornecimento,
                cc_concessionaria_energia, cc_concessionaria_agua,
                cc_instalacao_energia, cc_instalacao_agua,
                cc_telefone, cc_documento_titular,
                cc_protocolo_energia, cc_protocolo_agua,
                cc_nome, cc_cpf_cnpj, cc_email,
            ]

            # UF convertida automaticamente para MAIÚSCULO (requisito: sempre maiúsculas)
            uf_limpa = cc_uf.strip().upper()

            if any(c.strip() == "" for c in campos_cc):
                st.error("Por favor, preencha todos os campos do formulário!")
            elif len(uf_limpa) != 2 or not uf_limpa.isalpha():
                st.error("O campo 'UF' deve conter exatamente 2 letras maiúsculas (ex: SP, RJ)!")
            elif not cc_telefone.strip().isdigit() or len(cc_telefone.strip()) != 11:
                st.error("O campo 'Telefone' deve conter exatamente 11 dígitos numéricos!")
            elif not cc_cpf_cnpj.strip().isdigit():
                st.error("O campo 'CPF/CNPJ' deve conter apenas números!")
            else:
                try:
                    df_cc = conn.read(spreadsheet=url_planilha, worksheet="Contas de Consumo", ttl=0)

                    nova_conta = pd.DataFrame(
                        [
                            {
                                "Loja": cc_loja,
                                "UF": uf_limpa,
                                "Status": cc_status,
                                "Número do fornecimento": cc_num_fornecimento,
                                "Concessionária energia": cc_concessionaria_energia,
                                "Concessionária água": cc_concessionaria_agua,
                                "Número de instalação energia": cc_instalacao_energia,
                                "Número de instalação água": cc_instalacao_agua,
                                "Telefone": str(cc_telefone),
                                "Documento do titular": cc_documento_titular,
                                "Protocolo energia": cc_protocolo_energia,
                                "Protocolo água": cc_protocolo_agua,
                                "Nome": cc_nome,
                                "CPF/CNPJ": str(cc_cpf_cnpj),
                                "E-mail": cc_email,
                                "Cadastrado Por": st.session_state["usuario_logado"],
                            }
                        ]
                    )

                    df_cc_atualizado = pd.concat([df_cc, nova_conta], ignore_index=True)
                    conn.update(spreadsheet=url_planilha, worksheet="Contas de Consumo", data=df_cc_atualizado)

                    st.success("Conta de consumo cadastrada com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Contas de Consumo': {err}")
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Contas de Consumo")

    try:
        df_cc_view = conn.read(spreadsheet=url_planilha, worksheet="Contas de Consumo", ttl=0)

        if nivel == "Admin" and not df_cc_view.empty:
            st.info("Selecione as linhas que deseja remover e clique no botão abaixo.")

            df_cc_editor = df_cc_view.copy()
            df_cc_editor.insert(0, "Excluir", False)

            tabela_cc_editavel = st.data_editor(
                df_cc_editor,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )

            linhas_cc_remover = tabela_cc_editavel[tabela_cc_editavel["Excluir"] == True]

            if not linhas_cc_remover.empty:
                if st.button("Confirmar Exclusão das Contas de Consumo Selecionadas"):
                    df_cc_final = tabela_cc_editavel[tabela_cc_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Contas de Consumo", data=df_cc_final)
                    st.success("Conta(s) de consumo removida(s) com sucesso!")
                    st.rerun()
        else:
            st.dataframe(df_cc_view, use_container_width=True)

    except Exception as e:
        st.info("Nenhuma conta cadastrada ou a guia 'Contas de Consumo' ainda não foi criada no Google Sheets.")

# ==============================================================================
# NOVA ABA 6: CONTROLE DE ACESSOS
# ==============================================================================
elif aba_selecionada == "Controle de Acessos":
    st.title("Controle de Acessos")

    if nivel in ["Editor", "Admin"]:
        with st.form("form_controle_acessos", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                ca_loja = st.text_input("Loja")
                # UF: campo limitado a 2 caracteres; convertido para MAIÚSCULO automaticamente.
                ca_uf = st.text_input("UF (2 letras, ex: SP)", max_chars=2)
                ca_status = st.text_input("Status")
                ca_concessionaria_agua = st.text_input("Concessionária água")
                ca_login_agua = st.text_input("Login água")
                # Campo de senha com máscara (não exibe os caracteres digitados)
                ca_senha_agua = st.text_input("Senha água", type="password")

            with col2:
                ca_concessionaria_energia = st.text_input("Concessionária energia")
                ca_login_energia = st.text_input("Login energia")
                # Campo de senha com máscara
                ca_senha_energia = st.text_input("Senha energia", type="password")

            btn_salvar_ca = st.form_submit_button("Cadastrar Acesso")

        if btn_salvar_ca:
            campos_ca = [
                ca_loja, ca_uf, ca_status,
                ca_concessionaria_agua, ca_login_agua, ca_senha_agua,
                ca_concessionaria_energia, ca_login_energia, ca_senha_energia,
            ]

            uf_limpa_ca = ca_uf.strip().upper()

            if any(c.strip() == "" for c in campos_ca):
                st.error("Por favor, preencha todos os campos do formulário!")
            elif len(uf_limpa_ca) != 2 or not uf_limpa_ca.isalpha():
                st.error("O campo 'UF' deve conter exatamente 2 letras maiúsculas (ex: SP, RJ)!")
            else:
                try:
                    df_ca = conn.read(spreadsheet=url_planilha, worksheet="Controle de Acessos", ttl=0)

                    novo_acesso = pd.DataFrame(
                        [
                            {
                                "Loja": ca_loja,
                                "UF": uf_limpa_ca,
                                "Status": ca_status,
                                "Concessionária água": ca_concessionaria_agua,
                                "Login água": ca_login_agua,
                                "Senha água": ca_senha_agua,
                                "Concessionária energia": ca_concessionaria_energia,
                                "Login energia": ca_login_energia,
                                "Senha energia": ca_senha_energia,
                                "Cadastrado Por": st.session_state["usuario_logado"],
                            }
                        ]
                    )

                    df_ca_atualizado = pd.concat([df_ca, novo_acesso], ignore_index=True)
                    conn.update(spreadsheet=url_planilha, worksheet="Controle de Acessos", data=df_ca_atualizado)

                    st.success("Acesso cadastrado com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Controle de Acessos': {err}")
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Controle de Acessos")

    try:
        df_ca_view = conn.read(spreadsheet=url_planilha, worksheet="Controle de Acessos", ttl=0)

        if nivel == "Admin" and not df_ca_view.empty:
            st.info("Selecione as linhas que deseja remover e clique no botão abaixo.")

            df_ca_editor = df_ca_view.copy()
            df_ca_editor.insert(0, "Excluir", False)

            tabela_ca_editavel = st.data_editor(
                df_ca_editor,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )

            linhas_ca_remover = tabela_ca_editavel[tabela_ca_editavel["Excluir"] == True]

            if not linhas_ca_remover.empty:
                if st.button("Confirmar Exclusão dos Acessos Selecionados"):
                    df_ca_final = tabela_ca_editavel[tabela_ca_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Controle de Acessos", data=df_ca_final)
                    st.success("Acesso(s) removido(s) com sucesso!")
                    st.rerun()
        else:
            st.dataframe(df_ca_view, use_container_width=True)

    except Exception as e:
        st.info("Nenhum acesso cadastrado ou a guia 'Controle de Acessos' ainda não foi criada no Google Sheets.")

# ==============================================================================
# NOVA ABA 7: SENHAS CONCESSIONÁRIAS
# ==============================================================================
elif aba_selecionada == "Senhas Concessionárias":
    st.title("Senhas Concessionárias")

    if nivel in ["Editor", "Admin"]:
        with st.form("form_senhas_concessionarias", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                sc_empresa = st.text_input("Empresa")
                sc_concessionaria = st.text_input("Concessionária")
                sc_login = st.text_input("Login")

            with col2:
                # Campo de senha com máscara
                sc_senha = st.text_input("Senha", type="password")
                sc_cnpj_cpf = st.text_input("CNPJ/CPF")

            btn_salvar_sc = st.form_submit_button("Cadastrar Senha")

        if btn_salvar_sc:
            campos_sc = [sc_empresa, sc_concessionaria, sc_login, sc_senha, sc_cnpj_cpf]

            if any(c.strip() == "" for c in campos_sc):
                st.error("Por favor, preencha todos os campos do formulário!")
            else:
                try:
                    df_sc = conn.read(spreadsheet=url_planilha, worksheet="Senhas Concessionárias", ttl=0)

                    nova_senha = pd.DataFrame(
                        [
                            {
                                "Empresa": sc_empresa,
                                "Concessionária": sc_concessionaria,
                                "Login": sc_login,
                                "Senha": sc_senha,
                                "CNPJ/CPF": sc_cnpj_cpf,
                                "Cadastrado Por": st.session_state["usuario_logado"],
                            }
                        ]
                    )

                    df_sc_atualizado = pd.concat([df_sc, nova_senha], ignore_index=True)
                    conn.update(spreadsheet=url_planilha, worksheet="Senhas Concessionárias", data=df_sc_atualizado)

                    st.success("Senha cadastrada com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Senhas Concessionárias': {err}")
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Senhas Concessionárias")

    try:
        df_sc_view = conn.read(spreadsheet=url_planilha, worksheet="Senhas Concessionárias", ttl=0)

        if nivel == "Admin" and not df_sc_view.empty:
            st.info("Selecione as linhas que deseja remover e clique no botão abaixo.")

            df_sc_editor = df_sc_view.copy()
            df_sc_editor.insert(0, "Excluir", False)

            tabela_sc_editavel = st.data_editor(
                df_sc_editor,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )

            linhas_sc_remover = tabela_sc_editavel[tabela_sc_editavel["Excluir"] == True]

            if not linhas_sc_remover.empty:
                if st.button("Confirmar Exclusão das Senhas Selecionadas"):
                    df_sc_final = tabela_sc_editavel[tabela_sc_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Senhas Concessionárias", data=df_sc_final)
                    st.success("Senha(s) removida(s) com sucesso!")
                    st.rerun()
        else:
            st.dataframe(df_sc_view, use_container_width=True)

    except Exception as e:
        st.info("Nenhuma senha cadastrada ou a guia 'Senhas Concessionárias' ainda não foi criada no Google Sheets.")

# ==============================================================================
# NOVA ABA 8: ESPAÇOS DISPONÍVEIS
# ==============================================================================
elif aba_selecionada == "Espaços Disponíveis":
    st.title("Espaços Disponíveis")

    if nivel in ["Editor", "Admin"]:
        with st.form("form_espacos_disponiveis", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                esp_unidade = st.text_input("Unidade disponível")
                esp_endereco = st.text_input("Endereço")
                # Selectbox garante que só as opções válidas sejam escolhidas
                esp_interno_externo = st.selectbox("Interno/Externo", ["Interno", "Externo"])
                esp_espaco_disp = st.text_input("Espaço Disp.")

            with col2:
                # Campo numérico para m² — apenas números; o sufixo " m²" é aplicado automaticamente ao salvar.
                esp_metragem = st.number_input(
                    "m² (apenas números)",
                    min_value=0.0,
                    step=1.0,
                    format="%.2f"
                )
                esp_pontos_consumo = st.text_input("Pontos de consumo")

            btn_salvar_esp = st.form_submit_button("Cadastrar Espaço")

        if btn_salvar_esp:
            campos_esp = [esp_unidade, esp_endereco, esp_interno_externo, esp_espaco_disp, esp_pontos_consumo]

            if any(c.strip() == "" for c in campos_esp):
                st.error("Por favor, preencha todos os campos do formulário!")
            elif esp_metragem <= 0:
                st.error("O campo 'm²' deve ser maior que zero!")
            else:
                try:
                    df_esp = conn.read(spreadsheet=url_planilha, worksheet="Espaços Disponíveis", ttl=0)

                    # Adiciona automaticamente o sufixo "m²" ao valor numérico (formatação limpa)
                    metragem_formatada_esp = f"{esp_metragem:g} m²"

                    novo_espaco = pd.DataFrame(
                        [
                            {
                                "Unidade disponível": esp_unidade,
                                "Endereço": esp_endereco,
                                "Interno/Externo": esp_interno_externo,
                                "Espaço Disp.": esp_espaco_disp,
                                "m²": metragem_formatada_esp,
                                "Pontos de consumo": esp_pontos_consumo,
                                "Cadastrado Por": st.session_state["usuario_logado"],
                            }
                        ]
                    )

                    df_esp_atualizado = pd.concat([df_esp, novo_espaco], ignore_index=True)
                    conn.update(spreadsheet=url_planilha, worksheet="Espaços Disponíveis", data=df_esp_atualizado)

                    st.success("Espaço disponível cadastrado com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Espaços Disponíveis': {err}")
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Espaços Disponíveis")

    try:
        df_esp_view = conn.read(spreadsheet=url_planilha, worksheet="Espaços Disponíveis", ttl=0)

        if nivel == "Admin" and not df_esp_view.empty:
            st.info("Selecione as linhas que deseja remover e clique no botão abaixo.")

            df_esp_editor = df_esp_view.copy()
            df_esp_editor.insert(0, "Excluir", False)

            tabela_esp_editavel = st.data_editor(
                df_esp_editor,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )

            linhas_esp_remover = tabela_esp_editavel[tabela_esp_editavel["Excluir"] == True]

            if not linhas_esp_remover.empty:
                if st.button("Confirmar Exclusão dos Espaços Selecionados"):
                    df_esp_final = tabela_esp_editavel[tabela_esp_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Espaços Disponíveis", data=df_esp_final)
                    st.success("Espaço(s) removido(s) com sucesso!")
                    st.rerun()
        else:
            st.dataframe(df_esp_view, use_container_width=True)

    except Exception as e:
        st.info("Nenhum espaço cadastrado ou a guia 'Espaços Disponíveis' ainda não foi criada no Google Sheets.")

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
