import streamlit as st
from pipeline import ReviewPipeline
from models import CodeSubmission
from config import Config

st.set_page_config(page_title=Config.PAGE_TITLE, layout="wide", page_icon="🛠️")


def load_custom_css():
    with open("static/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_pipeline() -> ReviewPipeline:
    return ReviewPipeline()


def render_score_card(report: dict):
    st.markdown("### 📊 Code Health Report")

    overall = report.get("overall_score")
    if overall is not None:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Overall Score", f"{overall}/10")
        col2.metric("Readability", f"{report.get('readability', '—')}/10")
        col3.metric("Error Handling", f"{report.get('error_handling', '—')}/10")
        col4.metric("Best Practices", f"{report.get('best_practices', '—')}/10")
    else:
        st.warning("Could not generate a structured score for this submission.")

    st.markdown(f"**Summary:** {report.get('summary', 'No summary available.')}")


def render_input_section():
    st.markdown("### Submit Code for Review")

    col1, col2 = st.columns([4, 1])
    with col1:
        code = st.text_area("Paste your code here", height=300, label_visibility="collapsed",
                             placeholder="Paste a function, class, or small module...")
    with col2:
        language = st.selectbox("Language", Config.SUPPORTED_LANGUAGES)

    return code, language


def main():
    load_custom_css()
    pipeline = get_pipeline()

    st.title(Config.APP_TITLE)
    st.caption(Config.APP_CAPTION)
    st.markdown("---")

    code, language = render_input_section()

    if st.button("🔍 Run Review", type="primary"):
        submission = CodeSubmission(code=code, language=language)

        if not submission.is_valid():
            st.warning("Please paste some code first.")
            return

        if submission.char_count() > Config.MAX_CODE_LENGTH:
            st.warning(f"Code is too long ({submission.char_count()} chars). "
                       f"Please limit to under {Config.MAX_CODE_LENGTH} characters for this demo.")
            return

        with st.spinner("Analyzing code, checking for issues, generating tests..."):
            try:
                result = pipeline.run(submission)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                return

        st.markdown("---")
        render_score_card(result["report"])

        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["📝 Analysis", "🐛 Issues Found", "✅ Generated Tests"])
        with tab1:
            st.write(result["analysis"])
        with tab2:
            st.write(result["issues"])
        with tab3:
            st.code(result["tests"], language=language.lower())


if __name__ == "__main__":
    main()