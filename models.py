# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, inspect


db = SQLAlchemy()

# Tabelas associativas para relacionar TaxaProducao com as tabelas de capacidade por equipamento
taxa_teares_associativa = db.Table('taxa_teares_associativa',
    db.Column('taxa_producao_id', db.Integer, db.ForeignKey('taxa_producao.id'), primary_key=True),
    db.Column('capacidade_teares_id', db.Integer, db.ForeignKey('capacidade_teares.id'), primary_key=True),
    db.Column('processo', db.String(50), nullable=False)
)

taxa_jets_associativa = db.Table('taxa_jets_associativa',
    db.Column('taxa_producao_id', db.Integer, db.ForeignKey('taxa_producao.id'), primary_key=True),
    db.Column('capacidade_jets_id', db.Integer, db.ForeignKey('capacidade_jets.id'), primary_key=True),
    db.Column('processo', db.String(50), nullable=False)
)

taxa_ramas_associativa = db.Table('taxa_ramas_associativa',
    db.Column('taxa_producao_id', db.Integer, db.ForeignKey('taxa_producao.id'), primary_key=True),
    db.Column('capacidade_ramas_id', db.Integer, db.ForeignKey('capacidade_ramas.id'), primary_key=True),
    db.Column('processo', db.String(50), nullable=False)
)

# Modelo de Grupo (Group)
class Grupo(db.Model, UserMixin):
    __tablename__ = 'grupo'

    id = db.Column(db.Integer, primary_key=True)
    grupo_nome = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    periodo_atual = db.Column(db.Integer, nullable=False, default=12)
    estilo_demanda_id = db.Column(db.Integer, db.ForeignKey('estilo_demanda.id'), nullable=True)

    quantidade_teares = db.Column(db.Integer, nullable=False, default=0)
    quantidade_ramas = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo1 = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo2 = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo3 = db.Column(db.Integer, nullable=False, default=0)

    planos_producao = db.relationship('PlanoProducao', backref='grupo', lazy=True)
    planos_compra = db.relationship('PlanoCompras', backref='grupo', lazy=True)
    capacidades_teares = db.relationship('CapacidadeTeares', backref='grupo', lazy=True)
    capacidades_jets = db.relationship('CapacidadeJets', backref='grupo', lazy=True)
    capacidades_ramas = db.relationship('CapacidadeRamas', backref='grupo', lazy=True)


# Modelo de Plano de Produção (PlanoProducao)
class PlanoProducao(db.Model):
    __tablename__ = 'plano_producao'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo_numero = db.Column(db.Integer, nullable=False)
    periodo_modificado = db.Column(db.Integer, nullable=False)
    familia = db.Column(db.String(50), nullable=False)

    demanda_prevista = db.Column(db.Float, nullable=True)
    demanda_real = db.Column(db.Float, nullable=True)
    estoques_iniciais = db.Column(db.Float, nullable=True)
    producao_planejada = db.Column(db.Float, nullable=False)
    producao_real = db.Column(db.Float, nullable=True)
    estoques_finais = db.Column(db.Float, nullable=True)
    vendas_perdidas = db.Column(db.Float, nullable=True)
    vendas = db.Column(db.Float, nullable=True)

# Modelo de Plano de Compras (PlanoCompras)
class PlanoCompras(db.Model):
    __tablename__ = 'plano_compras'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo_numero = db.Column(db.Integer, nullable=False)
    periodo_modificado = db.Column(db.Integer, nullable=False)

    material = db.Column(db.String(50), nullable=False)
    consumo_previsto = db.Column(db.Float, nullable=True)
    consumo_real = db.Column(db.Float, nullable=True)
    estoques_iniciais = db.Column(db.Float, nullable=True)
    compra_planejada = db.Column(db.Float, nullable=False, default=0)
    compra_real = db.Column(db.Float, nullable=True)
    compra_emergencial = db.Column(db.Float, nullable=True)
    estoques_finais = db.Column(db.Float, nullable=True)


class EstiloDemanda(db.Model):
    __tablename__ = 'estilo_demanda'

    id = db.Column(db.Integer, primary_key=True)
    nome_estilo = db.Column(db.String(50), nullable=False, unique=True)

    quantidade_teares = db.Column(db.Integer, nullable=False, default=0)
    quantidade_ramas = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo1 = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo2 = db.Column(db.Integer, nullable=False, default=0)
    quantidade_jets_tipo3 = db.Column(db.Integer, nullable=False, default=0)

    grupos = db.relationship('Grupo', backref='estilo_demanda', lazy=True)


class PrevisaoDemanda(db.Model):
    __tablename__ = 'previsao_demanda'

    id = db.Column(db.Integer, primary_key=True)
    numero_periodo = db.Column(db.Integer, nullable=False)
    familia = db.Column(db.String(50), nullable=False)
    valor_previsao = db.Column(db.Float, nullable=False)
    estilo_demanda_id = db.Column(db.Integer, db.ForeignKey('estilo_demanda.id'), nullable=False)

    estilo_demanda = db.relationship('EstiloDemanda', backref=db.backref('previsoes', lazy=True))


# Modelo de Capacidade Teares 
class CapacidadeTeares(db.Model):
    __tablename__ = 'capacidade_teares'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo_numero = db.Column(db.Integer, nullable=False)
    periodo_modificado = db.Column(db.Integer, nullable=False)

    quantidade = db.Column(db.Float, nullable=True)
    capacidade_disponivel = db.Column(db.Float, nullable=True)
    capacidade_necessaria = db.Column(db.Float, nullable=True)
    capacidade_instalada = db.Column(db.Float, nullable=True)
    capacidade_terceirizada = db.Column(db.Integer, nullable=True, default=0)

    colmeia = db.Column(db.Float, nullable=True)
    piquet = db.Column(db.Float, nullable=True)
    maxim = db.Column(db.Float, nullable=True)
    setup = db.Column(db.Float, nullable=True)
    produtividade = db.Column(db.Float, nullable=True, default=0.1)
    numero_turnos = db.Column(db.Integer, nullable=True, default=2)

    validacao = db.Column(db.Boolean, nullable=False)

    # Relacionamento com TaxaProducao
    taxas_producao = db.relationship('TaxaProducao', secondary=taxa_teares_associativa, backref='capacidade_teares')


    # Atualizar capacidade instalada automaticamente
    @staticmethod
    def _calcular_capacidade_instalada(mapper, connection, target):
        state = inspect(target)
        # Checar se `quantidade` ou `numero_turnos` foram modificados
        #if state.attrs.quantidade.history.has_changes() or state.attrs.numero_turnos.history.has_changes():
        if target.quantidade and target.numero_turnos is not None:
            target.capacidade_instalada = target.quantidade * 7 * target.numero_turnos * 20
        else: 
            target.capacidade_instalada = 0

        CapacidadeTeares._calcular_capacidade_disponivel(target)
        CapacidadeTeares._calcular_produtividade(target)
        CapacidadeTeares._calcular_tempo_setup(target)
        CapacidadeTeares._validacao(target)

    @staticmethod
    def _calcular_capacidade_disponivel(target):
        if target.capacidade_instalada and target.capacidade_terceirizada is not None:
            target.capacidade_disponivel = target.capacidade_instalada + float(target.capacidade_terceirizada)
        else:
            target.capacidade_disponivel = 0

    @staticmethod
    def _calcular_produtividade(target):
        if target.colmeia and target.piquet and target.maxim is not None:
            target.produtividade = (target.colmeia + target.piquet + target.maxim) * 0.1 # 10% Perda Produtividade
        else:
            target.produtividade = 0

    @staticmethod
    def _calcular_tempo_setup(target):
        if target.quantidade and target.numero_turnos is not None:
            target.setup = target.quantidade * 4 * 0.25
        else:
            target.setup = 0

    @staticmethod
    def _validacao(target):
        if target.capacidade_disponivel >= target.capacidade_necessaria:
            target.validacao = True
        else: target.validacao = False

    @classmethod # Event listener para atualizar valores quando atualizar db
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls._calcular_capacidade_instalada)
        event.listen(cls, 'before_insert', cls._calcular_capacidade_instalada)



# Modelo de Capacidade Jets
class CapacidadeJets(db.Model):
    __tablename__ = 'capacidade_jets'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo_numero = db.Column(db.Integer, nullable=False)
    periodo_modificado = db.Column(db.Integer, nullable=False)

    quantidade_tipo1 = db.Column(db.Float, nullable=True)
    quantidade_tipo2 = db.Column(db.Float, nullable=True)
    quantidade_tipo3 = db.Column(db.Float, nullable=True)
    capacidade_tipo1 = db.Column(db.Float, nullable=True)
    capacidade_tipo2 = db.Column(db.Float, nullable=True)
    capacidade_tipo3 = db.Column(db.Float, nullable=True)
    capacidade_disponivel = db.Column(db.Float, nullable=True)
    capacidade_necessaria = db.Column(db.Float, nullable=True)
    capacidade_terceirizada = db.Column(db.Integer, nullable=True)
    capacidade_instalada = db.Column(db.Float, nullable=True)
    capacidade_instalada_tipo1 = db.Column(db.Float, nullable=True)
    capacidade_instalada_tipo2 = db.Column(db.Float, nullable=True)
    capacidade_instalada_tipo3 = db.Column(db.Float, nullable=True)

    colmeia = db.Column(db.Float, nullable=True)
    piquet = db.Column(db.Float, nullable=True)
    maxim = db.Column(db.Float, nullable=True)
    setup = db.Column(db.Float, nullable=True)
    produtividade = db.Column(db.Float, nullable=True, default=0.1)
    numero_turnos = db.Column(db.Integer, nullable=True, default=2)

    validacao = db.Column(db.Boolean, nullable=False)

    # Relacionamento com TaxaProducao
    taxas_producao = db.relationship('TaxaProducao', secondary=taxa_jets_associativa, backref='capacidade_jets')
    
    # Atualizar capacidade instalada automaticamente
    @staticmethod
    def _calcular_capacidade_instalada(mapper, connection, target):
        print(target.quantidade_tipo1)
        print(target.quantidade_tipo2)
        print(target.quantidade_tipo3)
        print(target.numero_turnos)
        if None not in (target.quantidade_tipo1, target.quantidade_tipo2, target.quantidade_tipo3, target.numero_turnos):
            print("ENTROU")
            target.capacidade_instalada_tipo1 = (7 * 20 * target.numero_turnos * target.quantidade_tipo1 * target.capacidade_tipo1) / 4.5 # Carga Média entre Purga/Tinturaria
            target.capacidade_instalada_tipo2 = (7 * 20 * target.numero_turnos * target.quantidade_tipo2 * target.capacidade_tipo2) / 4.5 # Carga Média entre Purga/Tinturaria
            target.capacidade_instalada_tipo3 = (7 * 20 * target.numero_turnos * target.quantidade_tipo3 * target.capacidade_tipo3) / 4.5 # Carga Média entre Purga/Tinturaria
            target.capacidade_instalada = target.capacidade_instalada_tipo1 + target.capacidade_instalada_tipo2 + target.capacidade_instalada_tipo3
        else: 
            target.capacidade_instalada = 0

        CapacidadeJets._calcular_capacidade_disponivel(target)
        CapacidadeJets._calcular_produtividade(target)
        CapacidadeJets._calcular_tempo_setup(target)
        CapacidadeJets._validacao(target)

    @staticmethod
    def _calcular_capacidade_disponivel(target):
        if None not in (target.capacidade_instalada, target.capacidade_terceirizada):
            target.capacidade_disponivel = target.capacidade_instalada + float(target.capacidade_terceirizada)
        else:
            target.capacidade_disponivel = 0

    @staticmethod
    def _calcular_produtividade(target):
        if None not in (target.colmeia, target.piquet, target.maxim):
            target.produtividade = (target.colmeia + target.piquet + target.maxim) * 0.15 # 10% Perda Produtividade
        else:
            target.produtividade = 0

    @staticmethod
    def _calcular_tempo_setup(target):
        if None not in (target.colmeia, target.piquet, target.maxim):
            target.setup = (target.colmeia + target.piquet + target.maxim) * 0.20 # 3 familias
        else:
            target.setup = 0

    @staticmethod
    def _validacao(target):
        if target.capacidade_disponivel >= target.capacidade_necessaria:
            target.validacao = True
        else: target.validacao = False


    @classmethod # Event listener para atualizar valores quando atualizar db
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls._calcular_capacidade_instalada)
        event.listen(cls, 'before_insert', cls._calcular_capacidade_instalada)

# Modelo de Capacidade Ramas
class CapacidadeRamas(db.Model):
    __tablename__ = 'capacidade_ramas'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo_numero = db.Column(db.Integer, nullable=False)
    periodo_modificado = db.Column(db.Integer, nullable=False)

    quantidade = db.Column(db.Float, nullable=True)
    capacidade_disponivel = db.Column(db.Float, nullable=True)
    capacidade_necessaria = db.Column(db.Float, nullable=True)
    capacidade_instalada = db.Column(db.Float, nullable=True)
    capacidade_terceirizada = db.Column(db.Integer, nullable=True)

    colmeia = db.Column(db.Float, nullable=True)
    piquet = db.Column(db.Float, nullable=True)
    maxim = db.Column(db.Float, nullable=True)
    setup = db.Column(db.Float, nullable=True)
    produtividade = db.Column(db.Float, nullable=True, default=0.1)
    numero_turnos = db.Column(db.Integer, nullable=True, default=2)

    validacao = db.Column(db.Boolean, nullable=False)

    # Relacionamento com TaxaProducao
    taxas_producao = db.relationship('TaxaProducao', secondary=taxa_ramas_associativa, backref='capacidade_ramas')

    # Atualizar capacidade instalada automaticamente
    @staticmethod
    def _calcular_capacidade_instalada(mapper, connection, target):
        state = inspect(target)
        # Checar se `quantidade` ou `numero_turnos` foram modificados
        #if state.attrs.quantidade.history.has_changes() or state.attrs.numero_turnos.history.has_changes():
        if target.quantidade and target.numero_turnos is not None:
            target.capacidade_instalada = target.quantidade * 7 * target.numero_turnos * 20
        else: 
            target.capacidade_instalada = 0

        CapacidadeRamas._calcular_capacidade_disponivel(target)
        CapacidadeRamas._calcular_produtividade(target)
        CapacidadeRamas._calcular_tempo_setup(target)
        CapacidadeRamas._validacao(target)

    @staticmethod
    def _calcular_capacidade_disponivel(target):
        if target.capacidade_instalada and target.capacidade_terceirizada is not None:
            target.capacidade_disponivel = target.capacidade_instalada + float(target.capacidade_terceirizada)
        else:
            target.capacidade_disponivel = 0

    @staticmethod
    def _calcular_produtividade(target):
        if target.colmeia and target.piquet and target.maxim is not None:
            target.produtividade = (target.colmeia + target.piquet + target.maxim) * 0.15 # 10% Perda Produtividade
        else:
            target.produtividade = 0

    @staticmethod
    def _calcular_tempo_setup(target):
        if target.quantidade and target.numero_turnos is not None:
            target.setup = target.quantidade * 4 * 0.25
        else:
            target.setup = 0

    @staticmethod
    def _validacao(target):
        if target.capacidade_disponivel >= target.capacidade_necessaria:
            target.validacao = True
        else: target.validacao = False

    @classmethod # Event listener para atualizar valores quando atualizar db
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls._calcular_capacidade_instalada)
        event.listen(cls, 'before_insert', cls._calcular_capacidade_instalada)

class TaxaProducao(db.Model):
    __tablename__ = 'taxa_producao'

    id = db.Column(db.Integer, primary_key=True)
    familia = db.Column(db.String(50), nullable=False)          # 'Colmeia', 'Piquet', 'Maxim'
    processo = db.Column(db.String(50), nullable=False)         # 'Malharia', 'Purga', etc.
    tipo_equipamento = db.Column(db.String(50), nullable=False) # 'Teares', 'Jets', 'Ramas'
    taxa = db.Column(db.Float, nullable=False)

    estilo_demanda_id = db.Column(db.Integer, db.ForeignKey('estilo_demanda.id'), nullable=True)
    estilo_demanda = db.relationship('EstiloDemanda', backref=db.backref('taxas_producao', lazy=True))


class RelatorioFinanceiro(db.Model):
    __tablename__ = 'relatorio_financeiro'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)  # Associação com o Grupo
    periodo = db.Column(db.Integer, nullable=False)

    # Colunas de custos e receitas
    custos_fixos = db.Column(db.Float, nullable=False, default=0.0)
    custos_compra_mp = db.Column(db.Float, nullable=False, default=0.0)
    custos_estoques = db.Column(db.Float, nullable=False, default=0.0)
    custos_terceirizacao = db.Column(db.Float, nullable=False, default=0.0)
    custos_capital = db.Column(db.Float, nullable=False, default=0.0)
    custos_vendas_perdidas = db.Column(db.Float, nullable=False, default=0.0)
    custos_totais = db.Column(db.Float, nullable=False, default=0.0)
    receitas_vendas = db.Column(db.Float, nullable=False, default=0.0)
    resultado_operacional = db.Column(db.Float, nullable=False, default=0.0)
    ro_acumulado = db.Column(db.Float, nullable=False, default=0.0)

    # Relacionamento com o Grupo (backref permite acessar relatórios financeiros a partir do grupo)
    grupo = db.relationship('Grupo', backref=db.backref('relatorios_financeiros', lazy=True))

    # Opcional: adiciona um método para calcular custos totais e resultado operacional se necessário
    def calcular_custos_totais(self):
        self.custos_totais = (self.custos_fixos + self.custos_compra_mp + self.custos_estoques +
                              self.custos_terceirizacao + self.custos_capital + self.custos_vendas_perdidas)
        self.resultado_operacional = self.receitas_vendas - self.custos_totais

class CustosFixos(db.Model):
    __tablename__ = 'custos_fixos'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)

    grupo = db.relationship('Grupo', backref=db.backref('custos_fixos', lazy=True))


class CustosCompraMP(db.Model):
    __tablename__ = 'custos_compra_mp'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)

    grupo = db.relationship('Grupo', backref=db.backref('custos_compra_mp', lazy=True))


class CustosEstoques(db.Model):
    __tablename__ = 'custos_estoques'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)

    grupo = db.relationship('Grupo', backref=db.backref('custos_estoques', lazy=True))


class CustosTerceirizacao(db.Model):
    __tablename__ = 'custos_terceirizacao'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)

    grupo = db.relationship('Grupo', backref=db.backref('custos_terceirizacao', lazy=True))


class CustosCapital(db.Model):
    __tablename__ = 'custos_capital'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)

    grupo = db.relationship('Grupo', backref=db.backref('custos_capital', lazy=True))


class CustosVendasPerdidas(db.Model):
    __tablename__ = 'custos_vendas_perdidas'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)

    grupo = db.relationship('Grupo', backref=db.backref('custos_vendas_perdidas', lazy=True))


class ReceitasVendas(db.Model):
    __tablename__ = 'receitas_vendas'

    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    periodo = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)

    grupo = db.relationship('Grupo', backref=db.backref('receitas_vendas', lazy=True))





class Custos(db.Model):
    __tablename__ = 'custos'

    id = db.Column(db.Integer, primary_key=True)

    # Custos fixos
    custo_fixo_tecelagem = db.Column(db.Float, nullable=False)
    custo_fixo_purga_jet1 = db.Column(db.Float, nullable=False)
    custo_fixo_purga_jet2 = db.Column(db.Float, nullable=False)
    custo_fixo_purga_jet3 = db.Column(db.Float, nullable=False)
    custo_fixo_fixacao_acabamento = db.Column(db.Float, nullable=False)

    # Custos variados
    tma = db.Column(db.Float, nullable=False)  # Taxa Mínima de Atratividade
    custo_unitario_compra_emergencia = db.Column(db.Float, nullable=False)
    taxa_armazenagem = db.Column(db.Float, nullable=False)

    # Custos de terceirização
    custo_terceirizacao_tecelagem = db.Column(db.Float, nullable=False)
    custo_terceirizacao_purga_tinturaria = db.Column(db.Float, nullable=False)
    custo_terceirizacao_fixacao_acabamento = db.Column(db.Float, nullable=False)

    # Taxas de desempenho
    taxa_desempenho_producao = db.Column(db.Float, nullable=False)
    taxa_desempenho_fornecimento_fios = db.Column(db.Float, nullable=False)
    taxa_desempenho_fornecimento_corantes = db.Column(db.Float, nullable=False)

    # Preços de aquisição e venda de equipamentos
    preco_aquisicao_teares = db.Column(db.Float, nullable=False)
    preco_venda_teares = db.Column(db.Float, nullable=False)

    preco_aquisicao_jet1 = db.Column(db.Float, nullable=False)
    preco_venda_jet1 = db.Column(db.Float, nullable=False)

    preco_aquisicao_jet2 = db.Column(db.Float, nullable=False)
    preco_venda_jet2 = db.Column(db.Float, nullable=False)

    preco_aquisicao_jet3 = db.Column(db.Float, nullable=False)
    preco_venda_jet3 = db.Column(db.Float, nullable=False)

    preco_aquisicao_rama = db.Column(db.Float, nullable=False)
    preco_venda_rama = db.Column(db.Float, nullable=False)

    # Preços de venda e custos de venda perdida para as famílias
    preco_venda_colmeia = db.Column(db.Float, nullable=False)
    preco_venda_piquet = db.Column(db.Float, nullable=False)
    preco_venda_maxim = db.Column(db.Float, nullable=False)

    custo_venda_perdida_colmeia = db.Column(db.Float, nullable=False)
    custo_venda_perdida_piquet = db.Column(db.Float, nullable=False)
    custo_venda_perdida_maxim = db.Column(db.Float, nullable=False)

    custo_unitario_colmeia = db.Column(db.Float, nullable=False)
    custo_unitario_piquet = db.Column(db.Float, nullable=False)
    custo_unitario_maxim = db.Column(db.Float, nullable=False)

    # Custos unitários para materiais
    custo_unitario_corantes = db.Column(db.Float, nullable=False)
    custo_unitario_fio_algodao = db.Column(db.Float, nullable=False)
    custo_unitario_fio_sintetico = db.Column(db.Float, nullable=False)