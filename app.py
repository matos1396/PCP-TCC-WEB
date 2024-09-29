# app.py
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, ProductionForm, PurchaseForm
from models import Grupo, PlanoProducao, PlanoCompras, db


app = Flask(__name__)
app.config.from_object('config.Config')


db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Grupo.query.get(int(user_id))


# Importar rotas
@app.route('/')
def index():
    return render_template('index.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Grupo.query.filter_by(grupo_nome=form.grupo_nome.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Nome do grupo ou senha incorretos.')
    return render_template('login.html', form=form)

# logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/production', methods=['GET', 'POST'])
@login_required
def production():
    form = ProductionForm()

    periodo_atual = current_user.periodo_atual
    periods = list(range(13, 25))

    colmeia_fields = {period: getattr(form, f'colmeia_{period}') for period in periods}
    piquet_fields = {period: getattr(form, f'piquet_{period}') for period in periods}
    maxim_fields = {period: getattr(form, f'maxim_{period}') for period in periods}

    if request.method == 'POST':
        for period in periods:
            if period >= periodo_atual:
                # *** Família Colméia ***
                producao_planejada = colmeia_fields[period].data
                existing_plan = PlanoProducao.query.filter_by(
                    periodo_numero=period, familia='Colméia', grupo_id=current_user.id
                ).order_by(PlanoProducao.periodo_modificado.desc()).first()

                if existing_plan:
                    if existing_plan.periodo_modificado == periodo_atual:
                        # Atualizar plano existente
                        existing_plan.producao_planejada = producao_planejada
                    else:
                        # Criar novo plano
                        new_plan = PlanoProducao(
                            periodo_numero=period,
                            familia='Colméia',
                            producao_planejada=producao_planejada,
                            periodo_modificado=periodo_atual,
                            grupo_id=current_user.id
                        )
                        db.session.add(new_plan)
                else:
                    # Caso não exista plano, criar outro
                    new_plan = PlanoProducao(
                        periodo_numero=period,
                        familia='Colméia',
                        producao_planejada=producao_planejada,
                        periodo_modificado=periodo_atual,
                        grupo_id=current_user.id
                    )
                    db.session.add(new_plan)

                # Mesma lógica para as outras famílias
                producao_planejada = piquet_fields[period].data
                existing_plan = PlanoProducao.query.filter_by(
                    periodo_numero=period, familia='Piquet', grupo_id=current_user.id
                ).order_by(PlanoProducao.periodo_modificado.desc()).first()

                if existing_plan:
                    if existing_plan.periodo_modificado == periodo_atual:
                        existing_plan.producao_planejada = producao_planejada
                    else:
                        new_plan = PlanoProducao(
                            periodo_numero=period,
                            familia='Piquet',
                            producao_planejada=producao_planejada,
                            periodo_modificado=periodo_atual,
                            grupo_id=current_user.id
                            )
                        db.session.add(new_plan)
                else:
                    new_plan = PlanoProducao(
                        periodo_numero=period,
                        familia='Piquet',
                        producao_planejada=producao_planejada,
                        periodo_modificado=periodo_atual,
                        grupo_id=current_user.id
                    )
                    db.session.add(new_plan)

                # Mesma lógica para as outras famílias
                producao_planejada = maxim_fields[period].data
                existing_plan = PlanoProducao.query.filter_by(
                    periodo_numero=period, familia='Maxim', grupo_id=current_user.id
                ).order_by(PlanoProducao.periodo_modificado.desc()).first()

                if existing_plan:
                    if existing_plan.periodo_modificado == periodo_atual:
                        existing_plan.producao_planejada = producao_planejada
                    else:
                        new_plan = PlanoProducao(
                            periodo_numero=period,
                            familia='Maxim',
                            producao_planejada=producao_planejada,
                            periodo_modificado=periodo_atual,
                            grupo_id=current_user.id
                        )
                        db.session.add(new_plan)
                else:
                    new_plan = PlanoProducao(
                        periodo_numero=period,
                        familia='Maxim',
                        producao_planejada=producao_planejada,
                        periodo_modificado=periodo_atual,
                        grupo_id=current_user.id
                    )
                    db.session.add(new_plan)

        db.session.commit()
        flash('Plano de produção salvo com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    elif request.method == 'GET':
        for period in periods:
            colmeia_plan = PlanoProducao.query.filter_by(
                periodo_numero=period, familia='Colméia', grupo_id=current_user.id
            ).filter(PlanoProducao.periodo_modificado <= periodo_atual).order_by(PlanoProducao.periodo_modificado.desc()).first()
            if colmeia_plan:
                colmeia_fields[period].data = colmeia_plan.producao_planejada

            piquet_plan = PlanoProducao.query.filter_by(
                periodo_numero=period, familia='Piquet', grupo_id=current_user.id
            ).filter(PlanoProducao.periodo_modificado <= periodo_atual).order_by(PlanoProducao.periodo_modificado.desc()).first()
            if piquet_plan:
                piquet_fields[period].data = piquet_plan.producao_planejada

            maxim_plan = PlanoProducao.query.filter_by(
                periodo_numero=period, familia='Maxim', grupo_id=current_user.id
            ).filter(PlanoProducao.periodo_modificado <= periodo_atual).order_by(PlanoProducao.periodo_modificado.desc()).first()
            if maxim_plan:
                maxim_fields[period].data = maxim_plan.producao_planejada

    return render_template(
        'production.html',
        form=form,
        periods=periods,
        periodo_atual=periodo_atual,
        colmeia_fields=colmeia_fields,
        piquet_fields=piquet_fields,
        maxim_fields=maxim_fields
    )


@app.route('/purchases', methods=['GET', 'POST'])
@login_required
def purchases():
    form = PurchaseForm()

    periodo_atual = current_user.periodo_atual  # Período atual do grupo
    periods = list(range(13, 25))  # Períodos de 13 a 24

    # Preparando dicionários de campos dinamicamente para os materiais
    fio_algodao_fields = {period: getattr(form, f'fio_algodao_{period}') for period in periods}
    fio_sintetico_fields = {period: getattr(form, f'fio_sintetico_{period}') for period in periods}
    corantes_fields = {period: getattr(form, f'corantes_{period}') for period in periods}

    if request.method == 'POST':
        for period in periods:
            if period >= periodo_atual:
                # *** Fio Algodão ***
                compra_planejada = fio_algodao_fields[period].data
                algodao_plan = PlanoCompras.query.filter_by(
                    periodo_numero=period, material='Fio Algodao', grupo_id=current_user.id
                ).order_by(PlanoCompras.periodo_modificado.desc()).first()

                if algodao_plan:
                    if algodao_plan.periodo_modificado == periodo_atual:
                        algodao_plan.compra_planejada = compra_planejada
                    else:
                        new_plan = PlanoCompras(
                            periodo_numero=period,
                            material='Fio Algodao',
                            compra_planejada=compra_planejada,
                            periodo_modificado=periodo_atual,
                            grupo_id=current_user.id
                        )
                        db.session.add(new_plan)
                else:
                    new_plan = PlanoCompras(
                        periodo_numero=period,
                        material='Fio Algodao',
                        compra_planejada=compra_planejada,
                        periodo_modificado=periodo_atual,
                        grupo_id=current_user.id
                    )
                    db.session.add(new_plan)

                # *** Fio Sintético ***
                compra_planejada = fio_sintetico_fields[period].data
                sintetico_plan = PlanoCompras.query.filter_by(
                    periodo_numero=period, material='Fio Sintetico', grupo_id=current_user.id
                ).order_by(PlanoCompras.periodo_modificado.desc()).first()

                if sintetico_plan:
                    if sintetico_plan.periodo_modificado == periodo_atual:
                        sintetico_plan.compra_planejada = compra_planejada
                    else:
                        new_plan = PlanoCompras(
                            periodo_numero=period,
                            material='Fio Sintetico',
                            compra_planejada=compra_planejada,
                            periodo_modificado=periodo_atual,
                            grupo_id=current_user.id
                        )
                        db.session.add(new_plan)
                else:
                    new_plan = PlanoCompras(
                        periodo_numero=period,
                        material='Fio Sintetico',
                        compra_planejada=compra_planejada,
                        periodo_modificado=periodo_atual,
                        grupo_id=current_user.id
                    )
                    db.session.add(new_plan)

                # *** Corantes ***
                compra_planejada = corantes_fields[period].data
                corantes_plan = PlanoCompras.query.filter_by(
                    periodo_numero=period, material='Corantes', grupo_id=current_user.id
                ).order_by(PlanoCompras.periodo_modificado.desc()).first()

                if corantes_plan:
                    if corantes_plan.periodo_modificado == periodo_atual:
                        corantes_plan.compra_planejada = compra_planejada
                    else:
                        new_plan = PlanoCompras(
                            periodo_numero=period,
                            material='Corantes',
                            compra_planejada=compra_planejada,
                            periodo_modificado=periodo_atual,
                            grupo_id=current_user.id
                        )
                        db.session.add(new_plan)
                else:
                    new_plan = PlanoCompras(
                        periodo_numero=period,
                        material='Corantes',
                        compra_planejada=compra_planejada,
                        periodo_modificado=periodo_atual,
                        grupo_id=current_user.id
                    )
                    db.session.add(new_plan)

        db.session.commit()
        flash('Plano de compras salvo com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    elif request.method == 'GET':
        for period in periods:
            # *** Fio Algodão ***
            algodao_plan = PlanoCompras.query.filter_by(
                periodo_numero=period, material='Fio Algodao', grupo_id=current_user.id
            ).filter(PlanoCompras.periodo_modificado <= periodo_atual).order_by(PlanoCompras.periodo_modificado.desc()).first()
            if algodao_plan:
                fio_algodao_fields[period].data = algodao_plan.compra_planejada

            # *** Fio Sintético ***
            sintetico_plan = PlanoCompras.query.filter_by(
                periodo_numero=period, material='Fio Sintetico', grupo_id=current_user.id
            ).filter(PlanoCompras.periodo_modificado <= periodo_atual).order_by(PlanoCompras.periodo_modificado.desc()).first()
            if sintetico_plan:
                fio_sintetico_fields[period].data = sintetico_plan.compra_planejada

            # *** Corantes ***
            corantes_plan = PlanoCompras.query.filter_by(
                periodo_numero=period, material='Corantes', grupo_id=current_user.id
            ).filter(PlanoCompras.periodo_modificado <= periodo_atual).order_by(PlanoCompras.periodo_modificado.desc()).first()
            if corantes_plan:
                corantes_fields[period].data = corantes_plan.compra_planejada

    return render_template(
        'purchases.html',
        form=form,
        periods=periods,
        periodo_atual=periodo_atual,
        fio_algodao_fields=fio_algodao_fields,
        fio_sintetico_fields=fio_sintetico_fields,
        corantes_fields=corantes_fields
    )





@app.route('/simulate', methods=['POST', 'GET'])
@login_required
def simulate():
    # Pega o grupo completo do usuário autenticado
    grupo = current_user

    # Obter o período atual
    periodo_atual = grupo.periodo_atual

    # Cálculos da simulação para o período atual

    ######### TODO: Aplicar lógica do game
    planos_producao = PlanoProducao.query.filter_by(grupo_id=grupo.id, periodo_numero=periodo_atual).all()
    planos_compra = PlanoCompras.query.filter_by(grupo_id=grupo.id, periodo_numero=periodo_atual).all()
    #########

    # Avançar para o próximo período
    grupo.periodo_atual += 1  # Incrementa o período atual do grupo
    db.session.commit()

    flash(f"Simulação completada! Agora você está no período {grupo.periodo_atual}.", "success")
    return redirect(url_for('dashboard'))


# Resultados
@app.route('/results')
@login_required
def results():
    planos_producao = PlanoProducao.query.filter_by(grupo_id=current_user.id).all()
    planos_compra = PlanoCompras.query.filter_by(grupo_id=current_user.id).all()
    return render_template('results.html', planos_producao=planos_producao, planos_compra=planos_compra)


#### BOTÃO PARA DEBUG ####

@app.route('/rollback_period', methods=['POST'])
@login_required
def rollback_period():
    grupo = current_user

    # Apenas volte o período se o período atual for maior que 1 (não pode ser menor que 1)
    if grupo.periodo_atual > 1:
        grupo.periodo_atual -= 1
        db.session.commit()
        flash(f"O período foi revertido! Agora você está no período {grupo.periodo_atual}.", "success")
    else:
        flash("Você já está no primeiro período. Não é possível voltar mais.", "warning")

    return redirect(url_for('dashboard'))


@app.route('/reset', methods=['POST'])
@login_required
def reset():
    if current_user.is_authenticated:
        # Limpa os dados das tabelas de produção e compras
        db.session.query(PlanoProducao).delete()
        db.session.query(PlanoCompras).delete()

        # Reinicia o periodo_atual de todos os grupos para 13
        groups = Grupo.query.all()
        for grupo in groups:
            grupo.periodo_atual = 13

        db.session.commit()
        flash('Banco de dados resetado e período atual reiniciado para 13.', 'success')

    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(debug=True)
