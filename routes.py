# routes.py
from app import app, db
from flask import render_template, redirect, url_for, flash
from models import User, ProductionPlan, PurchasePlan
from forms import LoginForm, ProductionForm, PurchaseForm
from flask_login import login_user, login_required, logout_user, current_user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(group_name=form.group_name.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Nome do grupo ou senha incorretos.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/production', methods=['GET', 'POST'])
@login_required
def production():
    form = ProductionForm()
    if form.validate_on_submit():
        plan = ProductionPlan(
            period=form.period.data,
            family_colmeia=form.family_colmeia.data,
            family_piquet=form.family_piquet.data,
            family_maxim=form.family_maxim.data,
            user_id=current_user.id
        )
        db.session.add(plan)
        db.session.commit()
        flash('Plano de produção salvo com sucesso.')
        return redirect(url_for('dashboard'))
    return render_template('production.html', form=form)

@app.route('/purchases', methods=['GET', 'POST'])
@login_required
def purchases():
    form = PurchaseForm()
    if form.validate_on_submit():
        purchase = PurchasePlan(
            period=form.period.data,
            fio_algodao=form.fio_algodao.data,
            fio_sintetico=form.fio_sintetico.data,
            corantes=form.corantes.data,
            user_id=current_user.id
        )
        db.session.add(purchase)
        db.session.commit()
        flash('Plano de compras salvo com sucesso.')
        return redirect(url_for('dashboard'))
    return render_template('purchases.html', form=form)

@app.route('/results')
@login_required
def results():
    production_plans = ProductionPlan.query.filter_by(user_id=current_user.id).all()
    purchase_plans = PurchasePlan.query.filter_by(user_id=current_user.id).all()
    return render_template('results.html', production_plans=production_plans, purchase_plans=purchase_plans)




@app.route('/production', methods=['GET', 'POST'])
@login_required
def production():
    form = ProductionForm()
    group = current_user.group  # Grupo do usuário autenticado
    current_period = group.current_period

    # Carregar apenas os planos de produção para períodos futuros
    future_periods = range(current_period + 1, 13)  # Exemplo de até 12 períodos

    if request.method == 'POST' and form.validate_on_submit():
        for period in future_periods:
            for family in ['Colméia', 'Piquet', 'Maxim']:
                production_plan = ProductionPlan.query.filter_by(
                    period_number=period, group_id=group.id, family=family
                ).first()

                if not production_plan:
                    production_plan = ProductionPlan(
                        period_number=period, group_id=group.id, family=family,
                        planned_production=form.get_field(f'planned_production_{family}_{period}').data
                    )
                    db.session.add(production_plan)
                else:
                    production_plan.planned_production = form.get_field(f'planned_production_{family}_{period}').data

        db.session.commit()
        flash('Planos de produção salvos para períodos futuros!', 'success')
        return redirect(url_for('production'))

    return render_template('production.html', form=form, periods=future_periods)
