# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    group_name = StringField('Nome do Grupo', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductionForm(FlaskForm):
    # Períodos de 13 a 18
    periods = range(13, 25)

    # Campos para Família Colméia
    for period in periods:
        vars()['colmeia_' + str(period)] = IntegerField(f'Colméia (Período {period})', validators=[DataRequired()])

    # Campos para Família Piquet
    for period in periods:
        vars()['piquet_' + str(period)] = IntegerField(f'Piquet (Período {period})', validators=[DataRequired()])

    # Campos para Família Maxim
    for period in periods:
        vars()['maxim_' + str(period)] = IntegerField(f'Maxim (Período {period})', validators=[DataRequired()])

    # Botão de submissão
    submit = SubmitField('Salvar Plano de Produção')

class PurchaseForm(FlaskForm):
    # Períodos de 13 a 18
    periods = range(13, 25)

    # Campos para Família Colméia
    for period in periods:
        vars()['fio_algodao_' + str(period)] = IntegerField(f'Fio Algodão (Período {period})', validators=[DataRequired()])

    # Campos para Família Piquet
    for period in periods:
        vars()['fio_sintetico_' + str(period)] = IntegerField(f'Fio Sintético (Período {period})', validators=[DataRequired()])

    # Campos para Família Maxim
    for period in periods:
        vars()['corantes_' + str(period)] = IntegerField(f'Corantes (Período {period})', validators=[DataRequired()])

    # Botão de submissão
    submit = SubmitField('Salvar Plano de Produção')
