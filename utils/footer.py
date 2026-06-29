import streamlit as st

_URL_PORTFOLIO = "https://makore-0612.github.io/zam_portfolio/"
_URL_REPO      = "https://github.com/makore-0612/Seismological_intelligence"
_URL_LINKEDIN  = "https://www.linkedin.com/in/ángel-zamora-072674378"


def render_footer():
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align:center; color:#888; font-size:0.82rem; padding:0.6rem 0 1.2rem 0;">
            © Ángel Zamora · 2026 &nbsp;·&nbsp;
            <a href="{_URL_PORTFOLIO}" target="_blank"
               style="color:#FF4B4B; text-decoration:none;">Acerca de</a>
            &nbsp;·&nbsp;
            <a href="{_URL_REPO}" target="_blank"
               style="color:#FF4B4B; text-decoration:none;">Repositorio</a>
            &nbsp;·&nbsp;
            <a href="{_URL_LINKEDIN}" target="_blank"
               style="color:#FF4B4B; text-decoration:none;">LinkedIn</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
