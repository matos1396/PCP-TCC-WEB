# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Optional, Length, EqualTo

class LoginForm(FlaskForm):
    grupo_nome = StringField('Nome do Grupo', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductionForm(FlaskForm):
    periods = range(13, 25)

    # Campos para Família Colméia
    for period in periods:
        # Campo para Produção Planejada e Real
        vars()['colmeia_' + str(period)] = IntegerField(f'Colméia (Período {period})', validators=[DataRequired()])
        vars()['colmeia_producao_real' + str(period)] = IntegerField(f'Colméia Produção Real (Período {period})', validators=[DataRequired()])
        # Campo para Demanda Prevista e Real
        vars()['colmeia_demanda_prevista_' + str(period)] = IntegerField(f'Demanda Prevista Colméia (Período {period})', validators=[DataRequired()])
        vars()['colmeia_demanda_real_' + str(period)] = IntegerField(f'Demanda Real Colméia (Período {period})', validators=[DataRequired()])
        # Campos para Estoques Iniciais (Produção)
        vars()['colmeia_estoque_inicial_' + str(period)] = IntegerField(f'Colmeia Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['colmeia_estoque_final_' + str(period)] = IntegerField(f'Colmeia Estoque Final (Período {period})', validators=[DataRequired()])
        # Campos para Vendas Perdida e Real
        vars()['colmeia_vendas_perdidas_' + str(period)] = IntegerField(f'Colmeia Vendas Perdidas (Período {period})', validators=[Optional()])
        vars()['colmeia_vendas_' + str(period)] = IntegerField(f'Colmeia Vendas (Período {period})', validators=[Optional()])

    # Campos para Família Piquet
    for period in periods:
        # Campo para Produção Planejada e Real
        vars()['piquet_' + str(period)] = IntegerField(f'Piquet (Período {period})', validators=[DataRequired()])
        vars()['piquet_producao_real' + str(period)] = IntegerField(f'Piquet Produção Real (Período {period})', validators=[DataRequired()])
        # Campo para Demanda Prevista e Real
        vars()['piquet_demanda_prevista_' + str(period)] = IntegerField(f'Demanda Prevista Piquet (Período {period})', validators=[DataRequired()])
        vars()['piquet_demanda_real_' + str(period)] = IntegerField(f'Demanda Real Piquet (Período {period})', validators=[DataRequired()])
        # Campos para Estoques Iniciais (Produção)
        vars()['piquet_estoque_inicial_' + str(period)] = IntegerField(f'Piquet Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['piquet_estoque_final_' + str(period)] = IntegerField(f'Piquet Estoque Final (Período {period})', validators=[Optional()])
        # Campos para Vendas Perdida e Real
        vars()['piquet_vendas_perdidas_' + str(period)] = IntegerField(f'Piquet Vendas Perdidas (Período {period})', validators=[Optional()])
        vars()['piquet_vendas_' + str(period)] = IntegerField(f'Piquet Vendas (Período {period})', validators=[Optional()])


    # Campos para Família Maxim
    for period in periods:
        # Campo para Produção Planejada e Real
        vars()['maxim_' + str(period)] = IntegerField(f'Maxim (Período {period})', validators=[DataRequired()])
        vars()['maxim_producao_real' + str(period)] = IntegerField(f'Maxim Produção Real (Período {period})', validators=[DataRequired()])
        # Campo para Demanda Prevista e Real
        vars()['maxim_demanda_prevista_' + str(period)] = IntegerField(f'Demanda Prevista Maxim (Período {period})', validators=[DataRequired()])
        vars()['maxim_demanda_real_' + str(period)] = IntegerField(f'Demanda Real Maxim (Período {period})', validators=[DataRequired()])
        # Campos para Estoques Iniciais (Produção)
        vars()['maxim_estoque_inicial_' + str(period)] = IntegerField(f'Maxim Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['maxim_estoque_final_' + str(period)] = IntegerField(f'Maxim Estoque Final (Período {period})', validators=[Optional()])
        # Campos para Vendas Perdida e Real
        vars()['maxim_vendas_perdidas_' + str(period)] = IntegerField(f'Maxim Vendas Perdidas (Período {period})', validators=[Optional()])
        vars()['maxim_vendas_' + str(period)] = IntegerField(f'Maxim Vendas (Período {period})', validators=[Optional()])


    # Botão para Submeter o Formulário
    submit = SubmitField('Salvar Plano de Produção')

class PurchaseForm(FlaskForm):
    periods = range(13, 25)

    # Campos para Fio Algodão
    for period in periods:
        # Campo para Compras Planejada, Real e Emergêncial
        vars()['fio_algodao_' + str(period)] = IntegerField(f'Fio Algodão (Período {period})', validators=[Optional()])
        vars()['fio_algodao_compra_real_' + str(period)] = IntegerField(f'Fio Algodão Compra Real (Período {period})', validators=[Optional()])
        vars()['fio_algodao_compra_emergencial_' + str(period)] = IntegerField(f'Fio Algodão Compra Emergêncial (Período {period})', validators=[Optional()])
        # Campo para Consumo Previsto e Real
        vars()['fio_algodao_consumo_previsto_' + str(period)] = IntegerField(f'Fio Algodão Consumo Previsto (Período {period})', validators=[Optional()])
        vars()['fio_algodao_consumo_real_' + str(period)] = IntegerField(f'Fio Algodão Consumo Real (Período {period})', validators=[Optional()])
        # Campo para Estoques Iniciais e Final
        vars()['fio_algodao_estoque_inicial_' + str(period)] = IntegerField(f'Fio Algodão Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['fio_algodao_estoque_final_' + str(period)] = IntegerField(f'Fio Algodão Estoque Final (Período {period})', validators=[Optional()])


    # Campos para Fio Sintético
    for period in periods:
        # Campo para Compras Planejada, Real e Emergencial
        vars()['fio_sintetico_' + str(period)] = IntegerField(f'Fio Sintético (Período {period})', validators=[Optional()])
        vars()['fio_sintetico_compra_real_' + str(period)] = IntegerField(f'Fio Sintético Compra Real (Período {period})', validators=[Optional()])
        vars()['fio_sintetico_compra_emergencial_' + str(period)] = IntegerField(f'Fio Sintético Compra Emergencial (Período {period})', validators=[Optional()])
        # Campo para Consumo Previsto e Real
        vars()['fio_sintetico_consumo_previsto_' + str(period)] = IntegerField(f'Fio Sintético Consumo Previsto (Período {period})', validators=[Optional()])
        vars()['fio_sintetico_consumo_real_' + str(period)] = IntegerField(f'Fio Sintético Consumo Real (Período {period})', validators=[Optional()])
        # Campo para Estoques Iniciais e Finais
        vars()['fio_sintetico_estoque_inicial_' + str(period)] = IntegerField(f'Fio Sintético Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['fio_sintetico_estoque_final_' + str(period)] = IntegerField(f'Fio Sintético Estoque Final (Período {period})', validators=[Optional()])

    # Campos para Corantes
    for period in periods:
        # Campo para Compras Planejada, Real e Emergencial
        vars()['corantes_' + str(period)] = IntegerField(f'Corantes (Período {period})', validators=[Optional()])
        vars()['corantes_compra_real_' + str(period)] = IntegerField(f'Corantes Compra Real (Período {period})', validators=[Optional()])
        vars()['corantes_compra_emergencial_' + str(period)] = IntegerField(f'Corantes Compra Emergencial (Período {period})', validators=[Optional()])
        # Campo para Consumo Previsto e Real
        vars()['corantes_consumo_previsto_' + str(period)] = IntegerField(f'Corantes Consumo Previsto (Período {period})', validators=[Optional()])
        vars()['corantes_consumo_real_' + str(period)] = IntegerField(f'Corantes Consumo Real (Período {period})', validators=[Optional()])
        # Campo para Estoques Iniciais e Finais
        vars()['corantes_estoque_inicial_' + str(period)] = IntegerField(f'Corantes Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['corantes_estoque_final_' + str(period)] = IntegerField(f'Corantes Estoque Final (Período {period})', validators=[Optional()])

    # Botão para Submeter o Formulário
    submit = SubmitField('Salvar Plano de Compras')


class TecelagemForm(FlaskForm):
    periods = range(13, 25)

    def validate_capacidade_teceirizada(form, field):
        if field.data and field.data % 420 != 0:
            raise ValidationError("A Capacidade Terceirizada deve ser um múltiplo de 420.")
    # Campos Tabelas Capacidade Necessária e Disponível
    for period in periods:
        # Tabela Capacidade Necessária
        # (Capacidade Disponível comum as duas tabelas)
        vars()['capacidade_disponivel_' + str(period)] = IntegerField(f'Capacidade Disponível (Período {period})', validators=[Optional()])
        vars()['capacidade_necessaria_' + str(period)] = IntegerField(f'Capacidade Necessária (Período {period})', validators=[Optional()])
        vars()['colmeia_horas_' + str(period)] = IntegerField(f'Capacidade Necessária Colmeia (Período {period})', validators=[Optional()])
        vars()['piquet_horas_' + str(period)] = IntegerField(f'Capacidade Necessária Piquet (Período {period})', validators=[Optional()])
        vars()['maxim_horas_' + str(period)] = IntegerField(f'Capacidade Necessária Maxim (Período {period})', validators=[Optional()])
        vars()['setup_' + str(period)] = IntegerField(f'Setup (Período {period})', validators=[Optional()])
        vars()['produtividade_' + str(period)] = IntegerField(f'Produtividade (Período {period})', validators=[Optional()])

        # Tabela Capacidade Disponível
        vars()['numero_turnos_' + str(period)] = IntegerField(f'Número de Turnos (Período {period})', validators=[Optional()])
        vars()['capacidade_instalada_' + str(period)] = IntegerField(f'Capacidade Instalada (Período {period})', validators=[Optional()])
        vars()['capacidade_teceirizada_' + str(period)] = IntegerField(f'Capacidade Terceirizada (Período {period})', validators=[Optional(), validate_capacidade_teceirizada])

        # Tabela Capacidade Futura
        vars()['quantidade_' + str(period)] = IntegerField(f'Quantidade (Período {period})', validators=[Optional()])
        vars()['ampliacoes_' + str(period)] = IntegerField(f'Ampliações (Período {period})', validators=[Optional()])
        vars()['reducoes_' + str(period)] = IntegerField(f'Reduções (Período {period})', validators=[Optional()])

    # Botão para Submeter o Formulário
    submit = SubmitField('Salvar Plano de Tecelagem')

class PurgaTinturariaForm(FlaskForm):
    periods = range(13, 25)

    def validate_capacidade_teceirizada(form, field):
        if field.data and field.data % 11200 != 0:
            raise ValidationError("A Capacidade Terceirizada deve ser um múltiplo de 11200.")
    # Campos Tabelas Capacidade Necessária e Disponível
    for period in periods:
        # Tabela Capacidade Necessária
        # (Capacidade Disponível comum as duas tabelas)
        vars()['capacidade_disponivel_' + str(period)] = IntegerField(f'Capacidade Disponível (Período {period})', validators=[Optional()])
        vars()['capacidade_necessaria_' + str(period)] = IntegerField(f'Capacidade Necessária (Período {period})', validators=[Optional()])
        vars()['colmeia_horas_' + str(period)] = IntegerField(f'Capacidade Necessária Colmeia (Período {period})', validators=[Optional()])
        vars()['piquet_horas_' + str(period)] = IntegerField(f'Capacidade Necessária Piquet (Período {period})', validators=[Optional()])
        vars()['maxim_horas_' + str(period)] = IntegerField(f'Capacidade Necessária Maxim (Período {period})', validators=[Optional()])
        vars()['setup_' + str(period)] = IntegerField(f'Setup (Período {period})', validators=[Optional()])
        vars()['produtividade_' + str(period)] = IntegerField(f'Produtividade (Período {period})', validators=[Optional()])

        # Tabela Capacidade Disponível
        vars()['numero_turnos_' + str(period)] = IntegerField(f'Número de Turnos (Período {period})', validators=[Optional()])
        vars()['capacidade_instalada_jet1_' + str(period)] = IntegerField(f'Capacidade Instalada Jet1 (Período {period})', validators=[Optional()])
        vars()['capacidade_instalada_jet2_' + str(period)] = IntegerField(f'Capacidade Instalada Jet2 (Período {period})', validators=[Optional()])
        vars()['capacidade_instalada_jet3_' + str(period)] = IntegerField(f'Capacidade Instalada Jet3 (Período {period})', validators=[Optional()])
        vars()['capacidade_teceirizada_' + str(period)] = IntegerField(f'Capacidade Terceirizada (Período {period})', validators=[Optional(), validate_capacidade_teceirizada])

        # Tabela Capacidade Futura
        vars()['quantidade_jet1_' + str(period)] = IntegerField(f'Quantidade Jet 1 (Período {period})', validators=[Optional()])
        vars()['quantidade_jet2_' + str(period)] = IntegerField(f'Quantidade Jet 2 (Período {period})', validators=[Optional()])
        vars()['quantidade_jet3_' + str(period)] = IntegerField(f'Quantidade Jet 3 (Período {period})', validators=[Optional()])
        vars()['ampliacoes_jet1_' + str(period)] = IntegerField(f'Ampliações Jet 1 (Período {period})', validators=[Optional()])
        vars()['ampliacoes_jet2_' + str(period)] = IntegerField(f'Ampliações Jet 2 (Período {period})', validators=[Optional()])
        vars()['ampliacoes_jet3_' + str(period)] = IntegerField(f'Ampliações Jet 3 (Período {period})', validators=[Optional()])
        vars()['reducoes_jet1_' + str(period)] = IntegerField(f'Reduções Jet 1 (Período {period})', validators=[Optional()])
        vars()['reducoes_jet2_' + str(period)] = IntegerField(f'Reduções Jet 2 (Período {period})', validators=[Optional()])
        vars()['reducoes_jet3_' + str(period)] = IntegerField(f'Reduções Jet 3 (Período {period})', validators=[Optional()])

    # Botão para Submeter o Formulário
    submit = SubmitField('Salvar Plano de Purga e Tinturaria')


class FixacaoAcabamentoForm(FlaskForm):
    periods = range(13, 25)

    def validate_capacidade_teceirizada(form, field):
        if field.data and field.data % 70 != 0:
            raise ValidationError("A Capacidade Terceirizada deve ser um múltiplo de 70.")
    # Campos Tabelas Capacidade Necessária e Disponível
    for period in periods:
        # Tabela Capacidade Necessária
        # (Capacidade Disponível comum as duas tabelas)
        vars()['capacidade_disponivel_' + str(period)] = IntegerField(f'Capacidade Disponível (Período {period})', validators=[Optional()])
        vars()['capacidade_necessaria_' + str(period)] = IntegerField(f'Capacidade Necessária (Período {period})', validators=[Optional()])
        vars()['colmeia_horas_' + str(period)] = IntegerField(f'Capacidade Necessária Colmeia (Período {period})', validators=[Optional()])
        vars()['piquet_horas_' + str(period)] = IntegerField(f'Capacidade Necessária Piquet (Período {period})', validators=[Optional()])
        vars()['maxim_horas_' + str(period)] = IntegerField(f'Capacidade Necessária Maxim (Período {period})', validators=[Optional()])
        vars()['setup_' + str(period)] = IntegerField(f'Setup (Período {period})', validators=[Optional()])
        vars()['produtividade_' + str(period)] = IntegerField(f'Produtividade (Período {period})', validators=[Optional()])

        # Tabela Capacidade Disponível
        vars()['numero_turnos_' + str(period)] = IntegerField(f'Número de Turnos (Período {period})', validators=[Optional()])
        vars()['capacidade_instalada_' + str(period)] = IntegerField(f'Capacidade Instalada (Período {period})', validators=[Optional()])
        vars()['capacidade_teceirizada_' + str(period)] = IntegerField(f'Capacidade Terceirizada (Período {period})', validators=[Optional(), validate_capacidade_teceirizada])

        # Tabela Capacidade Futura
        vars()['quantidade_' + str(period)] = IntegerField(f'Quantidade (Período {period})', validators=[Optional()])
        vars()['ampliacoes_' + str(period)] = IntegerField(f'Ampliações (Período {period})', validators=[Optional()])
        vars()['reducoes_' + str(period)] = IntegerField(f'Reduções (Período {period})', validators=[Optional()])


    # Botão para Submeter o Formulário
    submit = SubmitField('Salvar Plano de Fixação e Acabamento')


class CadastroGrupoForm(FlaskForm):
    grupo_nome = StringField('Nome do Grupo', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem coincidir.')])
    estilo_demanda = SelectField('Estilo de Demanda', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Cadastrar Grupo')