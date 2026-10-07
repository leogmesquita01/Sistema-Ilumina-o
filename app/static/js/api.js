/**
 * Módulo de Comunicação com a API Python (FastAPI)
 */

const API = {
    async listarPostes(filtros = {}) {
        const params = new URLSearchParams(filtros);
        const res = await fetch(`/api/postes?${params.toString()}`);
        if (!res.ok) throw new Error("Erro ao carregar postes");
        return await res.json();
    },

    async buscarPostes(termo) {
        if (!termo || termo.trim().length === 0) return [];
        const res = await fetch(`/api/postes/buscar?q=${encodeURIComponent(termo.trim())}`);
        if (!res.ok) throw new Error("Erro na busca de postes");
        return await res.json();
    },

    async obterPoste(codigo) {
        const res = await fetch(`/api/postes/${encodeURIComponent(codigo.trim())}`);
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Poste não encontrado");
        }
        return await res.json();
    },

    async cadastrarPoste(dados) {
        const res = await fetch("/api/postes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Erro ao cadastrar poste");
        }
        return await res.json();
    },

    async listarOrdens(status = null) {
        let url = "/api/ordens-servico";
        if (status) url += `?status=${encodeURIComponent(status)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("Erro ao listar ordens de serviço");
        return await res.json();
    },

    async criarOrdem(dados) {
        const res = await fetch("/api/ordens-servico", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Erro ao gerar ordem de serviço");
        }
        return await res.json();
    },

    async atualizarStatusOrdem(protocolo, status) {
        const res = await fetch(`/api/ordens-servico/${protocolo}/status?status=${encodeURIComponent(status)}`, {
            method: "PATCH"
        });
        if (!res.ok) throw new Error("Erro ao atualizar status da O.S.");
        return await res.json();
    },

    async obterEstatisticas() {
        const res = await fetch("/api/estatisticas");
        if (!res.ok) throw new Error("Erro ao obter estatísticas");
        return await res.json();
    },

    async importarPlanilha(formData) {
        const res = await fetch("/api/importar", {
            method: "POST",
            body: formData
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Erro ao importar planilha");
        }
        return await res.json();
    }
};

window.API = API;
