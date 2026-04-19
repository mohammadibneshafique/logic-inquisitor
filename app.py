"""
app.py — The Logic Inquisitor
Clean, simple, reliable. One input. One button. Three outputs.
"""

import streamlit as st
from pathlib import Path

# ─── Page config — MUST be very first Streamlit call ──────────────────────────
st.set_page_config(
    page_title="The Logic Inquisitor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── All other imports after page config ──────────────────────────────────────
from utils.session import init_session_state, reset_agent_statuses, add_submission_to_history
from agents.orchestrator import run_inquisitor
from agents.socrates import escalate_hint
from models.schemas import InquisitorState

# ─── Inject CSS ───────────────────────────────────────────────────────────────
_css = Path(__file__).parent / "assets" / "style.css"
with open(_css, encoding="utf-8") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

# ─── Init session state ───────────────────────────────────────────────────────
init_session_state()


# ══════════════════════════════════════════════════════════════════════════════
# HTML HELPERS  (no backslashes inside f-string expressions)
# ══════════════════════════════════════════════════════════════════════════════

def _lang_badge(language: str) -> str:
    styles = {
        "c":             ("#5C6BC0", "#1a1f3e"),
        "cpp":           ("#7B68EE", "#1e1a3e"),
        "java":          ("#E57373", "#3e1a1a"),
        "python":        ("#4FC3F7", "#0d2233"),
        "javascript":    ("#FFD54F", "#332b00"),
        "typescript":    ("#4FC3F7", "#0d2233"),
        "rust":          ("#FF8A65", "#3e2010"),
        "go":            ("#4DB6AC", "#0d2e2b"),
        "sql":           ("#9CCC65", "#1e2e0d"),
        "bash":          ("#A5D6A7", "#102212"),
        "logic_problem": ("#CE93D8", "#2a133e"),
        "pseudocode":    ("#B0BEC5", "#1a2030"),
        "unknown":       ("#78909C", "#1a2030"),
    }
    tc, bc = styles.get(language, ("#B0BEC5", "#1a2030"))
    label = language.upper().replace("_", " ")
    border = tc + "33"
    return (
        '<span class="lang-badge" '
        'style="color:' + tc + ';background:' + bc + ';border:1px solid ' + border + ';">'
        + label + '</span>'
    )


def _severity_badge(overall: str) -> str:
    icons = {"critical": "⚡", "high": "🔴", "medium": "🟡", "low": "🟢"}
    icon = icons.get(overall, "")
    return '<span class="badge badge-' + overall + '">' + icon + ' ' + overall.upper() + '</span>'


def _complexity_badge(tier: str) -> str:
    return '<span class="badge badge-' + tier + '">' + tier.upper() + '</span>'


def _conf_bar(confidence: float) -> str:
    pct = int(confidence * 100)
    color = "#10B981" if pct >= 80 else "#F59E0B" if pct >= 50 else "#F87171"
    return (
        '<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
        '<span style="font-size:11px;color:#4B5563;">Detection confidence</span>'
        '<span style="font-size:11px;font-family:monospace;color:' + color + ';">' + str(pct) + '%</span>'
        '</div>'
        '<div class="conf-bar-bg">'
        '<div class="conf-bar-fill" style="width:' + str(pct) + '%;background:' + color + ';"></div>'
        '</div>'
    )


def _sev_bar(label: str, value: int, color: str) -> str:
    pct = str(int((value / 5) * 100))
    val = str(value)
    return (
        '<div class="sev-bar-container">'
        '<span class="sev-label">' + label + '</span>'
        '<div class="sev-bar-bg">'
        '<div class="sev-bar-fill" style="width:' + pct + '%;background:' + color + ';"></div>'
        '</div>'
        '<span class="sev-value">' + val + '/5</span>'
        '</div>'
    )


def _tier_dots(current: int) -> str:
    html = ""
    for i in range(1, 4):
        cls = "active" if i <= current else "inactive"
        html += '<span class="tier-dot ' + cls + '"></span>'
    return html


def _agent_row(icon: str, name: str, desc: str, status: str) -> str:
    name_color = "#F9FAFB" if status != "idle" else "#6B7280"
    return (
        '<div class="agent-node ' + status + '">'
        '<span style="font-size:16px;">' + icon + '</span>'
        '<div style="flex:1;min-width:0;">'
        '<div style="font-size:12px;font-weight:500;color:' + name_color + ';">' + name + '</div>'
        '<div style="font-size:10px;color:#4B5563;">' + desc + '</div>'
        '</div>'
        '<div class="status-dot ' + status + '"></div>'
        '</div>'
    )


# ══════════════════════════════════════════════════════════════════════════════
# LEFT PANEL
# ══════════════════════════════════════════════════════════════════════════════

def render_left_panel() -> None:
    statuses = st.session_state.agent_statuses
    result: InquisitorState | None = st.session_state.last_result
    count = len(st.session_state.submission_history)

    st.markdown(
        '<div style="margin-bottom:12px;"><div class="section-label">⚡ Agent Pipeline</div></div>',
        unsafe_allow_html=True,
    )

    inquisitor_st = "complete" if result else "idle"
    rows = [
        ("🧠", "The Inquisitor",  "Orchestrator",      inquisitor_st),
        ("🌐", "The Linguist",    "Language detection", statuses["linguist"]),
        ("🔬", "The Pathologist", "Bug classification", statuses["pathologist"]),
        ("💡", "The Socrates",    "Hint generation",    statuses["socrates"]),
        ("📚", "The Archivist",   "Pattern tracking",   statuses["archivist"]),
    ]
    st.markdown("".join(_agent_row(i, n, d, s) for i, n, d, s in rows), unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    count_color = "#10B981" if count > 0 else "#4B5563"
    s_label = "submissions" if count != 1 else "submission"
    st.markdown(
        '<div style="text-align:center;padding:8px 0;">'
        '<div style="font-size:22px;font-weight:700;color:' + count_color + ';">' + str(count) + '</div>'
        '<div style="font-size:11px;color:#4B5563;">' + s_label + ' this session</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Archivist pattern cards
    if result and result.archivist_output and result.archivist_output.pattern_cards:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">📊 Pattern Analysis</div>', unsafe_allow_html=True)

        if result.archivist_output.learning_profile:
            lp = result.archivist_output.learning_profile
            st.markdown(
                '<div style="font-size:12px;color:#9CA3AF;font-style:italic;'
                'padding:10px 12px;background:rgba(255,255,255,0.03);'
                'border-radius:8px;margin-bottom:10px;line-height:1.6;">' + lp + '</div>',
                unsafe_allow_html=True,
            )

        sev_c = {"mild": "#10B981", "moderate": "#F59E0B", "persistent": "#F87171"}
        for card in result.archivist_output.pattern_cards:
            sc = sev_c.get(card.severity, "#6B7280")
            st.markdown(
                '<div class="pattern-card">'
                '<div class="concept-name">' + card.concept + '</div>'
                '<div class="pattern-meta">'
                '<span style="color:' + sc + ';">●</span> '
                + card.severity.capitalize() + ' · ' + str(card.occurrences) + '× · '
                '<a href="' + card.study_url + '" target="_blank" '
                'style="color:#6366F1;text-decoration:none;">' + card.study_resource + ' ↗</a>'
                '</div></div>',
                unsafe_allow_html=True,
            )

        if result.archivist_output.recommended_topics:
            st.markdown(
                '<div class="section-label" style="margin-top:12px;">📖 Study Topics</div>',
                unsafe_allow_html=True,
            )
            for topic in result.archivist_output.recommended_topics:
                st.markdown(
                    '<div style="font-size:11px;color:#9CA3AF;padding:3px 0;">→ ' + topic + '</div>',
                    unsafe_allow_html=True,
                )


# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT CARDS
# ══════════════════════════════════════════════════════════════════════════════

def render_context_card(result: InquisitorState) -> None:
    ctx = result.linguist_output
    if not ctx:
        return

    fw_html = ""
    if ctx.framework:
        fw_html += '&nbsp;·&nbsp;<span style="color:#9CA3AF;font-size:12px;">' + ctx.framework + '</span>'
    if ctx.runtime:
        fw_html += '&nbsp;·&nbsp;<span style="color:#6B7280;font-size:11px;">via ' + ctx.runtime + '</span>'

    input_labels = {
        "code": "Source Code", "error_log": "Error Log",
        "description": "Problem Description", "mixed": "Mixed Input",
    }
    it_label = input_labels.get(ctx.input_type, ctx.input_type)

    sigs_html = ""
    for sig in ctx.code_quality_signals:
        dc = {"high": "#F87171", "medium": "#F59E0B", "low": "#10B981"}.get(sig.severity, "#6B7280")
        sigs_html += (
            '<div class="quality-signal">'
            '<span style="background:' + dc + ';margin-top:4px;flex-shrink:0;'
            'width:6px;height:6px;border-radius:50%;display:inline-block;"></span>'
            '<span><strong style="color:' + dc + ';font-size:10px;">[' + sig.severity.upper() + ']</strong>'
            '&nbsp;' + sig.signal + '</span>'
            '</div>'
        )
    sigs_block = (
        '<div style="margin-bottom:8px;"><div class="section-label">Quality Signals</div>'
        + sigs_html + '</div>'
    ) if sigs_html else ""

    st.markdown(
        '<div class="output-card emerald">'
        '<div class="card-title">🌐 &nbsp; 01 · Detected Context</div>'
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">'
        + _lang_badge(ctx.language) + fw_html + '</div>'
        '<div style="margin-bottom:12px;">' + _conf_bar(ctx.confidence) + '</div>'
        '<div style="margin-bottom:12px;">'
        '<span style="font-size:11px;color:#4B5563;">Input type:&nbsp;</span>'
        '<span style="font-size:11px;color:#9CA3AF;background:rgba(255,255,255,0.05);'
        'padding:2px 8px;border-radius:4px;">' + it_label + '</span>'
        '</div>'
        + sigs_block +
        '<div style="border-top:1px solid rgba(255,255,255,0.06);padding-top:10px;'
        'font-size:12px;color:#6B7280;font-style:italic;">' + ctx.reasoning + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_topology_card(result: InquisitorState) -> None:
    topo = result.pathologist_output
    if not topo:
        return

    bug_label = topo.bug_type.replace("_", " ").title()
    cat_label  = topo.problem_category.replace("_", " ").title()
    sev = topo.severity

    region_html = ""
    if topo.affected_region:
        region_html = (
            '<div style="padding:8px 12px;background:rgba(245,158,11,0.06);'
            'border:1px solid rgba(245,158,11,0.15);border-radius:8px;margin-bottom:12px;">'
            '<div style="font-size:10px;color:#F59E0B;margin-bottom:2px;">Affected Region</div>'
            '<div style="font-size:12px;color:#FDE68A;">' + topo.affected_region + '</div>'
            '</div>'
        )

    st.markdown(
        '<div class="output-card coral">'
        '<div class="card-title" style="display:flex;justify-content:space-between;">'
        '<span>🔬 &nbsp; 02 · Problem Topology</span>'
        + _severity_badge(sev.overall) + '</div>'
        '<div style="display:flex;gap:12px;margin-bottom:14px;">'
        '<div style="flex:1;background:rgba(255,255,255,0.03);border-radius:8px;padding:10px 12px;">'
        '<div style="font-size:10px;color:#4B5563;margin-bottom:4px;">Bug Type</div>'
        '<div style="font-size:13px;font-weight:600;color:#F87171;">' + bug_label + '</div>'
        '</div>'
        '<div style="flex:1;background:rgba(255,255,255,0.03);border-radius:8px;padding:10px 12px;">'
        '<div style="font-size:10px;color:#4B5563;margin-bottom:4px;">Category</div>'
        '<div style="font-size:12px;color:#F9FAFB;">' + cat_label + '</div>'
        '</div>'
        '<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:10px 12px;">'
        '<div style="font-size:10px;color:#4B5563;margin-bottom:4px;">Complexity</div>'
        + _complexity_badge(topo.complexity_tier) + '</div>'
        '</div>'
        + region_html +
        '<div style="padding:10px 14px;background:rgba(255,255,255,0.03);'
        'border:1px solid rgba(255,255,255,0.06);border-radius:8px;margin-bottom:14px;">'
        '<div style="font-size:10px;color:#4B5563;margin-bottom:4px;">Conceptual Gap Exposed</div>'
        '<div style="font-size:13px;color:#D1D5DB;font-style:italic;line-height:1.6;">'
        '"' + topo.conceptual_gap + '"</div>'
        '</div>'
        '<div style="margin-bottom:10px;">'
        '<div class="section-label">Severity Matrix</div>'
        + _sev_bar("Impact", sev.impact, "#F87171")
        + _sev_bar("Frequency", sev.frequency, "#F59E0B")
        + _sev_bar("Detectability", sev.detectability, "#818CF8") +
        '</div>'
        '<div style="border-top:1px solid rgba(255,255,255,0.06);padding-top:10px;'
        'font-size:12px;color:#6B7280;font-style:italic;line-height:1.6;">'
        + topo.reasoning + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_guidance_card(result: InquisitorState) -> None:
    soc = result.socrates_output
    if not soc:
        return
    tier = st.session_state.current_tier
    hints = {1: soc.tier1, 2: soc.tier2, 3: soc.tier3}
    hint = hints.get(tier, soc.tier1)
    tier_colors = {1: "#10B981", 2: "#F59E0B", 3: "#F87171"}
    tc = tier_colors.get(tier, "#10B981")
    css_cls = "tier-" + str(tier)
    st.markdown(
        '<div class="output-card amber">'
        '<div class="card-title" style="display:flex;justify-content:space-between;">'
        '<span>💡 &nbsp; 03 · Socratic Guidance</span>'
        '<span style="display:flex;align-items:center;gap:4px;">'
        + _tier_dots(tier) +
        '<span style="font-size:10px;color:' + tc + ';margin-left:6px;">Tier ' + str(tier) + '/3</span>'
        '</span></div>'
        '<div class="hint-bubble ' + css_cls + '">' + hint + '</div>'
        '<a href="' + soc.concept_url + '" target="_blank" class="concept-link">'
        '📖 ' + soc.concept_name + ' &nbsp;↗</a>'
        '<div style="border-top:1px solid rgba(255,255,255,0.06);margin-top:12px;'
        'padding-top:8px;font-size:11px;color:#4B5563;">'
        'Use the hint ladder on the right to go deeper if still stuck.</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL
# ══════════════════════════════════════════════════════════════════════════════

def render_right_panel() -> None:
    result: InquisitorState | None = st.session_state.last_result

    st.markdown(
        '<div style="margin-bottom:12px;">'
        '<div class="section-label">🧠 Socratic Ladder</div>'
        '<div style="font-size:11px;color:#4B5563;line-height:1.5;">'
        'Discover the insight — one tier at a time.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    if not result or not result.socrates_output:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">🧠</div>'
            '<div>Submit code to unlock<br>the Socratic hint ladder.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    soc = result.socrates_output
    tier = st.session_state.current_tier
    hints = {1: soc.tier1, 2: soc.tier2, 3: soc.tier3}
    tier_colors = {1: "#10B981", 2: "#F59E0B", 3: "#F87171"}
    bar_color = tier_colors.get(tier, "#10B981")
    pct = str(int((tier / 3) * 100))

    st.markdown(
        '<div style="margin-bottom:16px;">'
        '<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
        '<span style="font-size:11px;color:#4B5563;">Hint depth</span>'
        '<span style="font-size:11px;font-family:monospace;color:' + bar_color + ';">'
        + str(tier) + '/3</span>'
        '</div>'
        '<div style="height:4px;background:rgba(255,255,255,0.06);border-radius:9999px;overflow:hidden;">'
        '<div style="width:' + pct + '%;height:100%;background:' + bar_color + ';border-radius:9999px;"></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    tier_cfg = [
        (1, "💚", "Tier I",   "Conceptual Nudge",   "#10B981", "tier-1"),
        (2, "🟡", "Tier II",  "Structural Pointer",  "#F59E0B", "tier-2"),
        (3, "🔴", "Tier III", "Minimal Unlock",      "#F87171", "tier-3"),
    ]

    for t_num, _icon, label, sublabel, color, css_cls in tier_cfg:
        is_active   = (t_num == tier)
        is_unlocked = (t_num <= tier)
        r_v = int(color[1:3], 16)
        g_v = int(color[3:5], 16)
        b_v = int(color[5:7], 16)
        b_alpha = "0.3" if is_active else "0.1"
        border_c = "rgba(" + str(r_v) + "," + str(g_v) + "," + str(b_v) + "," + b_alpha + ")"
        bg_c = "rgba(255,255,255," + ("0.04" if is_active else "0.02") + ")"
        name_c = color if is_unlocked else "#4B5563"
        lock = "🔓" if is_unlocked else "🔒"
        pill = (
            '<span style="font-size:10px;color:' + color + ';background:' + color + '20;'
            'padding:2px 6px;border-radius:9999px;">Active</span>'
        ) if is_active else ""
        br_radius = "8px 8px 0 0" if is_unlocked else "8px"
        mb = "0" if is_unlocked else "8px"
        header = (
            '<div style="display:flex;align-items:center;gap:8px;padding:10px 12px;'
            'background:' + bg_c + ';border:1px solid ' + border_c + ';'
            'border-radius:' + br_radius + ';margin-bottom:' + mb + ';">'
            '<span style="font-size:14px;">' + lock + '</span>'
            '<div style="flex:1;">'
            '<div style="font-size:12px;font-weight:500;color:' + name_c + ';">' + label + '</div>'
            '<div style="font-size:10px;color:#4B5563;">' + sublabel + '</div>'
            '</div>' + pill + '</div>'
        )
        if is_unlocked:
            hint_text = hints.get(t_num, "")
            content = (
                '<div style="padding:12px;background:' + bg_c + ';border:1px solid ' + border_c + ';'
                'border-top:none;border-radius:0 0 8px 8px;margin-bottom:10px;">'
                '<div class="hint-bubble ' + css_cls + '" style="margin:0;">' + hint_text + '</div>'
                '</div>'
            )
            st.markdown(header + content, unsafe_allow_html=True)
        else:
            st.markdown(header, unsafe_allow_html=True)

    st.markdown(
        '<a href="' + soc.concept_url + '" target="_blank" class="concept-link" '
        'style="display:flex;width:100%;box-sizing:border-box;">'
        '<span style="flex:1;">📖 ' + soc.concept_name + '</span><span>↗</span></a>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    if tier < 3:
        st.markdown('<div class="stuck-button">', unsafe_allow_html=True)
        if st.button("💬  I'm still stuck — go deeper", key="escalate_btn"):
            with st.spinner("Generating Tier " + str(tier + 1) + " hint..."):
                updated = escalate_hint(result, tier + 1)
                st.session_state.last_result = updated
                st.session_state.current_tier = tier + 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="text-align:center;padding:12px;background:rgba(248,113,113,0.06);'
            'border:1px solid rgba(248,113,113,0.2);border-radius:8px;">'
            '<div style="font-size:12px;font-weight:500;color:#F87171;">Tier III — maximum guidance</div>'
            '<div style="font-size:11px;color:#7F1D1D;margin-top:4px;">The answer is within reach.</div>'
            '</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # Hero header
    st.markdown(
        '<div style="text-align:center;padding:20px 0 10px;">'
        '<div class="hero-title">🧠 THE LOGIC INQUISITOR</div>'
        '<div class="hero-tagline">Don\'t get the answer. Get the insight.</div>'
        '<div style="font-size:11px;color:#374151;margin-top:6px;letter-spacing:0.08em;">'
        'A MULTI-AGENT SOCRATIC DEBUGGER · POWERED BY GEMINI 1.5 FLASH + LANGGRAPH'
        '</div></div><hr>',
        unsafe_allow_html=True,
    )

    col_left, col_center, col_right = st.columns([1.5, 4, 2])

    with col_left:
        render_left_panel()

    with col_center:
        st.markdown(
            '<div class="section-label">📋 Submit Your Code or Problem</div>',
            unsafe_allow_html=True,
        )

        # Single text input — no key/value conflict, no demo dropdown
        user_code = st.text_area(
            label="code_input",
            height=340,
            placeholder=(
                "Paste your code here — or describe your problem in plain English.\n\n"
                "Examples:\n"
                "  • C / Java / Python source code with a bug\n"
                "  • An error message or stack trace\n"
                "  • A logic or algorithm problem you cannot solve\n\n"
                "The Logic Inquisitor will NEVER give you the answer.\n"
                "It will guide you to discover it yourself."
            ),
            label_visibility="collapsed",
        )

        # INTERROGATE button
        clicked = st.button("🔍  INTERROGATE", use_container_width=True)

        if clicked:
            if not user_code.strip():
                st.error("Please paste your code or describe your problem first.")
            else:
                reset_agent_statuses()
                st.session_state.current_tier = 1
                st.session_state.agent_statuses["linguist"] = "active"

                with st.spinner("Running the 5-agent pipeline..."):
                    try:
                        result = run_inquisitor(
                            raw_input=user_code,
                            session_id=st.session_state.session_id,
                            session_history=st.session_state.submission_history,
                        )
                        for agent_key in ("linguist", "pathologist", "socrates", "archivist"):
                            if getattr(result, agent_key + "_output", None) is not None:
                                st.session_state.agent_statuses[agent_key] = "complete"
                        st.session_state.last_result = result
                        add_submission_to_history(result)
                        if result.error:
                            st.warning("Note: " + result.error)
                    except Exception as exc:
                        for k in st.session_state.agent_statuses:
                            if st.session_state.agent_statuses[k] == "active":
                                st.session_state.agent_statuses[k] = "error"
                        st.error("Pipeline error: " + str(exc))

                st.rerun()

        # Results
        result: InquisitorState | None = st.session_state.last_result
        if result:
            st.markdown(
                '<div style="margin-top:24px;"></div>'
                '<div class="section-label">📊 Three-Output Contract</div>',
                unsafe_allow_html=True,
            )
            if result.linguist_output:
                render_context_card(result)
            if result.pathologist_output:
                render_topology_card(result)
            if result.socrates_output:
                render_guidance_card(result)
        else:
            st.markdown(
                '<div class="empty-state" style="margin-top:40px;">'
                '<div class="empty-state-icon">🔍</div>'
                '<div style="font-size:14px;color:#6B7280;">No submission yet</div>'
                '<div style="font-size:12px;color:#374151;margin-top:6px;'
                'max-width:280px;margin-left:auto;margin-right:auto;line-height:1.6;">'
                'Paste your code above and click INTERROGATE.'
                '</div></div>',
                unsafe_allow_html=True,
            )

    with col_right:
        render_right_panel()

    st.markdown(
        '<div class="footer-text">'
        'Built for Agenticthon 2025 &nbsp;·&nbsp;'
        'Powered by Google Gemini 1.5 Flash + LangGraph &nbsp;·&nbsp;'
        '100% Free'
        '</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
