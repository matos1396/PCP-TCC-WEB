# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, FloatField, DecimalField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    grupo_nome = StringField('Nome do Grupo', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductionForm(FlaskForm):
    periods = range(13, 25)

    # Campos para Família Colméia
    for period in periods:
        # Campo para Produção Planejada e Real
        vars()['colmeia_' + str(period)] = DecimalField(f'Colméia (Período {period})', validators=[DataRequired()])
        vars()['colmeia_producao_real' + str(period)] = DecimalField(f'Colméia Produção Real (Período {period})', validators=[DataRequired()])
        # Campo para Demanda Prevista e Real
        vars()['colmeia_demanda_prevista_' + str(period)] = DecimalField(f'Demanda Prevista Colméia (Período {period})', validators=[DataRequired()])
        vars()['colmeia_demanda_real_' + str(period)] = DecimalField(f'Demanda Real Colméia (Período {period})', validators=[DataRequired()])
        # Campos para Estoques Iniciais (Produção)
        vars()['colmeia_estoque_inicial_' + str(period)] = DecimalField(f'Colmeia Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['colmeia_estoque_final_' + str(period)] = DecimalField(f'Colmeia Estoque Final (Período {period})', validators=[DataRequired()])
        # Campos para Vendas Perdida e Real
        vars()['colmeia_vendas_perdidas_' + str(period)] = DecimalField(f'Colmeia Vendas Perdidas (Período {period})', validators=[Optional()])
        vars()['colmeia_vendas_' + str(period)] = DecimalField(f'Colmeia Vendas (Período {period})', validators=[Optional()])

    # Campos para Família Piquet
    for period in periods:
        # Campo para Produção Planejada e Real
        vars()['piquet_' + str(period)] = DecimalField(f'Piquet (Período {period})', validators=[DataRequired()])
        vars()['piquet_producao_real' + str(period)] = DecimalField(f'Piquet Produção Real (Período {period})', validators=[DataRequired()])
        # Campo para Demanda Prevista e Real
        vars()['piquet_demanda_prevista_' + str(period)] = DecimalField(f'Demanda Prevista Piquet (Período {period})', validators=[DataRequired()])
        vars()['piquet_demanda_real_' + str(period)] = DecimalField(f'Demanda Real Piquet (Período {period})', validators=[DataRequired()])
        # Campos para Estoques Iniciais (Produção)
        vars()['piquet_estoque_inicial_' + str(period)] = DecimalField(f'Piquet Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['piquet_estoque_final_' + str(period)] = DecimalField(f'Piquet Estoque Final (Período {period})', validators=[Optional()])
        # Campos para Vendas Perdida e Real
        vars()['piquet_vendas_perdidas_' + str(period)] = DecimalField(f'Piquet Vendas Perdidas (Período {period})', validators=[Optional()])
        vars()['piquet_vendas_' + str(period)] = DecimalField(f'Piquet Vendas (Período {period})', validators=[Optional()])


    # Campos para Família Maxim
    for period in periods:
        # Campo para Produção Planejada e Real
        vars()['maxim_' + str(period)] = DecimalField(f'Maxim (Período {period})', validators=[DataRequired()])
        vars()['maxim_producao_real' + str(period)] = DecimalField(f'Maxim Produção Real (Período {period})', validators=[DataRequired()])
        # Campo para Demanda Prevista e Real
        vars()['maxim_demanda_prevista_' + str(period)] = DecimalField(f'Demanda Prevista Maxim (Período {period})', validators=[DataRequired()])
        vars()['maxim_demanda_real_' + str(period)] = DecimalField(f'Demanda Real Maxim (Período {period})', validators=[DataRequired()])
        # Campos para Estoques Iniciais (Produção)
        vars()['maxim_estoque_inicial_' + str(period)] = DecimalField(f'Maxim Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['maxim_estoque_final_' + str(period)] = DecimalField(f'Maxim Estoque Final (Período {period})', validators=[Optional()])
        # Campos para Vendas Perdida e Real
        vars()['maxim_vendas_perdidas_' + str(period)] = DecimalField(f'Maxim Vendas Perdidas (Período {period})', validators=[Optional()])
        vars()['maxim_vendas_' + str(period)] = DecimalField(f'Maxim Vendas (Período {period})', validators=[Optional()])


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
        vars()['fio_algodao_estoque_inicial_' + str(period)] = DecimalField(f'Fio Algodão Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['fio_algodao_estoque_final_' + str(period)] = DecimalField(f'Fio Algodão Estoque Final (Período {period})', validators=[Optional()])


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
        vars()['fio_sintetico_estoque_inicial_' + str(period)] = DecimalField(f'Fio Sintético Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['fio_sintetico_estoque_final_' + str(period)] = DecimalField(f'Fio Sintético Estoque Final (Período {period})', validators=[Optional()])

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
        vars()['corantes_estoque_inicial_' + str(period)] = DecimalField(f'Corantes Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['corantes_estoque_final_' + str(period)] = DecimalField(f'Corantes Estoque Final (Período {period})', validators=[Optional()])

    # Botão para Submeter o Formulário
    submit = SubmitField('Salvar Plano de Compras')
