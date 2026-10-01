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
import uuid
import re
import io
import base64
import threading
import unicodedata

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

try:
    import altair as alt
except Exception:
    alt = None

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from googleapiclient.errors import HttpError
    DRIVE_LIBS_AVAILABLE = True
except Exception:
    Credentials = None
    Request = None
    build = None
    MediaIoBaseUpload = None
    HttpError = Exception
    DRIVE_LIBS_AVAILABLE = False

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
        background-color: #1E0A22;
        color: #FFD80F;
        text-align: center;
        padding: 12px 20px;
        font-size: 12px;
        font-weight: bold;
        border-top: 1px solid #FFD80F;
        border-radius: 8px;
        margin-top: 80px;
        margin-bottom: 20px;
    }
    </style>
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

def registrar_log(acao, detalhe=""):
    try:
        df_logs = ler_aba_padronizada("Logs", ["Data/Hora", "Usuário", "Nível", "Ação", "Detalhe"])
        agora_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        usuario_log = st.session_state.get("usuario_logado", "") or "—"
        nivel_log = st.session_state.get("nivel_acesso", "") or "—"
        nova_linha = pd.DataFrame([{
            "Data/Hora": agora_str,
            "Usuário": usuario_log,
            "Nível": nivel_log,
            "Ação": acao,
            "Detalhe": str(detalhe),
        }])
        df_logs = pd.concat([df_logs, nova_linha], ignore_index=True)
        for col_log in ["Data/Hora", "Usuário", "Nível", "Ação", "Detalhe"]:
            if col_log not in df_logs.columns:
                df_logs[col_log] = ""
        df_logs = df_logs[["Data/Hora", "Usuário", "Nível", "Ação", "Detalhe"]]
        df_logs = _preparar_df_para_sheets(df_logs)
        conn.update(spreadsheet=url_planilha, worksheet="Logs", data=df_logs)
    except Exception:
        pass

def _previa_linha_para_confirmacao(row, colunas_chave):
    partes = []
    for col in colunas_chave:
        if col in row.index:
            valor = str(row[col]).strip()
            if valor and valor.lower() != "none":
                partes.append(f"{col}: {valor}")
    if not partes:
        return "(linha sem dados visíveis)"
    return " | ".join(partes[:3])

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

    chave_confirmacao = f"confirmacao_exclusao_{key_prefix}"

    if indices_alterados:
        st.warning(f"⚠️ Você tem {len(indices_alterados)} linha(s) com alterações não salvas. Clique em 'Salvar Alterações' para aplicar.")

    col_btn1, col_btn2 = st.columns([1, 1])

    with col_btn1:
        if st.button("💾 Salvar Alterações", key=f"salvar_{key_prefix}"):
            if chave_confirmacao in st.session_state:
                del st.session_state[chave_confirmacao]

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
                    st.session_state[chave_confirmacao] = {
                        "indices": list(indices_excluir),
                        "df_congelado": df_original.copy(),
                    }
                    st.rerun()

    if chave_confirmacao in st.session_state and st.session_state[chave_confirmacao]:
        dados_pendentes = st.session_state[chave_confirmacao]
        indices_pendentes = dados_pendentes.get("indices", [])
        df_congelado = dados_pendentes.get("df_congelado", pd.DataFrame())

        if indices_pendentes:
            st.markdown("---")
            st.error(
                f"⚠️ **Confirmação de Exclusão** — Você está prestes a remover "
                f"**{len(indices_pendentes)} registro(s)** de `{nome_aba}`. "
                f"Esta ação **não pode ser desfeita**."
            )

            st.write("**Registros que serão removidos:**")
            colunas_chave = [c for c in df_congelado.columns if c not in colunas_auditoria][:4]

            for idx in indices_pendentes:
                if idx < len(df_congelado):
                    linha = df_congelado.iloc[idx]
                    previa = _previa_linha_para_confirmacao(linha, colunas_chave)
                    st.write(f"- **Linha {idx + 1}:** {previa}")

            st.write("")

            col_c1, col_c2 = st.columns([1, 1])

            with col_c1:
                if st.button("✅ Confirmar Exclusão Definitiva", key=f"confirma_remocao_{key_prefix}"):
                    df_final = df_congelado.drop(index=indices_pendentes, errors="ignore").reset_index(drop=True)

                    for col in df_final.columns:
                        df_final[col] = df_final[col].astype("object")

                    df_final = _preparar_df_para_sheets(df_final)

                    try:
                        conn.update(spreadsheet=url_planilha, worksheet=nome_aba, data=df_final)
                        if chave_confirmacao in st.session_state:
                            del st.session_state[chave_confirmacao]
                        st.success(f"{len(indices_pendentes)} registro(s) removido(s) com sucesso!")
                        st.rerun()
                    except Exception as ex_del:
                        st.error(f"Erro ao excluir na planilha: {ex_del}")
                        with st.expander("Detalhes técnicos do erro"):
                            st.code(traceback.format_exc())

            with col_c2:
                if st.button("❌ Cancelar Exclusão", key=f"cancela_remocao_{key_prefix}"):
                    if chave_confirmacao in st.session_state:
                        del st.session_state[chave_confirmacao]
                    st.info("Exclusão cancelada. Nenhum registro foi removido.")
                    st.rerun()


# ==============================================================================
# MÓDULO: ANDAMENTO DE ENCERRAMENTOS
# ==============================================================================

COLUNAS_ENCERRAMENTOS = [
    "UUID Processo",
    "ID Processo",
    "Tipo Processo",
    "Loja",
    "Apelidos da Loja",
    "Data de Criação",
    "Notificação",
    "Data do envio da notificação",
    "Data do fechamento",
    "Contagem mercadoria",
    "Data da contagem",
    "Retirada mercadoria",
    "Data da retirada",
    "Desmobilização",
    "Data da desmobilização",
    "Retirada da fachada / comunicação visual",
    "Data da retirada da com. visual",
    "Contas de consumo",
    "Data do envio das contas de consumo",
    "Vistoria de devolução",
    "Data da vistoria de devolução",
    "Entrega das chaves",
    "Data da entrega das chaves",
    "Orçamentos enviados?",
    "Adequações",
    "Distrato contas a pagar",
    "Data do envio para o contas a pagar",
    "Distrato jurídico",
    "Data do envio para o jurídico",
    "Distrato aprovação",
    "Data do envio do distrato para aprovação",
    "Distrato",
    "Contas pagamento",
    "Data do envio da solicitação de pagamento para o contas a pagar",
    "Para legal baixa no CNPJ",
    "Próximo passo / observações",
    "Estado do processo",
    "Data de conclusão",
    "Data de arquivamento",
    "Arquivado por",
    "Motivo do arquivamento",
    "Cadastrado Por",
    "Última Alteração Por",
    "Data da Alteração",
]

COLUNAS_HISTORICO_ENC = [
    "ID Histórico",
    "UUID Processo",
    "ID Processo",
    "Loja",
    "Data/Hora",
    "Usuário",
    "Nível",
    "Tipo de ação",
    "Campo alterado",
    "Valor anterior",
    "Valor novo",
    "Detalhe",
]

COLUNAS_DOCUMENTOS_ENC = [
    "UUID Documento",
    "ID Documento",
    "UUID Processo",
    "ID Processo",
    "Loja",
    "Categoria",
    "Descrição",
    "Nome original",
    "Drive File ID",
    "SHA-256",
    "Data do envio",
    "Enviado Por",
    "Tamanho (bytes)",
    "Tipo MIME",
    "Estado Documento",
    "Excluído por",
    "Data da exclusão",
]

COLUNAS_CONTROLE_SISTEMA = [
    "Chave",
    "Valor",
    "Atualizado em",
    "Atualizado por",
]

STATUS_ETAPAS_ENC = {
    "Notificação": {
        "opcoes": ["Pendente", "Enviada"],
        "terminais": {"Enviada"},
    },
    "Contagem mercadoria": {
        "opcoes": ["Pendente", "Agendado", "Concluído"],
        "terminais": {"Concluído"},
    },
    "Retirada mercadoria": {
        "opcoes": ["Pendente", "Agendado", "Concluído"],
        "terminais": {"Concluído"},
    },
    "Desmobilização": {
        "opcoes": ["Pendente", "Agendado", "Concluído"],
        "terminais": {"Concluído"},
    },
    "Retirada da fachada / comunicação visual": {
        "opcoes": ["Pendente", "Agendado", "Concluído"],
        "terminais": {"Concluído"},
    },
    "Contas de consumo": {
        "opcoes": ["Pendente", "Agendado", "Concluído"],
        "terminais": {"Concluído"},
    },
    "Vistoria de devolução": {
        "opcoes": ["Pendente", "Agendado", "Concluído"],
        "terminais": {"Concluído"},
    },
    "Entrega das chaves": {
        "opcoes": ["Pendente", "Agendado", "Concluído"],
        "terminais": {"Concluído"},
    },
    "Adequações": {
        "opcoes": ["Pendente", "Agendado", "Concluído", "Não se aplica"],
        "terminais": {"Concluído", "Não se aplica"},
        "nao_se_aplica": True,
    },
    "Distrato contas a pagar": {
        "opcoes": ["Pendente", "Agendado", "Enviado"],
        "terminais": {"Enviado"},
    },
    "Distrato jurídico": {
        "opcoes": ["Pendente", "Enviado", "Concluído"],
        "terminais": {"Concluído"},
    },
    "Distrato aprovação": {
        "opcoes": ["Pendente", "Enviado", "Aprovado"],
        "terminais": {"Aprovado"},
    },
    "Distrato": {
        "opcoes": ["Pendente", "Enviado", "Assinado"],
        "terminais": {"Assinado"},
    },
    "Contas pagamento": {
        "opcoes": ["Pendente", "Enviado", "Pago"],
        "terminais": {"Pago"},
    },
    "Para legal baixa no CNPJ": {
        "opcoes": ["Pendente", "Enviado", "Baixado"],
        "terminais": {"Baixado"},
    },
}

# Data obrigatória quando a etapa chega a estes status.
REGRAS_DATA_ENC = {
    "Notificação": ("Data do envio da notificação", {"Enviada"}),
    "Contagem mercadoria": ("Data da contagem", {"Agendado", "Concluído"}),
    "Retirada mercadoria": ("Data da retirada", {"Agendado", "Concluído"}),
    "Desmobilização": ("Data da desmobilização", {"Agendado", "Concluído"}),
    "Retirada da fachada / comunicação visual": (
        "Data da retirada da com. visual", {"Agendado", "Concluído"}
    ),
    "Contas de consumo": (
        "Data do envio das contas de consumo", {"Agendado", "Concluído"}
    ),
    "Vistoria de devolução": (
        "Data da vistoria de devolução", {"Agendado", "Concluído"}
    ),
    "Entrega das chaves": (
        "Data da entrega das chaves", {"Agendado", "Concluído"}
    ),
    "Distrato contas a pagar": (
        "Data do envio para o contas a pagar", {"Agendado", "Enviado"}
    ),
    "Distrato jurídico": (
        "Data do envio para o jurídico", {"Enviado", "Concluído"}
    ),
    "Distrato aprovação": (
        "Data do envio do distrato para aprovação", {"Enviado", "Aprovado"}
    ),
    "Contas pagamento": (
        "Data do envio da solicitação de pagamento para o contas a pagar", {"Enviado", "Pago"}
    ),
}

PERMISSOES_DOCUMENTOS = {
    "Leitor": {"visualizar": True, "enviar": False, "baixar": False, "excluir": False},
    "Editor": {"visualizar": True, "enviar": True, "baixar": True, "excluir": False},
    "Admin": {"visualizar": True, "enviar": True, "baixar": True, "excluir": True},
    "Con": {"visualizar": True, "enviar": True, "baixar": True, "excluir": True},
}

CATEGORIAS_DOCUMENTOS_ENC = [
    "Contrato",
    "Notificação",
    "Vistoria de entrada",
    "Vistoria de devolução",
    "Entrega das chaves",
    "Contagem de mercadoria",
    "Retirada de mercadoria",
    "Comunicação visual",
    "Contas de consumo",
    "Adequações",
    "Distrato",
    "Jurídico",
    "Financeiro / Pagamento",
    "Baixa CNPJ",
    "Outros",
]

MAX_PDF_MB = 30
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
ID_PROCESSO_LOCK = threading.Lock()


def _texto_limpo(valor):
    if valor is None or pd.isna(valor):
        return ""
    texto = str(valor).strip()
    if texto.lower() in {"none", "nan", "nat"}:
        return ""
    return texto


def _normalizar_texto(valor):
    texto = unicodedata.normalize("NFKD", _texto_limpo(valor))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def _formatar_data(valor):
    if valor is None or valor == "":
        return ""
    if isinstance(valor, datetime.datetime):
        valor = valor.date()
    if isinstance(valor, datetime.date):
        return valor.strftime("%d/%m/%Y")
    return _texto_limpo(valor)


def _parse_data(valor):
    texto = _texto_limpo(valor)
    if not texto:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    try:
        convertido = pd.to_datetime(texto, dayfirst=True, errors="coerce")
        if pd.notna(convertido):
            return convertido.date()
    except Exception:
        pass
    return None


def _data_input_opcional(label, valor_atual, key, disabled=False, help_text=None):
    valor = _parse_data(valor_atual)
    return st.date_input(
        label,
        value=valor,
        format="DD/MM/YYYY",
        key=key,
        disabled=disabled,
        help=help_text,
    )


def _indice_status(campo, valor):
    opcoes = STATUS_ETAPAS_ENC[campo]["opcoes"]
    valor = _texto_limpo(valor)
    return opcoes.index(valor) if valor in opcoes else 0


def _separar_apelidos(valor):
    if not _texto_limpo(valor):
        return []
    partes = re.split(r"[;\n,]+", _texto_limpo(valor))
    return [p.strip() for p in partes if p.strip()]


def _juntar_apelidos(valor):
    if isinstance(valor, (list, tuple, set)):
        itens = [str(v).strip() for v in valor if str(v).strip()]
    else:
        itens = _separar_apelidos(valor)
    # remove duplicatas mantendo ordem
    vistos = set()
    saida = []
    for item in itens:
        norm = _normalizar_texto(item)
        if norm and norm not in vistos:
            vistos.add(norm)
            saida.append(item)
    return "; ".join(saida)


def _opcao_documento_permitida(acao):
    nivel_atual = st.session_state.get("nivel_acesso", "Leitor")
    return bool(PERMISSOES_DOCUMENTOS.get(nivel_atual, {}).get(acao, False))


def _obter_df_encerramentos():
    return ler_aba_padronizada("Encerramentos", COLUNAS_ENCERRAMENTOS)


def _obter_processo_por_uuid(uuid_processo, df=None):
    if df is None:
        df = _obter_df_encerramentos()
    if df.empty:
        return None, None
    mascara = df["UUID Processo"].astype(str).str.strip() == str(uuid_processo).strip()
    indices = df.index[mascara].tolist()
    if not indices:
        return None, None
    idx = indices[0]
    return idx, df.loc[idx].copy()


def _maior_sequencia_existente(prefixo, df_enc=None):
    if df_enc is None:
        df_enc = _obter_df_encerramentos()
    maior = 0
    if df_enc.empty or "ID Processo" not in df_enc.columns:
        return maior
    padrao = re.compile(rf"^{re.escape(prefixo.upper())}-\d{{4}}-(\d+)$")
    for valor in df_enc["ID Processo"].astype(str):
        m = padrao.match(valor.strip().upper())
        if m:
            maior = max(maior, int(m.group(1)))
    return maior


def gerar_id_processo(prefixo="ENC"):
    """Gera PREFIXO-ANO-SEQUÊNCIA. A sequência é contínua e independente por prefixo."""
    prefixo = str(prefixo).strip().upper()
    if not re.fullmatch(r"[A-Z]{2,6}", prefixo):
        raise ValueError("Prefixo de processo inválido.")

    with ID_PROCESSO_LOCK:
        df_enc = _obter_df_encerramentos()
        maior_existente = _maior_sequencia_existente(prefixo, df_enc)

        df_ctrl = ler_aba_padronizada("Controle do Sistema", COLUNAS_CONTROLE_SISTEMA)
        chave = f"SEQ_{prefixo}"
        valor_ctrl = 0
        idx_ctrl = None

        if not df_ctrl.empty:
            mascara = df_ctrl["Chave"].astype(str).str.strip().str.upper() == chave
            indices = df_ctrl.index[mascara].tolist()
            if indices:
                idx_ctrl = indices[0]
                try:
                    valor_ctrl = int(float(_texto_limpo(df_ctrl.at[idx_ctrl, "Valor"]) or 0))
                except Exception:
                    valor_ctrl = 0

        proximo = max(maior_existente, valor_ctrl) + 1
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        usuario = st.session_state.get("usuario_logado", "")

        if idx_ctrl is None:
            nova = pd.DataFrame([{
                "Chave": chave,
                "Valor": str(proximo),
                "Atualizado em": agora,
                "Atualizado por": usuario,
            }])
            df_ctrl = pd.concat([df_ctrl, nova], ignore_index=True)
        else:
            df_ctrl.at[idx_ctrl, "Valor"] = str(proximo)
            df_ctrl.at[idx_ctrl, "Atualizado em"] = agora
            df_ctrl.at[idx_ctrl, "Atualizado por"] = usuario

        try:
            conn.update(
                spreadsheet=url_planilha,
                worksheet="Controle do Sistema",
                data=_preparar_df_para_sheets(df_ctrl[COLUNAS_CONTROLE_SISTEMA]),
            )
        except Exception as exc:
            raise RuntimeError(
                "Não foi possível atualizar a aba 'Controle do Sistema'. "
                "Confirme se ela existe com as colunas corretas."
            ) from exc

        ano = datetime.date.today().year
        return f"{prefixo}-{ano}-{proximo:06d}"


def _linha_historico(processo, tipo_acao, campo="", valor_anterior="", valor_novo="", detalhe=""):
    return {
        "ID Histórico": str(uuid.uuid4()),
        "UUID Processo": _texto_limpo(processo.get("UUID Processo", "")),
        "ID Processo": _texto_limpo(processo.get("ID Processo", "")),
        "Loja": _texto_limpo(processo.get("Loja", "")),
        "Data/Hora": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Usuário": st.session_state.get("usuario_logado", "") or "—",
        "Nível": st.session_state.get("nivel_acesso", "") or "—",
        "Tipo de ação": tipo_acao,
        "Campo alterado": campo,
        "Valor anterior": _texto_limpo(valor_anterior),
        "Valor novo": _texto_limpo(valor_novo),
        "Detalhe": detalhe,
    }


def registrar_historico_encerramento(processo, eventos):
    """eventos: lista de dicts com tipo_acao/campo/valor_anterior/valor_novo/detalhe."""
    if not eventos:
        return
    try:
        df_hist = ler_aba_padronizada("Histórico Encerramentos", COLUNAS_HISTORICO_ENC)
        linhas = []
        for evento in eventos:
            linhas.append(_linha_historico(
                processo,
                evento.get("tipo_acao", "Alteração"),
                evento.get("campo", ""),
                evento.get("valor_anterior", ""),
                evento.get("valor_novo", ""),
                evento.get("detalhe", ""),
            ))
        df_hist = pd.concat([df_hist, pd.DataFrame(linhas)], ignore_index=True)
        df_hist = df_hist[COLUNAS_HISTORICO_ENC]
        conn.update(
            spreadsheet=url_planilha,
            worksheet="Histórico Encerramentos",
            data=_preparar_df_para_sheets(df_hist),
        )
    except Exception as exc:
        registrar_log(
            "Falha histórico encerramento",
            f"{_texto_limpo(processo.get('ID Processo', ''))}: {exc}",
        )
        st.warning(
            "A alteração foi salva, mas não foi possível registrar o histórico detalhado. "
            "Verifique a aba 'Histórico Encerramentos'."
        )


def validar_consistencia_encerramento(row):
    erros = []
    if not _texto_limpo(row.get("Loja", "")):
        erros.append("O campo 'Loja' é obrigatório.")
    if not _texto_limpo(row.get("Data do fechamento", "")):
        erros.append("A 'Data do fechamento' é obrigatória.")

    for campo_status, (campo_data, status_que_exigem_data) in REGRAS_DATA_ENC.items():
        status = _texto_limpo(row.get(campo_status, ""))
        data_val = _texto_limpo(row.get(campo_data, ""))
        if status in status_que_exigem_data and not data_val:
            erros.append(f"'{campo_data}' é obrigatória quando '{campo_status}' está como '{status}'.")
    return erros


def calcular_progresso_encerramento(row):
    total = 0
    finalizadas = 0
    pendentes = 0
    andamento = 0

    for campo, regra in STATUS_ETAPAS_ENC.items():
        status = _texto_limpo(row.get(campo, "")) or "Pendente"
        if campo == "Adequações" and status == "Não se aplica":
            continue

        total += 1
        if status in regra["terminais"]:
            finalizadas += 1
        elif status == "Pendente":
            pendentes += 1
        else:
            andamento += 1

    percentual = (finalizadas / total * 100) if total else 100.0
    return {
        "total": total,
        "finalizadas": finalizadas,
        "pendentes": pendentes,
        "andamento": andamento,
        "percentual": percentual,
    }


def processo_pronto_para_concluir(row):
    for campo, regra in STATUS_ETAPAS_ENC.items():
        status = _texto_limpo(row.get(campo, "")) or "Pendente"
        if campo == "Adequações" and status == "Não se aplica":
            continue
        if status not in regra["terminais"]:
            return False
    return len(validar_consistencia_encerramento(row)) == 0


def _salvar_df_encerramentos(df):
    df = df[COLUNAS_ENCERRAMENTOS]
    conn.update(
        spreadsheet=url_planilha,
        worksheet="Encerramentos",
        data=_preparar_df_para_sheets(df),
    )


def salvar_alteracoes_encerramento(uuid_processo, alteracoes, detalhe_acao="Atualização do acompanhamento"):
    df = _obter_df_encerramentos()
    idx, original = _obter_processo_por_uuid(uuid_processo, df)
    if idx is None:
        return False, "Processo não encontrado. Atualize a página e tente novamente."

    if _texto_limpo(original.get("Estado do processo", "Ativo")) != "Ativo":
        return False, "Somente processos ativos podem ser alterados no Acompanhamento."

    novo = original.copy()
    eventos = []
    for campo, valor in alteracoes.items():
        if campo not in df.columns:
            continue
        if isinstance(valor, (datetime.date, datetime.datetime)):
            valor = _formatar_data(valor)
        elif campo == "Apelidos da Loja":
            valor = _juntar_apelidos(valor)
        else:
            valor = _texto_limpo(valor)

        anterior = original.get(campo, "")
        if _valor_mudou(anterior, valor):
            novo[campo] = valor
            eventos.append({
                "tipo_acao": "Alteração",
                "campo": campo,
                "valor_anterior": anterior,
                "valor_novo": valor,
                "detalhe": detalhe_acao,
            })

    if not eventos:
        return False, "Nenhuma alteração foi detectada."

    erros = validar_consistencia_encerramento(novo)
    if erros:
        return False, "\n".join(erros)

    usuario = st.session_state.get("usuario_logado", "")
    agora = datetime.datetime.now()
    novo["Última Alteração Por"] = usuario
    novo["Data da Alteração"] = agora.strftime("%d/%m/%Y %H:%M")

    concluiu_agora = False
    if processo_pronto_para_concluir(novo):
        novo["Estado do processo"] = "Concluído"
        novo["Data de conclusão"] = agora.strftime("%d/%m/%Y %H:%M")
        concluiu_agora = True
        eventos.append({
            "tipo_acao": "Conclusão automática",
            "campo": "Estado do processo",
            "valor_anterior": original.get("Estado do processo", "Ativo"),
            "valor_novo": "Concluído",
            "detalhe": "Todas as etapas obrigatórias atingiram seus estados finais.",
        })

    for campo in df.columns:
        df.at[idx, campo] = novo.get(campo, "")

    try:
        _salvar_df_encerramentos(df)
    except Exception as exc:
        return False, f"Erro ao salvar no Google Sheets: {exc}"

    registrar_historico_encerramento(novo, eventos)
    registrar_log("Atualizou encerramento", f"{novo.get('ID Processo')} — {novo.get('Loja')}")

    if concluiu_agora:
        return True, (
            f"Alterações salvas. O processo {novo.get('ID Processo')} foi concluído automaticamente "
            "porque todas as etapas obrigatórias foram finalizadas."
        )
    return True, "Alterações salvas com sucesso."


def criar_novo_encerramento(loja, apelidos, data_fechamento, notificacao, data_notificacao, observacoes):
    loja = _texto_limpo(loja)
    if not loja:
        return False, "Informe a loja.", None
    if data_fechamento is None:
        return False, "Informe a data do fechamento.", None
    if notificacao == "Enviada" and data_notificacao is None:
        return False, "Informe a data do envio da notificação.", None

    try:
        id_processo = gerar_id_processo("ENC")
    except Exception as exc:
        return False, str(exc), None

    uuid_processo = str(uuid.uuid4())
    agora = datetime.datetime.now()
    usuario = st.session_state.get("usuario_logado", "")

    registro = {c: "" for c in COLUNAS_ENCERRAMENTOS}
    registro.update({
        "UUID Processo": uuid_processo,
        "ID Processo": id_processo,
        "Tipo Processo": "ENC",
        "Loja": loja,
        "Apelidos da Loja": _juntar_apelidos(apelidos),
        "Data de Criação": agora.strftime("%d/%m/%Y %H:%M"),
        "Notificação": notificacao,
        "Data do envio da notificação": _formatar_data(data_notificacao),
        "Data do fechamento": _formatar_data(data_fechamento),
        "Contagem mercadoria": "Pendente",
        "Retirada mercadoria": "Pendente",
        "Desmobilização": "Pendente",
        "Retirada da fachada / comunicação visual": "Pendente",
        "Contas de consumo": "Pendente",
        "Vistoria de devolução": "Pendente",
        "Entrega das chaves": "Pendente",
        "Adequações": "Pendente",
        "Distrato contas a pagar": "Pendente",
        "Distrato jurídico": "Pendente",
        "Distrato aprovação": "Pendente",
        "Distrato": "Pendente",
        "Contas pagamento": "Pendente",
        "Para legal baixa no CNPJ": "Pendente",
        "Próximo passo / observações": _texto_limpo(observacoes),
        "Estado do processo": "Ativo",
        "Cadastrado Por": usuario,
        "Última Alteração Por": "",
        "Data da Alteração": "",
    })

    erros = validar_consistencia_encerramento(registro)
    if erros:
        return False, "\n".join(erros), None

    df = _obter_df_encerramentos()
    df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    try:
        _salvar_df_encerramentos(df)
    except Exception as exc:
        return False, (
            "Não foi possível salvar na aba 'Encerramentos'. "
            f"Confirme se ela existe com as colunas corretas. Detalhes: {exc}"
        ), None

    registrar_historico_encerramento(registro, [{
        "tipo_acao": "Criação",
        "campo": "Estado do processo",
        "valor_anterior": "",
        "valor_novo": "Ativo",
        "detalhe": "Processo de encerramento criado.",
    }])
    registrar_log("Criou encerramento", f"{id_processo} — {loja}")
    return True, f"Encerramento {id_processo} criado com sucesso.", registro


def arquivar_encerramento(uuid_processo, motivo):
    motivo = _texto_limpo(motivo)
    if not motivo:
        return False, "O motivo do arquivamento é obrigatório."

    df = _obter_df_encerramentos()
    idx, processo = _obter_processo_por_uuid(uuid_processo, df)
    if idx is None:
        return False, "Processo não encontrado."
    if _texto_limpo(processo.get("Estado do processo")) != "Ativo":
        return False, "Somente processos ativos podem ser arquivados."

    usuario = st.session_state.get("usuario_logado", "")
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    anterior = processo.copy()

    df.at[idx, "Estado do processo"] = "Arquivado"
    df.at[idx, "Data de arquivamento"] = agora
    df.at[idx, "Arquivado por"] = usuario
    df.at[idx, "Motivo do arquivamento"] = motivo
    df.at[idx, "Última Alteração Por"] = usuario
    df.at[idx, "Data da Alteração"] = agora

    try:
        _salvar_df_encerramentos(df)
    except Exception as exc:
        return False, f"Erro ao arquivar: {exc}"

    processo_novo = df.loc[idx].copy()
    registrar_historico_encerramento(processo_novo, [{
        "tipo_acao": "Arquivamento",
        "campo": "Estado do processo",
        "valor_anterior": anterior.get("Estado do processo", "Ativo"),
        "valor_novo": "Arquivado",
        "detalhe": motivo,
    }])
    registrar_log("Arquivou encerramento", f"{processo_novo.get('ID Processo')} — {motivo}")
    return True, "Processo arquivado com sucesso."


def restaurar_ou_reabrir_encerramento(uuid_processo):
    if st.session_state.get("nivel_acesso") not in ["Admin", "Con"]:
        return False, "Somente Admin/Con podem restaurar ou reabrir processos."

    df = _obter_df_encerramentos()
    idx, processo = _obter_processo_por_uuid(uuid_processo, df)
    if idx is None:
        return False, "Processo não encontrado."

    estado_anterior = _texto_limpo(processo.get("Estado do processo"))
    if estado_anterior not in ["Concluído", "Arquivado"]:
        return False, "Este processo já está ativo."

    usuario = st.session_state.get("usuario_logado", "")
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    df.at[idx, "Estado do processo"] = "Ativo"
    df.at[idx, "Última Alteração Por"] = usuario
    df.at[idx, "Data da Alteração"] = agora

    if estado_anterior == "Concluído":
        df.at[idx, "Data de conclusão"] = ""
        tipo = "Reabertura"
    else:
        df.at[idx, "Data de arquivamento"] = ""
        df.at[idx, "Arquivado por"] = ""
        df.at[idx, "Motivo do arquivamento"] = ""
        tipo = "Restauração"

    try:
        _salvar_df_encerramentos(df)
    except Exception as exc:
        return False, f"Erro ao restaurar/reabrir: {exc}"

    processo_novo = df.loc[idx].copy()
    registrar_historico_encerramento(processo_novo, [{
        "tipo_acao": tipo,
        "campo": "Estado do processo",
        "valor_anterior": estado_anterior,
        "valor_novo": "Ativo",
        "detalhe": f"{tipo} manual por Admin/Con.",
    }])
    registrar_log(tipo + " de encerramento", f"{processo_novo.get('ID Processo')}")
    return True, "Processo devolvido ao acompanhamento ativo."


def render_historico_processo(uuid_processo):
    try:
        df_hist = ler_aba_padronizada("Histórico Encerramentos", COLUNAS_HISTORICO_ENC)
    except Exception:
        df_hist = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUNAS_HISTORICO_ENC})

    if df_hist.empty:
        st.info("Ainda não há histórico registrado para este processo.")
        return

    filtro = df_hist[
        df_hist["UUID Processo"].astype(str).str.strip() == str(uuid_processo).strip()
    ].copy()
    if filtro.empty:
        st.info("Ainda não há histórico registrado para este processo.")
        return

    filtro = filtro.iloc[::-1].reset_index(drop=True)
    colunas_visiveis = [
        "Data/Hora", "Usuário", "Nível", "Tipo de ação", "Campo alterado",
        "Valor anterior", "Valor novo", "Detalhe",
    ]
    st.dataframe(filtro[colunas_visiveis], use_container_width=True, hide_index=True)


def _drive_config():
    try:
        cfg = st.secrets["google_drive"]
        return {
            "client_id": str(cfg["client_id"]),
            "client_secret": str(cfg["client_secret"]),
            "refresh_token": str(cfg["refresh_token"]),
            "token_uri": str(cfg.get("token_uri", "https://oauth2.googleapis.com/token")),
            "root_folder_id": str(cfg.get("root_folder_id", "")).strip(),
        }
    except Exception:
        return None


def drive_disponivel():
    cfg = _drive_config()
    return DRIVE_LIBS_AVAILABLE and bool(cfg and cfg.get("client_id") and cfg.get("client_secret") and cfg.get("refresh_token"))


@st.cache_resource(show_spinner=False)
def obter_drive_service():
    if not DRIVE_LIBS_AVAILABLE:
        raise RuntimeError(
            "Dependências do Google Drive não instaladas. Instale: "
            "google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )
    cfg = _drive_config()
    if not cfg:
        raise RuntimeError("Configuração [google_drive] ausente no st.secrets.")

    creds = Credentials(
        token=None,
        refresh_token=cfg["refresh_token"],
        token_uri=cfg["token_uri"],
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
        scopes=DRIVE_SCOPES,
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _escape_drive_query(valor):
    return str(valor).replace("\\", "\\\\").replace("'", "\\'")


def obter_ou_criar_pasta_raiz_drive(service):
    cfg = _drive_config() or {}
    root_id = cfg.get("root_folder_id", "")
    if root_id:
        return root_id

    nome = "Encerramentos - Sistema"
    q = (
        "mimeType='application/vnd.google-apps.folder' and trashed=false and "
        f"name='{_escape_drive_query(nome)}'"
    )
    resp = service.files().list(q=q, spaces="drive", fields="files(id,name)", pageSize=10).execute()
    arquivos = resp.get("files", [])
    if arquivos:
        return arquivos[0]["id"]

    pasta = service.files().create(
        body={"name": nome, "mimeType": "application/vnd.google-apps.folder"},
        fields="id",
    ).execute()
    return pasta["id"]


def obter_ou_criar_pasta_processo(service, processo):
    root_id = obter_ou_criar_pasta_raiz_drive(service)
    uuid_proc = _texto_limpo(processo.get("UUID Processo"))
    q = (
        "mimeType='application/vnd.google-apps.folder' and trashed=false and "
        f"'{_escape_drive_query(root_id)}' in parents and "
        f"appProperties has {{ key='uuid_processo' and value='{_escape_drive_query(uuid_proc)}' }}"
    )
    resp = service.files().list(q=q, spaces="drive", fields="files(id,name)", pageSize=10).execute()
    arquivos = resp.get("files", [])
    if arquivos:
        return arquivos[0]["id"]

    nome = f"{_texto_limpo(processo.get('ID Processo'))} - {_texto_limpo(processo.get('Loja'))}"
    pasta = service.files().create(
        body={
            "name": nome[:180],
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [root_id],
            "appProperties": {"uuid_processo": uuid_proc},
        },
        fields="id",
    ).execute()
    return pasta["id"]


def validar_nome_pdf_para_loja(nome_arquivo, processo):
    nome_norm = _normalizar_texto(PathLikeName.remove_pdf_extension(nome_arquivo))
    candidatos = [_texto_limpo(processo.get("Loja", ""))] + _separar_apelidos(processo.get("Apelidos da Loja", ""))
    candidatos_norm = [_normalizar_texto(c) for c in candidatos if _normalizar_texto(c)]
    return any(c in nome_norm for c in candidatos_norm)


class PathLikeName:
    @staticmethod
    def remove_pdf_extension(nome):
        nome = str(nome)
        return re.sub(r"(?i)\.pdf$", "", nome).strip()


def validar_pdf_upload(uploaded_file, processo, hashes_existentes):
    nome = uploaded_file.name or "arquivo.pdf"
    mime = (uploaded_file.type or "").lower().strip()
    dados = uploaded_file.getvalue()

    if not nome.lower().endswith(".pdf"):
        return False, "A extensão do arquivo precisa ser .pdf.", None, None
    if mime and mime not in {"application/pdf", "application/x-pdf"}:
        return False, f"Tipo MIME não reconhecido como PDF ({mime}).", None, None
    if len(dados) > MAX_PDF_MB * 1024 * 1024:
        return False, f"O arquivo ultrapassa o limite de {MAX_PDF_MB} MB.", None, None
    if b"%PDF-" not in dados[:1024]:
        return False, "O conteúdo do arquivo não possui uma assinatura PDF válida (%PDF-).", None, None
    if not validar_nome_pdf_para_loja(nome, processo):
        return False, "O nome do PDF precisa conter o nome da loja ou um apelido autorizado.", None, None

    hash_pdf = hashlib.sha256(dados).hexdigest()
    if hash_pdf in hashes_existentes:
        return False, "Este mesmo arquivo já foi enviado para este encerramento.", None, hash_pdf
    return True, "Arquivo válido.", dados, hash_pdf


def enviar_pdf_drive(service, processo, nome, dados):
    pasta_id = obter_ou_criar_pasta_processo(service, processo)
    media = MediaIoBaseUpload(io.BytesIO(dados), mimetype="application/pdf", resumable=False)
    metadata = {
        "name": nome,
        "parents": [pasta_id],
        "mimeType": "application/pdf",
        "appProperties": {
            "uuid_processo": _texto_limpo(processo.get("UUID Processo")),
            "id_processo": _texto_limpo(processo.get("ID Processo")),
        },
    }
    arquivo = service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name,mimeType,size",
    ).execute()
    return arquivo


def baixar_pdf_drive(service, file_id):
    request = service.files().get_media(fileId=file_id)
    return request.execute()


def excluir_pdf_drive(service, file_id):
    service.files().delete(fileId=file_id).execute()


def _obter_documentos_encerramento():
    return ler_aba_padronizada("Documentos Encerramentos", COLUNAS_DOCUMENTOS_ENC)


def _documentos_ativos_processo(uuid_processo):
    df = _obter_documentos_encerramento()
    if df.empty:
        return df
    mask = (
        (df["UUID Processo"].astype(str).str.strip() == str(uuid_processo).strip())
        & (df["Estado Documento"].astype(str).str.strip().str.lower() != "excluído")
    )
    return df[mask].copy().reset_index(drop=True)


def salvar_lote_documentos(processo, categoria, descricao, arquivos):
    if not _opcao_documento_permitida("enviar"):
        return [], [{"nome": "—", "erro": "Seu perfil não possui permissão para enviar documentos."}]
    if _texto_limpo(processo.get("Estado do processo")) == "Arquivado":
        return [], [{"nome": "—", "erro": "Processos arquivados não aceitam novos documentos."}]
    if not drive_disponivel():
        return [], [{"nome": "—", "erro": "Google Drive ainda não está configurado no st.secrets."}]

    df_docs = _obter_documentos_encerramento()
    ativos = _documentos_ativos_processo(processo.get("UUID Processo"))
    hashes = set(ativos["SHA-256"].astype(str).str.strip().tolist()) if not ativos.empty else set()

    try:
        service = obter_drive_service()
    except Exception as exc:
        return [], [{"nome": "—", "erro": f"Falha ao conectar ao Google Drive: {exc}"}]

    aprovados = []
    rejeitados = []
    drive_ids_criados = []
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    usuario = st.session_state.get("usuario_logado", "")

    for arq in arquivos:
        valido, msg, dados, hash_pdf = validar_pdf_upload(arq, processo, hashes)
        if not valido:
            rejeitados.append({"nome": arq.name, "erro": msg})
            continue

        try:
            remoto = enviar_pdf_drive(service, processo, arq.name, dados)
            drive_ids_criados.append(remoto["id"])
            uuid_doc = str(uuid.uuid4())
            registro = {
                "UUID Documento": uuid_doc,
                "ID Documento": f"DOC-{datetime.date.today().year}-{uuid_doc.split('-')[0].upper()}",
                "UUID Processo": _texto_limpo(processo.get("UUID Processo")),
                "ID Processo": _texto_limpo(processo.get("ID Processo")),
                "Loja": _texto_limpo(processo.get("Loja")),
                "Categoria": categoria,
                "Descrição": _texto_limpo(descricao),
                "Nome original": arq.name,
                "Drive File ID": remoto["id"],
                "SHA-256": hash_pdf,
                "Data do envio": agora,
                "Enviado Por": usuario,
                "Tamanho (bytes)": str(len(dados)),
                "Tipo MIME": "application/pdf",
                "Estado Documento": "Ativo",
                "Excluído por": "",
                "Data da exclusão": "",
            }
            aprovados.append(registro)
            hashes.add(hash_pdf)
        except Exception as exc:
            rejeitados.append({"nome": arq.name, "erro": f"Falha no upload para o Drive: {exc}"})

    if aprovados:
        try:
            df_docs = pd.concat([df_docs, pd.DataFrame(aprovados)], ignore_index=True)
            df_docs = df_docs[COLUNAS_DOCUMENTOS_ENC]
            conn.update(
                spreadsheet=url_planilha,
                worksheet="Documentos Encerramentos",
                data=_preparar_df_para_sheets(df_docs),
            )
        except Exception as exc:
            # Rollback best-effort para não deixar arquivos órfãos no Drive.
            for file_id in drive_ids_criados:
                try:
                    excluir_pdf_drive(service, file_id)
                except Exception:
                    pass
            return [], rejeitados + [{
                "nome": "—",
                "erro": (
                    "Os arquivos foram revertidos do Drive porque não foi possível salvar os metadados na aba "
                    f"'Documentos Encerramentos': {exc}"
                ),
            }]

        eventos = []
        for doc in aprovados:
            eventos.append({
                "tipo_acao": "Documento enviado",
                "campo": "Documentos",
                "valor_anterior": "",
                "valor_novo": doc["Nome original"],
                "detalhe": f"Categoria: {doc['Categoria']} | ID Documento: {doc['ID Documento']}",
            })
        registrar_historico_encerramento(processo, eventos)
        registrar_log(
            "Enviou documento(s) de encerramento",
            f"{processo.get('ID Processo')} — {len(aprovados)} arquivo(s)",
        )

    return aprovados, rejeitados


def excluir_documento_encerramento(uuid_documento):
    if not _opcao_documento_permitida("excluir"):
        return False, "Seu perfil não possui permissão para excluir documentos."
    if not drive_disponivel():
        return False, "Google Drive não está configurado."

    df_docs = _obter_documentos_encerramento()
    if df_docs.empty:
        return False, "Documento não encontrado."
    mask = df_docs["UUID Documento"].astype(str).str.strip() == str(uuid_documento).strip()
    indices = df_docs.index[mask].tolist()
    if not indices:
        return False, "Documento não encontrado."
    idx = indices[0]
    doc = df_docs.loc[idx].copy()
    if _texto_limpo(doc.get("Estado Documento")).lower() == "excluído":
        return False, "Este documento já foi excluído."

    try:
        service = obter_drive_service()
        excluir_pdf_drive(service, _texto_limpo(doc.get("Drive File ID")))
    except Exception as exc:
        return False, f"Não foi possível excluir o arquivo do Google Drive: {exc}"

    usuario = st.session_state.get("usuario_logado", "")
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    df_docs.at[idx, "Estado Documento"] = "Excluído"
    df_docs.at[idx, "Excluído por"] = usuario
    df_docs.at[idx, "Data da exclusão"] = agora

    try:
        conn.update(
            spreadsheet=url_planilha,
            worksheet="Documentos Encerramentos",
            data=_preparar_df_para_sheets(df_docs[COLUNAS_DOCUMENTOS_ENC]),
        )
    except Exception as exc:
        return False, (
            "O arquivo foi removido do Drive, mas houve falha ao atualizar o registro no Sheets: "
            f"{exc}"
        )

    df_enc = _obter_df_encerramentos()
    _, processo = _obter_processo_por_uuid(doc.get("UUID Processo"), df_enc)
    if processo is not None:
        registrar_historico_encerramento(processo, [{
            "tipo_acao": "Documento excluído",
            "campo": "Documentos",
            "valor_anterior": doc.get("Nome original", ""),
            "valor_novo": "",
            "detalhe": f"Categoria: {doc.get('Categoria', '')} | ID Documento: {doc.get('ID Documento', '')}",
        }])
    registrar_log("Excluiu documento de encerramento", f"{doc.get('ID Processo')} — {doc.get('Nome original')}")
    return True, "Documento excluído com sucesso."


def _render_pdf_bytes(pdf_bytes, key):
    try:
        st.pdf(pdf_bytes, height=720, key=key)
        return
    except Exception:
        pass

    # Fallback para instalações sem o extra streamlit[pdf].
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    html = (
        '<iframe src="data:application/pdf;base64,' + b64 + '" '
        'width="100%" height="720" style="border:1px solid #FFD80F;border-radius:8px;"></iframe>'
    )
    components.html(html, height=740, scrolling=True)


def _formatar_tamanho_bytes(valor):
    try:
        tamanho = int(float(valor))
    except Exception:
        return "—"
    for unidade in ["B", "KB", "MB", "GB"]:
        if tamanho < 1024 or unidade == "GB":
            return f"{tamanho:.0f} {unidade}" if unidade == "B" else f"{tamanho:.1f} {unidade}"
        tamanho /= 1024
    return "—"


def render_documentos_processo(processo):
    uuid_proc = _texto_limpo(processo.get("UUID Processo"))
    docs = _documentos_ativos_processo(uuid_proc)

    if _opcao_documento_permitida("enviar") and _texto_limpo(processo.get("Estado do processo")) != "Arquivado":
        st.subheader("Adicionar documentos")
        categoria = st.selectbox(
            "Categoria",
            CATEGORIAS_DOCUMENTOS_ENC,
            key=f"doc_categoria_{uuid_proc}",
        )
        descricao = st.text_input(
            "Descrição opcional",
            key=f"doc_desc_{uuid_proc}",
            placeholder="Ex.: versão assinada pela locadora",
        )
        arquivos = st.file_uploader(
            "Selecionar PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"doc_upload_{uuid_proc}",
            help=(
                f"Cada arquivo deve ter no máximo {MAX_PDF_MB} MB e conter no nome a loja "
                "ou um dos apelidos autorizados."
            ),
        )
        if arquivos and st.button("Enviar documentos válidos", key=f"doc_enviar_{uuid_proc}"):
            with st.spinner("Validando e enviando documentos..."):
                aprovados, rejeitados = salvar_lote_documentos(processo, categoria, descricao, arquivos)
            if aprovados:
                st.success(f"{len(aprovados)} documento(s) enviado(s) com sucesso.")
            for item in rejeitados:
                st.error(f"{item['nome']}: {item['erro']}")
            if aprovados:
                st.rerun()

    st.divider()
    st.subheader("Documentos vinculados")
    if docs.empty:
        st.info("Nenhum documento foi anexado a este processo ainda.")
        return

    categorias = sorted(set(docs["Categoria"].astype(str).str.strip().tolist()))
    filtro_cat = st.selectbox(
        "Filtrar categoria",
        ["Todas"] + [c for c in categorias if c],
        key=f"doc_filtro_cat_{uuid_proc}",
    )
    if filtro_cat != "Todas":
        docs = docs[docs["Categoria"].astype(str).str.strip() == filtro_cat].reset_index(drop=True)

    for _, doc in docs.iloc[::-1].iterrows():
        nome = _texto_limpo(doc.get("Nome original"))
        categoria_doc = _texto_limpo(doc.get("Categoria"))
        titulo = f"{categoria_doc} — {nome}" if categoria_doc else nome
        with st.expander(titulo, expanded=False):
            st.caption(
                f"Enviado por {_texto_limpo(doc.get('Enviado Por')) or '—'} em "
                f"{_texto_limpo(doc.get('Data do envio')) or '—'} • "
                f"{_formatar_tamanho_bytes(doc.get('Tamanho (bytes)'))}"
            )
            if _texto_limpo(doc.get("Descrição")):
                st.write(_texto_limpo(doc.get("Descrição")))

            col_v, col_d, col_x = st.columns(3)
            with col_v:
                if st.button("Visualizar", key=f"view_doc_{doc['UUID Documento']}"):
                    st.session_state["doc_visualizar_uuid"] = doc["UUID Documento"]
            with col_d:
                if _opcao_documento_permitida("baixar"):
                    cache_key = f"doc_bytes_{doc['UUID Documento']}"
                    if cache_key not in st.session_state:
                        if st.button("Preparar download", key=f"prep_dl_{doc['UUID Documento']}"):
                            try:
                                service = obter_drive_service()
                                st.session_state[cache_key] = baixar_pdf_drive(service, doc["Drive File ID"])
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Falha ao preparar download: {exc}")
                    else:
                        st.download_button(
                            "Baixar PDF",
                            data=st.session_state[cache_key],
                            file_name=nome,
                            mime="application/pdf",
                            key=f"dl_doc_{doc['UUID Documento']}",
                        )
            with col_x:
                if _opcao_documento_permitida("excluir"):
                    if st.button("Excluir", key=f"del_doc_{doc['UUID Documento']}"):
                        st.session_state["doc_confirmar_exclusao"] = doc["UUID Documento"]
                        st.rerun()

            if st.session_state.get("doc_confirmar_exclusao") == doc["UUID Documento"]:
                st.error(f"Confirmar exclusão definitiva do Drive: **{nome}**?")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Confirmar exclusão", key=f"confirm_del_doc_{doc['UUID Documento']}"):
                        ok, msg = excluir_documento_encerramento(doc["UUID Documento"])
                        st.session_state.pop("doc_confirmar_exclusao", None)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                with c2:
                    if st.button("Cancelar", key=f"cancel_del_doc_{doc['UUID Documento']}"):
                        st.session_state.pop("doc_confirmar_exclusao", None)
                        st.rerun()

    visualizar_uuid = st.session_state.get("doc_visualizar_uuid")
    if visualizar_uuid:
        selecionado = docs[docs["UUID Documento"].astype(str) == str(visualizar_uuid)]
        if selecionado.empty:
            # pode estar fora do filtro atual: procura no conjunto completo
            todos = _documentos_ativos_processo(uuid_proc)
            selecionado = todos[todos["UUID Documento"].astype(str) == str(visualizar_uuid)]
        if not selecionado.empty:
            doc = selecionado.iloc[0]
            st.divider()
            st.subheader(f"Visualização — {doc['Nome original']}")
            try:
                service = obter_drive_service()
                pdf_bytes = baixar_pdf_drive(service, doc["Drive File ID"])
                _render_pdf_bytes(pdf_bytes, key=f"pdf_{visualizar_uuid}")
                if st.button("Fechar visualização", key=f"close_pdf_{visualizar_uuid}"):
                    st.session_state.pop("doc_visualizar_uuid", None)
                    st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível carregar o PDF: {exc}")


def _opcoes_processos(df):
    opcoes = []
    mapa = {}
    for _, row in df.iterrows():
        rotulo = f"{_texto_limpo(row.get('ID Processo'))} — {_texto_limpo(row.get('Loja'))}"
        # Evita colisão visual se houver dados legados duplicados.
        rotulo_unico = rotulo
        n = 2
        while rotulo_unico in mapa:
            rotulo_unico = f"{rotulo} ({n})"
            n += 1
        mapa[rotulo_unico] = _texto_limpo(row.get("UUID Processo"))
        opcoes.append(rotulo_unico)
    return opcoes, mapa


def _filtrar_processos_busca(df, busca):
    busca = _normalizar_texto(busca)
    if not busca:
        return df
    def corresponde(row):
        alvo = " ".join([
            _normalizar_texto(row.get("ID Processo", "")),
            _normalizar_texto(row.get("Loja", "")),
            _normalizar_texto(row.get("Apelidos da Loja", "")),
        ])
        return busca in alvo
    mask = df.apply(corresponde, axis=1)
    return df[mask].copy()


def _render_cabecalho_processo(processo):
    progresso = calcular_progresso_encerramento(processo)
    st.subheader(f"{processo.get('ID Processo')} — {processo.get('Loja')}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Estado", _texto_limpo(processo.get("Estado do processo")) or "Ativo")
    c2.metric("Fechamento", _texto_limpo(processo.get("Data do fechamento")) or "—")
    c3.metric("Progresso", f"{progresso['percentual']:.0f}%")
    c4.metric("Etapas finalizadas", f"{progresso['finalizadas']}/{progresso['total']}")


def _erro_lista(erros):
    for erro in erros:
        st.error(erro)


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

                registrar_log("Login", "Login realizado com sucesso")

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
    registrar_log("Logout", "Logout manual pelo usuário")
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
    "Andamento de Encerramentos",
]
if nivel in ["Admin", "Con"]:
    opcoes_menu.append("👥 Gerenciar Usuários")
    opcoes_menu.append("📜 Logs de Auditoria")
if nivel == "Con" and st.session_state["aba_secreta_desbloqueada"]:
    opcoes_menu.append("🎮 Sala Secreta: Jogo da Forca")
    opcoes_menu.append("🐍 Sala Secreta: Jogo da Cobrinha")

if "menu_navegacao" not in st.session_state or st.session_state["menu_navegacao"] not in opcoes_menu:
    st.session_state["menu_navegacao"] = opcoes_menu[0]

aba_selecionada = st.sidebar.radio("Navegação", opcoes_menu, key="menu_navegacao")

st.sidebar.markdown('<span id="secret-btn-marker"></span>', unsafe_allow_html=True)
if st.sidebar.button(" ", key="btn_secreto"):
    if nivel == "Con":
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


elif aba_selecionada == "Andamento de Encerramentos":
    st.title("Andamento de Encerramentos")

    submenu_enc = st.radio(
        "Seção",
        ["Visão Geral", "Novo Encerramento", "Acompanhamento", "Concluídos / Arquivados", "Documentos"],
        horizontal=True,
        key="enc_submenu",
        label_visibility="collapsed",
    )

    df_enc = _obter_df_encerramentos()

    if submenu_enc == "Visão Geral":
        st.subheader("Visão Geral")
        if df_enc.empty:
            st.info("Nenhum encerramento foi cadastrado ainda.")
        else:
            estados = df_enc["Estado do processo"].astype(str).str.strip()
            df_ativos = df_enc[estados.eq("Ativo")].copy()
            qtd_concluidos = int(estados.eq("Concluído").sum())
            qtd_arquivados = int(estados.eq("Arquivado").sum())

            total_pendentes = 0
            total_andamento = 0
            total_finalizadas = 0
            total_aplicaveis = 0
            linhas_progresso = []

            for _, row in df_ativos.iterrows():
                p = calcular_progresso_encerramento(row)
                total_pendentes += p["pendentes"]
                total_andamento += p["andamento"]
                total_finalizadas += p["finalizadas"]
                total_aplicaveis += p["total"]
                linhas_progresso.append({
                    "ID": row.get("ID Processo", ""),
                    "Loja": row.get("Loja", ""),
                    "Progresso": round(p["percentual"], 1),
                    "Pendentes": p["pendentes"],
                    "Em andamento": p["andamento"],
                    "Finalizadas": p["finalizadas"],
                })

            progresso_geral = (total_finalizadas / total_aplicaveis * 100) if total_aplicaveis else 0.0

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Encerramentos ativos", len(df_ativos))
            c2.metric("Etapas pendentes", total_pendentes)
            c3.metric("Em andamento", total_andamento)
            c4.metric("Finalizadas", total_finalizadas)
            c5.metric("Progresso geral", f"{progresso_geral:.0f}%")

            c6, c7 = st.columns(2)
            c6.metric("Processos concluídos", qtd_concluidos)
            c7.metric("Processos arquivados", qtd_arquivados)

            st.divider()
            st.subheader("Situação geral das etapas ativas")
            resumo = pd.DataFrame({
                "Situação": ["Pendente", "Em andamento", "Finalizado"],
                "Quantidade": [total_pendentes, total_andamento, total_finalizadas],
            })
            resumo = resumo[resumo["Quantidade"] > 0]

            if resumo.empty:
                st.info("Não há etapas ativas para representar no gráfico.")
            elif alt is not None:
                chart = (
                    alt.Chart(resumo)
                    .mark_arc(innerRadius=65, outerRadius=120)
                    .encode(
                        theta=alt.Theta(field="Quantidade", type="quantitative"),
                        color=alt.Color(
                            field="Situação",
                            type="nominal",
                            scale=alt.Scale(
                                domain=["Pendente", "Em andamento", "Finalizado"],
                                range=["#FFD80F", "#FF9F1C", "#2ECC71"],
                            ),
                            legend=alt.Legend(title="Situação"),
                        ),
                        tooltip=["Situação", "Quantidade"],
                    )
                    .properties(height=330)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.dataframe(resumo, use_container_width=True, hide_index=True)

            st.subheader("Progresso por loja")
            if linhas_progresso:
                df_prog = pd.DataFrame(linhas_progresso).sort_values(
                    by=["Progresso", "Loja"], ascending=[True, True]
                )
                st.dataframe(
                    df_prog,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Progresso": st.column_config.ProgressColumn(
                            "Progresso",
                            min_value=0,
                            max_value=100,
                            format="%.1f%%",
                        )
                    },
                )
            else:
                st.info("Não há processos ativos no momento.")

    elif submenu_enc == "Novo Encerramento":
        st.subheader("Novo Encerramento")
        if nivel not in ["Editor", "Admin", "Con"]:
            st.warning("Seu perfil possui permissão apenas para consulta.")
        else:
            st.caption(
                "O ID ENC é gerado automaticamente com o ano vigente e sequência contínua. "
                "O UUID técnico fica armazenado apenas no banco."
            )
            with st.form("form_novo_encerramento", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    novo_loja = st.text_input("Loja *")
                    novo_apelidos = st.text_input(
                        "Apelidos autorizados da loja",
                        help="Opcional. Separe por ponto e vírgula. Esses nomes também poderão validar PDFs.",
                        placeholder="Ex.: Interlagos; Mega Interlagos",
                    )
                    novo_data_fechamento = st.date_input(
                        "Data do fechamento *",
                        value=None,
                        format="DD/MM/YYYY",
                    )
                with c2:
                    novo_notificacao = st.selectbox(
                        "Notificação",
                        STATUS_ETAPAS_ENC["Notificação"]["opcoes"],
                    )
                    novo_data_notificacao = st.date_input(
                        "Data do envio da notificação",
                        value=None,
                        format="DD/MM/YYYY",
                        help="Obrigatória se a notificação já estiver como Enviada.",
                    )
                    novo_obs = st.text_area("Próximo passo / observações", height=120)

                criar_enc = st.form_submit_button("Criar encerramento")

            if criar_enc:
                ok, msg, registro = criar_novo_encerramento(
                    novo_loja,
                    novo_apelidos,
                    novo_data_fechamento,
                    novo_notificacao,
                    novo_data_notificacao,
                    novo_obs,
                )
                if ok:
                    st.success(msg)
                    if registro is not None:
                        st.info(f"ID criado: **{registro['ID Processo']}**")
                    st.rerun()
                else:
                    st.error(msg)

    elif submenu_enc == "Acompanhamento":
        st.subheader("Acompanhamento")
        if df_enc.empty:
            st.info("Nenhum encerramento cadastrado.")
        else:
            df_ativos = df_enc[
                df_enc["Estado do processo"].astype(str).str.strip().eq("Ativo")
            ].copy()
            if df_ativos.empty:
                st.info("Não há encerramentos ativos. Consulte 'Concluídos / Arquivados'.")
            else:
                busca = st.text_input(
                    "Buscar por ID, loja ou apelido",
                    key="enc_busca_acomp",
                    placeholder="Ex.: ENC-2026-000098 ou Interlagos",
                )
                df_filtrado = _filtrar_processos_busca(df_ativos, busca)
                if df_filtrado.empty:
                    st.warning("Nenhum processo ativo corresponde à busca.")
                else:
                    opcoes, mapa = _opcoes_processos(df_filtrado)
                    escolha = st.selectbox("Selecione o encerramento", opcoes, key="enc_escolha_acomp")
                    uuid_escolhido = mapa[escolha]
                    _, processo = _obter_processo_por_uuid(uuid_escolhido, df_enc)
                    _render_cabecalho_processo(processo)

                    parte = st.radio(
                        "Parte do acompanhamento",
                        [
                            "Identificação e Notificação",
                            "Operação da Loja",
                            "Encerramento Operacional",
                            "Distratos / Financeiro / Jurídico",
                        ],
                        horizontal=True,
                        key=f"enc_parte_{uuid_escolhido}",
                    )

                    somente_leitura = nivel not in ["Editor", "Admin", "Con"]
                    alteracoes = {}

                    with st.form(f"form_acomp_{uuid_escolhido}_{parte}"):
                        if parte == "Identificação e Notificação":
                            c1, c2 = st.columns(2)
                            with c1:
                                alteracoes["Loja"] = st.text_input(
                                    "Loja",
                                    value=_texto_limpo(processo.get("Loja")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Apelidos da Loja"] = st.text_input(
                                    "Apelidos autorizados",
                                    value=_texto_limpo(processo.get("Apelidos da Loja")),
                                    disabled=somente_leitura,
                                    help="Separe por ponto e vírgula.",
                                )
                                alteracoes["Data do fechamento"] = _data_input_opcional(
                                    "Data do fechamento",
                                    processo.get("Data do fechamento"),
                                    key=f"dfech_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                            with c2:
                                alteracoes["Notificação"] = st.selectbox(
                                    "Notificação",
                                    STATUS_ETAPAS_ENC["Notificação"]["opcoes"],
                                    index=_indice_status("Notificação", processo.get("Notificação")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data do envio da notificação"] = _data_input_opcional(
                                    "Data do envio da notificação",
                                    processo.get("Data do envio da notificação"),
                                    key=f"dnotif_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )

                        elif parte == "Operação da Loja":
                            c1, c2 = st.columns(2)
                            with c1:
                                alteracoes["Contagem mercadoria"] = st.selectbox(
                                    "Contagem mercadoria",
                                    STATUS_ETAPAS_ENC["Contagem mercadoria"]["opcoes"],
                                    index=_indice_status("Contagem mercadoria", processo.get("Contagem mercadoria")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data da contagem"] = _data_input_opcional(
                                    "Data da contagem",
                                    processo.get("Data da contagem"),
                                    key=f"dcont_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                                alteracoes["Retirada mercadoria"] = st.selectbox(
                                    "Retirada mercadoria",
                                    STATUS_ETAPAS_ENC["Retirada mercadoria"]["opcoes"],
                                    index=_indice_status("Retirada mercadoria", processo.get("Retirada mercadoria")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data da retirada"] = _data_input_opcional(
                                    "Data da retirada",
                                    processo.get("Data da retirada"),
                                    key=f"dret_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                            with c2:
                                alteracoes["Desmobilização"] = st.selectbox(
                                    "Desmobilização",
                                    STATUS_ETAPAS_ENC["Desmobilização"]["opcoes"],
                                    index=_indice_status("Desmobilização", processo.get("Desmobilização")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data da desmobilização"] = _data_input_opcional(
                                    "Data da desmobilização",
                                    processo.get("Data da desmobilização"),
                                    key=f"ddesmob_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                                alteracoes["Retirada da fachada / comunicação visual"] = st.selectbox(
                                    "Retirada da fachada / comunicação visual",
                                    STATUS_ETAPAS_ENC["Retirada da fachada / comunicação visual"]["opcoes"],
                                    index=_indice_status(
                                        "Retirada da fachada / comunicação visual",
                                        processo.get("Retirada da fachada / comunicação visual"),
                                    ),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data da retirada da com. visual"] = _data_input_opcional(
                                    "Data da retirada da com. visual",
                                    processo.get("Data da retirada da com. visual"),
                                    key=f"dcomvis_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )

                        elif parte == "Encerramento Operacional":
                            c1, c2 = st.columns(2)
                            with c1:
                                alteracoes["Contas de consumo"] = st.selectbox(
                                    "Contas de consumo",
                                    STATUS_ETAPAS_ENC["Contas de consumo"]["opcoes"],
                                    index=_indice_status("Contas de consumo", processo.get("Contas de consumo")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data do envio das contas de consumo"] = _data_input_opcional(
                                    "Data do envio das contas de consumo",
                                    processo.get("Data do envio das contas de consumo"),
                                    key=f"dcontcons_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                                alteracoes["Vistoria de devolução"] = st.selectbox(
                                    "Vistoria de devolução",
                                    STATUS_ETAPAS_ENC["Vistoria de devolução"]["opcoes"],
                                    index=_indice_status("Vistoria de devolução", processo.get("Vistoria de devolução")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data da vistoria de devolução"] = _data_input_opcional(
                                    "Data da vistoria de devolução",
                                    processo.get("Data da vistoria de devolução"),
                                    key=f"dvist_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                            with c2:
                                alteracoes["Entrega das chaves"] = st.selectbox(
                                    "Entrega das chaves",
                                    STATUS_ETAPAS_ENC["Entrega das chaves"]["opcoes"],
                                    index=_indice_status("Entrega das chaves", processo.get("Entrega das chaves")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data da entrega das chaves"] = _data_input_opcional(
                                    "Data da entrega das chaves",
                                    processo.get("Data da entrega das chaves"),
                                    key=f"dchaves_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                                alteracoes["Adequações"] = st.selectbox(
                                    "Adequações",
                                    STATUS_ETAPAS_ENC["Adequações"]["opcoes"],
                                    index=_indice_status("Adequações", processo.get("Adequações")),
                                    disabled=somente_leitura,
                                )
                            alteracoes["Orçamentos enviados?"] = st.text_area(
                                "Orçamentos enviados?",
                                value=_texto_limpo(processo.get("Orçamentos enviados?")),
                                disabled=somente_leitura,
                                height=100,
                            )

                        else:
                            c1, c2 = st.columns(2)
                            with c1:
                                alteracoes["Distrato contas a pagar"] = st.selectbox(
                                    "Distrato contas a pagar",
                                    STATUS_ETAPAS_ENC["Distrato contas a pagar"]["opcoes"],
                                    index=_indice_status("Distrato contas a pagar", processo.get("Distrato contas a pagar")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data do envio para o contas a pagar"] = _data_input_opcional(
                                    "Data do envio para o contas a pagar",
                                    processo.get("Data do envio para o contas a pagar"),
                                    key=f"dcp_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                                alteracoes["Distrato jurídico"] = st.selectbox(
                                    "Distrato jurídico",
                                    STATUS_ETAPAS_ENC["Distrato jurídico"]["opcoes"],
                                    index=_indice_status("Distrato jurídico", processo.get("Distrato jurídico")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data do envio para o jurídico"] = _data_input_opcional(
                                    "Data do envio para o jurídico",
                                    processo.get("Data do envio para o jurídico"),
                                    key=f"djur_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                                alteracoes["Distrato aprovação"] = st.selectbox(
                                    "Distrato aprovação",
                                    STATUS_ETAPAS_ENC["Distrato aprovação"]["opcoes"],
                                    index=_indice_status("Distrato aprovação", processo.get("Distrato aprovação")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data do envio do distrato para aprovação"] = _data_input_opcional(
                                    "Data do envio do distrato para aprovação",
                                    processo.get("Data do envio do distrato para aprovação"),
                                    key=f"daprov_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                            with c2:
                                alteracoes["Distrato"] = st.selectbox(
                                    "Distrato",
                                    STATUS_ETAPAS_ENC["Distrato"]["opcoes"],
                                    index=_indice_status("Distrato", processo.get("Distrato")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Contas pagamento"] = st.selectbox(
                                    "Contas pagamento",
                                    STATUS_ETAPAS_ENC["Contas pagamento"]["opcoes"],
                                    index=_indice_status("Contas pagamento", processo.get("Contas pagamento")),
                                    disabled=somente_leitura,
                                )
                                alteracoes["Data do envio da solicitação de pagamento para o contas a pagar"] = _data_input_opcional(
                                    "Data do envio da solicitação de pagamento para o contas a pagar",
                                    processo.get("Data do envio da solicitação de pagamento para o contas a pagar"),
                                    key=f"dpag_{uuid_escolhido}",
                                    disabled=somente_leitura,
                                )
                                alteracoes["Para legal baixa no CNPJ"] = st.selectbox(
                                    "Para legal baixa no CNPJ",
                                    STATUS_ETAPAS_ENC["Para legal baixa no CNPJ"]["opcoes"],
                                    index=_indice_status("Para legal baixa no CNPJ", processo.get("Para legal baixa no CNPJ")),
                                    disabled=somente_leitura,
                                )
                            alteracoes["Próximo passo / observações"] = st.text_area(
                                "Próximo passo / observações",
                                value=_texto_limpo(processo.get("Próximo passo / observações")),
                                disabled=somente_leitura,
                                height=150,
                            )

                        salvar = False
                        if not somente_leitura:
                            salvar = st.form_submit_button("Salvar alterações")

                    if salvar:
                        ok, msg = salvar_alteracoes_encerramento(uuid_escolhido, alteracoes)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            _erro_lista(msg.split("\n"))

                    if somente_leitura:
                        st.info("Seu perfil está em modo somente leitura.")

                    if nivel in ["Editor", "Admin", "Con"]:
                        st.divider()
                        st.subheader("Arquivar antes da conclusão")
                        st.caption(
                            "Use somente quando o encerramento sair do fluxo antes da conclusão. "
                            "O motivo é obrigatório e ficará registrado no histórico."
                        )
                        if st.button("Arquivar processo", key=f"btn_arq_{uuid_escolhido}"):
                            st.session_state["enc_arquivar_uuid"] = uuid_escolhido
                            st.rerun()

                        if st.session_state.get("enc_arquivar_uuid") == uuid_escolhido:
                            motivo_base = st.selectbox(
                                "Motivo do arquivamento",
                                [
                                    "Loja permanecerá aberta",
                                    "Projeto cancelado",
                                    "Encerramento suspenso",
                                    "Cadastro duplicado",
                                    "Processo substituído",
                                    "Outro",
                                ],
                                key=f"mot_arq_{uuid_escolhido}",
                            )
                            complemento = st.text_area(
                                "Detalhes / justificativa",
                                key=f"det_arq_{uuid_escolhido}",
                                help="Obrigatório para 'Outro'; recomendado nos demais casos.",
                            )
                            motivo_final = motivo_base
                            if complemento.strip():
                                motivo_final = f"{motivo_base}: {complemento.strip()}"
                            if motivo_base == "Outro" and not complemento.strip():
                                st.warning("Informe a justificativa para o motivo 'Outro'.")
                            ca, cb = st.columns(2)
                            with ca:
                                if st.button("Confirmar arquivamento", key=f"conf_arq_{uuid_escolhido}"):
                                    if motivo_base == "Outro" and not complemento.strip():
                                        st.error("A justificativa é obrigatória para 'Outro'.")
                                    else:
                                        ok, msg = arquivar_encerramento(uuid_escolhido, motivo_final)
                                        st.session_state.pop("enc_arquivar_uuid", None)
                                        if ok:
                                            st.success(msg)
                                            st.rerun()
                                        else:
                                            st.error(msg)
                            with cb:
                                if st.button("Cancelar arquivamento", key=f"cancel_arq_{uuid_escolhido}"):
                                    st.session_state.pop("enc_arquivar_uuid", None)
                                    st.rerun()

                    st.divider()
                    with st.expander("Histórico do processo", expanded=False):
                        render_historico_processo(uuid_escolhido)

    elif submenu_enc == "Concluídos / Arquivados":
        st.subheader("Concluídos / Arquivados")
        if df_enc.empty:
            st.info("Nenhum encerramento cadastrado.")
        else:
            estados_validos = ["Concluído", "Arquivado"]
            df_fechados = df_enc[
                df_enc["Estado do processo"].astype(str).str.strip().isin(estados_validos)
            ].copy()
            if df_fechados.empty:
                st.info("Nenhum processo concluído ou arquivado ainda.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    filtro_estado = st.selectbox(
                        "Situação",
                        ["Todos", "Concluído", "Arquivado"],
                        key="enc_filtro_fechados_estado",
                    )
                with c2:
                    busca = st.text_input(
                        "Buscar por ID, loja ou apelido",
                        key="enc_busca_fechados",
                    )
                consulta = df_fechados.copy()
                if filtro_estado != "Todos":
                    consulta = consulta[
                        consulta["Estado do processo"].astype(str).str.strip() == filtro_estado
                    ]
                consulta = _filtrar_processos_busca(consulta, busca)

                if consulta.empty:
                    st.warning("Nenhum processo corresponde aos filtros.")
                else:
                    tabela = consulta[[
                        "ID Processo", "Loja", "Data do fechamento", "Estado do processo",
                        "Data de conclusão", "Data de arquivamento", "Arquivado por", "Motivo do arquivamento",
                    ]].copy()
                    st.dataframe(tabela, use_container_width=True, hide_index=True)

                    opcoes, mapa = _opcoes_processos(consulta)
                    escolha = st.selectbox(
                        "Abrir detalhes",
                        opcoes,
                        key="enc_escolha_fechado",
                    )
                    uuid_escolhido = mapa[escolha]
                    _, processo = _obter_processo_por_uuid(uuid_escolhido, df_enc)
                    _render_cabecalho_processo(processo)
                    if _texto_limpo(processo.get("Motivo do arquivamento")):
                        st.warning(f"Motivo do arquivamento: {processo.get('Motivo do arquivamento')}")

                    with st.expander("Histórico do processo", expanded=False):
                        render_historico_processo(uuid_escolhido)

                    if nivel in ["Admin", "Con"]:
                        acao_nome = "Reabrir processo" if processo.get("Estado do processo") == "Concluído" else "Restaurar para acompanhamento"
                        if st.button(acao_nome, key=f"reativar_{uuid_escolhido}"):
                            st.session_state["enc_confirmar_reativar"] = uuid_escolhido
                            st.rerun()
                        if st.session_state.get("enc_confirmar_reativar") == uuid_escolhido:
                            st.error(
                                f"Confirmar: **{acao_nome}** para {processo.get('ID Processo')}? "
                                "A ação será registrada no histórico."
                            )
                            cr1, cr2 = st.columns(2)
                            with cr1:
                                if st.button("Confirmar", key=f"conf_reativar_{uuid_escolhido}"):
                                    ok, msg = restaurar_ou_reabrir_encerramento(uuid_escolhido)
                                    st.session_state.pop("enc_confirmar_reativar", None)
                                    if ok:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                            with cr2:
                                if st.button("Cancelar", key=f"cancel_reativar_{uuid_escolhido}"):
                                    st.session_state.pop("enc_confirmar_reativar", None)
                                    st.rerun()

    elif submenu_enc == "Documentos":
        st.subheader("Documentos")
        if not _opcao_documento_permitida("visualizar"):
            st.error("Seu perfil não possui permissão para visualizar documentos.")
        elif df_enc.empty:
            st.info("Cadastre um encerramento antes de anexar documentos.")
        else:
            if not drive_disponivel():
                st.warning(
                    "A área documental está pronta, mas o Google Drive ainda não foi configurado. "
                    "Depois de adicionar as credenciais OAuth em [google_drive] no st.secrets, "
                    "upload, visualização, download e exclusão serão habilitados."
                )
                if not DRIVE_LIBS_AVAILABLE:
                    st.code(
                        "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib streamlit[pdf]"
                    )

            busca = st.text_input(
                "Buscar processo por ID, loja ou apelido",
                key="enc_busca_docs",
            )
            consulta = _filtrar_processos_busca(df_enc, busca)
            if consulta.empty:
                st.warning("Nenhum processo corresponde à busca.")
            else:
                opcoes, mapa = _opcoes_processos(consulta)
                escolha = st.selectbox("Selecione o processo", opcoes, key="enc_escolha_docs")
                uuid_escolhido = mapa[escolha]
                _, processo = _obter_processo_por_uuid(uuid_escolhido, df_enc)
                _render_cabecalho_processo(processo)
                render_documentos_processo(processo)


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
                nomes_encerrados = []
                for idx in indices_marcados:
                    if 0 <= idx < len(tokens_ordem):
                        token_alvo = tokens_ordem[idx]
                        if token_alvo in SESSOES:
                            nome_sessao = SESSOES[token_alvo].get("usuario", "").title()
                            SESSOES.pop(token_alvo, None)
                            encerradas += 1
                            nomes_encerrados.append(nome_sessao)

                if encerradas > 0:
                    registrar_log(
                        "Forçou logout",
                        f"Encerrou {encerradas} sessão(ões): {', '.join(nomes_encerrados)}"
                    )

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

                    registrar_log(
                        "Sincronizou secrets",
                        f"{len(novas_linhas)} usuário(s): {', '.join([l['Usuário'] for l in novas_linhas])}"
                    )

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

                registrar_log("Criou usuário", f"{user_limpo} ({novo_nivel})")

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
                nivel_alvo = escolha.split(" (")[-1].strip(")")
                df_usr_final = df_usr_rem[
                    df_usr_rem["Usuário"].astype(str).str.strip().str.lower() != user_alvo
                ]
                df_usr_final = _preparar_df_para_sheets(df_usr_final)
                try:
                    conn.update(spreadsheet=url_planilha, worksheet="Usuários", data=df_usr_final)
                    sessoes_encerradas = encerrar_sessoes_do_usuario(user_alvo)

                    detalhe_remocao = f"{user_alvo} ({nivel_alvo})"
                    if sessoes_encerradas > 0:
                        detalhe_remocao += f" — {sessoes_encerradas} sessão(ões) encerrada(s)"
                    registrar_log("Removeu usuário", detalhe_remocao)

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

elif aba_selecionada == "📜 Logs de Auditoria":
    st.title("Logs de Auditoria")

    if nivel not in ["Admin", "Con"]:
        st.error("Você não tem permissão para acessar esta página.")
        st.stop()

    st.write("Histórico de ações sensíveis do sistema — ordenado do mais recente para o mais antigo.")

    try:
        df_logs = ler_aba_padronizada("Logs", ["Data/Hora", "Usuário", "Nível", "Ação", "Detalhe"])
    except Exception as e:
        st.error(f"Erro ao ler a aba 'Logs': {e}")
        df_logs = pd.DataFrame({c: pd.Series(dtype="object") for c in ["Data/Hora", "Usuário", "Nível", "Ação", "Detalhe"]})

    if df_logs.empty:
        st.info("Nenhum log registrado ainda. As ações começam a ser gravadas a partir da próxima interação.")
    else:
        df_logs = df_logs.reset_index(drop=True)

        col_f1, col_f2, col_f3, col_f4 = st.columns(4)

        with col_f1:
            usuarios_disponiveis = sorted(set(df_logs["Usuário"].astype(str).str.strip().tolist()))
            usuarios_disponiveis = [u for u in usuarios_disponiveis if u and u != "—"]
            filtro_usuario = st.selectbox(
                "Filtrar por usuário",
                ["Todos"] + usuarios_disponiveis,
                key="log_filtro_usuario"
            )

        with col_f2:
            acoes_disponiveis = sorted(set(df_logs["Ação"].astype(str).str.strip().tolist()))
            acoes_disponiveis = [a for a in acoes_disponiveis if a]
            filtro_acao = st.selectbox(
                "Filtrar por ação",
                ["Todas"] + acoes_disponiveis,
                key="log_filtro_acao"
            )

        with col_f3:
            niveis_disponiveis = sorted(set(df_logs["Nível"].astype(str).str.strip().tolist()))
            niveis_disponiveis = [n for n in niveis_disponiveis if n and n != "—"]
            filtro_nivel = st.selectbox(
                "Filtrar por nível",
                ["Todos"] + niveis_disponiveis,
                key="log_filtro_nivel"
            )

        with col_f4:
            limite_exibicao = st.selectbox(
                "Mostrar últimos",
                [100, 250, 500, 1000, 5000],
                index=2,
                key="log_limite"
            )

        df_filtrado = df_logs.copy()

        if filtro_usuario != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Usuário"].astype(str).str.strip() == filtro_usuario]

        if filtro_acao != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Ação"].astype(str).str.strip() == filtro_acao]

        if filtro_nivel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Nível"].astype(str).str.strip() == filtro_nivel]

        df_filtrado = df_filtrado.iloc[::-1].reset_index(drop=True)

        total_filtrado = len(df_filtrado)
        df_exibicao = df_filtrado.head(limite_exibicao).copy()

        st.info(
            f"Exibindo **{len(df_exibicao)}** de **{total_filtrado}** registro(s) "
            f"(total geral: **{len(df_logs)}**)."
        )

        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

elif aba_selecionada == "🎮 Sala Secreta: Jogo da Forca":
    if nivel != "Con":
        st.error("Você não tem permissão para acessar esta sala secreta.")
        st.stop()

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
    if nivel != "Con":
        st.error("Você não tem permissão para acessar esta sala secreta.")
        st.stop()

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

st.markdown(
    """
    <div class="footer-autoria">
        Desenvolvido exclusivamente por Raphael Santos | © Todos os direitos reservados
    </div>
    """,
    unsafe_allow_html=True,
)
