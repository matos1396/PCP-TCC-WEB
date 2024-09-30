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
        # Campo para Produção Planejada
        vars()['colmeia_' + str(period)] = DecimalField(f'Colméia (Período {period})', validators=[DataRequired()])
        # Campo para Demanda Prevista
        vars()['colmeia_demanda_prevista_' + str(period)] = IntegerField(f'Demanda Prevista Colméia (Período {period})', validators=[DataRequired()])
        # Campos para Estoques Iniciais (Produção)
        vars()['colmeia_estoque_inicial_' + str(period)] = IntegerField(f'Colmeia Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['colmeia_estoque_final_' + str(period)] = IntegerField(f'Colmeia Estoque Final (Período {period})', validators=[Optional()])
        vars()['colmeia_vendas_perdidas_' + str(period)] = IntegerField(f'Colmeia Vendas Perdidas (Período {period})', validators=[Optional()])
        vars()['colmeia_vendas_' + str(period)] = IntegerField(f'Colmeia Vendas (Período {period})', validators=[Optional()])

    # Campos para Família Piquet
    for period in periods:
        # Campo para Produção Planejada
        vars()['piquet_' + str(period)] = IntegerField(f'Piquet (Período {period})', validators=[DataRequired()])
        # Campo para Demanda Prevista
        vars()['piquet_demanda_prevista_' + str(period)] = IntegerField(f'Demanda Prevista Piquet (Período {period})', validators=[DataRequired()])
        # Campos para Estoques Iniciais (Produção)
        vars()['piquet_estoque_inicial_' + str(period)] = IntegerField(f'Piquet Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['piquet_estoque_final_' + str(period)] = IntegerField(f'Piquet Estoque Final (Período {period})', validators=[Optional()])
        vars()['piquet_vendas_perdidas_' + str(period)] = IntegerField(f'Piquet Vendas Perdidas (Período {period})', validators=[Optional()])
        vars()['piquet_vendas_' + str(period)] = IntegerField(f'Piquet Vendas (Período {period})', validators=[Optional()])


    # Campos para Família Maxim
    for period in periods:
        # Campo para Produção Planejada
        vars()['maxim_' + str(period)] = IntegerField(f'Maxim (Período {period})', validators=[DataRequired()])
        # Campo para Demanda Prevista
        vars()['maxim_demanda_prevista_' + str(period)] = IntegerField(f'Demanda Prevista Maxim (Período {period})', validators=[DataRequired()])
        # Campos para Estoques Iniciais (Produção)
        vars()['maxim_estoque_inicial_' + str(period)] = IntegerField(f'Maxim Estoque Inicial (Período {period})', validators=[Optional()])
        vars()['maxim_estoque_final_' + str(period)] = IntegerField(f'Maxim Estoque Final (Período {period})', validators=[Optional()])
        vars()['maxim_vendas_perdidas_' + str(period)] = IntegerField(f'Maxim Vendas Perdidas (Período {period})', validators=[Optional()])
        vars()['maxim_vendas_' + str(period)] = IntegerField(f'Maxim Vendas (Período {period})', validators=[Optional()])


    # Botão para Submeter o Formulário
    submit = SubmitField('Salvar Plano de Produção')

class PurchaseForm(FlaskForm):
    periods = range(13, 25)

    # Campos para Fio Algodão
    for period in periods:
        vars()['fio_algodao_' + str(period)] = IntegerField(f'Fio Algodão (Período {period})', validators=[Optional()])

    # Campos para Fio Sintético
    for period in periods:
        vars()['fio_sintetico_' + str(period)] = IntegerField(f'Fio Sintético (Período {period})', validators=[Optional()])

    # Campos para Corantes
    for period in periods:
        vars()['corantes_' + str(period)] = IntegerField(f'Corantes (Período {period})', validators=[Optional()])

    submit = SubmitField('Salvar Plano de Compras')
