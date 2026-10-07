"""
Dados Iniciais de Demonstração (Seed Data)
Cadastra postes e ordens de serviço realistas no município de Boa Saúde / RN
para demonstração e testes imediatos.
"""

from app.database.conexao import obter_conexao as get_connection, inicializar_banco as init_db

# Postes de exemplo baseados na malha urbana e comunidades de Boa Saúde / RN
SAMPLE_POSTES = [
    # Centro e Entorno da Praça da Matriz
    {
        "codigo": "CSR-1001",
        "latitude": -6.16112,
        "longitude": -35.60251,
        "logradouro": "Praça Monsenhor Expedito",
        "bairro": "Centro",
        "referencia": "Em frente à Igreja Matriz",
        "tipo_luminaria": "LED",
        "potencia": 150,
        "tipo_poste": "Concreto Circular",
        "tipo_braco": "Pétala Dupla",
        "status": "normal",
        "observacoes": "Luminária de alta potência instalada na revitalização da praça."
    },
    {
        "codigo": "CSR-1002",
        "latitude": -6.16145,
        "longitude": -35.60280,
        "logradouro": "Rua Manoel Cirilo",
        "bairro": "Centro",
        "referencia": "Esquina com o Mercado Público",
        "tipo_luminaria": "Vapor de Sódio",
        "potencia": 70,
        "tipo_poste": "Concreto Duplo T",
        "tipo_braco": "Braço Médio 2m",
        "status": "chamado_aberto",
        "observacoes": "Morador informou que a lâmpada pisca e apaga por volta das 20h."
    },
    {
        "codigo": "CSR-1003",
        "latitude": -6.16080,
        "longitude": -35.60210,
        "logradouro": "Rua Pedro Freire",
        "bairro": "Centro",
        "referencia": "Próximo à Secretaria de Obras e Infraestrutura",
        "tipo_luminaria": "LED",
        "potencia": 100,
        "tipo_poste": "Concreto Duplo T",
        "tipo_braco": "Braço Médio 2m",
        "status": "normal",
        "observacoes": "Poste com transformador acoplado."
    },
    {
        "codigo": "CSR-1004",
        "latitude": -6.16185,
        "longitude": -35.60330,
        "logradouro": "Rua Severino Ramos",
        "bairro": "Centro",
        "referencia": "Próximo à Unidade Básica de Saúde (UBS)",
        "tipo_luminaria": "Vapor de Sódio",
        "potencia": 70,
        "tipo_poste": "Concreto Duplo T",
        "tipo_braco": "Braço Curto 1m",
        "status": "defeito_urgente",
        "observacoes": "Relé fotoelétrico colado. Lâmpada acesa 24 horas, risco de curto."
    },
    {
        "codigo": "CSR-1005",
        "latitude": -6.16230,
        "longitude": -35.60395,
        "logradouro": "Av. São Francisco",
        "bairro": "Centro",
        "referencia": "Entrada principal da cidade",
        "tipo_luminaria": "LED",
        "potencia": 150,
        "tipo_poste": "Concreto Circular",
        "tipo_braco": "Braço Longo 3m",
        "status": "normal",
        "observacoes": "Avenida principal, luminária moderna."
    },
    {
        "codigo": "CSR-1006",
        "latitude": -6.16010,
        "longitude": -35.60150,
        "logradouro": "Rua São José",
        "bairro": "Centro",
        "referencia": "Ao lado da Farmácia Popular",
        "tipo_luminaria": "LED",
        "potencia": 100,
        "tipo_poste": "Concreto Duplo T",
        "tipo_braco": "Braço Médio 2m",
        "status": "normal",
        "observacoes": "Substituído recentemente em mutirão."
    },
    # Bairro Bela Vista / Alto
    {
        "codigo": "CSR-1007",
        "latitude": -6.15920,
        "longitude": -35.60080,
        "logradouro": "Rua Bela Vista",
        "bairro": "Bela Vista",
        "referencia": "Subida da caixa d'água",
        "tipo_luminaria": "Vapor de Mercúrio",
        "potencia": 125,
        "tipo_poste": "Concreto Duplo T",
        "tipo_braco": "Braço Médio 2m",
        "status": "chamado_aberto",
        "observacoes": "Lâmpada antiga que queimou na última chuva."
    },
    {
        "codigo": "CSR-1008",
        "latitude": -6.15870,
        "longitude": -35.60010,
        "logradouro": "Rua João Pessoa",
        "bairro": "Bela Vista",
        "referencia": "Próximo à Escola Municipal",
        "tipo_luminaria": "LED",
        "potencia": 100,
        "tipo_poste": "Concreto Duplo T",
        "tipo_braco": "Braço Médio 2m",
        "status": "normal",
        "observacoes": "Iluminação do entorno escolar."
    },
    # Comunidades Rurais de Boa Saúde
    {
        "codigo": "CSR-1009",
        "latitude": -6.16540,
        "longitude": -35.60820,
        "logradouro": "Estrada Principal",
        "bairro": "Comunidade Lagoa do Mato",
        "referencia": "Em frente ao campo de futebol de terra",
        "tipo_luminaria": "Vapor de Sódio",
        "potencia": 70,
        "tipo_poste": "Madeira Tratada",
        "tipo_braco": "Braço Curto 1m",
        "status": "normal",
        "observacoes": "Poste de madeira em bom estado na zona rural."
    },
    {
        "codigo": "CSR-1010",
        "latitude": -6.16680,
        "longitude": -35.61100,
        "logradouro": "Acesso ao Sítio Córrego",
        "bairro": "Comunidade Córrego",
        "referencia": "Bifurcação para o poço comunitário",
        "tipo_luminaria": "LED",
        "potencia": 100,
        "tipo_poste": "Concreto Duplo T",
        "tipo_braco": "Braço Médio 2m",
        "status": "chamado_aberto",
        "observacoes": "Falta de energia pontual ou relé desconectado."
    },
    {
        "codigo": "CSR-1011",
        "latitude": -6.15650,
        "longitude": -35.59720,
        "logradouro": "Estrada do Manhoso",
        "bairro": "Comunidade Manhoso",
        "referencia": "Próximo à Associação dos Produtores",
        "tipo_luminaria": "Vapor de Sódio",
        "potencia": 70,
        "tipo_poste": "Concreto Duplo T",
        "tipo_braco": "Braço Médio 2m",
        "status": "normal",
        "observacoes": "Rede monofásica rural."
    },
    {
        "codigo": "CSR-1012",
        "latitude": -6.16310,
        "longitude": -35.60520,
        "logradouro": "Rua Projetada A",
        "bairro": "Novo Horizonte",
        "referencia": "Loteamento novo",
        "tipo_luminaria": "LED",
        "potencia": 100,
        "tipo_poste": "Concreto Circular",
        "tipo_braco": "Braço Médio 2m",
        "status": "normal",
        "observacoes": "Instalado no padrão novo da Neoenergia."
    }
]

SAMPLE_ORDENS = [
    {
        "protocolo": "OS-2026-001",
        "codigo_poste": "CSR-1002",
        "defeito": "Lâmpada piscando e apagando",
        "prioridade": "Normal",
        "materiais": '[{"item": "Lâmpada LED 100W", "quantidade": 1}, {"item": "Relé Fotoelétrico", "quantidade": 1}]',
        "solicitante": "Morador via Ouvidoria",
        "status": "aberta",
        "observacoes": "Substituir luminária de vapor de sódio 70W antiga por LED 100W."
    },
    {
        "protocolo": "OS-2026-002",
        "codigo_poste": "CSR-1004",
        "defeito": "Relé colado (lâmpada acesa o dia todo)",
        "prioridade": "Urgente",
        "materiais": '[{"item": "Relé Fotoelétrico 100-240V", "quantidade": 1}, {"item": "Conector Perfurante", "quantidade": 2}]',
        "solicitante": "Secretaria de Infraestrutura",
        "status": "aberta",
        "observacoes": "Rua do posto de saúde, trocar o relé urgente para economizar energia da prefeitura."
    }
]

def seed_database():
    """Popula o banco com os postes de exemplo caso esteja vazio."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM postes;")
    count = cursor.fetchone()[0]

    if count == 0:
        print("Populando banco com postes de Boa Saúde/RN...")
        for p in SAMPLE_POSTES:
            cursor.execute("""
                INSERT OR IGNORE INTO postes (
                    codigo, latitude, longitude, logradouro, bairro, referencia,
                    tipo_luminaria, potencia, tipo_poste, tipo_braco, status, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["codigo"], p["latitude"], p["longitude"], p["logradouro"], p["bairro"],
                p["referencia"], p["tipo_luminaria"], p["potencia"], p["tipo_poste"],
                p["tipo_braco"], p["status"], p["observacoes"]
            ))

        for os_item in SAMPLE_ORDENS:
            cursor.execute("""
                INSERT OR IGNORE INTO ordens_servico (
                    protocolo, codigo_poste, defeito, prioridade, materiais, solicitante, status, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_item["protocolo"], os_item["codigo_poste"], os_item["defeito"],
                os_item["prioridade"], os_item["materiais"], os_item["solicitante"],
                os_item["status"], os_item["observacoes"]
            ))

        conn.commit()
        print(f"Banco populado com {len(SAMPLE_POSTES)} postes e {len(SAMPLE_ORDENS)} ordens de serviço!")
    else:
        print(f"O banco já possui {count} postes cadastrados.")

    conn.close()

if __name__ == "__main__":
    seed_database()
