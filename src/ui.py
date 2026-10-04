"""Componentes visuais compartilhados pela experiência TrailPack."""

import base64
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]


def render_header() -> None:
    artwork = base64.b64encode((ROOT / 'assets/trail-landscape.svg').read_bytes()).decode()
    st.markdown('''<style>
    .block-container {max-width:1180px;padding-top:4.5rem;padding-bottom:3rem;}
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
    @media(min-width:641px) and (max-width:1000px) {
      [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
      [data-testid="stColumn"] {min-width:calc(50% - 1rem);flex:1 1 calc(50% - 1rem);}
    }
    @media(max-width:640px) {.hero {padding:25px;}.hero h1 {font-size:2.35rem;}.brand span {display:none;}}
    </style>''', unsafe_allow_html=True)
    st.markdown('<div class="brand">🎒 TrailPack <span>MENOS PESO. MAIS CAMINHO.</span></div>', unsafe_allow_html=True)
    st.markdown(f'''<div class="hero" style="background-image:linear-gradient(90deg,#123b32ee,#123b3266,transparent),url(data:image/svg+xml;base64,{artwork})">
    <span class="pill">O próximo caminho começa aqui</span>
    <h1>Uma boa aventura<br>começa na mochila.</h1>
    <p>Escolha seu percurso. Equilibre sua carga. Descubra o que levar para a próxima trilha.</p>
    <div class="eyebrow">01 Planeje &nbsp; / &nbsp; 02 Monte &nbsp; / &nbsp; 03 Explore</div></div>''', unsafe_allow_html=True)


def render_recommendation(result) -> None:
    """Exibe o resultado submetido, sem depender de alterações no formulário."""
    st.divider()
    st.subheader("03 · Sua mochila, pronta para revisar")
    st.write(f"**{result.trilha.nome}** · {result.trilha.distancia:g} km · {result.trilha.duracao:g} h · {result.trilha.pessoas} pessoa(s)")
    st.caption("Resultado da última montagem. Após editar o percurso, clique em Montar minha mochila para recalcular.")
    weight, space, value = st.columns(3)
    weight.metric("Peso na mochila", f"{result.peso_total:.2f} kg", help="Soma dos essenciais e recursos selecionados.")
    space.metric("Espaço restante", f"{result.capacidade_restante:.2f} kg")
    value.metric("Pontos de utilidade", f"{result.valor_total:.0f}", help="Pontuação heurística para este cenário; não é uma medida de segurança ou suficiência.")
    used = result.peso_total / result.trilha.capacidade if result.trilha.capacidade else 0
    st.progress(min(1.0, max(0.0, used)), text=f"Carga usada: {used:.0%} de {result.trilha.capacidade:g} kg")
    if result.itens:
        st.success("✦ Planejamento montado · Confira os itens antes de sair.")
        essentials, resources = st.tabs(["🛡️ Itens reservados", "💧 Recursos otimizados"])
        for panel, essential in ((essentials, True), (resources, False)):
            with panel:
                selected = [item for item in result.itens if (item.essencial or not item.divisivel) == essential]
                if not selected:
                    st.info("Nenhum item neste grupo para a capacidade informada.")
                else:
                    st.dataframe([
                        {"Item": item.nome, "Categoria": item.categoria.value,
                         "Quantidade (un. do catálogo)": round(item.quantidade_padrao, 3),
                         "Peso (kg)": round(item.peso_total, 3),
                         "Utilidade/kg": round(item.valor_base / item.peso, 1)}
                        for item in selected
                    ], use_container_width=True, hide_index=True)
        st.caption("Quantidade: água e isotônico em litros; alimentos e mistura energética em kg; equipamentos em unidades.")
        st.subheader("Por que estes itens foram recomendados?")
        for item in result.itens:
            reasons = result.justificativas.get(item.nome, [])
            if reasons:
                with st.expander(item.nome):
                    for reason in reasons:
                        st.write(f"• {reason}")
        checklist = f"TrailPack — {result.trilha.nome}\n\n" + "\n".join(
            f"[ ] {item.nome}: {item.quantidade_padrao:.3g} un. do catálogo ({item.peso_total:.3f} kg)"
            for item in result.itens)
        checklist += f"\n\nPeso total: {result.peso_total:.2f} / {result.trilha.capacidade:.2f} kg\n"
        st.download_button("↓ Levar meu checklist", checklist, file_name="trailpack-checklist.txt", mime="text/plain")
    for warning in result.avisos:
        st.info(warning)
    st.caption("A pontuação ajuda a comparar recursos. Ela não garante quantidades suficientes de água, alimentos ou equipamentos para o percurso.")
