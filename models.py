# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# TODO: Adicionar depois password_hash antes de salvar no banco de dados
# Modelo de Grupo (Group)
class Grupo(db.Model, UserMixin):
    __tablename__ = 'grupo'

    id = db.Column(db.Integer, primary_key=True)
    grupo_nome = db.Column(db.String(150), unique=True, nullable=False)  # Nome do grupo
    password = db.Column(db.String(150), nullable=False)
    periodo_atual = db.Column(db.Integer, nullable=False, default=12)  # Período atual do grupo
    estilo_demanda_id = db.Column(db.Integer, db.ForeignKey('estilo_demanda.id'), nullable=True)

    quantidade_teares = db.Column(db.Integer, nullable=False, default=0)
    quantidade_ramas = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo1 = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo2 = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo3 = db.Column(db.Integer, nullable=False, default=0)


    # Relacionamento com as outras tabelas(backref em ambos os modelos)
    planos_producao = db.relationship('PlanoProducao', backref='grupo', lazy=True)
    planos_compra = db.relationship('PlanoCompras', backref='grupo', lazy=True)
    capacidades_teares = db.relationship('CapacidadeTeares', backref='grupo', lazy=True)
    capacidades_jets = db.relationship('CapacidadeJets', backref='grupo', lazy=True)
    capacidades_ramas = db.relationship('CapacidadeRamas', backref='grupo', lazy=True)


# Modelo de Plano de Produção (PlanoProducao)
class PlanoProducao(db.Model):
    __tablename__ = 'plano_producao'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)  # Grupo associado
    periodo_numero = db.Column(db.Integer, nullable=False)  # Número do período (Ex: 1, 2, 3...)
    periodo_modificado = db.Column(db.Integer, nullable=False)  # Período no qual foi feita a alteração
    familia = db.Column(db.String(50), nullable=False)  # Família

    # Informações do Plano de Produção
    demanda_prevista = db.Column(db.Float, nullable=True)  # Demanda prevista
    demanda_real = db.Column(db.Float, nullable=True)  # Demanda real (após simulação)
    estoques_iniciais = db.Column(db.Float, nullable=True)  # Estoques Iniciais
    producao_planejada = db.Column(db.Float, nullable=False)  # Produção planejada
    producao_real = db.Column(db.Float, nullable=True)  # Produção real (após simulação)
    estoques_finais = db.Column(db.Float, nullable=True)  # Estoques Finais (após simulação)
    vendas_perdidas = db.Column(db.Float, nullable=True)  # Vendas Perdidas
    vendas = db.Column(db.Float, nullable=True)  # Vendas Efetivadas

# Modelo de Plano de Compras (PlanoCompras)
class PlanoCompras(db.Model):
    __tablename__ = 'plano_compras'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)  # Grupo associado
    periodo_numero = db.Column(db.Integer, nullable=False)  # Número do período (Ex: 1, 2, 3...)
    periodo_modificado = db.Column(db.Integer, nullable=False) # Período no qual foi feita a alteração

    material = db.Column(db.String(50), nullable=False)  # Ex: Fio Algodão, Fio Sintético, Corantes

    # Informações do Plano de Compras
    consumo_previsto = db.Column(db.Float, nullable=True)  # Consumo previsto
    consumo_real = db.Column(db.Float, nullable=True)  # Consumo real (após simulação)
    estoques_iniciais = db.Column(db.Float, nullable=True)  # Estoques Iniciais
    compra_planejada = db.Column(db.Float, nullable=False)  # Compras planejadas
    compra_real = db.Column(db.Float, nullable=True)  # Compras reais (após simulação)
    compra_emergencial = db.Column(db.Float, nullable=True)  # Compras Emergenciais (após simulação)
    estoques_finais = db.Column(db.Float, nullable=True)  # Estoques Finais (após simulação)


class EstiloDemanda(db.Model):
    __tablename__ = 'estilo_demanda'

    id = db.Column(db.Integer, primary_key=True)
    nome_estilo = db.Column(db.String(50), nullable=False, unique=True)  # Ex: 'Baixa', 'Média', 'Alta'

    # Quantidade Inicial
    quantidade_teares = db.Column(db.Integer, nullable=False, default=0)
    quantidade_ramas = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo1 = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo2 = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo3 = db.Column(db.Integer, nullable=False, default=0)

    # Relationship with Grupo
    grupos = db.relationship('Grupo', backref='estilo_demanda', lazy=True)



class PrevisaoDemanda(db.Model):
    __tablename__ = 'previsao_demanda'

    id = db.Column(db.Integer, primary_key=True)
    numero_periodo = db.Column(db.Integer, nullable=False)  # Ex: 1, 2, 3...
    familia = db.Column(db.String(50), nullable=False)  # Ex: 'Colmeia', 'Piquet', 'Maxim'
    valor_previsao = db.Column(db.Float, nullable=False)  # Valor da previsão de demanda
    estilo_demanda_id = db.Column(db.Integer, db.ForeignKey('estilo_demanda.id'), nullable=False)

    # Relacionamento com EstiloDemanda (várias previsões podem ter o mesmo estilo de demanda)
    estilo_demanda = db.relationship('EstiloDemanda', backref=db.backref('previsoes', lazy=True))


# Modelo de Capacidade Teares 
class CapacidadeTeares(db.Model):
    __tablename__ = 'capacidade_teares'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo_numero = db.Column(db.Integer, nullable=False)
    periodo_modificado = db.Column(db.Integer, nullable=False)

    capacidade_disponivel = db.Column(db.Float, nullable=True)
    capacidade_necessaria = db.Column(db.Float, nullable=True)
    capacidade_instalada = db.Column(db.Float, nullable=True)
    capacidade_terceirizada = db.Column(db.Float, nullable=True)

    colmeia = db.Column(db.Float, nullable=True)
    piquet = db.Column(db.Float, nullable=True)
    maxim = db.Column(db.Float, nullable=True)
    setup = db.Column(db.Float, nullable=True)
    produtividade = db.Column(db.Float, nullable=True)

    numero_turnos = db.Column(db.Integer, nullable=True)

# Modelo de Capacidade Jets
class CapacidadeJets(db.Model):
    __tablename__ = 'capacidade_jets'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo_numero = db.Column(db.Integer, nullable=False)
    periodo_modificado = db.Column(db.Integer, nullable=False)

    capacidade_disponivel = db.Column(db.Float, nullable=True)
    capacidade_necessaria = db.Column(db.Float, nullable=True)
    capacidade_terceirizada = db.Column(db.Float, nullable=True)
    capacidade_instalada = db.Column(db.Float, nullable=True)
    capacidade_instalada_tipo1 = db.Column(db.Float, nullable=True)
    capacidade_instalada_tipo2 = db.Column(db.Float, nullable=True)
    capacidade_instalada_tipo3 = db.Column(db.Float, nullable=True)

    colmeia = db.Column(db.Float, nullable=True)
    piquet = db.Column(db.Float, nullable=True)
    maxim = db.Column(db.Float, nullable=True)
    setup = db.Column(db.Float, nullable=True)
    produtividade = db.Column(db.Float, nullable=True)

    numero_turnos = db.Column(db.Integer, nullable=True)


# Modelo de Capacidade Ramas
class CapacidadeRamas(db.Model):
    __tablename__ = 'capacidade_ramas'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo_numero = db.Column(db.Integer, nullable=False)
    periodo_modificado = db.Column(db.Integer, nullable=False)

    capacidade_disponivel = db.Column(db.Float, nullable=True)
    capacidade_necessaria = db.Column(db.Float, nullable=True)
    capacidade_instalada = db.Column(db.Float, nullable=True)
    capacidade_terceirizada = db.Column(db.Float, nullable=True)

    colmeia = db.Column(db.Float, nullable=True)
    piquet = db.Column(db.Float, nullable=True)
    maxim = db.Column(db.Float, nullable=True)
    setup = db.Column(db.Float, nullable=True)
    produtividade = db.Column(db.Float, nullable=True)

    numero_turnos = db.Column(db.Integer, nullable=True)


class TaxaProducao(db.Model):
    __tablename__ = 'taxa_producao'

    id = db.Column(db.Integer, primary_key=True)
    familia = db.Column(db.String(50), nullable=False)          # 'Colmeia', 'Piquet', 'Maxim'
    processo = db.Column(db.String(50), nullable=False)         # 'Malharia', 'Purga', etc.
    tipo_equipamento = db.Column(db.String(50), nullable=False) # 'Teares', 'Jets', 'Ramas'
    taxa = db.Column(db.Float, nullable=False)

    # Caso as taxas dependem do Estilo demanda
    estilo_demanda_id = db.Column(db.Integer, db.ForeignKey('estilo_demanda.id'), nullable=True)
    estilo_demanda = db.relationship('EstiloDemanda', backref=db.backref('taxas_producao', lazy=True))
