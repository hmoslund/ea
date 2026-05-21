import streamlit as st
import pandas as pd

st.set_page_config(page_title="EA Capability Mapper", layout="wide")

MAIN_STYLE = """
<style>
body {
    background-color: white;
}
section.main {
    background: white !important;
}
[data-testid="stHeader"] {
    background: white !important;
}
[data-testid="stToolbar"] {
    background: white !important;
}
.stButton>button {
    background-color: white !important;
    color: black !important;
    font-weight: 700;
}
.stButton>button:hover {
    background-color: #f0f0f0 !important;
}
.ea-table {
    border-collapse: collapse;
    width: 100%;
    color: white;
    background: #1c5e22;
    margin-bottom: 16px;
}
.ea-table th,
.ea-table td {
    border: 1px solid rgba(255, 255, 255, 0.12);
    padding: 10px;
    text-align: left;
}
.ea-table th {
    background: #134015;
    color: white;
}
.ea-table td {
    background: #1f6a28;
    color: white;
}
.ea-map-l1 {
    background: #0e2e65;
    color: white;
    padding: 16px;
    border-radius: 10px;
    margin-bottom: 14px;
    font-size: 22px;
    font-weight: 700;
    width: 25ch;
}
.ea-map-l2 {
    background: #0a4b9b;
    color: white;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 10px;
    font-size: 18px;
    font-weight: 600;
    width: 25ch;
}
.ea-map-l3 {
    background: white;
    color: black;
    padding: 10px;
    border-radius: 6px;
    margin-bottom: 8px;
    font-size: 15px;
    border: 1px solid #d9d9d9;
    width: 25ch;
}
.ea-map-l3 a {
    color: #0b5394;
    text-decoration: none;
    font-weight: 600;
}
.ea-map-l3 a:hover {
    text-decoration: underline;
}
div:has(> .render-btns-start) + [data-testid="stHorizontalBlock"] .stButton > button {
    background-color: #d4d4d4 !important;
    color: #333 !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important;
}
div:has(> .render-btns-start) + [data-testid="stHorizontalBlock"] .stButton > button:hover {
    background-color: #bdbdbd !important;
}
</style>
"""

st.markdown(MAIN_STYLE, unsafe_allow_html=True)

st.title("Enterprise Application Capability Mapper")
st.markdown(
    "Use a `;`-delimited CSV to load L1-L3 capability data, edit the rows, and render a clear hierarchical view for executive review."
)

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["A", "B", "C", "D"])
    st.session_state.sort_desc = True
    st.session_state.show_map = False
    st.session_state.map_level = "L3"  # "L2" or "L3"

SKIP_L1 = {"Database and Data Mngt.", "App. Platf. and Infrastr.", "IT Management"}


def load_csv(csv_file):
    encodings = ['utf-8', 'cp1252', 'iso-8859-1', 'latin-1', 'utf-8-sig']

    for encoding in encodings:
        try:
            df = pd.read_csv(csv_file, sep=";", header=0, dtype=str, keep_default_na=False, encoding=encoding)
            if df.empty or len(df.columns) == 0:
                continue
            return _process_df(df)
        except (UnicodeDecodeError, pd.errors.EmptyDataError):
            continue
        except Exception:
            continue

    st.error("Could not read CSV file. Please ensure the file is a valid semicolon-delimited CSV file with proper encoding (UTF-8, Windows-1252, or ISO-8859-1).")
    return None


def _process_df(df):
    df = df.iloc[3:]
    df = df.iloc[:, :4]
    df.columns = ["A", "B", "C", "D"]
    df = df.fillna("")
    df = df.head(400)
    return df


def render_table(df: pd.DataFrame):
    if df.empty:
        st.info("No capability rows available yet.")
        return

    df = df[df[['A', 'B', 'C', 'D']].apply(lambda x: x.str.strip().ne('').any(), axis=1)]

    if df.empty:
        st.info("No capability rows with content available.")
        return

    html = df.to_html(index=False, classes="ea-table", escape=False)
    st.markdown(html, unsafe_allow_html=True)


def render_hierarchy_l3(df: pd.DataFrame):
    """Full L1 → L2 → L3 hierarchy (original behaviour)."""
    if df.empty:
        st.info("Upload or add rows before rendering the capability map.")
        return

    df = df.copy()
    sort_order = [False, False, False] if st.session_state.sort_desc else [True, True, True]
    df = df.sort_values(by=["A", "B", "C"], ascending=sort_order, ignore_index=True)

    unique_a = [a for a in df["A"].dropna().map(str).replace("", "(empty)").unique().tolist()
                if a not in SKIP_L1]
    if not unique_a:
        st.info("No L1 values to render.")
        return

    st.markdown("## Capability Map (L3)")
    st.markdown("<div style='background:white; padding: 20px; border-radius: 18px; box-shadow: 0 0 18px rgba(0,0,0,0.06);'>", unsafe_allow_html=True)

    columns_per_row = len(unique_a)
    for row_start in range(0, len(unique_a), columns_per_row):
        row_slice = unique_a[row_start:row_start + columns_per_row]
        cols = st.columns(len(row_slice), gap="large")
        for col, a_value in zip(cols, row_slice):
            with col:
                st.markdown(f"<div class='ea-map-l1'>{a_value}</div>", unsafe_allow_html=True)
                sub_a = df[df["A"] == a_value]
                if sub_a.empty:
                    continue

                for b_value, group_b in sub_a.groupby("B", sort=False):
                    if str(b_value).strip() == "":
                        b_value = "(no L2)"
                    st.markdown(f"<div class='ea-map-l2'>{b_value}</div>", unsafe_allow_html=True)
                    for _, row in group_b.iterrows():
                        l3_base = row["D"] or "(no L3)"
                        row3 = str(row["C"]).strip()
                        l3_text = l3_base + " " + row3 if row3 else l3_base
                        url = "https://me.sap.com/processnavigator/SolS/EARL_SolS-013/2602/SolP/" + row3 if row3 else ""
                        if url:
                            safe_url = url.replace('"', '%22')
                            l3_html = f"<a href='{safe_url}' target='_blank'>{l3_text}</a>"
                        else:
                            l3_html = l3_text
                        st.markdown(f"<div class='ea-map-l3'>{l3_html}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_hierarchy_l2(df: pd.DataFrame):
    """L1 → L2 only hierarchy (no L3 shown)."""
    if df.empty:
        st.info("Upload or add rows before rendering the capability map.")
        return

    df = df.copy()
    sort_order = [False, False] if st.session_state.sort_desc else [True, True]
    df = df.sort_values(by=["A", "B"], ascending=sort_order, ignore_index=True)

    unique_a = [a for a in df["A"].dropna().map(str).replace("", "(empty)").unique().tolist()
                if a not in SKIP_L1]
    if not unique_a:
        st.info("No L1 values to render.")
        return

    st.markdown("## Capability Map (L2)")
    st.markdown("<div style='background:white; padding: 20px; border-radius: 18px; box-shadow: 0 0 18px rgba(0,0,0,0.06);'>", unsafe_allow_html=True)

    columns_per_row = len(unique_a)
    for row_start in range(0, len(unique_a), columns_per_row):
        row_slice = unique_a[row_start:row_start + columns_per_row]
        cols = st.columns(len(row_slice), gap="large")
        for col, a_value in zip(cols, row_slice):
            with col:
                st.markdown(f"<div class='ea-map-l1'>{a_value}</div>", unsafe_allow_html=True)
                sub_a = df[df["A"] == a_value]
                if sub_a.empty:
                    continue

                # Collect unique L2 values for this L1
                seen_b = []
                for b_value in sub_a["B"].tolist():
                    b_str = str(b_value).strip() or "(no L2)"
                    if b_str not in seen_b:
                        seen_b.append(b_str)

                for b_str in seen_b:
                    st.markdown(f"<div class='ea-map-l2'>{b_str}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ── Main routing ──────────────────────────────────────────────────────────────

if st.session_state.show_map:
    if st.session_state.map_level == "L2":
        render_hierarchy_l2(st.session_state.df)
    else:
        render_hierarchy_l3(st.session_state.df)

    if st.button("Back to Editor"):
        st.session_state.show_map = False
        st.rerun()

else:
    uploaded_file = st.file_uploader("Upload CSV file (semicolon-delimited)", type=["csv"])
    if uploaded_file is not None:
        uploaded_df = load_csv(uploaded_file)
        if uploaded_df is not None:
            st.session_state.df = uploaded_df

    st.markdown("---")

    sort_choice = st.radio(
        "Sort order for A, B, C",
        options=["Descending (default)", "Ascending"],
        index=0 if st.session_state.sort_desc else 1,
        key="sort_choice",
    )
    st.session_state.sort_desc = sort_choice.startswith("Descending")

    # ── Two render buttons side by side ──────────────────────────────────────
    st.markdown('<div class="render-btns-start" style="display:none"></div>', unsafe_allow_html=True)
    btn_col1, btn_col2, _ = st.columns([2, 2, 6])
    with btn_col1:
        if st.button("Render capability map L2"):
            st.session_state.map_level = "L2"
            st.session_state.show_map = True
            st.rerun()
    with btn_col2:
        if st.button("Render capability map L3"):
            st.session_state.map_level = "L3"
            st.session_state.show_map = True
            st.rerun()

    st.subheader("Capability list")
    render_table(
        st.session_state.df.sort_values(
            by=["A", "B", "C"],
            ascending=[not st.session_state.sort_desc] * 3,
            ignore_index=True,
        ) if not st.session_state.df.empty else st.session_state.df
    )

    st.markdown("### Edit capabilities")
    with st.form("add_row_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            new_a = st.text_input("L1 value (A)")
        with col2:
            new_b = st.text_input("L2 value (B)")
        with col3:
            new_c = st.text_input("L3 value (C)")
        with col4:
            new_d = st.text_input("Link URL (D)")
        add_submitted = st.form_submit_button("Add row")

    if add_submitted:
        new_row = {"A": new_a, "B": new_b, "C": new_c, "D": new_d}
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Row added.")

    if not st.session_state.df.empty:
        delete_options = st.session_state.df.apply(
            lambda r: f"{r['A']} / {r['B']} / {r['C']} / {r['D']}", axis=1
        ).tolist()
        selected_to_delete = st.multiselect(
            "Select rows to delete",
            options=list(range(len(delete_options))),
            format_func=lambda index: delete_options[index],
        )
        if st.button("Delete selected rows"):
            keep = [i for i in range(len(st.session_state.df)) if i not in selected_to_delete]
            st.session_state.df = st.session_state.df.iloc[keep].reset_index(drop=True)
            st.success("Selected rows deleted.")

    st.markdown(
        "---\n" +
        "**CSV format note:** The file must use `;` as a separator. The first 3 rows are disregarded. Only the first 4 columns are used: Column 1 = L1, Column 2 = L2, Column 3 = Row3 (added to L3 text and used for hyperlink), Column 4 = L3. L3 hyperlinks point to https://me.sap.com/processnavigator/SolS/EARL_SolS-013/2602/SolP/ + Row3."
    )
