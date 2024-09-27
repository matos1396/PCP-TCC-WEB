# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Modelo de Grupo (Group)
class Group(db.Model, UserMixin):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(150), unique=True, nullable=False)  # Nome do grupo
    password = db.Column(db.String(150), nullable=False)
    current_period = db.Column(db.Integer, nullable=False, default=1)  # Período atual do grupo
    modified_period = db.Column(db.Integer, nullable=False)  # Período no qual foi feita a alteração

    # Relacionamento com ProductionPlan e PurchasePlan (backref em ambos os modelos)
    production_plans = db.relationship('ProductionPlan', backref='group', lazy=True)
    purchase_plans = db.relationship('PurchasePlan', backref='group', lazy=True)

    # Adicione outros campos relevantes para o grupo se necessário (ex: email, senha, etc.)

# Modelo de Plano de Produção (ProductionPlan)
class ProductionPlan(db.Model):
    __tablename__ = 'production_plan'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)  # Grupo associado
    period_number = db.Column(db.Integer, nullable=False)  # Número do período (Ex: 1, 2, 3...)

    # Família de Produtos
    family = db.Column(db.String(50), nullable=False)  # Ex: Colméia, Piquet, Maxim

    # Informações do Plano de Produção
    demanda_prevista = db.Column(db.Integer, nullable=True)  # Demanda prevista
    demanda_real = db.Column(db.Integer, nullable=True)  # Demanda real (após simulação)
    estoques_iniciais = db.Column(db.Integer, nullable=True)  # Estoques Iniciais
    planned_production = db.Column(db.Integer, nullable=False)  # Produção planejada
    real_production = db.Column(db.Integer, nullable=True)  # Produção real (após simulação)
    estoques_finais = db.Column(db.Integer, nullable=True)  # Estoques Finais (após simulação)
    vendas_perdidas = db.Column(db.Integer, nullable=True)  # Vendas Perdidas
    vendas = db.Column(db.Integer, nullable=True)  # Vendas Efetivadas
    
    # Relacionamento com o grupo (via ForeignKey group_id)

# Modelo de Plano de Compras (PurchasePlan)
class PurchasePlan(db.Model):
    __tablename__ = 'purchase_plan'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)  # Grupo associado
    period_number = db.Column(db.Integer, nullable=False)  # Número do período (Ex: 1, 2, 3...)

    # Tipo de Material
    material = db.Column(db.String(50), nullable=False)  # Ex: Fio Algodão, Fio Sintético, Corantes

    # Informações do Plano de Compras
    consumo_previsto = db.Column(db.Integer, nullable=True)  # Consumo previsto
    consumo_real = db.Column(db.Integer, nullable=True)  # Consumo real (após simulação)
    estoques_iniciais = db.Column(db.Integer, nullable=True)  # Estoques Iniciais
    planned_purchase = db.Column(db.Integer, nullable=False)  # Compras planejadas
    real_purchase = db.Column(db.Integer, nullable=True)  # Compras reais (após simulação)
    estoques_finais = db.Column(db.Integer, nullable=True)  # Estoques Finais (após simulação)