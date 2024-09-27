# app.py
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, ProductionForm, PurchaseForm
from models import Group, ProductionPlan, PurchasePlan, db


app = Flask(__name__)
app.config.from_object('config.Config')


db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Group.query.get(int(user_id))


# Importar rotas
@app.route('/')
def index():
    return render_template('index.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Group.query.filter_by(group_name=form.group_name.data).first()
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

    current_period = current_user.current_period
    periods = list(range(13, 25))

    colmeia_fields = {period: getattr(form, f'colmeia_{period}') for period in periods}
    piquet_fields = {period: getattr(form, f'piquet_{period}') for period in periods}
    maxim_fields = {period: getattr(form, f'maxim_{period}') for period in periods}

    if request.method == 'POST':
        for period in periods:
            if period >= current_period:
                # *** Família Colméia ***
                planned_production = colmeia_fields[period].data
                existing_plan = ProductionPlan.query.filter_by(
                    period_number=period, family='Colméia', group_id=current_user.id
                ).order_by(ProductionPlan.modified_period.desc()).first()

                if existing_plan:
                    if existing_plan.modified_period == current_period:
                        # Atualizar plano existente
                        existing_plan.planned_production = planned_production
                    else:
                        # Criar novo plano
                        new_plan = ProductionPlan(
                            period_number=period,
                            family='Colméia',
                            planned_production=planned_production,
                            modified_period=current_period,
                            group_id=current_user.id
                        )
                        db.session.add(new_plan)
                else:
                    # Caso não exista plano, criar outro
                    new_plan = ProductionPlan(
                        period_number=period,
                        family='Colméia',
                        planned_production=planned_production,
                        modified_period=current_period,
                        group_id=current_user.id
                    )
                    db.session.add(new_plan)

                # Mesma lógica para as outras famílias
                planned_production = piquet_fields[period].data
                existing_plan = ProductionPlan.query.filter_by(
                    period_number=period, family='Piquet', group_id=current_user.id
                ).order_by(ProductionPlan.modified_period.desc()).first()

                if existing_plan:
                    if existing_plan.modified_period == current_period:
                        existing_plan.planned_production = planned_production
                    else:
                        new_plan = ProductionPlan(
                            period_number=period,
                            family='Piquet',
                            planned_production=planned_production,
                            modified_period=current_period,
                            group_id=current_user.id
                            )
                        db.session.add(new_plan)
                else:
                    new_plan = ProductionPlan(
                        period_number=period,
                        family='Piquet',
                        planned_production=planned_production,
                        modified_period=current_period,
                        group_id=current_user.id
                    )
                    db.session.add(new_plan)

                # Mesma lógica para as outras famílias
                planned_production = maxim_fields[period].data
                existing_plan = ProductionPlan.query.filter_by(
                    period_number=period, family='Maxim', group_id=current_user.id
                ).order_by(ProductionPlan.modified_period.desc()).first()

                if existing_plan:
                    if existing_plan.modified_period == current_period:
                        existing_plan.planned_production = planned_production
                    else:
                        new_plan = ProductionPlan(
                            period_number=period,
                            family='Maxim',
                            planned_production=planned_production,
                            modified_period=current_period,
                            group_id=current_user.id
                        )
                        db.session.add(new_plan)
                else:
                    new_plan = ProductionPlan(
                        period_number=period,
                        family='Maxim',
                        planned_production=planned_production,
                        modified_period=current_period,
                        group_id=current_user.id
                    )
                    db.session.add(new_plan)

        db.session.commit()
        flash('Plano de produção salvo com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    elif request.method == 'GET':
        for period in periods:
            colmeia_plan = ProductionPlan.query.filter_by(
                period_number=period, family='Colméia', group_id=current_user.id
            ).filter(ProductionPlan.modified_period <= current_period).order_by(ProductionPlan.modified_period.desc()).first()
            if colmeia_plan:
                colmeia_fields[period].data = colmeia_plan.planned_production

            piquet_plan = ProductionPlan.query.filter_by(
                period_number=period, family='Piquet', group_id=current_user.id
            ).filter(ProductionPlan.modified_period <= current_period).order_by(ProductionPlan.modified_period.desc()).first()
            if piquet_plan:
                piquet_fields[period].data = piquet_plan.planned_production

            maxim_plan = ProductionPlan.query.filter_by(
                period_number=period, family='Maxim', group_id=current_user.id
            ).filter(ProductionPlan.modified_period <= current_period).order_by(ProductionPlan.modified_period.desc()).first()
            if maxim_plan:
                maxim_fields[period].data = maxim_plan.planned_production

    return render_template(
        'production.html',
        form=form,
        periods=periods,
        current_period=current_period,
        colmeia_fields=colmeia_fields,
        piquet_fields=piquet_fields,
        maxim_fields=maxim_fields
    )


@app.route('/purchases', methods=['GET', 'POST'])
@login_required
def purchases():
    form = PurchaseForm()

    current_period = current_user.current_period  # Período atual do grupo
    periods = list(range(13, 25))  # Períodos de 13 a 24

    # Preparando dicionários de campos dinamicamente para os materiais
    fio_algodao_fields = {period: getattr(form, f'fio_algodao_{period}') for period in periods}
    fio_sintetico_fields = {period: getattr(form, f'fio_sintetico_{period}') for period in periods}
    corantes_fields = {period: getattr(form, f'corantes_{period}') for period in periods}

    if request.method == 'POST':
        for period in periods:
            if period >= current_period:
                # *** Fio Algodão ***
                planned_purchase = fio_algodao_fields[period].data
                algodao_plan = PurchasePlan.query.filter_by(
                    period_number=period, material='Fio Algodao', group_id=current_user.id
                ).order_by(PurchasePlan.modified_period.desc()).first()

                if algodao_plan:
                    if algodao_plan.modified_period == current_period:
                        algodao_plan.planned_purchase = planned_purchase
                    else:
                        new_plan = PurchasePlan(
                            period_number=period,
                            material='Fio Algodao',
                            planned_purchase=planned_purchase,
                            modified_period=current_period,
                            group_id=current_user.id
                        )
                        db.session.add(new_plan)
                else:
                    new_plan = PurchasePlan(
                        period_number=period,
                        material='Fio Algodao',
                        planned_purchase=planned_purchase,
                        modified_period=current_period,
                        group_id=current_user.id
                    )
                    db.session.add(new_plan)

                # *** Fio Sintético ***
                planned_purchase = fio_sintetico_fields[period].data
                sintetico_plan = PurchasePlan.query.filter_by(
                    period_number=period, material='Fio Sintetico', group_id=current_user.id
                ).order_by(PurchasePlan.modified_period.desc()).first()

                if sintetico_plan:
                    if sintetico_plan.modified_period == current_period:
                        sintetico_plan.planned_purchase = planned_purchase
                    else:
                        new_plan = PurchasePlan(
                            period_number=period,
                            material='Fio Sintetico',
                            planned_purchase=planned_purchase,
                            modified_period=current_period,
                            group_id=current_user.id
                        )
                        db.session.add(new_plan)
                else:
                    new_plan = PurchasePlan(
                        period_number=period,
                        material='Fio Sintetico',
                        planned_purchase=planned_purchase,
                        modified_period=current_period,
                        group_id=current_user.id
                    )
                    db.session.add(new_plan)

                # *** Corantes ***
                planned_purchase = corantes_fields[period].data
                corantes_plan = PurchasePlan.query.filter_by(
                    period_number=period, material='Corantes', group_id=current_user.id
                ).order_by(PurchasePlan.modified_period.desc()).first()

                if corantes_plan:
                    if corantes_plan.modified_period == current_period:
                        corantes_plan.planned_purchase = planned_purchase
                    else:
                        new_plan = PurchasePlan(
                            period_number=period,
                            material='Corantes',
                            planned_purchase=planned_purchase,
                            modified_period=current_period,
                            group_id=current_user.id
                        )
                        db.session.add(new_plan)
                else:
                    new_plan = PurchasePlan(
                        period_number=period,
                        material='Corantes',
                        planned_purchase=planned_purchase,
                        modified_period=current_period,
                        group_id=current_user.id
                    )
                    db.session.add(new_plan)

        db.session.commit()
        flash('Plano de compras salvo com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    elif request.method == 'GET':
        for period in periods:
            # *** Fio Algodão ***
            algodao_plan = PurchasePlan.query.filter_by(
                period_number=period, material='Fio Algodao', group_id=current_user.id
            ).filter(PurchasePlan.modified_period <= current_period).order_by(PurchasePlan.modified_period.desc()).first()
            if algodao_plan:
                fio_algodao_fields[period].data = algodao_plan.planned_purchase

            # *** Fio Sintético ***
            sintetico_plan = PurchasePlan.query.filter_by(
                period_number=period, material='Fio Sintetico', group_id=current_user.id
            ).filter(PurchasePlan.modified_period <= current_period).order_by(PurchasePlan.modified_period.desc()).first()
            if sintetico_plan:
                fio_sintetico_fields[period].data = sintetico_plan.planned_purchase

            # *** Corantes ***
            corantes_plan = PurchasePlan.query.filter_by(
                period_number=period, material='Corantes', group_id=current_user.id
            ).filter(PurchasePlan.modified_period <= current_period).order_by(PurchasePlan.modified_period.desc()).first()
            if corantes_plan:
                corantes_fields[period].data = corantes_plan.planned_purchase

    return render_template(
        'purchases.html',
        form=form,
        periods=periods,
        current_period=current_period,
        fio_algodao_fields=fio_algodao_fields,
        fio_sintetico_fields=fio_sintetico_fields,
        corantes_fields=corantes_fields
    )





@app.route('/simulate', methods=['POST', 'GET'])
@login_required
def simulate():
    # Pega o grupo completo do usuário autenticado
    group = current_user

    # Obter o período atual
    current_period = group.current_period

    # Cálculos da simulação para o período atual

    ######### TODO: Aplicar lógica do game
    production_plans = ProductionPlan.query.filter_by(group_id=group.id, period_number=current_period).all()
    purchase_plans = PurchasePlan.query.filter_by(group_id=group.id, period_number=current_period).all()
    #########

    # Avançar para o próximo período
    group.current_period += 1  # Incrementa o período atual do grupo
    db.session.commit()

    flash(f"Simulação completada! Agora você está no período {group.current_period}.", "success")
    return redirect(url_for('dashboard'))


# Resultados
@app.route('/results')
@login_required
def results():
    production_plans = ProductionPlan.query.filter_by(group_id=current_user.id).all()
    purchase_plans = PurchasePlan.query.filter_by(group_id=current_user.id).all()
    return render_template('results.html', production_plans=production_plans, purchase_plans=purchase_plans)


#### BOTÃO PARA DEBUG ####

@app.route('/rollback_period', methods=['POST'])
@login_required
def rollback_period():
    group = current_user

    # Apenas volte o período se o período atual for maior que 1 (não pode ser menor que 1)
    if group.current_period > 1:
        group.current_period -= 1
        db.session.commit()
        flash(f"O período foi revertido! Agora você está no período {group.current_period}.", "success")
    else:
        flash("Você já está no primeiro período. Não é possível voltar mais.", "warning")

    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(debug=True)
