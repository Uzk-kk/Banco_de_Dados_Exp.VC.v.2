# Customização CSS e Rodapé de Autoria
st.markdown(
    """
    <style>
    /* Fundo da aplicação */
    .stApp, [data-testid="stSidebar"] { 
        background-color: #341539 !important; 
    }

    /* Títulos e Rótulos principais */
    h1, h2, h3, label, [data-testid="stMarkdownContainer"] p { 
        color: #FFD80F !important; 
        font-weight: bold !important; 
    }

    /* Inputs de Texto */
    div[data-baseweb="input"] > div { 
        background-color: #FFD80F !important; 
        border-radius: 8px !important; 
    }
    div[data-baseweb="input"] input { 
        color: #000000 !important; /* Cor preta para legibilidade sobre fundo amarelo */
        font-weight: bold !important;
    }

    /* Forms e Botões */
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

    /* ==========================================================================
       1. ESTILIZAÇÃO DO BOTÃO RADIO (Navegação)
       ========================================================================== */
    /* Texto das opções do radio */
    div[data-testid="stRadioButton"] label p {
        color: #FFD80F !important;
    }

    /* Circulo do Radio Marcado (Background e Borda) */
    div[data-testid="stRadioButton"] div[role="radiogroup"] [aria-checked="true"] {
        border-color: #FFD80F !important;
        background-color: #FFD80F !important;
    }

    /* Ponto interno do Radio Marcado */
    div[data-testid="stRadioButton"] div[role="radiogroup"] [aria-checked="true"] > div {
        background-color: #341539 !important;
    }

    /* Borda do Radio Desmarcado */
    div[data-testid="stRadioButton"] div[role="radiogroup"] [aria-checked="false"] {
        border-color: #FFD80F !important;
        background-color: transparent !important;
    }

    /* ==========================================================================
       2. ESTILIZAÇÃO DO SLIDER (Avaliação)
       ========================================================================== */
    /* Bolinha / Puxador */
    div[data-baseweb="slider"] [role="slider"] {
        background-color: #FFD80F !important;
        border-color: #FFD80F !important;
        box-shadow: 0px 0px 5px rgba(255, 216, 15, 0.8) !important;
    }

    /* Barra preenchida (Ativa) */
    div[data-baseweb="slider"] > div > div > div:nth-child(2) {
        background-color: #FFD80F !important;
    }

    /* Trilha inativa do Slider */
    div[data-baseweb="slider"] > div > div {
        background-color: rgba(255, 216, 15, 0.3) !important;
    }

    /* Rótulos de texto / números do slider */
    div[data-testid="stSlider"] [data-testid="stTickBar"] div,
    div[data-testid="stSlider"] div {
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
