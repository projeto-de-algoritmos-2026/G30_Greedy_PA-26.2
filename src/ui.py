"""Componentes visuais compartilhados pela experiência TrailPack."""

import base64
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]


def render_header() -> None:
    artwork = base64.b64encode((ROOT / 'assets/trail-landscape.svg').read_bytes()).decode()
    st.markdown('''<style>
    .block-container {max-width:1180px;padding-top:2rem;padding-bottom:3rem;}
    h1,h2,h3 {letter-spacing:-.035em;}
    .brand {font-size:1.2rem;font-weight:800;letter-spacing:-.03em;margin-bottom:1rem;}
    .brand span {font-size:.7rem;letter-spacing:.16em;margin-left:1rem;color:#677b6f;}
    .hero {border-radius:24px;padding:42px;margin-bottom:24px;background-size:cover;
      background-position:center;min-height:270px;color:#fff9e8;}
    .hero h1 {font-size:3.4rem;line-height:1.06;color:#fff9e8;max-width:540px;margin:12px 0;}
    .hero p {max-width:450px;color:#f2f1dc;font-size:1.05rem;}
    .eyebrow {font-size:.72rem;letter-spacing:.17em;font-weight:700;text-transform:uppercase;}
    .pill {display:inline-block;background:#ffffff20;border:1px solid #ffffff40;
      border-radius:30px;padding:6px 12px;font-size:.75rem;}
    [data-testid="stMetric"] {background:#fffdf6;border:1px solid #dee3d7;border-radius:16px;padding:16px;}
    [data-testid="stForm"] {background:#fffdf6;border-radius:20px;}
    div.stButton > button, div.stFormSubmitButton > button {border-radius:12px;min-height:46px;}
    @media(max-width:640px) {.hero {padding:25px;}.hero h1 {font-size:2.35rem;}.brand span {display:none;}}
    </style>''', unsafe_allow_html=True)
    st.markdown('<div class="brand">🎒 TrailPack <span>MENOS PESO. MAIS CAMINHO.</span></div>', unsafe_allow_html=True)
    st.markdown(f'''<div class="hero" style="background-image:linear-gradient(90deg,#123b32ee,#123b3266,transparent),url(data:image/svg+xml;base64,{artwork})">
    <span class="pill">O próximo caminho começa aqui</span>
    <h1>Uma boa aventura<br>começa na mochila.</h1>
    <p>Escolha seu percurso. Equilibre sua carga. Descubra o que levar para a próxima trilha.</p>
    <div class="eyebrow">01 Planeje &nbsp; / &nbsp; 02 Monte &nbsp; / &nbsp; 03 Explore</div></div>''', unsafe_allow_html=True)
