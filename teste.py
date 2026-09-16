# ==============================================================================
# SISTEMA DE CADASTRO RÁPIDO, PRESTADORES, SUBLOCATÁRIOS E GERENTES DE LOJA
# Autor: Raphael Santos
# Propriedade Intelectual e Desenvolvimento: Raphael Santos
# Licença: Uso Exclusivo Autorizado - Proibida Replicação ou Alteração sem Autorização
# Data de Criação: Set/2026
# ==============================================================================

import datetime
import random
import secrets  
import hashlib  
import hmac     
import time     
import traceback
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Sistema de Cadastro e Gestão", layout="wide")

st.markdown(
    """
    <style>
    .stApp { 
        background-color: #341539 !important; 
    }

    [data-testid="stSidebar"] {
        background-color: #262730 !important;
        border-right: 1px solid rgba(255, 216, 15, 0.2) !important;
    }

    h1, h2, h3, label, [data-testid="stMarkdownContainer"] p { 
        color: #FFD80F !important; 
        font-weight: bold !important; 
    }

    div[data-baseweb="input"] > div { 
        background-color: #262730 !important; 
        border: 1px solid rgba(255, 216, 15, 0.3) !important;
        border-radius: 8px !important; 
    }
    div[data-baseweb="input"] input { 
        color: #FFFFFF !important; 
        font-weight: normal !important;
    }

    [data-testid="stForm"] { border: none !important; padding: 0 !important; }

    div.stButton > button, div[data-testid="stFormSubmitButton"] > button { 
        background-color: #FFD80F !important; 
        color: #7B2CBF !important; 
        border-radius: 8px !important; 
        border: none !important; 
        padding: 10px 24px !important; 
        font-weight: bold !important; 
    }

    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div,
    div.stButton > button label,
    div[data-testid="stFormSubmitButton"] > button p,
    div[data-testid="stFormSubmitButton"] > button span,
    div[data-testid="stFormSubmitButton"] > button div,
    div[data-testid="stFormSubmitButton"] > button label {
        color: #7B2CBF !important;
        font-weight: bold !important;
    }

    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { 
        background-color: #7B2CBF !important; 
        color: #FFD80F !important; 
    }

    div.stButton > button:hover p,
    div.stButton > button:hover span,
    div.stButton > button:hover div,
    div.stButton > button:hover label,
    div[data-testid="stFormSubmitButton"] > button:hover p,
    div[data-testid="stFormSubmitButton"] > button:hover span,
    div[data-testid="stFormSubmitButton"] > button:hover div,
    div[data-testid="stFormSubmitButton"] > button:hover label {
        color: #FFD80F !important;
        font-weight: bold !important;
    }

    div.element-container:has(#secret-btn-marker) + div.element-container button,
    div.element-container:has(#secret-btn-marker) + div.element-container button p,
    div.element-container:has(#secret-btn-marker) + div.element-container button span,
    div.element-container:has(#secret-btn-marker) + div.element-container button div,
    div.element-container:has(#secret-btn-marker) + div.element-container button label {
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
    div.element-container:has(#secret-btn-marker) + div.element-container button:hover,
    div.element-container:has(#secret-btn-marker) + div.element-container button:hover p,
    div.element-container:has(#secret-btn-marker) + div.element-container button:hover span,
    div.element-container:has(#secret-btn-marker) + div.element-container button:hover div,
    div.element-container:has(#secret-btn-marker) + div.element-container button:hover label {
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
    }

    div[data-testid="stRadioButton"] label p {
        color: #FFD80F !important;
    }

    div[data-testid="stRadioButton"] [aria-checked="true"] div:first-child,
    div[data-testid="stRadioButton"] [data-baseweb="radio"] input:checked + div {
        border-color: #FFD80F !important;
        background-color: #FFD80F !important;
    }

    div[data-testid="stRadioButton"] [aria-checked="true"] div:first-child > div,
    div[data-testid="stRadioButton"] [data-baseweb="radio"] input:checked + div > div {
        background-color: #262730 !important;
    }

    div[data-testid="stRadioButton"] [aria-checked="false"] div:first-child,
    div[data-testid="stRadioButton"] [data-baseweb="radio"] input:not(:checked) + div {
        border-color: #FFD80F !important;
        background-color: transparent !important;
    }

    div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] ~ div,
    div[data-testid="stSlider"] [data-baseweb="slider"] div[style*="background-color"],
    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {
        background: #FFD80F !important;
        background-color: #FFD80F !important;
    }

    div[data-testid="stSlider"] [role="slider"] {
        background-color: #FFD80F !important;
        border-color: #FFD80F !important;
        box-shadow: 0px 0px 6px rgba(255, 216, 15, 0.9) !important;
    }

    div[data-testid="stSlider"] [data-testid="stTickBar"] div,
    div[data-testid="stSlider"] div,
    div[data-testid="stSlider"] p {
        color: #FFD80F !important;
    }

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

def gerar_hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.strip().encode("utf-8")).hexdigest()

try:
    dados_secrets = st.secrets["USUARIOS"]
    USUARIOS_SECRETS = {k.strip().lower(): v for k, v in dados_secrets.items()}
except Exception:
    USUARIOS_SECRETS = {}

conn = st.connection("gsheets", type=GSheetsConnection)
url_planilha = st.secrets["connections"]["gsheets"]["spreadsheet"]

def ler_aba_padronizada(nome_aba, colunas_esperadas):
    try:
        df = conn.read(spreadsheet=url_planilha, worksheet=nome_aba, ttl=0)
    except Exception:
        return pd.DataFrame({c: pd.Series(dtype="object") for c in colunas_esperadas})

    if df is None or df.empty:
        return pd.DataFrame({c: pd.Series(dtype="object") for c in colunas_esperadas})

    df = df.loc[:, ~df.columns.duplicated()].copy()

    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = ""

    df = df[colunas_esperadas].copy()

    for col in df.columns:
        df[col] = df[col].astype("object")
        df[col] = df[col].where(pd.notna(df[col]), "")

    return df

def carregar_usuarios():
    usuarios = dict(USUARIOS_SECRETS)
    try:
        df = conn.read(spreadsheet=url_planilha, worksheet="Usuários", ttl=0)
        if df is not None and not df.empty:
            df = df.loc[:, ~df.columns.duplicated()]
            for _, row in df.iterrows():
                u = str(row.get("Usuário", "")).strip().lower()
                if not u:
                    continue
                usuarios[u] = {
                    "senha": str(row.get("Senha", "")).strip(),
                    "nivel": str(row.get("Nível", "")).strip(),
                    "cadastrado_por": str(row.get("Cadastrado Por", "")).strip(),
                    "data": str(row.get("Data", "")).strip(),
                }
    except Exception:
        pass
    return usuarios

def validar_campo(nome_campo, valor, regra):
    v = str(valor).strip()
    if regra == "uf":
        if len(v) != 2 or not v.isalpha():
            return False, "deve conter exatamente 2 letras (ex: SP, RJ)"
    elif regra == "telefone":
        if not v.isdigit() or len(v) != 11:
            return False, "deve conter exatamente 11 dígitos numéricos"
    elif regra == "cpf_cnpj":
        if not v.isdigit():
            return False, "deve conter apenas números"
    elif regra == "m2":
        num_str = v.replace("m²", "").replace("m2", "").strip()
        try:
            num = float(num_str)
            if num <= 0:
                return False, "deve ser maior que zero"
        except ValueError:
            return False, "deve ser um valor numérico"
    return True, ""

def _valor_mudou(v_orig, v_edit):
    v_orig_vazio = pd.isna(v_orig) or str(v_orig).strip() == "" or str(v_orig).strip().lower() == "none"
    v_edit_vazio = pd.isna(v_edit) or str(v_edit).strip() == "" or str(v_edit).strip().lower() == "none"

    if v_orig_vazio and v_edit_vazio:
        return False
    if v_orig_vazio or v_edit_vazio:
        return True

    s1 = str(v_orig).strip()
    s2 = str(v_edit).strip()

    if s1 == s2:
        return False

    try:
        return float(s1) != float(s2)
    except (ValueError, TypeError):
        return True

def _preparar_df_para_sheets(df):
    df_out = df.copy()
    for col in df_out.columns:
        df_out[col] = df_out[col].astype("object")
        df_out[col] = df_out[col].apply(
            lambda x: "" if (x is None or (isinstance(x, float) and pd.isna(x)) or x is pd.NA or x is pd.NaT) else x
        )
    df_out = df_out.replace({pd.NA: "", None: "", pd.NaT: ""})
    return df_out

def render_editor_com_edicao(df, nome_aba, colunas_auditoria, validacoes, key_prefix):
    for col_aud in colunas_auditoria:
        if col_aud not in df.columns:
            df[col_aud] = ""

    df_original = df.reset_index(drop=True).copy()
    df_editor = df.copy()
    df_editor.insert(0, "Excluir", False)

    colunas_disabled = ["Cadastrado Por"] + colunas_auditoria
    colunas_disabled = [c for c in colunas_disabled if c in df_editor.columns]

    tabela_editavel = st.data_editor(
        df_editor,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=colunas_disabled,
        key=f"editor_{key_prefix}"
    )

    df_editado = tabela_editavel.drop(columns=["Excluir"]).reset_index(drop=True)

    for col in df_editado.columns:
        df_editado[col] = df_editado[col].astype("object")

    colunas_dados = [c for c in df_original.columns if c not in colunas_auditoria]
    alteracoes = {}
    for idx in df_original.index:
        if idx not in df_editado.index:
            continue
        for col in colunas_dados:
            if col not in df_editado.columns:
                continue
            if _valor_mudou(df_original.loc[idx, col], df_editado.loc[idx, col]):
                if idx not in alteracoes:
                    alteracoes[idx] = {}
                alteracoes[idx][col] = df_editado.loc[idx, col]

    indices_alterados = sorted(alteracoes.keys())

    linhas_marcadas_excluir = tabela_editavel[tabela_editavel["Excluir"] == True]
    indices_excluir = linhas_marcadas_excluir.index.tolist()
    conflitos = sorted(set(indices_alterados) & set(indices_excluir))

    if indices_alterados:
        st.warning(f"⚠️ Você tem {len(indices_alterados)} linha(s) com alterações não salvas. Clique em 'Salvar Alterações' para aplicar.")

    col_btn1, col_btn2 = st.columns([1, 1])

    with col_btn1:
        if st.button("💾 Salvar Alterações", key=f"salvar_{key_prefix}"):
            if conflitos:
                st.error(
                    "Conflito detectado: você não pode editar e marcar para excluir a mesma linha ao mesmo tempo. "
                    f"Linhas em conflito: {[i + 1 for i in conflitos]}. Desmarque 'Excluir' ou desfaça a edição."
                )
            elif not indices_alterados:
                st.warning("Nenhuma alteração detectada para salvar.")
            else:
                erros = []
                for idx, cells in alteracoes.items():
                    for col, novo_valor in cells.items():
                        if col in validacoes:
                            ok, msg = validar_campo(col, novo_valor, validacoes[col])
                            if not ok:
                                erros.append(f"Linha {idx + 1} → {col}: {msg}")

                if erros:
                    for e in erros:
                        st.error(e)
                    st.info(
                        "💡 Apenas as células que você editou são validadas. "
                        "Dados pré-existentes na planilha que não passam nas regras "
                        "não bloqueiam o salvamento."
                    )
                else:
                    agora_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                    usuario_atual = st.session_state.get("usuario_logado", "")

                    for col_aud in colunas_auditoria:
                        if col_aud in df_editado.columns:
                            df_editado[col_aud] = df_editado[col_aud].astype("object")

                    for idx in indices_alterados:
                        df_editado.at[idx, "Última Alteração Por"] = str(usuario_atual)
                        df_editado.at[idx, "Data da Alteração"] = str(agora_str)

                    df_para_salvar = _preparar_df_para_sheets(df_editado)

                    try:
                        conn.update(spreadsheet=url_planilha, worksheet=nome_aba, data=df_para_salvar)
                        st.success(f"{len(indices_alterados)} linha(s) atualizada(s) com sucesso!")
                        st.rerun()
                    except Exception as ex_save:
                        st.error(f"Erro ao salvar na planilha: {ex_save}")
                        with st.expander("Detalhes técnicos do erro"):
                            st.code(traceback.format_exc())

    with col_btn2:
        if not linhas_marcadas_excluir.empty:
            if st.button("Confirmar Exclusão dos Selecionados", key=f"excluir_{key_prefix}"):
                if conflitos:
                    st.error(
                        "Conflito detectado: você não pode editar e excluir a mesma linha ao mesmo tempo. "
                        f"Desfaça as edições das linhas: {[i + 1 for i in conflitos]}."
                    )
                else:
                    df_final = tabela_editavel[tabela_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    df_final = df_final.copy()
                    for col in df_final.columns:
                        df_final[col] = df_final[col].astype("object")
                    df_final = _preparar_df_para_sheets(df_final)
                    try:
                        conn.update(spreadsheet=url_planilha, worksheet=nome_aba, data=df_final)
                        st.success("Registro(s) removido(s) com sucesso!")
                        st.rerun()
                    except Exception as ex_del:
                        st.error(f"Erro ao excluir na planilha: {ex_del}")
                        with st.expander("Detalhes técnicos do erro"):
                            st.code(traceback.format_exc())

@st.cache_resource
def obter_armazenamento_sessoes():
    return {}

SESSOES = obter_armazenamento_sessoes()
DURACAO_SESSAO_SEGUNDOS = 8 * 60 * 60

def criar_sessao(usuario: str, nivel: str) -> str:
    token = secrets.token_urlsafe(32)
    SESSOES[token] = {
        "usuario": usuario,
        "nivel": nivel,
        "expira_em": time.time() + DURACAO_SESSAO_SEGUNDOS,
    }
    return token

def validar_sessao(token: str):
    sessao = SESSOES.get(token)
    if not sessao:
        return None
    if time.time() > sessao["expira_em"]:
        SESSOES.pop(token, None)
        return None
    return sessao["usuario"], sessao["nivel"]

def encerrar_sessao(token: str):
    SESSOES.pop(token, None)

def encerrar_sessoes_do_usuario(nome_usuario: str) -> int:
    nome_lower = str(nome_usuario).strip().lower()
    if not nome_lower:
        return 0
    tokens_para_remover = [
        token for token, dados in list(SESSOES.items())
        if str(dados.get("usuario", "")).strip().lower() == nome_lower
    ]
    for token in tokens_para_remover:
        SESSOES.pop(token, None)
    return len(tokens_para_remover)

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
        st.query_params.clear()

if st.session_state.get("autenticado"):
    token_atual = st.session_state.get("session_token")
    sessao_atual = SESSOES.get(token_atual, {}) if token_atual else {}
    token_valido = bool(token_atual) and bool(sessao_atual) and time.time() <= sessao_atual.get("expira_em", 0)
    if not token_valido:
        st.session_state["mensagem_sessao_encerrada"] = "Sua sessão foi encerrada. Faça login novamente."
        st.session_state["autenticado"] = False
        st.session_state.pop("usuario_logado", None)
        st.session_state.pop("nivel_acesso", None)
        st.session_state.pop("session_token", None)
        st.session_state["aba_secreta_desbloqueada"] = False
        st.query_params.clear()
        st.rerun()

MAX_TENTATIVAS = 5
BLOQUEIO_SEGUNDOS = 60

if "tentativas_login" not in st.session_state:
    st.session_state["tentativas_login"] = 0
if "bloqueado_ate" not in st.session_state:
    st.session_state["bloqueado_ate"] = 0

if not st.session_state["autenticado"]:
    st.title("Acesso Restrito")

    if st.session_state.get("mensagem_sessao_encerrada"):
        st.warning(st.session_state["mensagem_sessao_encerrada"])
        del st.session_state["mensagem_sessao_encerrada"]

    USUARIOS = carregar_usuarios()

    if not USUARIOS:
        st.error(
            "Nenhum usuário cadastrado. Configure st.secrets['USUARIOS'] (bootstrap) "
            "ou crie a aba 'Usuários' na planilha com as colunas: Usuário, Senha, Nível."
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

            senha_correta = hmac.compare_digest(hash_senha_digitada, hash_esperado)

            if usuario_existe and senha_correta:
                nivel_usuario = USUARIOS[usuario_limpo]["nivel"]
                token = criar_sessao(usuario_limpo, nivel_usuario)

                st.session_state["autenticado"] = True
                st.session_state["usuario_logado"] = usuario_input.strip().title()
                st.session_state["nivel_acesso"] = nivel_usuario
                st.session_state["session_token"] = token
                st.session_state["tentativas_login"] = 0

                st.query_params["session"] = token
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

if "aba_secreta_desbloqueada" not in st.session_state:
    st.session_state["aba_secreta_desbloqueada"] = False

nivel = st.session_state.get("nivel_acesso")

st.sidebar.title("Menu do Sistema")
st.sidebar.write(f"Usuário: **{st.session_state.get('usuario_logado')}**")
st.sidebar.write(f"Perfil: **{nivel}**")

if st.sidebar.button("Sair"):
    encerrar_sessao(st.session_state.get("session_token"))
    st.session_state["autenticado"] = False
    st.session_state.pop("usuario_logado", None)
    st.session_state.pop("nivel_acesso", None)
    st.session_state.pop("session_token", None)
    st.session_state["aba_secreta_desbloqueada"] = False
    st.session_state["menu_navegacao"] = "Cadastro Rápido"
    st.query_params.clear()
    st.rerun()

st.sidebar.divider()

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
if nivel in ["Admin", "Con"]:
    opcoes_menu.append("👥 Gerenciar Usuários")
if st.session_state["aba_secreta_desbloqueada"]:
    opcoes_menu.append("🎮 Sala Secreta: Jogo da Forca")
    opcoes_menu.append("🐍 Sala Secreta: Jogo da Cobrinha")

if "menu_navegacao" not in st.session_state or st.session_state["menu_navegacao"] not in opcoes_menu:
    st.session_state["menu_navegacao"] = opcoes_menu[0]

aba_selecionada = st.sidebar.radio("Navegação", opcoes_menu, key="menu_navegacao")

st.sidebar.markdown('<span id="secret-btn-marker"></span>', unsafe_allow_html=True)
if st.sidebar.button(" ", key="btn_secreto"):
    st.session_state["aba_secreta_desbloqueada"] = not st.session_state["aba_secreta_desbloqueada"]
    st.rerun()

if aba_selecionada == "Cadastro Rápido":
    st.title("Cadastro Rápido de Dados")

    COLUNAS_CR = [
        "Loja", "Nome Completo", "Endereço", "Telefone", "E-mail", "Status",
        "Cadastrado Por", "Última Alteração Por", "Data da Alteração",
    ]

    if nivel in ["Editor", "Admin", "Con"]:
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
                    df_existente = ler_aba_padronizada("Cadastro Rápido", COLUNAS_CR)

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
                                "Última Alteração Por": "",
                                "Data da Alteração": "",
                            }
                        ]
                    )

                    df_atualizado = pd.concat([df_existente, novo_dado], ignore_index=True)
                    df_atualizado = df_atualizado[COLUNAS_CR]
                    df_atualizado = _preparar_df_para_sheets(df_atualizado)
                    conn.update(spreadsheet=url_planilha, worksheet="Cadastro Rápido", data=df_atualizado)

                    st.success("Dados salvos com sucesso no Google Sheets!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na planilha: {err}")
                    with st.expander("Detalhes técnicos"):
                        st.code(traceback.format_exc())
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Cadastros")

    try:
        df = ler_aba_padronizada("Cadastro Rápido", COLUNAS_CR)
    except Exception as e:
        st.error(f"Erro ao ler a aba 'Cadastro Rápido': {e}")
        df = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_CR})

    if nivel in ["Editor", "Admin", "Con"] and not df.empty:
        st.info("Você pode editar qualquer célula diretamente na tabela (exceto 'Cadastrado Por' e colunas de auditoria). Ao terminar, clique em 'Salvar Alterações'.")
        render_editor_com_edicao(
            df,
            nome_aba="Cadastro Rápido",
            colunas_auditoria=["Última Alteração Por", "Data da Alteração"],
            validacoes={"Telefone": "telefone"},
            key_prefix="cadastro_rapido",
        )
    elif df.empty:
        st.info("Nenhum dado cadastrado ainda.")
    else:
        st.dataframe(df, use_container_width=True)

elif aba_selecionada == "Controle de Prestadores":
    st.title("Controle de Prestadores de Serviço")

    COLUNAS_CP = [
        "Região", "Prestador de Serviço", "Serviços", "Telefone", "E-mail",
        "Avaliação de 0 a 5", "Prazo pag.", "NF.",
        "Cadastrado Por", "Última Alteração Por", "Data da Alteração",
    ]

    if nivel in ["Editor", "Admin", "Con"]:
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
                    df_prestadores = ler_aba_padronizada("Controle de Prestadores", COLUNAS_CP)

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
                                "Última Alteração Por": "",
                                "Data da Alteração": "",
                            }
                        ]
                    )

                    df_p_atualizado = pd.concat([df_prestadores, novo_prestador], ignore_index=True)
                    df_p_atualizado = df_p_atualizado[COLUNAS_CP]
                    df_p_atualizado = _preparar_df_para_sheets(df_p_atualizado)
                    conn.update(spreadsheet=url_planilha, worksheet="Controle de Prestadores", data=df_p_atualizado)

                    st.success("Prestador cadastrado com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Controle de Prestadores': {err}")
                    with st.expander("Detalhes técnicos"):
                        st.code(traceback.format_exc())
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Prestadores")

    try:
        df_p = ler_aba_padronizada("Controle de Prestadores", COLUNAS_CP)
    except Exception as e:
        st.error(f"Erro ao ler a aba 'Controle de Prestadores': {e}")
        df_p = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_CP})

    if nivel in ["Editor", "Admin", "Con"] and not df_p.empty:
        st.info("Você pode editar qualquer célula diretamente na tabela (exceto 'Cadastrado Por' e colunas de auditoria). Ao terminar, clique em 'Salvar Alterações'.")
        render_editor_com_edicao(
            df_p,
            nome_aba="Controle de Prestadores",
            colunas_auditoria=["Última Alteração Por", "Data da Alteração"],
            validacoes={"Telefone": "telefone"},
            key_prefix="prestadores",
        )
    elif df_p.empty:
        st.info("Nenhum prestador cadastrado ainda.")
    else:
        st.dataframe(df_p, use_container_width=True)

elif aba_selecionada == "Sublocatários":
    st.title("Controle de Sublocatários")

    COLUNAS_SUB = [
        "Loja", "Endereço", "Nome completo", "Telefone",
        "Nome do representante legal", "E-mail",
        "Data de inicio", "Data de encerramento",
        "Tipo de espaço", "Metragem ocupada",
        "Demanda de energia", "Pontos de consumo", "Segmento",
        "Horário de funcionamento",
        "Cadastrado Por", "Última Alteração Por", "Data da Alteração",
    ]

    if nivel in ["Editor", "Admin", "Con"]:
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
                    df_sub = ler_aba_padronizada("Sublocatários", COLUNAS_SUB)

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
                                "Última Alteração Por": "",
                                "Data da Alteração": "",
                            }
                        ]
                    )

                    df_sub_atualizado = pd.concat([df_sub, novo_sublocatario], ignore_index=True)
                    df_sub_atualizado = df_sub_atualizado[COLUNAS_SUB]
                    df_sub_atualizado = _preparar_df_para_sheets(df_sub_atualizado)
                    conn.update(spreadsheet=url_planilha, worksheet="Sublocatários", data=df_sub_atualizado)

                    st.success("Sublocatário cadastrado com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Sublocatários': {err}")
                    with st.expander("Detalhes técnicos"):
                        st.code(traceback.format_exc())
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Sublocatários")

    try:
        df_s = ler_aba_padronizada("Sublocatários", COLUNAS_SUB)
    except Exception as e:
        st.error(f"Erro ao ler a aba 'Sublocatários': {e}")
        df_s = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_SUB})

    if nivel in ["Editor", "Admin", "Con"] and not df_s.empty:
        st.info("Você pode editar qualquer célula diretamente na tabela (exceto 'Cadastrado Por' e colunas de auditoria). Ao terminar, clique em 'Salvar Alterações'.")
        render_editor_com_edicao(
            df_s,
            nome_aba="Sublocatários",
            colunas_auditoria=["Última Alteração Por", "Data da Alteração"],
            validacoes={"Telefone": "telefone", "Metragem ocupada": "m2"},
            key_prefix="sublocatarios",
        )
    elif df_s.empty:
        st.info("Nenhum sublocatário cadastrado ainda.")
    else:
        st.dataframe(df_s, use_container_width=True)

elif aba_selecionada == "Controle Gerentes de Loja":
    st.title("Controle Gerentes de Loja")

    COLUNAS_G = [
        "Loja", "Nome", "Telefone", "E-mail", "Cargo",
        "Cadastrado Por", "Última Alteração Por", "Data da Alteração",
    ]

    if nivel in ["Editor", "Admin", "Con"]:
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
                    df_gerentes = ler_aba_padronizada("Controle Gerentes de Loja", COLUNAS_G)

                    novo_gerente = pd.DataFrame(
                        [
                            {
                                "Loja": g_loja,
                                "Nome": g_nome,
                                "Telefone": str(g_tel),
                                "E-mail": g_email,
                                "Cargo": g_cargo,
                                "Cadastrado Por": st.session_state["usuario_logado"],
                                "Última Alteração Por": "",
                                "Data da Alteração": "",
                            }
                        ]
                    )

                    df_g_atualizado = pd.concat([df_gerentes, novo_gerente], ignore_index=True)
                    df_g_atualizado = df_g_atualizado[COLUNAS_G]
                    df_g_atualizado = _preparar_df_para_sheets(df_g_atualizado)
                    conn.update(spreadsheet=url_planilha, worksheet="Controle Gerentes de Loja", data=df_g_atualizado)

                    st.success("Gerente cadastrado com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Controle Gerentes de Loja': {err}")
                    with st.expander("Detalhes técnicos"):
                        st.code(traceback.format_exc())
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Gerentes de Loja")

    try:
        df_g = ler_aba_padronizada("Controle Gerentes de Loja", COLUNAS_G)
    except Exception as e:
        st.error(f"Erro ao ler a aba 'Controle Gerentes de Loja': {e}")
        df_g = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_G})

    if nivel in ["Editor", "Admin", "Con"] and not df_g.empty:
        st.info("Você pode editar qualquer célula diretamente na tabela (exceto 'Cadastrado Por' e colunas de auditoria). Ao terminar, clique em 'Salvar Alterações'.")
        render_editor_com_edicao(
            df_g,
            nome_aba="Controle Gerentes de Loja",
            colunas_auditoria=["Última Alteração Por", "Data da Alteração"],
            validacoes={"Telefone": "telefone"},
            key_prefix="gerentes",
        )
    elif df_g.empty:
        st.info("Nenhum gerente cadastrado ainda.")
    else:
        st.dataframe(df_g, use_container_width=True)

elif aba_selecionada == "Contas de Consumo":
    st.title("Contas de Consumo")

    COLUNAS_CC = [
        "Loja", "UF", "Status", "Número do fornecimento",
        "Concessionária energia", "Concessionária água",
        "Número de instalação energia", "Número de instalação água",
        "Telefone", "Documento do titular",
        "Protocolo energia", "Protocolo água",
        "Nome", "CPF/CNPJ", "E-mail",
        "Cadastrado Por", "Última Alteração Por", "Data da Alteração",
    ]

    if nivel in ["Editor", "Admin", "Con"]:
        with st.form("form_contas_consumo", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                cc_loja = st.text_input("Loja")
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
            campos_cc = [
                cc_loja, cc_uf, cc_status, cc_num_fornecimento,
                cc_concessionaria_energia, cc_concessionaria_agua,
                cc_instalacao_energia, cc_instalacao_agua,
                cc_telefone, cc_documento_titular,
                cc_protocolo_energia, cc_protocolo_agua,
                cc_nome, cc_cpf_cnpj, cc_email,
            ]

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
                    df_cc = ler_aba_padronizada("Contas de Consumo", COLUNAS_CC)

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
                                "Última Alteração Por": "",
                                "Data da Alteração": "",
                            }
                        ]
                    )

                    df_cc_atualizado = pd.concat([df_cc, nova_conta], ignore_index=True)
                    df_cc_atualizado = df_cc_atualizado[COLUNAS_CC]
                    df_cc_atualizado = _preparar_df_para_sheets(df_cc_atualizado)
                    conn.update(spreadsheet=url_planilha, worksheet="Contas de Consumo", data=df_cc_atualizado)

                    st.success("Conta de consumo cadastrada com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Contas de Consumo': {err}")
                    with st.expander("Detalhes técnicos"):
                        st.code(traceback.format_exc())
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Contas de Consumo")

    try:
        df_cc_view = ler_aba_padronizada("Contas de Consumo", COLUNAS_CC)
    except Exception as e:
        st.error(f"Erro ao ler a aba 'Contas de Consumo': {e}")
        df_cc_view = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_CC})

    if nivel in ["Editor", "Admin", "Con"] and not df_cc_view.empty:
        st.info("Você pode editar qualquer célula diretamente na tabela (exceto 'Cadastrado Por' e colunas de auditoria). Ao terminar, clique em 'Salvar Alterações'.")
        render_editor_com_edicao(
            df_cc_view,
            nome_aba="Contas de Consumo",
            colunas_auditoria=["Última Alteração Por", "Data da Alteração"],
            validacoes={"UF": "uf", "Telefone": "telefone", "CPF/CNPJ": "cpf_cnpj"},
            key_prefix="contas_consumo",
        )
    elif df_cc_view.empty:
        st.info("Nenhuma conta cadastrada ainda.")
    else:
        st.dataframe(df_cc_view, use_container_width=True)

elif aba_selecionada == "Controle de Acessos":
    st.title("Controle de Acessos")

    COLUNAS_CA = [
        "Loja", "UF", "Status",
        "Concessionária água", "Login água", "Senha água",
        "Concessionária energia", "Login energia", "Senha energia",
        "Cadastrado Por", "Última Alteração Por", "Data da Alteração",
    ]

    if nivel in ["Editor", "Admin", "Con"]:
        with st.form("form_controle_acessos", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                ca_loja = st.text_input("Loja")
                ca_uf = st.text_input("UF (2 letras, ex: SP)", max_chars=2)
                ca_status = st.text_input("Status")
                ca_concessionaria_agua = st.text_input("Concessionária água")
                ca_login_agua = st.text_input("Login água")
                ca_senha_agua = st.text_input("Senha água", type="password")

            with col2:
                ca_concessionaria_energia = st.text_input("Concessionária energia")
                ca_login_energia = st.text_input("Login energia")
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
                    df_ca = ler_aba_padronizada("Controle de Acessos", COLUNAS_CA)

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
                                "Última Alteração Por": "",
                                "Data da Alteração": "",
                            }
                        ]
                    )

                    df_ca_atualizado = pd.concat([df_ca, novo_acesso], ignore_index=True)
                    df_ca_atualizado = df_ca_atualizado[COLUNAS_CA]
                    df_ca_atualizado = _preparar_df_para_sheets(df_ca_atualizado)
                    conn.update(spreadsheet=url_planilha, worksheet="Controle de Acessos", data=df_ca_atualizado)

                    st.success("Acesso cadastrado com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Controle de Acessos': {err}")
                    with st.expander("Detalhes técnicos"):
                        st.code(traceback.format_exc())
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Controle de Acessos")

    try:
        df_ca_view = ler_aba_padronizada("Controle de Acessos", COLUNAS_CA)
    except Exception as e:
        st.error(f"Erro ao ler a aba 'Controle de Acessos': {e}")
        df_ca_view = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_CA})

    if nivel in ["Editor", "Admin", "Con"] and not df_ca_view.empty:
        st.info("Você pode editar qualquer célula diretamente na tabela (exceto 'Cadastrado Por' e colunas de auditoria). Ao terminar, clique em 'Salvar Alterações'.")
        render_editor_com_edicao(
            df_ca_view,
            nome_aba="Controle de Acessos",
            colunas_auditoria=["Última Alteração Por", "Data da Alteração"],
            validacoes={"UF": "uf"},
            key_prefix="controle_acessos",
        )
    elif df_ca_view.empty:
        st.info("Nenhum acesso cadastrado ainda.")
    else:
        st.dataframe(df_ca_view, use_container_width=True)

elif aba_selecionada == "Senhas Concessionárias":
    st.title("Senhas Concessionárias")

    COLUNAS_SC = [
        "Empresa", "Concessionária", "Login", "Senha", "CNPJ/CPF",
        "Cadastrado Por", "Última Alteração Por", "Data da Alteração",
    ]

    if nivel in ["Editor", "Admin", "Con"]:
        with st.form("form_senhas_concessionarias", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                sc_empresa = st.text_input("Empresa")
                sc_concessionaria = st.text_input("Concessionária")
                sc_login = st.text_input("Login")

            with col2:
                sc_senha = st.text_input("Senha", type="password")
                sc_cnpj_cpf = st.text_input("CNPJ/CPF")

            btn_salvar_sc = st.form_submit_button("Cadastrar Senha")

        if btn_salvar_sc:
            campos_sc = [sc_empresa, sc_concessionaria, sc_login, sc_senha, sc_cnpj_cpf]

            if any(c.strip() == "" for c in campos_sc):
                st.error("Por favor, preencha todos os campos do formulário!")
            else:
                try:
                    df_sc = ler_aba_padronizada("Senhas Concessionárias", COLUNAS_SC)

                    nova_senha = pd.DataFrame(
                        [
                            {
                                "Empresa": sc_empresa,
                                "Concessionária": sc_concessionaria,
                                "Login": sc_login,
                                "Senha": sc_senha,
                                "CNPJ/CPF": sc_cnpj_cpf,
                                "Cadastrado Por": st.session_state["usuario_logado"],
                                "Última Alteração Por": "",
                                "Data da Alteração": "",
                            }
                        ]
                    )

                    df_sc_atualizado = pd.concat([df_sc, nova_senha], ignore_index=True)
                    df_sc_atualizado = df_sc_atualizado[COLUNAS_SC]
                    df_sc_atualizado = _preparar_df_para_sheets(df_sc_atualizado)
                    conn.update(spreadsheet=url_planilha, worksheet="Senhas Concessionárias", data=df_sc_atualizado)

                    st.success("Senha cadastrada com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Senhas Concessionárias': {err}")
                    with st.expander("Detalhes técnicos"):
                        st.code(traceback.format_exc())
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Senhas Concessionárias")

    try:
        df_sc_view = ler_aba_padronizada("Senhas Concessionárias", COLUNAS_SC)
    except Exception as e:
        st.error(f"Erro ao ler a aba 'Senhas Concessionárias': {e}")
        df_sc_view = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_SC})

    if nivel in ["Editor", "Admin", "Con"] and not df_sc_view.empty:
        st.info("Você pode editar qualquer célula diretamente na tabela (exceto 'Cadastrado Por' e colunas de auditoria). Ao terminar, clique em 'Salvar Alterações'.")
        render_editor_com_edicao(
            df_sc_view,
            nome_aba="Senhas Concessionárias",
            colunas_auditoria=["Última Alteração Por", "Data da Alteração"],
            validacoes={},
            key_prefix="senhas_concessionarias",
        )
    elif df_sc_view.empty:
        st.info("Nenhuma senha cadastrada ainda.")
    else:
        st.dataframe(df_sc_view, use_container_width=True)

elif aba_selecionada == "Espaços Disponíveis":
    st.title("Espaços Disponíveis")

    COLUNAS_ESP = [
        "Unidade disponível", "Endereço", "Interno/Externo",
        "Espaço Disp.", "m²", "Pontos de consumo",
        "Cadastrado Por", "Última Alteração Por", "Data da Alteração",
    ]

    if nivel in ["Editor", "Admin", "Con"]:
        with st.form("form_espacos_disponiveis", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                esp_unidade = st.text_input("Unidade disponível")
                esp_endereco = st.text_input("Endereço")
                esp_interno_externo = st.selectbox("Interno/Externo", ["Interno", "Externo"])
                esp_espaco_disp = st.text_input("Espaço Disp.")

            with col2:
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
                    df_esp = ler_aba_padronizada("Espaços Disponíveis", COLUNAS_ESP)

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
                                "Última Alteração Por": "",
                                "Data da Alteração": "",
                            }
                        ]
                    )

                    df_esp_atualizado = pd.concat([df_esp, novo_espaco], ignore_index=True)
                    df_esp_atualizado = df_esp_atualizado[COLUNAS_ESP]
                    df_esp_atualizado = _preparar_df_para_sheets(df_esp_atualizado)
                    conn.update(spreadsheet=url_planilha, worksheet="Espaços Disponíveis", data=df_esp_atualizado)

                    st.success("Espaço disponível cadastrado com sucesso!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Erro ao salvar na guia 'Espaços Disponíveis': {err}")
                    with st.expander("Detalhes técnicos"):
                        st.code(traceback.format_exc())
    else:
        st.warning("Seu perfil (Leitor) possui permissão apenas para visualização dos dados.")

    st.divider()
    st.subheader("Visualização do Banco de Dados - Espaços Disponíveis")

    try:
        df_esp_view = ler_aba_padronizada("Espaços Disponíveis", COLUNAS_ESP)
    except Exception as e:
        st.error(f"Erro ao ler a aba 'Espaços Disponíveis': {e}")
        df_esp_view = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_ESP})

    if nivel in ["Editor", "Admin", "Con"] and not df_esp_view.empty:
        st.info("Você pode editar qualquer célula diretamente na tabela (exceto 'Cadastrado Por' e colunas de auditoria). Ao terminar, clique em 'Salvar Alterações'.")
        render_editor_com_edicao(
            df_esp_view,
            nome_aba="Espaços Disponíveis",
            colunas_auditoria=["Última Alteração Por", "Data da Alteração"],
            validacoes={"m²": "m2"},
            key_prefix="espacos_disponiveis",
        )
    elif df_esp_view.empty:
        st.info("Nenhum espaço cadastrado ainda.")
    else:
        st.dataframe(df_esp_view, use_container_width=True)

elif aba_selecionada == "👥 Gerenciar Usuários":
    st.title("Gerenciar Usuários")

    if nivel not in ["Admin", "Con"]:
        st.error("Você não tem permissão para acessar esta página.")
        st.stop()

    st.subheader("🟢 Sessões Ativas")
    agora_ts = time.time()

    tokens_ordem = []
    sessoes_ativas = []
    for token, dados in list(SESSOES.items()):
        if agora_ts <= dados.get("expira_em", 0):
            tokens_ordem.append(token)
            sessoes_ativas.append({
                "Encerrar": False,
                "Usuário": dados["usuario"].title(),
                "Nível": dados["nivel"],
                "Expira em": datetime.datetime.fromtimestamp(dados["expira_em"]).strftime("%d/%m/%Y %H:%M:%S"),
            })

    if sessoes_ativas:
        df_sessoes = pd.DataFrame(sessoes_ativas).reset_index(drop=True)
        tabela_sessoes = st.data_editor(
            df_sessoes,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=["Usuário", "Nível", "Expira em"],
            key="editor_sessoes_ativas",
        )

        linhas_marcadas_sessao = tabela_sessoes[tabela_sessoes["Encerrar"] == True]

        if not linhas_marcadas_sessao.empty:
            indices_marcados = linhas_marcadas_sessao.index.tolist()
            usuarios_a_encerrar = [tabela_sessoes.loc[i, "Usuário"] for i in indices_marcados]

            st.warning(
                f"⚠️ {len(indices_marcados)} sessão(ões) selecionada(s) para encerramento: "
                f"{', '.join(usuarios_a_encerrar)}."
            )

            if st.button("🚪 Forçar Logout das Sessões Selecionadas"):
                encerradas = 0
                for idx in indices_marcados:
                    if 0 <= idx < len(tokens_ordem):
                        token_alvo = tokens_ordem[idx]
                        if token_alvo in SESSOES:
                            SESSOES.pop(token_alvo, None)
                            encerradas += 1

                st.success(f"{encerradas} sessão(ões) encerrada(s) com sucesso!")
                st.rerun()
    else:
        st.info("Nenhuma sessão ativa no momento.")

    st.divider()

    st.subheader("📋 Usuários Cadastrados")
    usuarios_atuais = carregar_usuarios()
    lista_usuarios = []
    for user, dados in usuarios_atuais.items():
        eh_secret = user in USUARIOS_SECRETS
        lista_usuarios.append({
            "Usuário": user,
            "Nível": dados.get("nivel", ""),
            "Origem": "Secrets (bootstrap)" if eh_secret else "Planilha",
            "Cadastrado Por": dados.get("cadastrado_por", "") or ("Bootstrap (servidor)" if eh_secret else ""),
            "Data": dados.get("data", ""),
        })
    if lista_usuarios:
        df_usuarios_vis = pd.DataFrame(lista_usuarios)
        df_usuarios_vis = df_usuarios_vis.sort_values(by=["Origem", "Nível", "Usuário"]).reset_index(drop=True)
        st.dataframe(df_usuarios_vis, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum usuário cadastrado.")

    secrets_pendentes = []
    try:
        df_usr_check = ler_aba_padronizada("Usuários", ["Usuário", "Senha", "Nível", "Cadastrado Por", "Data"])
        usuarios_planilha_lower = set(
            df_usr_check["Usuário"].astype(str).str.strip().str.lower().tolist()
        )
        for user_secret, dados_secret in USUARIOS_SECRETS.items():
            if user_secret not in usuarios_planilha_lower:
                secrets_pendentes.append(user_secret)
    except Exception:
        secrets_pendentes = list(USUARIOS_SECRETS.keys())

    if secrets_pendentes:
        st.warning(
            f"⚠️ Existem {len(secrets_pendentes)} usuário(s) apenas no secrets (bootstrap) "
            f"que ainda não estão na planilha: {', '.join(sorted(secrets_pendentes))}."
        )
        if st.button("🔄 Sincronizar Secrets para Planilha"):
            try:
                df_usr_sync = ler_aba_padronizada("Usuários", ["Usuário", "Senha", "Nível", "Cadastrado Por", "Data"])
                usuarios_planilha_lower = set(
                    df_usr_sync["Usuário"].astype(str).str.strip().str.lower().tolist()
                )
                novas_linhas = []
                agora_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                for user_secret, dados_secret in USUARIOS_SECRETS.items():
                    if user_secret in usuarios_planilha_lower:
                        continue
                    novas_linhas.append({
                        "Usuário": user_secret,
                        "Senha": str(dados_secret.get("senha", "")).strip(),
                        "Nível": str(dados_secret.get("nivel", "")).strip(),
                        "Cadastrado Por": "Bootstrap (servidor)",
                        "Data": agora_str,
                    })
                if novas_linhas:
                    df_usr_sync = pd.concat(
                        [df_usr_sync, pd.DataFrame(novas_linhas)],
                        ignore_index=True,
                    )
                    for col_sync in ["Usuário", "Senha", "Nível", "Cadastrado Por", "Data"]:
                        if col_sync not in df_usr_sync.columns:
                            df_usr_sync[col_sync] = ""
                    df_usr_sync = df_usr_sync[["Usuário", "Senha", "Nível", "Cadastrado Por", "Data"]]
                    df_usr_sync = _preparar_df_para_sheets(df_usr_sync)
                    conn.update(spreadsheet=url_planilha, worksheet="Usuários", data=df_usr_sync)
                    st.success(f"{len(novas_linhas)} usuário(s) sincronizado(s) com sucesso!")
                    st.rerun()
                else:
                    st.info("Nada para sincronizar.")
            except Exception as e:
                st.error(f"Erro ao sincronizar secrets com a planilha: {e}")
                with st.expander("Detalhes técnicos"):
                    st.code(traceback.format_exc())
    else:
        st.success("✅ Todos os usuários dos secrets já estão na planilha.")

    st.divider()

    st.subheader("➕ Adicionar Novo Usuário")
    if nivel == "Admin":
        niveis_disponiveis = ["Leitor", "Editor"]
    else:
        niveis_disponiveis = ["Leitor", "Editor", "Admin"]

    with st.form("form_add_usuario", clear_on_submit=True):
        novo_user = st.text_input("Nome de usuário")
        nova_senha = st.text_input("Senha", type="password")
        novo_nivel = st.selectbox("Nível", niveis_disponiveis)
        btn_add = st.form_submit_button("Adicionar Usuário")

    if btn_add:
        user_limpo = novo_user.strip().lower()
        senha_limpa = nova_senha.strip()

        if not user_limpo or not senha_limpa:
            st.error("Usuário e senha são obrigatórios.")
        elif user_limpo in usuarios_atuais:
            st.error(f"O usuário '{user_limpo}' já existe (secrets ou planilha).")
        else:
            try:
                df_usr = ler_aba_padronizada("Usuários", ["Usuário", "Senha", "Nível", "Cadastrado Por", "Data"])
                nova_linha = pd.DataFrame([{
                    "Usuário": user_limpo,
                    "Senha": gerar_hash_senha(senha_limpa),
                    "Nível": novo_nivel,
                    "Cadastrado Por": st.session_state.get("usuario_logado", ""),
                    "Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                }])
                df_usr = pd.concat([df_usr, nova_linha], ignore_index=True)
                for col_add in ["Usuário", "Senha", "Nível", "Cadastrado Por", "Data"]:
                    if col_add not in df_usr.columns:
                        df_usr[col_add] = ""
                df_usr = df_usr[["Usuário", "Senha", "Nível", "Cadastrado Por", "Data"]]
                df_usr = _preparar_df_para_sheets(df_usr)
                conn.update(spreadsheet=url_planilha, worksheet="Usuários", data=df_usr)
                st.success(f"Usuário '{user_limpo}' adicionado com sucesso como {novo_nivel}!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao adicionar usuário: {e}")
                with st.expander("Detalhes técnicos"):
                    st.code(traceback.format_exc())

    st.divider()

    st.subheader("🗑️ Remover Usuário")
    try:
        df_usr_rem = ler_aba_padronizada("Usuários", ["Usuário", "Senha", "Nível", "Cadastrado Por", "Data"])
    except Exception:
        df_usr_rem = pd.DataFrame({c: pd.Series(dtype="object") for c in ["Usuário", "Senha", "Nível", "Cadastrado Por", "Data"]})

    if df_usr_rem.empty:
        st.info("Não há usuários cadastrados na planilha para remover.")
    else:
        usuario_logado_lower = st.session_state.get("usuario_logado", "").strip().lower()
        removiveis = []
        for _, row in df_usr_rem.iterrows():
            user_r = str(row.get("Usuário", "")).strip().lower()
            nivel_r = str(row.get("Nível", "")).strip()
            if not user_r:
                continue
            if user_r == usuario_logado_lower:
                continue
            if nivel == "Admin" and nivel_r in ["Editor", "Leitor"]:
                removiveis.append((user_r, nivel_r))
            elif nivel == "Con" and nivel_r in ["Admin", "Editor", "Leitor"]:
                removiveis.append((user_r, nivel_r))

        if not removiveis:
            st.info("Você não tem permissão para remover nenhum usuário cadastrado na planilha.")
        else:
            opcoes_remover = [f"{u} ({n})" for u, n in removiveis]
            escolha = st.selectbox("Selecione o usuário que deseja remover", opcoes_remover, key="user_remover")
            if st.button("Confirmar Remoção"):
                user_alvo = escolha.split(" (")[0].strip().lower()
                df_usr_final = df_usr_rem[
                    df_usr_rem["Usuário"].astype(str).str.strip().str.lower() != user_alvo
                ]
                df_usr_final = _preparar_df_para_sheets(df_usr_final)
                try:
                    conn.update(spreadsheet=url_planilha, worksheet="Usuários", data=df_usr_final)
                    sessoes_encerradas = encerrar_sessoes_do_usuario(user_alvo)
                    if sessoes_encerradas > 0:
                        st.success(
                            f"Usuário '{user_alvo}' removido com sucesso! "
                            f"{sessoes_encerradas} sessão(ões) ativa(s) encerrada(s) automaticamente."
                        )
                    else:
                        st.success(f"Usuário '{user_alvo}' removido com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao remover usuário: {e}")
                    with st.expander("Detalhes técnicos"):
                        st.code(traceback.format_exc())

elif aba_selecionada == "🎮 Sala Secreta: Jogo da Forca":
    st.title("🕵️‍♂️ Área Secreta - Jogo da Forca")
    st.write("Parabéns por encontrar o modo secreto! Descanse um pouco e jogue uma partida.")

    PALAVRAS_FORCA = ["STREAMLIT", "PYTHON", "GERENTE", "SUBLOCATARIO", "PRESTADOR", "CADASTRO", "SISTEMA", "LOJA", "CONTRATO"]

    if "palavra_secreta" not in st.session_state:
        st.session_state["palavra_secreta"] = random.choice(PALAVRAS_FORCA)
        st.session_state["letras_chutadas"] = []
        st.session_state["tentativas_restantes"] = 6

    def reiniciar_jogo():
        st.session_state["palavra_secreta"] = random.choice(PALAVRAS_FORCA)
        st.session_state["letras_chutadas"] = []
        st.session_state["tentativas_restantes"] = 6

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
        palavra_exibida = "".join([letra if letra in st.session_state["letras_chutadas"] else " _ " for letra in st.session_state["palavra_secreta"]])
        st.subheader(f"Palavra: {palavra_exibida}")
        st.write(f"Tentativas restantes: **{st.session_state['tentativas_restantes']}**")
        st.write(f"Letras já tentadas: {', '.join(st.session_state['letras_chutadas'])}")

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

elif aba_selecionada == "🐍 Sala Secreta: Jogo da Cobrinha":
    st.title("🐍 Área Secreta - Jogo da Cobrinha")
    st.write(
        "Você desbloqueou o segundo modo secreto! Use as setas ⬆ ⬇ ⬅ ➡ do teclado "
        "para jogar. Se as setas não responderem, clique uma vez sobre o tabuleiro "
        "para dar foco ao jogo."
    )

    SNAKE_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  * { box-sizing: border-box; }
  html, body {
    background: #341539;
    color: #FFD80F;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    margin: 0;
    padding: 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100%;
  }
  h2 { color: #FFD80F; margin: 0 0 12px 0; }
  canvas {
    background: #262730;
    border: 2px solid #FFD80F;
    border-radius: 8px;
    display: block;
    outline: none;
    cursor: pointer;
  }
  .info { color: #FFD80F; margin-top: 12px; font-weight: bold; }
  .status { color: #FFD80F; margin-top: 6px; font-size: 14px; text-align: center; }
  button {
    background: #FFD80F;
    color: #000;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    margin-top: 14px;
    font-size: 14px;
  }
  button:hover { background: #7B2CBF; color: #FFF; }
</style>
</head>
<body>
  <h2>🐍 Jogo da Cobrinha</h2>
  <canvas id="game" width="400" height="400" tabindex="0"></canvas>
  <div class="info">Pontos: <span id="score">0</span> &nbsp;|&nbsp; Recorde desta sessão: <span id="high">0</span></div>
  <div class="status" id="status">Use as setas ⬆ ⬇ ⬅ ➡ para jogar</div>
  <button onclick="resetGame()">🔄 Reiniciar</button>

  <script>
  (function () {
    const canvas = document.getElementById('game');
    const ctx = canvas.getContext('2d');
    const box = 20;
    const cols = canvas.width / box;
    const rows = canvas.height / box;

    const INTERVALO_LENTO = 300;
    const INTERVALO_RAPIDO = 30;
    const PONTOS_POR_ACELERACAO = 1;
    const PASSO_ACELERACAO_MS = 10;

    let snake, dir, nextDir, food, score, high, gameOver, timeoutId;

    high = 0;
    document.getElementById('high').textContent = high;

    function getIntervaloAtual() {
      const reduzido = Math.floor(score / PONTOS_POR_ACELERACAO) * PASSO_ACELERACAO_MS;
      const intervalo = INTERVALO_LENTO - reduzido;
      return Math.max(INTERVALO_RAPIDO, intervalo);
    }

    function scheduleTick() {
      if (timeoutId) clearTimeout(timeoutId);
      timeoutId = setTimeout(function () {
        tick();
        if (!gameOver) scheduleTick();
      }, getIntervaloAtual());
    }

    function placeFood() {
      let attempts = 0;
      do {
        food = {
          x: Math.floor(Math.random() * cols),
          y: Math.floor(Math.random() * rows)
        };
        attempts++;
      } while (snake.some(s => s.x === food.x && s.y === food.y) && attempts < 500);
    }

    function resetGame() {
      snake = [{x: 5, y: 5}, {x: 4, y: 5}, {x: 3, y: 5}];
      dir = {x: 1, y: 0};
      nextDir = {x: 1, y: 0};
      score = 0;
      gameOver = false;
      document.getElementById('score').textContent = '0';
      document.getElementById('status').textContent = 'Use as setas ⬆ ⬇ ⬅ ➡ para jogar';
      placeFood();
      if (timeoutId) clearTimeout(timeoutId);
      draw();
      scheduleTick();
      canvas.focus();
    }

    function tick() {
      if (gameOver) return;
      dir = nextDir;

      const head = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};

      if (
        head.x < 0 || head.x >= cols ||
        head.y < 0 || head.y >= rows ||
        snake.some(s => s.x === head.x && s.y === head.y)
      ) {
        gameOver = true;
        if (score > high) {
          high = score;
          document.getElementById('high').textContent = high;
        }
        document.getElementById('status').textContent =
          '☠️ Game Over! Pontuação final: ' + score;
        return;
      }

      snake.unshift(head);

      if (head.x === food.x && head.y === food.y) {
        score++;
        document.getElementById('score').textContent = score;
        placeFood();
      } else {
        snake.pop();
      }

      draw();
    }

    function draw() {
      ctx.fillStyle = '#262730';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = 'rgba(255, 216, 15, 0.08)';
      ctx.lineWidth = 1;
      for (let i = 0; i <= cols; i++) {
        ctx.beginPath();
        ctx.moveTo(i * box + 0.5, 0);
        ctx.lineTo(i * box + 0.5, canvas.height);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, i * box + 0.5);
        ctx.lineTo(canvas.width, i * box + 0.5);
        ctx.stroke();
      }

      ctx.fillStyle = '#7B2CBF';
      ctx.beginPath();
      ctx.arc(food.x * box + box / 2, food.y * box + box / 2, box / 2 - 2, 0, Math.PI * 2);
      ctx.fill();

      snake.forEach((s, i) => {
        if (i === 0) {
          ctx.fillStyle = '#FFD80F';
        } else {
          const alpha = 0.55 + 0.4 * (1 - i / Math.max(1, snake.length));
          ctx.fillStyle = 'rgba(255, 216, 15, ' + alpha + ')';
        }
        ctx.fillRect(s.x * box + 1, s.y * box + 1, box - 2, box - 2);
      });
    }

    window.addEventListener('keydown', function (e) {
      const k = e.key;
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].indexOf(k) !== -1) {
        e.preventDefault();
      }
      if (k === 'ArrowUp' && dir.y === 0) nextDir = {x: 0, y: -1};
      else if (k === 'ArrowDown' && dir.y === 0) nextDir = {x: 0, y: 1};
      else if (k === 'ArrowLeft' && dir.x === 0) nextDir = {x: -1, y: 0};
      else if (k === 'ArrowRight' && dir.x === 0) nextDir = {x: 1, y: 0};
    });

    canvas.addEventListener('click', function () { canvas.focus(); });
    window.addEventListener('load', function () { canvas.focus(); });

    resetGame();
  })();
  </script>
</body>
</html>
"""

    components.html(SNAKE_HTML, height=620, scrolling=False)
