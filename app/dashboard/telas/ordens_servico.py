"""
Tela: Controle e Gestão de Ordens de Serviço
Acompanhamento dos chamados, histórico e baixa de manutenções realizadas.
"""

import streamlit as st
from app.servicos.ordens_service import listar_ordens, concluir_ordem_servico

def renderizar_tela_ordens_servico():
    st.markdown('<h1 class="montserrat-title">📋 Ordens de Serviço & Manutenções</h1>', unsafe_allow_html=True)
    st.caption("Acompanhe o status dos chamados de iluminação pública e dê baixa nos serviços concluídos.")

    # Filtro de Status
    c_filtro, c_busca = st.columns([1, 2])
    with c_filtro:
        filtro_status = st.selectbox("Status:", ["Todos", "aberta", "concluida"])

    ordens = listar_ordens(filtro_status=filtro_status)

    if not ordens:
        st.info("Nenhuma ordem de serviço encontrada com este filtro.", icon="ℹ️")
        return

    st.write(f"Total encontrado: **{len(ordens)}** ordem(ns)")

    for os_item in ordens:
        is_aberta = os_item["status"] == "aberta"
        cor_borda = "#F59E0B" if is_aberta else "#10B981"
        cor_badge = "#F59E0B" if is_aberta else "#10B981"
        txt_status = "CHAMADO EM ABERTO" if is_aberta else "CONCLUÍDO / RESOLVIDO"

        materiais_str = ", ".join([f"{m.get('quantidade', 1)}x {m.get('item', '')}" for m in os_item.get("materiais_lista", [])]) or "Sem materiais especificados"

        with st.container():
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid {cor_borda}; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="font-family: 'JetBrains Mono'; font-weight: 800; font-size: 16px; color: #FFFFFF;">{os_item['protocolo']}</span>
                            <span style="margin-left: 10px; font-weight: 700; color: #38BDF8; font-size: 14px;">Poste {os_item['codigo_poste']}</span>
                            <div style="font-size: 12px; color: #94A3B8; margin-top: 3px;">📍 {os_item.get('logradouro', '')} &bull; {os_item.get('bairro', '')}</div>
                        </div>
                        <span style="background: {cor_badge}22; color: {cor_badge}; border: 1px solid {cor_badge}; font-size: 10px; font-weight: 800; padding: 4px 10px; border-radius: 20px;">
                            {txt_status}
                        </span>
                    </div>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.06); font-size: 13px; color: #E2E8F0;">
                        <b>Defeito:</b> {os_item['defeito']} <span style="color: #94A3B8;">(Prioridade: {os_item['prioridade']})</span><br>
                        <b>Materiais requisitados:</b> <span style="color: #38BDF8;">{materiais_str}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_btn, col_espaco = st.columns([1, 3])
            with col_btn:
                if is_aberta:
                    if st.button(f"✅ Concluir Reparo ({os_item['protocolo']})", key=f"btn_concluir_{os_item['protocolo']}", type="primary"):
                        concluir_ordem_servico(os_item["protocolo"])
                        st.success(f"Ordem {os_item['protocolo']} marcada como concluída! O poste voltou ao status normal.")
                        st.rerun()
