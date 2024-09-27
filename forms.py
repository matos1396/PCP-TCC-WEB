# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    group_name = StringField('Nome do Grupo', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductionForm(FlaskForm):
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
