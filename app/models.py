"""
Modelos de Dados (Pydantic)
Define a estrutura dos dados que transitam nas requisições da API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class PosteBase(BaseModel):
    codigo: str = Field(..., description="Código da plaqueta COSERN (ex: CSR-10492)")
    latitude: float = Field(..., description="Latitude geográfica")
    longitude: float = Field(..., description="Longitude geográfica")
    logradouro: Optional[str] = "Não informado"
    bairro: Optional[str] = "Centro"
    referencia: Optional[str] = ""
    tipo_luminaria: Optional[str] = "LED"
    potencia: Optional[int] = 100
    tipo_poste: Optional[str] = "Concreto Duplo T"
    tipo_braco: Optional[str] = "Braço Médio 2m"
    status: Optional[str] = "normal"
    observacoes: Optional[str] = ""

class PosteCreate(PosteBase):
    pass

class PosteResponse(PosteBase):
    id: int
    data_atualizacao: Optional[str] = None

class ItemMaterial(BaseModel):
    item: str
    quantidade: int

class OrdemServicoCreate(BaseModel):
    codigo_poste: str
    defeito: str
    prioridade: Optional[str] = "Normal"
    materiais: List[ItemMaterial] = []
    solicitante: Optional[str] = "Secretaria de Infraestrutura"
    observacoes: Optional[str] = ""

class OrdemServicoResponse(BaseModel):
    id: int
    protocolo: str
    codigo_poste: str
    defeito: str
    prioridade: str
    materiais: List[Dict[str, Any]] = []
    solicitante: str
    status: str
    data_abertura: str
    data_conclusao: Optional[str] = None
    observacoes: Optional[str] = ""
