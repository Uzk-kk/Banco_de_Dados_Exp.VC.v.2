import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import hashlib
import hmac
import secrets
import time
import random
import re

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILIZAÇÃO CSS
# ==========================================
st.set_page_config(
    page_title="Sistema Integrado de Gestão",
    page_icon="🏢",
    layout="wide"
)

# Estilização CSS customizada mantendo o tema Roxo/Amarelo (#341539 / #FFD80F)
st.markdown("""
    <style>
    /* Estilo geral da página */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Cores principais nos botões */
    div.stButton > button:first-child {
        background-color: #341539;
        color: #FFD80F;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #FFD80F;
        color: #341539;
        border: 1px solid #341539;
    }
    
    /* Rodapé fixo */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #341539;
        color: #FFD80F;
        text-align: center;
        padding: 8px;
        font-size: 12px;
        z-index: 999;
    }
    </style>
    <div class="footer">
        Sistema Interno de Gestão - Todos os direitos reservados © 2026
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. SISTEMA DE AUTENTICAÇÃO E SEGURANÇA
# ==========================================

@st.cache_resource
def get_session_store():
    """Armazena sessões ativas em memória."""
    return {}

session_store = get_session_store()

def gerar_hash_senha(senha: str) -> str:
    """Gera hash SHA-256 seguro para a senha."""
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

def verificar_senha(senha_digitada: str, hash_armazenado: str) -> bool:
    """Verifica a senha usando HMAC para prevenção contra timing attacks."""
    hash_digitado = gerar_hash_senha(senha_digitada)
    return hmac.compare_digest(hash_digitado, hash_armazenado)

def autenticar_usuario():
    """Gerencia a tela de login e controle de taxas de tentativas (Rate Limit)."""
    USUARIOS = {
        "admin": {"nome": "Administrador", "senha_hash": gerar_hash_senha("admin123"), "perfil": "Admin"},
        "editor": {"nome": "Editor de Dados", "senha_hash": gerar_hash_senha("editor123"), "perfil": "Editor"},
        "leitor": {"nome": "Usuário Leitor", "senha_hash": gerar_hash_senha("leitor123"), "perfil": "Leitor"}
    }

    query_params = st.query_params
    token_sessao = query_params.get("session_token", None)

    if token_sessao and token_sessao in session_store:
        return session_store[token_sessao]

    st.title("🔐 Acesso ao Sistema")
    
    if "tentativas_login" not in st.session_state:
        st.session_state["tentativas_login"] = 0
    if "bloqueado_ate" not in st.session_state:
        st.session_state["bloqueado_ate"] = 0

    if time.time() < st.session_state["bloqueado_ate"]:
        tempo_restante = int(st.session_state["bloqueado_ate"] - time.time())
        st.error(f"Muitas tentativas incorretas. Aguarde {tempo_restante} segundos para tentar novamente.")
        st.stop()

    with st.form("form_login"):
        usuario = st.text_input("Usuário:").strip().lower()
        senha = st.text_input("Senha:", type="password")
        btn_login = st.form_submit_button("Entrar")

        if btn_login:
            if usuario in USUARIOS and verificar_senha(senha, USUARIOS[usuario]["senha_hash"]):
                st.session_state["tentativas_login"] = 0
                novo_token = secrets.token_hex(16)
                dados_usuario = USUARIOS[usuario]
                dados_usuario["login"] = usuario
                session_store[novo_token] = dados_usuario
                st.query_params["session_token"] = novo_token
                st.success("Login efetuado com sucesso!")
                st.rerun()
            else:
                st.session_state["tentativas_login"] += 1
                if st.session_state["tentativas_login"] >= 5:
                    st.session_state["bloqueado_ate"] = time.time() + 300
                    st.error("Número máximo de tentativas excedido! Bloqueado por 5 minutos.")
                else:
                    st.error("Usuário ou senha incorretos.")
                st.stop()
    return None

dados_usuario = autenticar_usuario()

if not dados_usuario:
    st.stop()

# ==========================================
# 3. CONEXÃO GOOGLE SHEETS
# ==========================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url_planilha = st.secrets["connections"]["gsheets"]["spreadsheet"]
except Exception as e:
    st.error("Erro ao conectar à planilha do Google Sheets. Verifique o arquivo secrets.toml.")
    st.stop()

# ==========================================
# 4. BARRA LATERAL E NAVEGAÇÃO
# ==========================================
st.sidebar.title(f"Bem-vindo(a), {dados_usuario['nome']}")
st.sidebar.caption(f"Perfil: **{dados_usuario['perfil']}**")

if st.sidebar.button("Sair / Logout"):
    token_atual = st.query_params.get("session_token", None)
    if token_atual in session_store:
        del session_store[token_atual]
    st.query_params.clear()
    st.rerun()

st.sidebar.divider()

opcoes_menu = [
    "Cadastro Rápido",
    "Controle de Prestadores",
    "Sublocatários",
    "Controle Gerentes de Loja",
    "💡 Contas de Consumo",
    "🔑 Controle de Acessos",
    "🔒 Senhas Concessionárias",
    "📐 Espaços Disponíveis"
]

if st.session_state.get("desbloqueou_secreta", False):
    opcoes_menu.append("🎮 Sala Secreta: Jogo da Forca")

aba_selecionada = st.sidebar.radio("Selecione o Módulo:", opcoes_menu)

st.sidebar.markdown("---")
if st.sidebar.button("⚙️", help="Recurso oculto"):
    st.session_state["desbloqueou_secreta"] = True
    st.sidebar.success("Sala Secreta Desbloqueada!")
    st.rerun()

usuario_autenticado = dados_usuario["nome"]

# ==========================================
# 5. CONTEÚDO DAS PÁGINAS E NAVEGAÇÃO
# ==========================================

# --- ABA: CADASTRO RÁPIDO ---
if aba_selecionada == "Cadastro Rápido":
    st.title("⚡ Cadastro Rápido Geral")
    st.write("Utilize esta aba para registros ágeis de entradas gerais.")
    
    with st.form("form_cadastro_rapido"):
        col1, col2 = st.columns(2)
        with col1:
            nome_item = st.text_input("Nome do Registro / Item:")
            categoria = st.selectbox("Categoria:", ["Geral", "Urgente", "Manutenção", "Outros"])
        with col2:
            observacao = st.text_area("Observações:")
        
        btn_salvar = st.form_submit_button("Salvar Registro")
        
        if btn_salvar:
            if not nome_item:
                st.warning("Por favor, informe o nome do registro.")
            else:
                novo_dado = pd.DataFrame([{
                    "Nome": nome_item,
                    "Categoria": categoria,
                    "Observação": observacao,
                    "Cadastrado por": usuario_autenticado
                }])
                try:
                    df_existente = conn.read(spreadsheet=url_planilha, worksheet="Cadastro Rápido")
                    df_final = pd.concat([df_existente, novo_dado], ignore_index=True)
                except:
                    df_final = novo_dado
                
                conn.update(spreadsheet=url_planilha, worksheet="Cadastro Rápido", data=df_final)
                st.success("Cadastro salvo com sucesso!")

    st.subheader("Registros Cadastrados")
    try:
        df_cadastros = conn.read(spreadsheet=url_planilha, worksheet="Cadastro Rápido")
        if dados_usuario["perfil"] in ["Admin", "Editor"]:
            df_cadastros["Excluir"] = False
            tabela_cadastros = st.data_editor(df_cadastros, hide_index=True, use_container_width=True)
            if not tabela_cadastros[tabela_cadastros["Excluir"] == True].empty:
                if st.button("Confirmar Exclusão de Registros"):
                    df_atualizado = tabela_cadastros[tabela_cadastros["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Cadastro Rápido", data=df_atualizado)
                    st.success("Registro(s) removido(s)!")
                    st.rerun()
        else:
            st.dataframe(df_cadastros, use_container_width=True)
    except Exception as e:
        st.info("Nenhum registro encontrado na guia 'Cadastro Rápido'.")

# --- ABA: CONTROLE DE PRESTADORES ---
elif aba_selecionada == "Controle de Prestadores":
    st.title("🛠️ Controle de Prestadores de Serviço")
    
    with st.form("form_prestadores"):
        c1, c2 = st.columns(2)
        with c1:
            prestador = st.text_input("Razão Social / Nome do Prestador:")
            cnpj = st.text_input("CPF/CNPJ (Apenas números):")
        with c2:
            servico = st.text_input("Tipo de Serviço Prestado:")
            contato = st.text_input("Telefone / Contato:")
        
        btn_prestador = st.form_submit_button("Cadastrar Prestador")
        if btn_prestador:
            cnpj_limpo = re.sub(r'\D', '', cnpj)
            df_novo = pd.DataFrame([{
                "Prestador": prestador,
                "CNPJ/CPF": cnpj_limpo,
                "Serviço": servico,
                "Contato": contato,
                "Cadastrado por": usuario_autenticado
            }])
            try:
                df_ex = conn.read(spreadsheet=url_planilha, worksheet="Prestadores")
                df_f = pd.concat([df_ex, df_novo], ignore_index=True)
            except:
                df_f = df_novo
            conn.update(spreadsheet=url_planilha, worksheet="Prestadores", data=df_f)
            st.success("Prestador cadastrado com sucesso!")

    st.subheader("Prestadores Cadastrados")
    try:
        df_prest = conn.read(spreadsheet=url_planilha, worksheet="Prestadores")
        if dados_usuario["perfil"] in ["Admin", "Editor"]:
            df_prest["Excluir"] = False
            tabela_prest = st.data_editor(df_prest, hide_index=True, use_container_width=True)
            if not tabela_prest[tabela_prest["Excluir"] == True].empty:
                if st.button("Confirmar Exclusão de Prestadores"):
                    df_atualizado = tabela_prest[tabela_prest["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Prestadores", data=df_atualizado)
                    st.success("Prestador(es) removido(s)!")
                    st.rerun()
        else:
            st.dataframe(df_prest, use_container_width=True)
    except Exception as e:
        st.info("Nenhum prestador cadastrado na guia 'Prestadores'.")

# --- ABA: SUBLOCATÁRIOS ---
elif aba_selecionada == "Sublocatários":
    st.title("🏢 Gestão de Sublocatários")
    
    with st.form("form_sublocatarios"):
        c1, c2 = st.columns(2)
        with c1:
            nome_sub = st.text_input("Nome do Sublocatário:")
            espaco = st.text_input("Espaço / Loja Ocupada:")
        with c2:
            valor = st.number_input("Valor do Aluguel (R$):", min_value=0.0, format="%.2f")
            vencimento = st.date_input("Data de Vencimento do Contrato:")
        
        btn_sub = st.form_submit_button("Salvar Sublocatário")
        if btn_sub:
            df_novo = pd.DataFrame([{
                "Sublocatário": nome_sub,
                "Espaço": espaco,
                "Valor": valor,
                "Vencimento": str(vencimento),
                "Cadastrado por": usuario_autenticado
            }])
            try:
                df_ex = conn.read(spreadsheet=url_planilha, worksheet="Sublocatarios")
                df_f = pd.concat([df_ex, df_novo], ignore_index=True)
            except:
                df_f = df_novo
            conn.update(spreadsheet=url_planilha, worksheet="Sublocatarios", data=df_f)
            st.success("Sublocatário registrado com sucesso!")

    st.subheader("Sublocatários Cadastrados")
    try:
        df_sub = conn.read(spreadsheet=url_planilha, worksheet="Sublocatarios")
        if dados_usuario["perfil"] in ["Admin", "Editor"]:
            df_sub["Excluir"] = False
            tabela_sub = st.data_editor(df_sub, hide_index=True, use_container_width=True)
            if not tabela_sub[tabela_sub["Excluir"] == True].empty:
                if st.button("Confirmar Exclusão de Sublocatários"):
                    df_atualizado = tabela_sub[tabela_sub["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Sublocatarios", data=df_atualizado)
                    st.success("Sublocatário(s) removido(s)!")
                    st.rerun()
        else:
            st.dataframe(df_sub, use_container_width=True)
    except Exception as e:
        st.info("Nenhum registro encontrado na guia 'Sublocatarios'.")

# --- ABA: CONTROLE GERENTES DE LOJA ---
elif aba_selecionada == "Controle Gerentes de Loja":
    st.title("👔 Controle de Gerentes de Loja")
    
    with st.form("form_gerentes"):
        c1, c2 = st.columns(2)
        with c1:
            loja = st.text_input("Nome / Número da Loja:")
            gerente = st.text_input("Nome do Gerente:")
        with c2:
            telefone = st.text_input("Telefone de Contato:")
            email = st.text_input("E-mail:")
        
        btn_gerente = st.form_submit_button("Cadastrar Gerente")
        if btn_gerente:
            df_novo = pd.DataFrame([{
                "Loja": loja,
                "Gerente": gerente,
                "Telefone": telefone,
                "E-mail": email,
                "Cadastrado por": usuario_autenticado
            }])
            try:
                df_ex = conn.read(spreadsheet=url_planilha, worksheet="Controle Gerentes de Loja")
                df_f = pd.concat([df_ex, df_novo], ignore_index=True)
            except:
                df_f = df_novo
            conn.update(spreadsheet=url_planilha, worksheet="Controle Gerentes de Loja", data=df_f)
            st.success("Gerente registrado!")

    st.subheader("Gerentes Cadastrados")
    try:
        df_g = conn.read(spreadsheet=url_planilha, worksheet="Controle Gerentes de Loja")
        
        if dados_usuario["perfil"] in ["Admin", "Editor"]:
            df_g["Excluir"] = False
            tabela_g_editavel = st.data_editor(
                df_g,
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

# --- ABA: CONTAS DE CONSUMO (NOVA) ---
elif aba_selecionada == "💡 Contas de Consumo":
    st.title("💡 Gestão de Contas de Consumo")
    
    with st.form("form_contas_consumo"):
        col1, col2, col3 = st.columns(3)
        with col1:
            loja = st.text_input("Loja:")
            uf = st.text_input("UF (Máx. 2 letras):", max_chars=2).upper()
            status = st.selectbox("Status:", ["Ativo", "Inativo", "Pendente", "Em Análise"])
            num_fornecimento = st.text_input("Número do fornecimento:")
            doc_titular = st.text_input("Documento do titular:")
        
        with col2:
            concessionaria_energia = st.text_input("Concessionária energia:")
            concessionaria_agua = st.text_input("Concessionária água:")
            num_inst_energia = st.text_input("Número de instalação energia:")
            num_inst_agua = st.text_input("Número de instalação água:")
            telefone = st.text_input("Telefone:")
            
        with col3:
            protocolo_energia = st.text_input("Protocolo energia:")
            protocolo_agua = st.text_input("Protocolo água:")
            nome = st.text_input("Nome:")
            cpf_cnpj = st.text_input("CPF/CNPJ (Apenas números):")
            email = st.text_input("E-mail:")

        btn_salvar_consumo = st.form_submit_button("Cadastrar Conta de Consumo")

        if btn_salvar_consumo:
            cpf_cnpj_limpo = re.sub(r'\D', '', cpf_cnpj)
            
            if len(uf) != 2 or not uf.isalpha():
                st.warning("O campo UF deve conter exatamente 2 letras.")
            else:
                novo_registro = pd.DataFrame([{
                    "Loja": loja,
                    "UF": uf,
                    "Status": status,
                    "Número do fornecimento": num_fornecimento,
                    "Concessionária energia": concessionaria_energia,
                    "Concessionária água": concessionaria_agua,
                    "Número de instalação energia": num_inst_energia,
                    "Número de instalação água": num_inst_agua,
                    "Telefone": telefone,
                    "Documento do titular": doc_titular,
                    "Protocolo energia": protocolo_energia,
                    "Protocolo água": protocolo_agua,
                    "Nome": nome,
                    "CPF/CNPJ": cpf_cnpj_limpo,
                    "E-mail": email,
                    "Cadastrado por": usuario_autenticado
                }])
                try:
                    df_ex = conn.read(spreadsheet=url_planilha, worksheet="Contas de Consumo")
                    df_final = pd.concat([df_ex, novo_registro], ignore_index=True)
                except:
                    df_final = novo_registro
                
                conn.update(spreadsheet=url_planilha, worksheet="Contas de Consumo", data=df_final)
                st.success("Conta de consumo registrada com sucesso!")
                st.rerun()

    st.subheader("Registros de Contas de Consumo")
    try:
        df_consumo = conn.read(spreadsheet=url_planilha, worksheet="Contas de Consumo")
        if dados_usuario["perfil"] in ["Admin", "Editor"]:
            df_consumo["Excluir"] = False
            tabela_editavel = st.data_editor(df_consumo, hide_index=True, use_container_width=True)
            if not tabela_editavel[tabela_editavel["Excluir"] == True].empty:
                if st.button("Confirmar Exclusão dos Registros Selecionados"):
                    df_atualizado = tabela_editavel[tabela_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Contas de Consumo", data=df_atualizado)
                    st.success("Registro(s) removido(s) com sucesso!")
                    st.rerun()
        else:
            st.dataframe(df_consumo, use_container_width=True)
    except:
        st.info("Nenhum registro encontrado na guia 'Contas de Consumo'.")

# --- ABA: CONTROLE DE ACESSOS (NOVA) ---
elif aba_selecionada == "🔑 Controle de Acessos":
    st.title("🔑 Controle de Acessos Concessionárias")
    
    with st.form("form_controle_acessos"):
        c1, c2 = st.columns(2)
        with c1:
            loja = st.text_input("Loja:")
            uf = st.text_input("UF (Máx. 2 letras):", max_chars=2).upper()
            status = st.selectbox("Status:", ["Ativo", "Inativo", "Pendente"])
            concessionaria_agua = st.text_input("Concessionária água:")
            login_agua = st.text_input("Login água:")
            senha_agua = st.text_input("Senha água:", type="password")
        
        with c2:
            concessionaria_energia = st.text_input("Concessionária energia:")
            login_energia = st.text_input("Login energia:")
            senha_energia = st.text_input("Senha energia:", type="password")

        btn_salvar_acesso = st.form_submit_button("Salvar Controle de Acesso")

        if btn_salvar_acesso:
            if len(uf) != 2 or not uf.isalpha():
                st.warning("O campo UF deve conter exatamente 2 letras.")
            else:
                novo_acesso = pd.DataFrame([{
                    "Loja": loja,
                    "UF": uf,
                    "Status": status,
                    "Concessionária água": concessionaria_agua,
                    "Login água": login_agua,
                    "Senha água": senha_agua,
                    "Concessionária energia": concessionaria_energia,
                    "Login energia": login_energia,
                    "Senha energia": senha_energia,
                    "Cadastrado por": usuario_autenticado
                }])
                try:
                    df_ex = conn.read(spreadsheet=url_planilha, worksheet="Controle de Acessos")
                    df_final = pd.concat([df_ex, novo_acesso], ignore_index=True)
                except:
                    df_final = novo_acesso
                
                conn.update(spreadsheet=url_planilha, worksheet="Controle de Acessos", data=df_final)
                st.success("Controle de acesso cadastrado com sucesso!")
                st.rerun()

    st.subheader("Acessos Cadastrados")
    try:
        df_acessos = conn.read(spreadsheet=url_planilha, worksheet="Controle de Acessos")
        if dados_usuario["perfil"] in ["Admin", "Editor"]:
            df_acessos["Excluir"] = False
            tabela_editavel = st.data_editor(df_acessos, hide_index=True, use_container_width=True)
            if not tabela_editavel[tabela_editavel["Excluir"] == True].empty:
                if st.button("Confirmar Exclusão de Acessos"):
                    df_atualizado = tabela_editavel[tabela_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Controle de Acessos", data=df_atualizado)
                    st.success("Acesso(s) removido(s)!")
                    st.rerun()
        else:
            st.dataframe(df_acessos, use_container_width=True)
    except:
        st.info("Nenhum registro encontrado na guia 'Controle de Acessos'.")

# --- ABA: SENHAS CONCESSIONÁRIAS (NOVA) ---
elif aba_selecionada == "🔒 Senhas Concessionárias":
    st.title("🔒 Cadastro de Senhas de Concessionárias")
    
    with st.form("form_senhas_concessionarias"):
        c1, c2 = st.columns(2)
        with c1:
            empresa = st.text_input("Empresa:")
            concessionaria = st.text_input("Concessionária:")
            cnpj_cpf = st.text_input("CNPJ/CPF (Apenas números):")
        with c2:
            login = st.text_input("Login:")
            senha = st.text_input("Senha:", type="password")

        btn_salvar_senha = st.form_submit_button("Cadastrar Senha")

        if btn_salvar_senha:
            cnpj_cpf_limpo = re.sub(r'\D', '', cnpj_cpf)
            nova_senha = pd.DataFrame([{
                "Empresa": empresa,
                "Concessionária": concessionaria,
                "Login": login,
                "Senha": senha,
                "CNPJ/CPF": cnpj_cpf_limpo,
                "Cadastrado por": usuario_autenticado
            }])
            try:
                df_ex = conn.read(spreadsheet=url_planilha, worksheet="Senhas Concessionarias")
                df_final = pd.concat([df_ex, nova_senha], ignore_index=True)
            except:
                df_final = nova_senha
            
            conn.update(spreadsheet=url_planilha, worksheet="Senhas Concessionarias", data=df_final)
            st.success("Senha cadastrada com sucesso!")
            st.rerun()

    st.subheader("Senhas Registradas")
    try:
        df_senhas = conn.read(spreadsheet=url_planilha, worksheet="Senhas Concessionarias")
        if dados_usuario["perfil"] in ["Admin", "Editor"]:
            df_senhas["Excluir"] = False
            tabela_editavel = st.data_editor(df_senhas, hide_index=True, use_container_width=True)
            if not tabela_editavel[tabela_editavel["Excluir"] == True].empty:
                if st.button("Confirmar Exclusão de Senhas"):
                    df_atualizado = tabela_editavel[tabela_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Senhas Concessionarias", data=df_atualizado)
                    st.success("Senha(s) removida(s)!")
                    st.rerun()
        else:
            st.dataframe(df_senhas, use_container_width=True)
    except:
        st.info("Nenhum registro encontrado na guia 'Senhas Concessionarias'.")

# --- ABA: ESPAÇOS DISPONÍVEIS (NOVA) ---
elif aba_selecionada == "📐 Espaços Disponíveis":
    st.title("📐 Gestão de Espaços Disponíveis")
    
    with st.form("form_espacos_disponiveis"):
        c1, c2 = st.columns(2)
        with c1:
            unidade = st.text_input("Unidade disponível:")
            endereco = st.text_input("Endereço:")
            tipo_espaco = st.selectbox("Interno/Externo:", ["Interno", "Externo"])
        with c2:
            espaco_disp = st.text_input("Espaço Disp.:")
            area_m2 = st.number_input("Área (m²):", min_value=0.0, step=1.0, format="%.2f")
            pontos_consumo = st.text_input("Pontos de consumo:")

        btn_salvar_espaco = st.form_submit_button("Cadastrar Espaço Disponível")

        if btn_salvar_espaco:
            area_formatada = f"{area_m2} m²"
            
            novo_espaco = pd.DataFrame([{
                "Unidade disponível": unidade,
                "Endereço": endereco,
                "Interno/Externo": tipo_espaco,
                "Espaço Disp.": espaco_disp,
                "m²": area_formatada,
                "Pontos de consumo": pontos_consumo,
                "Cadastrado por": usuario_autenticado
            }])
            try:
                df_ex = conn.read(spreadsheet=url_planilha, worksheet="Espacos Disponiveis")
                df_final = pd.concat([df_ex, novo_espaco], ignore_index=True)
            except:
                df_final = novo_espaco
            
            conn.update(spreadsheet=url_planilha, worksheet="Espacos Disponiveis", data=df_final)
            st.success("Espaço disponível cadastrado com sucesso!")
            st.rerun()

    st.subheader("Lista de Espaços Disponíveis")
    try:
        df_espacos = conn.read(spreadsheet=url_planilha, worksheet="Espacos Disponiveis")
        if dados_usuario["perfil"] in ["Admin", "Editor"]:
            df_espacos["Excluir"] = False
            tabela_editavel = st.data_editor(df_espacos, hide_index=True, use_container_width=True)
            if not tabela_editavel[tabela_editavel["Excluir"] == True].empty:
                if st.button("Confirmar Exclusão de Espaços"):
                    df_atualizado = tabela_editavel[tabela_editavel["Excluir"] == False].drop(columns=["Excluir"])
                    conn.update(spreadsheet=url_planilha, worksheet="Espacos Disponiveis", data=df_atualizado)
                    st.success("Espaço(s) removido(s)!")
                    st.rerun()
        else:
            st.dataframe(df_espacos, use_container_width=True)
    except:
        st.info("Nenhum registro encontrado na guia 'Espacos Disponiveis'.")

# --- ABA SECRETA: JOGO DA FORCA ---
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
