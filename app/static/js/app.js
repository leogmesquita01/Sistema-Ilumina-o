/**
 * Aplicação Principal - Gestão e Mapa de Postes COSERN
 * Boa Saúde / RN - Secretaria de Infraestrutura
 */

// Coordenadas Centrais de Boa Saúde / RN
const BOA_SAUDE_COORDS = [-6.1611, -35.6025];
const DEFAULT_ZOOM = 15;

let map;
let markerClusterGroup;
let markersMap = new Map(); // codigo -> marker
let activePole = null;
let currentLayer = "streets";
let streetTileLayer, satelliteTileLayer;

// Inicialização
document.addEventListener("DOMContentLoaded", () => {
    initMap();
    setupEvents();
    loadStats();
    loadPoles();
});

// ==========================================
// INICIALIZAÇÃO DO MAPA
// ==========================================
function initMap() {
    map = L.map("map", {
        center: BOA_SAUDE_COORDS,
        zoom: DEFAULT_ZOOM,
        zoomControl: false
    });

    // Camada de Ruas (OpenStreetMap)
    streetTileLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap'
    });

    // Camada de Satélite (Esri World Imagery - Excelente para estradas rurais e postes)
    satelliteTileLayer = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
        maxZoom: 19,
        attribution: '&copy; Esri &mdash; Imagens de Satélite'
    });

    streetTileLayer.addTo(map);

    // Controles de Zoom no canto inferior direito
    L.control.zoom({ position: "bottomright" }).addTo(map);

    // Grupo com clusterização para alta performance
    markerClusterGroup = L.markerClusterGroup({
        maxClusterRadius: 40,
        disableClusteringAtZoom: 18,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false
    });
    map.addLayer(markerClusterGroup);
}

// Alternar entre visão de Rua e Satélite
function toggleMapLayer() {
    const btn = document.getElementById("toggleSatelliteBtn");
    if (currentLayer === "streets") {
        map.removeLayer(streetTileLayer);
        satelliteTileLayer.addTo(map);
        currentLayer = "satellite";
        btn.innerHTML = `<i data-lucide="map" class="w-4 h-4 mr-1"></i> Ver Ruas`;
        btn.classList.add("bg-sky-700", "text-white");
    } else {
        map.removeLayer(satelliteTileLayer);
        streetTileLayer.addTo(map);
        currentLayer = "streets";
        btn.innerHTML = `<i data-lucide="satellite" class="w-4 h-4 mr-1"></i> Satélite`;
        btn.classList.remove("bg-sky-700", "text-white");
    }
    if (window.lucide) lucide.createIcons();
}

// Cria ícone SVG customizado para o poste
function createPoleIcon(status = "normal", isSelected = false) {
    let colorClass = "normal";
    if (status === "chamado_aberto") colorClass = "chamado_aberto";
    if (status === "urgente" || status === "defeito_urgente") colorClass = "urgente";
    if (isSelected) colorClass += " selected";

    return L.divIcon({
        className: "custom-div-icon",
        html: `
            <div class="pole-marker ${colorClass}" style="width: 28px; height: 28px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2v20M5 5h14M7 9h10M9 13h6"/>
                </svg>
            </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
        popupAnchor: [0, -14]
    });
}

// ==========================================
// CARREGAMENTO DE DADOS
// ==========================================
async function loadPoles(filtroStatus = null) {
    try {
        const filtros = {};
        if (filtroStatus) filtros.status = filtroStatus;

        const postes = await API.listarPostes(filtros);
        markerClusterGroup.clearLayers();
        markersMap.clear();

        postes.forEach(p => {
            const marker = L.marker([p.latitude, p.longitude], {
                icon: createPoleIcon(p.status)
            });

            marker.on("click", () => {
                selectPole(p);
            });

            marker.bindTooltip(`<b>${p.codigo}</b><br>${p.logradouro}`, {
                direction: "top",
                offset: [0, -10]
            });

            markersMap.set(p.codigo, marker);
            markerClusterGroup.addLayer(marker);
        });

    } catch (err) {
        console.error("Erro ao carregar postes:", err);
    }
}

async function loadStats() {
    try {
        const stats = await API.obterEstatisticas();
        document.getElementById("statTotalPostes").textContent = stats.total_postes.toLocaleString();
        document.getElementById("statTaxaLed").textContent = `${stats.taxa_led}%`;
        document.getElementById("statChamados").textContent = stats.total_chamados;
        document.getElementById("statOsAbertas").textContent = stats.os_abertas;
    } catch (err) {
        console.error("Erro ao carregar estatísticas:", err);
    }
}

// ==========================================
// SELEÇÃO E EXIBIÇÃO DO POSTE
// ==========================================
async function selectPole(posteSummary) {
    try {
        // Carrega dados completos do poste com histórico
        const poste = await API.obterPoste(posteSummary.codigo);
        activePole = poste;

        // Centraliza mapa suavemente
        map.flyTo([poste.latitude, poste.longitude], 18, { duration: 1.2 });

        // Abre gaveta lateral
        const drawer = document.getElementById("poleDrawer");
        drawer.classList.remove("translate-x-full");

        // Preenche campos
        document.getElementById("drawerCodigo").textContent = poste.codigo;
        
        // Status Badge
        const badge = document.getElementById("drawerStatusBadge");
        if (poste.status === "chamado_aberto") {
            badge.className = "px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800 border border-amber-300";
            badge.textContent = "Chamado Aberto";
        } else if (poste.status === "urgente" || poste.status === "defeito_urgente") {
            badge.className = "px-2.5 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 border border-red-300";
            badge.textContent = "Defeito Urgente";
        } else {
            badge.className = "px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300";
            badge.textContent = "Operação Normal";
        }

        document.getElementById("drawerLogradouro").textContent = poste.logradouro || "Não informado";
        document.getElementById("drawerBairro").textContent = poste.bairro || "Boa Saúde - Centro";
        document.getElementById("drawerReferencia").textContent = poste.referencia || "Sem ponto de referência";
        document.getElementById("drawerCoords").textContent = `${poste.latitude.toFixed(6)}, ${poste.longitude.toFixed(6)}`;
        document.getElementById("drawerLuminaria").textContent = `${poste.tipo_luminaria} (${poste.potencia}W)`;
        document.getElementById("drawerPoste").textContent = `${poste.tipo_poste} / ${poste.tipo_braco}`;
        document.getElementById("drawerObs").textContent = poste.observacoes || "Nenhuma observação cadastrada.";

        // Link Google Maps para navegação do motorista
        const gmapsBtn = document.getElementById("drawerGmapsBtn");
        gmapsBtn.href = `https://www.google.com/maps/dir/?api=1&destination=${poste.latitude},${poste.longitude}`;

        // Histórico de O.S.
        const histContainer = document.getElementById("drawerHistorico");
        histContainer.innerHTML = "";
        if (poste.historico_os && poste.historico_os.length > 0) {
            poste.historico_os.forEach(os => {
                const item = document.createElement("div");
                item.className = "p-2.5 bg-slate-50 border border-slate-200 rounded text-xs space-y-1";
                item.innerHTML = `
                    <div class="flex justify-between font-semibold text-slate-700">
                        <span>${os.protocolo}</span>
                        <span class="text-slate-500">${os.status.toUpperCase()}</span>
                    </div>
                    <div class="text-slate-600">${os.defeito}</div>
                    <div class="text-[11px] text-slate-400">Aberto em: ${new Date(os.data_abertura).toLocaleDateString("pt-BR")}</div>
                `;
                histContainer.appendChild(item);
            });
        } else {
            histContainer.innerHTML = `<p class="text-xs text-slate-400 italic">Nenhum chamado anterior registrado.</p>`;
        }

        if (window.lucide) lucide.createIcons();

    } catch (err) {
        alert("Erro ao carregar detalhes do poste: " + err.message);
    }
}

function closeDrawer() {
    document.getElementById("poleDrawer").classList.add("translate-x-full");
}

// ==========================================
// BUSCA INSTANTÂNEA POR CÓDIGO OU RUA
// ==========================================
let searchDebounceTimeout = null;

function setupEvents() {
    const searchInput = document.getElementById("searchInput");
    const searchResults = document.getElementById("searchResults");

    searchInput.addEventListener("input", (e) => {
        clearTimeout(searchDebounceTimeout);
        const termo = e.target.value.trim();

        if (termo.length === 0) {
            searchResults.classList.add("hidden");
            searchResults.innerHTML = "";
            return;
        }

        searchDebounceTimeout = setTimeout(async () => {
            try {
                const resultados = await API.buscarPostes(termo);
                searchResults.innerHTML = "";

                if (resultados.length === 0) {
                    searchResults.innerHTML = `
                        <div class="p-3 text-sm text-slate-500 text-center">
                            Nenhum poste encontrado com "<b>${termo}</b>"
                        </div>
                    `;
                } else {
                    resultados.forEach(p => {
                        const div = document.createElement("div");
                        div.className = "p-2.5 hover:bg-sky-50 cursor-pointer border-b border-slate-100 flex items-center justify-between text-sm transition-colors";
                        
                        let statusColor = "bg-emerald-500";
                        if (p.status === "chamado_aberto") statusColor = "bg-amber-500";
                        if (p.status === "urgente") statusColor = "bg-red-500";

                        div.innerHTML = `
                            <div>
                                <div class="font-bold text-slate-800 flex items-center gap-1.5">
                                    <span class="w-2 h-2 rounded-full ${statusColor}"></span>
                                    ${p.codigo}
                                </div>
                                <div class="text-xs text-slate-500">${p.logradouro} &bull; ${p.bairro}</div>
                            </div>
                            <span class="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600">${p.tipo_luminaria} ${p.potencia}W</span>
                        `;

                        div.addEventListener("click", () => {
                            searchResults.classList.add("hidden");
                            searchInput.value = p.codigo;
                            selectPole(p);
                        });

                        searchResults.appendChild(div);
                    });
                }
                searchResults.classList.remove("hidden");
            } catch (err) {
                console.error("Erro na busca:", err);
            }
        }, 200);
    });

    // Fecha dropdown se clicar fora
    document.addEventListener("click", (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add("hidden");
        }
    });

    // Enter direto na busca seleciona o primeiro
    searchInput.addEventListener("keydown", async (e) => {
        if (e.key === "Enter") {
            const termo = searchInput.value.trim();
            if (termo) {
                const resultados = await API.buscarPostes(termo);
                if (resultados.length > 0) {
                    searchResults.classList.add("hidden");
                    selectPole(resultados[0]);
                }
            }
        }
    });

    // Botão de Satélite
    document.getElementById("toggleSatelliteBtn").addEventListener("click", toggleMapLayer);

    // Botão GPS
    document.getElementById("locateMeBtn").addEventListener("click", locateUser);

    // Filtros de Status no Topo
    document.querySelectorAll(".filter-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active", "bg-sky-600", "text-white"));
            btn.classList.add("active", "bg-sky-600", "text-white");
            const status = btn.dataset.status;
            loadPoles(status === "todos" ? null : status);
        });
    });

    // Importador Drag & Drop
    setupImportEvents();
}

// GPS / Geolocalização em Campo
function locateUser() {
    if (!navigator.geolocation) {
        alert("Geolocalização não suportada pelo seu navegador.");
        return;
    }
    const btn = document.getElementById("locateMeBtn");
    btn.classList.add("animate-pulse");

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            btn.classList.remove("animate-pulse");
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;

            map.flyTo([lat, lng], 18);

            const userIcon = L.divIcon({
                className: "user-loc-icon",
                html: `<div class="w-4 h-4 bg-blue-600 rounded-full border-2 border-white shadow-lg animate-ping"></div>`,
                iconSize: [16, 16]
            });
            L.marker([lat, lng], { icon: userIcon }).addTo(map).bindPopup("Você está aqui").openPopup();
        },
        (err) => {
            btn.classList.remove("animate-pulse");
            alert("Não foi possível obter a sua localização GPS: " + err.message);
        },
        { enableHighAccuracy: true }
    );
}

// ==========================================
// MODAL DE ORDEM DE SERVIÇO & MATERIAIS
// ==========================================
function openOrderModal() {
    if (!activePole) return;

    document.getElementById("modalOsCodigo").textContent = activePole.codigo;
    document.getElementById("modalOsLocal").textContent = `${activePole.logradouro} - ${activePole.bairro}`;
    document.getElementById("modalOsLuminaria").textContent = `${activePole.tipo_luminaria} ${activePole.potencia}W`;

    // Sugere lâmpada com a potência exata do poste
    const lampadaCheck = document.getElementById("matLampadaCheck");
    const lampadaLabel = document.getElementById("matLampadaLabel");
    if (activePole.tipo_luminaria === "LED") {
        lampadaLabel.textContent = `Lâmpada LED ${activePole.potencia}W`;
    } else {
        lampadaLabel.textContent = `Lâmpada LED ${activePole.potencia}W (Modernização de ${activePole.tipo_luminaria})`;
    }
    lampadaCheck.checked = true;

    document.getElementById("orderModal").classList.remove("hidden");
    if (window.lucide) lucide.createIcons();
}

function closeOrderModal() {
    document.getElementById("orderModal").classList.add("hidden");
    document.getElementById("osCreatedSuccess").classList.add("hidden");
    document.getElementById("osFormContent").classList.remove("hidden");
}

async function submitOrder() {
    if (!activePole) return;

    const defeito = document.getElementById("osDefeito").value;
    const prioridade = document.getElementById("osPrioridade").value;
    const solicitante = document.getElementById("osSolicitante").value || "Secretaria de Infraestrutura";
    const observacoes = document.getElementById("osObs").value;

    // Coleta materiais selecionados
    const materiais = [];
    document.querySelectorAll(".material-checkbox:checked").forEach(cb => {
        const itemNome = cb.dataset.item;
        const qtdInput = document.querySelector(`.material-qtd[data-item="${itemNome}"]`);
        const qtd = qtdInput ? parseInt(qtdInput.value, 10) : 1;
        materiais.push({ item: itemNome, quantidade: qtd });
    });

    const payload = {
        codigo_poste: activePole.codigo,
        defeito,
        prioridade,
        materiais,
        solicitante,
        observacoes
    };

    try {
        const res = await API.criarOrdem(payload);

        // Exibe tela de sucesso e botão WhatsApp
        document.getElementById("osFormContent").classList.add("hidden");
        const successBox = document.getElementById("osCreatedSuccess");
        successBox.classList.remove("hidden");

        document.getElementById("successProtocolo").textContent = res.protocolo;

        // Monta mensagem do WhatsApp formatada para a equipe de eletricistas
        const materiaisTexto = materiais.map(m => `  • ${m.quantidade}x ${m.item}`).join("\n");
        const mapsLink = `https://www.google.com/maps/dir/?api=1&destination=${activePole.latitude},${activePole.longitude}`;
        
        const msgWhats = `🚨 *ORDEM DE SERVIÇO DE ILUMINAÇÃO PÚBLICA*\n` +
            `*Prefeitura de Boa Saúde / RN*\n\n` +
            `📄 *Protocolo:* ${res.protocolo}\n` +
            `📍 *Poste:* ${activePole.codigo}\n` +
            `🛣️ *Endereço:* ${activePole.logradouro} - ${activePole.bairro}\n` +
            `⚠️ *Defeito:* ${defeito} (Prioridade: ${prioridade})\n` +
            `💡 *Luminária:* ${activePole.tipo_luminaria} ${activePole.potencia}W\n\n` +
            `🧰 *MATERIAIS NECESSÁRIOS PARA A VIATURA:*\n${materiaisTexto || "  • Conforme vistoria no local"}\n\n` +
            `🧭 *ROTA GPS DO POSTE:*\n${mapsLink}`;

        const zapBtn = document.getElementById("osWhatsAppBtn");
        zapBtn.href = `https://wa.me/?text=${encodeURIComponent(msgWhats)}`;

        // Atualiza dados na tela
        loadStats();
        loadPoles();
        selectPole(activePole);

    } catch (err) {
        alert("Erro ao criar Ordem de Serviço: " + err.message);
    }
}

// ==========================================
// MODAL DE LISTAGEM DE ORDENS DE SERVIÇO
// ==========================================
async function openOrdersListModal() {
    const modal = document.getElementById("ordersListModal");
    modal.classList.remove("hidden");
    await refreshOrdersTable();
}

function closeOrdersListModal() {
    document.getElementById("ordersListModal").classList.add("hidden");
}

async function refreshOrdersTable() {
    try {
        const ordens = await API.listarOrdens();
        const tbody = document.getElementById("ordersTableBody");
        tbody.innerHTML = "";

        if (ordens.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-slate-500">Nenhuma Ordem de Serviço cadastrada.</td></tr>`;
            return;
        }

        ordens.forEach(os => {
            const tr = document.createElement("tr");
            tr.className = "border-b border-slate-100 hover:bg-slate-50 text-xs";

            let statusBadge = "bg-amber-100 text-amber-800";
            if (os.status === "concluida") statusBadge = "bg-emerald-100 text-emerald-800";
            if (os.status === "cancelada") statusBadge = "bg-slate-100 text-slate-600";

            const materiaisList = os.materiais && os.materiais.length > 0 
                ? os.materiais.map(m => `${m.quantidade}x ${m.item}`).join(", ")
                : "Sem materiais";

            tr.innerHTML = `
                <td class="p-3 font-bold text-slate-800">${os.protocolo}</td>
                <td class="p-3">
                    <span class="font-semibold text-sky-700 cursor-pointer hover:underline" onclick="closeOrdersListModal(); API.obterPoste('${os.codigo_poste}').then(selectPole)">
                        ${os.codigo_poste}
                    </span>
                    <div class="text-[11px] text-slate-500">${os.logradouro || ""}</div>
                </td>
                <td class="p-3 text-slate-700 font-medium">${os.defeito}</td>
                <td class="p-3 text-slate-600 max-w-xs truncate" title="${materiaisList}">${materiaisList}</td>
                <td class="p-3">
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-semibold ${statusBadge}">${os.status.toUpperCase()}</span>
                </td>
                <td class="p-3 text-right">
                    ${os.status !== "concluida" ? `
                        <button onclick="concluirOS('${os.protocolo}')" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded text-xs transition-colors">
                            Concluir Reparo
                        </button>
                    ` : `<span class="text-emerald-600 font-medium">Resolvido</span>`}
                </td>
            `;

            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Erro ao carregar lista de OS:", err);
    }
}

async function concluirOS(protocolo) {
    if (!confirm(`Deseja marcar o chamado ${protocolo} como concluído? O poste voltará ao status normal.`)) return;
    try {
        await API.atualizarStatusOrdem(protocolo, "concluida");
        await refreshOrdersTable();
        loadStats();
        loadPoles();
        if (activePole) selectPole(activePole);
    } catch (err) {
        alert("Erro ao concluir O.S.: " + err.message);
    }
}

// ==========================================
// IMPORTADOR DE PLANILHAS COSERN / ANEEL
// ==========================================
function openImportModal() {
    document.getElementById("importModal").classList.remove("hidden");
}

function closeImportModal() {
    document.getElementById("importModal").classList.add("hidden");
    document.getElementById("importResultBox").classList.add("hidden");
    document.getElementById("importFile").value = "";
}

function setupImportEvents() {
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("importFile");

    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("border-sky-500", "bg-sky-50");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("border-sky-500", "bg-sky-50");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("border-sky-500", "bg-sky-50");
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append("arquivo", file);

    const btn = document.getElementById("importSubmitBtn");
    btn.disabled = true;
    btn.textContent = "Processando arquivo...";

    try {
        const res = await API.importarPlanilha(formData);
        btn.disabled = false;
        btn.textContent = "Importar Planilha";

        const resultBox = document.getElementById("importResultBox");
        resultBox.classList.remove("hidden");
        resultBox.innerHTML = `
            <div class="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-sm">
                <p class="font-bold">✅ Importação concluída com sucesso!</p>
                <p>Total de linhas: <b>${res.total_linhas}</b></p>
                <p>Postes inseridos / atualizados: <b>${res.importados}</b></p>
                ${res.erros > 0 ? `<p class="text-amber-700">Avisos/Erros: ${res.erros}</p>` : ""}
            </div>
        `;

        loadStats();
        loadPoles();

    } catch (err) {
        btn.disabled = false;
        btn.textContent = "Importar Planilha";
        alert("Erro na importação: " + err.message);
    }
}
