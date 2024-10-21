# app.py
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, ProductionForm, PurchaseForm, TecelagemForm, PurgaTinturariaForm, FixacaoAcabamentoForm
from models import (Grupo,PlanoProducao,PlanoCompras,PrevisaoDemanda,
                    CapacidadeJets,CapacidadeRamas,CapacidadeTeares,TaxaProducao,Custos,
                    RelatorioFinanceiro,CustosCapital,CustosCompraMP,CustosEstoques,
                    CustosFixos,CustosTerceirizacao,CustosVendasPerdidas,ReceitasVendas,
                    db)
from simulacao import simulacao
from utils.func_auxiliares import atualizar_plano_compras, atualizar_capacidade_maquinas, atualizar_financeiro

import time # Para Testes

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

    periods = list(range(13, 25))
    periodo_atual = current_user.periodo_atual
    estilo_demanda = current_user.estilo_demanda


    # Campos para Demanda
    previsoes_por_familia = {
        'Colmeia': {period: getattr(form, f'colmeia_demanda_prevista_{period}') for period in periods},
        'Piquet': {period: getattr(form, f'piquet_demanda_prevista_{period}') for period in periods},
        'Maxim': {period: getattr(form, f'maxim_demanda_prevista_{period}') for period in periods}
    }
    demanda_real_por_familia = { #- somente ler
        'Colmeia': {period: getattr(form, f'colmeia_demanda_real_{period}') for period in periods},
        'Piquet': {period: getattr(form, f'piquet_demanda_real_{period}') for period in periods},
        'Maxim': {period: getattr(form, f'maxim_demanda_real_{period}') for period in periods}
    }

    # Campos para produção
    producao_planejada_por_familia = {
        'Colmeia': {period: getattr(form, f'colmeia_{period}') for period in periods},
        'Piquet': {period: getattr(form, f'piquet_{period}') for period in periods},
        'Maxim': {period: getattr(form, f'maxim_{period}') for period in periods}
    }
    producao_real_por_familia = { # somente ler
        'Colmeia': {period: getattr(form, f'colmeia_producao_real{period}') for period in periods},
        'Piquet': {period: getattr(form, f'piquet_producao_real{period}') for period in periods},
        'Maxim': {period: getattr(form, f'maxim_producao_real{period}') for period in periods}
    }

    # Campos Estoques - somente ler
    estoques_iniciais_por_familia = {
        'Colmeia': {period: getattr(form, f'colmeia_estoque_inicial_{period}') for period in periods},
        'Piquet': {period: getattr(form, f'piquet_estoque_inicial_{period}') for period in periods},
        'Maxim': {period: getattr(form, f'maxim_estoque_inicial_{period}') for period in periods}
    }
    estoques_finais_por_familia = {
        'Colmeia': {period: getattr(form, f'colmeia_estoque_final_{period}') for period in periods},
        'Piquet': {period: getattr(form, f'piquet_estoque_final_{period}') for period in periods},
        'Maxim': {period: getattr(form, f'maxim_estoque_final_{period}') for period in periods}
    }

    # Campos vendas - somente ler
    vendas_perdidas_por_familia = {
        'Colmeia': {period: getattr(form, f'colmeia_vendas_perdidas_{period}') for period in periods},
        'Piquet': {period: getattr(form, f'piquet_vendas_perdidas_{period}') for period in periods},
        'Maxim': {period: getattr(form, f'maxim_vendas_perdidas_{period}') for period in periods}
    }
    vendas_por_familia = {
        'Colmeia': {period: getattr(form, f'colmeia_vendas_{period}') for period in periods},
        'Piquet': {period: getattr(form, f'piquet_vendas_{period}') for period in periods},
        'Maxim': {period: getattr(form, f'maxim_vendas_{period}') for period in periods}
    }


    if request.method == 'POST':
        for familia in ['Colmeia', 'Piquet', 'Maxim']:
            for period in periods:
                if period >= periodo_atual:
                    # Obter os valores atuais do forms
                    demanda_prevista = previsoes_por_familia[familia][period].data
                    demanda_real = demanda_real_por_familia[familia][period].data
                    producao_planejada = producao_planejada_por_familia[familia][period].data
                    producao_real = producao_real_por_familia[familia][period].data
                    estoque_inicial = estoques_iniciais_por_familia[familia][period].data
                    estoque_final = estoques_finais_por_familia[familia][period].data
                    vendas_perdidas = vendas_perdidas_por_familia[familia][period].data
                    vendas = vendas_por_familia[familia][period].data

                    # Atualizar ou criar novo plano de produção
                    existing_plan = PlanoProducao.query.filter_by(
                        periodo_numero=period, familia=familia, grupo_id=current_user.id
                    ).order_by(PlanoProducao.periodo_modificado.desc()).first()

                    if existing_plan:
                        if existing_plan.periodo_modificado == periodo_atual:
                            # Atualizar o plano existente
                            existing_plan.demanda_prevista = demanda_prevista
                            existing_plan.demanda_real = demanda_real
                            existing_plan.producao_planejada = producao_planejada
                            existing_plan.producao_real = producao_real
                            existing_plan.estoques_iniciais = estoque_inicial
                            existing_plan.estoques_finais = estoque_final
                            existing_plan.vendas_perdidas = vendas_perdidas
                            existing_plan.vendas = vendas
                        else:
                            # Criar um novo plano
                            new_plan = PlanoProducao(
                                grupo_id=current_user.id,
                                periodo_numero=period,
                                periodo_modificado=periodo_atual,
                                familia=familia,

                                demanda_prevista=demanda_prevista,
                                demanda_real=demanda_real,
                                producao_planejada=producao_planejada,
                                producao_real=producao_real,
                                estoques_iniciais=estoque_inicial,
                                estoques_finais=estoque_final,
                                vendas_perdidas=vendas_perdidas,
                                vendas=vendas
                            )

                            db.session.add(new_plan)

        # TODO: Finalizar Implementação
        ####### Atualizar as outras TABELAS#####
        ### TEST
        start_time = time.time()

        atualizar_plano_compras(current_user)
        atualizar_capacidade_maquinas(current_user)
        atualizar_financeiro(current_user)

        end_time = time.time()  # Tempo final
        execution_time = end_time - start_time  # Calcular o tempo de execução
        print(f"Tempo de execução: {execution_time:.4f} segundos")  # Exibir o tempo de execução


        ####### Fim atualização ######

        db.session.commit()
        flash(f'Plano de produção salvo com sucesso! #Debug Time = {execution_time:.4f} segundos', 'success')
        return redirect(url_for('dashboard'))

    elif request.method == 'GET':
        # Preencher o formulário com os dados do banco de dados
        for familia in ['Colmeia', 'Piquet', 'Maxim']:
            for period in periods:
                plan = PlanoProducao.query.filter_by(
                    periodo_numero=period, familia=familia, grupo_id=current_user.id
                ).filter(PlanoProducao.periodo_modificado <= periodo_atual).order_by(PlanoProducao.periodo_modificado.desc()).first()

                if plan:
                    # Preencher os campos
                    producao_planejada_por_familia[familia][period].data = plan.producao_planejada
                    producao_real_por_familia[familia][period].data = plan.producao_real
                    previsoes_por_familia[familia][period].data = plan.demanda_prevista
                    demanda_real_por_familia[familia][period].data = plan.demanda_real
                    estoques_iniciais_por_familia[familia][period].data = plan.estoques_iniciais
                    estoques_finais_por_familia[familia][period].data = plan.estoques_finais
                    vendas_perdidas_por_familia[familia][period].data = plan.vendas_perdidas
                    vendas_por_familia[familia][period].data = plan.vendas

    return render_template(
        'production.html',
        form = form,
        periods = periods,
        periodo_atual = periodo_atual,
        producao_planejada_por_familia = producao_planejada_por_familia,
        producao_real_por_familia = producao_real_por_familia,
        previsoes_por_familia = previsoes_por_familia,
        estoques_iniciais_por_familia = estoques_iniciais_por_familia,
        estoques_finais_por_familia = estoques_finais_por_familia,
        vendas_perdidas_por_familia = vendas_perdidas_por_familia,
        vendas_por_familia = vendas_por_familia,
        demanda_real_por_familia = demanda_real_por_familia
    )


@app.route('/purchases', methods=['GET', 'POST'])
@login_required
def purchases():
    form = PurchaseForm()

    periods = list(range(13, 25))
    periodo_atual = current_user.periodo_atual

    # Campos para os materiais (Fio Algodão, Fio Sintético, Corantes)
    compras_por_material = {
        'Fio Algodao': {period: getattr(form, f'fio_algodao_{period}') for period in periods},
        'Fio Sintetico': {period: getattr(form, f'fio_sintetico_{period}') for period in periods},
        'Corantes': {period: getattr(form, f'corantes_{period}') for period in periods}
    }
    compras_real_por_material = {
        'Fio Algodao': {period: getattr(form, f'fio_algodao_compra_real_{period}') for period in periods},
        'Fio Sintetico': {period: getattr(form, f'fio_sintetico_compra_real_{period}') for period in periods},
        'Corantes': {period: getattr(form, f'corantes_compra_real_{period}') for period in periods}
    }
    compras_emergencial_por_material = {
        'Fio Algodao': {period: getattr(form, f'fio_algodao_compra_emergencial_{period}') for period in periods},
        'Fio Sintetico': {period: getattr(form, f'fio_sintetico_compra_emergencial_{period}') for period in periods},
        'Corantes': {period: getattr(form, f'corantes_compra_emergencial_{period}') for period in periods}
    }

    # Campos Estoques Inicial e Final
    estoques_iniciais_por_material = {
        'Fio Algodao': {period: getattr(form, f'fio_algodao_estoque_inicial_{period}', None) for period in periods},
        'Fio Sintetico': {period: getattr(form, f'fio_sintetico_estoque_inicial_{period}', None) for period in periods},
        'Corantes': {period: getattr(form, f'corantes_estoque_inicial_{period}', None) for period in periods}
    }
    estoques_finais_por_material = {
        'Fio Algodao': {period: getattr(form, f'fio_algodao_estoque_final_{period}', None) for period in periods},
        'Fio Sintetico': {period: getattr(form, f'fio_sintetico_estoque_final_{period}', None) for period in periods},
        'Corantes': {period: getattr(form, f'corantes_estoque_final_{period}', None) for period in periods}
    }

    # Campo Consumo Previsto e Real
    consumo_previsto_por_material = {
        'Fio Algodao': {period: getattr(form, f'fio_algodao_consumo_previsto_{period}', None) for period in periods},
        'Fio Sintetico': {period: getattr(form, f'fio_sintetico_consumo_previsto_{period}', None) for period in periods},
        'Corantes': {period: getattr(form, f'corantes_consumo_previsto_{period}', None) for period in periods}
    }
    consumo_real_por_material = {
        'Fio Algodao': {period: getattr(form, f'fio_algodao_consumo_real_{period}', None) for period in periods},
        'Fio Sintetico': {period: getattr(form, f'fio_sintetico_consumo_real_{period}', None) for period in periods},
        'Corantes': {period: getattr(form, f'corantes_consumo_real_{period}', None) for period in periods}
    }

    if request.method == 'POST':
        for material in ['Fio Algodao', 'Fio Sintetico', 'Corantes']:
            for period in periods:
                if period >= periodo_atual:
                    # Obter os valores atuais do forms
                    consumo_previsto = consumo_previsto_por_material[material][period].data
                    consumo_real = consumo_real_por_material[material][period].data
                    estoque_inicial = estoques_iniciais_por_material[material][period].data
                    estoque_final = estoques_finais_por_material[material][period].data
                    compra_planejada = compras_por_material[material][period].data
                    compra_real = compras_real_por_material[material][period].data
                    compra_emergencial = compras_emergencial_por_material[material][period].data

                    # Atualizar ou criar novo plano de compras
                    existing_plan = PlanoCompras.query.filter_by(
                        periodo_numero=period, material=material, grupo_id=current_user.id
                    ).order_by(PlanoCompras.periodo_modificado.desc()).first()

                    if existing_plan:
                        if existing_plan.periodo_modificado == periodo_atual:
                            # Atualizar o plano existente
                            existing_plan.consumo_previsto = consumo_previsto
                            existing_plan.consumo_real = consumo_real
                            existing_plan.estoques_iniciais = estoque_inicial
                            existing_plan.estoques_finais = estoque_final
                            existing_plan.compra_planejada = compra_planejada
                            existing_plan.compra_real = compra_real
                            existing_plan.compra_emergencial = compra_emergencial

                        else:
                            new_plan = PlanoCompras(
                                grupo_id=current_user.id,
                                periodo_numero=period,
                                periodo_modificado=periodo_atual,
                                material= material,

                                consumo_previsto = consumo_previsto,
                                consumo_real = consumo_real,
                                estoques_iniciais = estoque_inicial,
                                estoques_finais = estoque_final,
                                compra_planejada = compra_planejada,
                                compra_real = compra_real,
                                compra_emergencial = compra_emergencial
                            )

                            db.session.add(new_plan)

        db.session.commit()
        flash('Plano de compras salvo com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    elif request.method == 'GET':
        # Preencher o formulário com os dados do banco de dados
        for material in ['Fio Algodao', 'Fio Sintetico', 'Corantes']:
            for period in periods:
                plan = PlanoCompras.query.filter_by(
                    periodo_numero=period, material=material, grupo_id=current_user.id
                ).filter(PlanoCompras.periodo_modificado <= periodo_atual).order_by(PlanoCompras.periodo_modificado.desc()).first()

                if plan:
                    # Preencher os campos
                    compras_por_material[material][period].data = plan.compra_planejada
                    compras_real_por_material[material][period].data = plan.compra_real
                    compras_emergencial_por_material[material][period].data = plan.compra_emergencial
                    consumo_previsto_por_material[material][period].data = plan.consumo_previsto
                    consumo_real_por_material[material][period].data = plan.consumo_real
                    estoques_iniciais_por_material[material][period].data = plan.estoques_iniciais
                    estoques_finais_por_material[material][period].data = plan.estoques_finais


    return render_template(
        'purchases.html',
        form=form,
        periods=periods,
        periodo_atual=periodo_atual,
        compras_por_material=compras_por_material,
        compras_real_por_material=compras_real_por_material,
        compras_emergencial_por_material=compras_emergencial_por_material,
        estoques_iniciais_por_material=estoques_iniciais_por_material,
        estoques_finais_por_material=estoques_finais_por_material,
        consumo_previsto_por_material=consumo_previsto_por_material,
        consumo_real_por_material=consumo_real_por_material
    )


@app.route('/tecelagem', methods=['GET', 'POST'])
@login_required
def tecelagem():

    form = TecelagemForm()
    maquina = "Teares"

    periods = range(13, 25)
    periodo_atual = current_user.periodo_atual

 #                             'Fio Algodao': {period: getattr(form, f'fio_algodao_estoque_final_{period}', None) for period in periods}
    numero_turnos_dici =          {maquina: {period: getattr(form, f'numero_turnos_{period}', None) for period in periods}}
    capacidade_disponivel_dici =  {maquina: {period: getattr(form, f'capacidade_disponivel_{period}') for period in periods}}
    capacidade_necessaria_dici =  {maquina: {period: getattr(form, f'capacidade_necessaria_{period}') for period in periods}}
    colmeia_horas_dici =          {maquina: {period: getattr(form, f'colmeia_horas_{period}') for period in periods}}
    piquet_horas_dici =           {maquina: {period: getattr(form, f'piquet_horas_{period}') for period in periods}}
    maxim_horas_dici =            {maquina: {period: getattr(form, f'maxim_horas_{period}') for period in periods}}
    setup_dici =                  {maquina: {period: getattr(form, f'setup_{period}') for period in periods}}
    produtividade_dici =          {maquina: {period: getattr(form, f'produtividade_{period}') for period in periods}}
    capacidade_instalada_dici =   {maquina: {period: getattr(form, f'capacidade_instalada_{period}') for period in periods}}
    capacidade_teceirizada_dici = {maquina: {period: getattr(form, f'capacidade_teceirizada_{period}') for period in periods}}
    ampliacoes_dici =             {maquina: {period: getattr(form, f'ampliacoes_{period}', None) for period in periods}}
    reducoes_dici =               {maquina: {period: getattr(form, f'reducoes_{period}', None) for period in periods}}
    quantidade_dici =             {maquina: {period: getattr(form, f'quantidade_{period}', None) for period in periods}}

    if request.method == 'POST':
        for period in periods:
            if period >= periodo_atual:
                print("AQUI ####",numero_turnos_dici[maquina][period].data)
                #print("###", numero_turnos,"2 ####", numero_turnos[maquina])
                numero_turnos = numero_turnos_dici[maquina][period].data
                capacidade_disponivel = capacidade_disponivel_dici[maquina][period].data
                capacidade_necessaria = capacidade_necessaria_dici[maquina][period].data
                colmeia_horas = colmeia_horas_dici[maquina][period].data
                piquet_horas = piquet_horas_dici[maquina][period].data
                maxim_horas = maxim_horas_dici[maquina][period].data
                setup = setup_dici[maquina][period].data
                produtividade = produtividade_dici[maquina][period].data
                capacidade_instalada = capacidade_instalada_dici[maquina][period].data
                capacidade_teceirizada = capacidade_teceirizada_dici[maquina][period].data
                ampliacoes = ampliacoes_dici[maquina][period].data
                reducoes = reducoes_dici[maquina][period].data

                # Atualizar ou criar CapacidadeTeares
                existing_plan = CapacidadeTeares.query.filter_by(
                    periodo_numero=period, grupo_id=current_user.id
                ).order_by(CapacidadeTeares.periodo_modificado.desc()).first()

                if existing_plan:
                    if existing_plan.periodo_modificado == periodo_atual:
                        # Atualizar o plano existente
                        existing_plan.numero_turnos = numero_turnos
                        existing_plan.capacidade_terceirizada = capacidade_teceirizada
                        existing_plan.ampliacoes = ampliacoes
                        existing_plan.reducoes = reducoes

                    else:
                        # Criar um novo plano
                        new_plan = CapacidadeTeares(
                            grupo_id=current_user.id,
                            periodo_numero=period,
                            periodo_modificado=periodo_atual,

                           numero_turnos = numero_turnos,
                           capacidade_disponivel = capacidade_disponivel,
                           capacidade_necessaria = capacidade_necessaria,
                           colmeia_horas = colmeia_horas,
                           piquet_horas = piquet_horas,
                           maxim_horas = maxim_horas,
                           setup = setup,
                           produtividade = produtividade,
                           capacidade_instalada = capacidade_instalada,
                           capacidade_teceirizada = capacidade_teceirizada,
                           ampliacoes=ampliacoes,
                           reducoes=reducoes
                        )

                        db.session.add(new_plan)

        db.session.commit()
        flash('Plano de Tecelagem salvo com sucesso!', 'success')
        return redirect(url_for('dashboard'))


    elif request.method == 'GET':
        for period in periods:
            capacidade_teares = CapacidadeTeares.query.filter_by(
                periodo_numero=period, grupo_id=current_user.id
            ).filter(CapacidadeTeares.periodo_modificado <= periodo_atual).order_by(CapacidadeTeares.periodo_modificado.desc()).first()

            if capacidade_teares:
                numero_turnos_dici[maquina][period].data = capacidade_teares.numero_turnos
                capacidade_disponivel_dici[maquina][period].data = capacidade_teares.capacidade_disponivel
                capacidade_necessaria_dici[maquina][period].data = capacidade_teares.capacidade_necessaria
                colmeia_horas_dici[maquina][period].data = capacidade_teares.colmeia
                piquet_horas_dici[maquina][period].data = capacidade_teares.piquet
                maxim_horas_dici[maquina][period].data = capacidade_teares.maxim
                setup_dici[maquina][period].data = capacidade_teares.setup
                produtividade_dici[maquina][period].data = capacidade_teares.produtividade
                capacidade_instalada_dici[maquina][period].data = capacidade_teares.capacidade_instalada
                capacidade_teceirizada_dici[maquina][period].data = capacidade_teares.capacidade_terceirizada
                ampliacoes_dici[maquina][period].data = capacidade_teares.ampliacoes
                reducoes_dici[maquina][period].data = capacidade_teares.reducoes
                quantidade_dici[maquina][period].data = capacidade_teares.quantidade

    return render_template('tecelagem.html',
                           form=form,
                           periods=periods,
                           periodo_atual=periodo_atual,
                           numero_turnos = numero_turnos_dici,
                           capacidade_disponivel = capacidade_disponivel_dici,
                           capacidade_necessaria = capacidade_necessaria_dici,
                           colmeia_horas = colmeia_horas_dici,
                           piquet_horas = piquet_horas_dici,
                           maxim_horas = maxim_horas_dici,
                           setup = setup_dici,
                           produtividade = produtividade_dici,
                           capacidade_instalada = capacidade_instalada_dici,
                           capacidade_teceirizada = capacidade_teceirizada_dici,
                           ampliacoes=ampliacoes_dici,
                           reducoes=reducoes_dici,
                           quantidade=quantidade_dici)


# Purga e Tinturaria (Jets)
@app.route('/purga_tinturaria', methods=['GET', 'POST'])
@login_required
def purga_tinturaria():

    form = PurgaTinturariaForm()
    maquina = "Jet"
    periods = range(13, 25)
    periodo_atual = current_user.periodo_atual

    numero_turnos_dici =             {maquina: {period: getattr(form, f'numero_turnos_{period}') for period in periods}}
    capacidade_disponivel_dici =     {maquina: {period: getattr(form, f'capacidade_disponivel_{period}') for period in periods}}
    capacidade_necessaria_dici =     {maquina: {period: getattr(form, f'capacidade_necessaria_{period}') for period in periods}}
    colmeia_horas_dici =             {maquina: {period: getattr(form, f'colmeia_horas_{period}') for period in periods}}
    piquet_horas_dici =              {maquina: {period: getattr(form, f'piquet_horas_{period}') for period in periods}}
    maxim_horas_dici =               {maquina: {period: getattr(form, f'maxim_horas_{period}') for period in periods}}
    setup_dici =                     {maquina: {period: getattr(form, f'setup_{period}') for period in periods}}
    produtividade_dici =             {maquina: {period: getattr(form, f'produtividade_{period}') for period in periods}}
    capacidade_instalada_jet1_dici = {maquina: {period: getattr(form, f'capacidade_instalada_jet1_{period}') for period in periods}}
    capacidade_instalada_jet2_dici = {maquina: {period: getattr(form, f'capacidade_instalada_jet2_{period}') for period in periods}}
    capacidade_instalada_jet3_dici = {maquina: {period: getattr(form, f'capacidade_instalada_jet3_{period}') for period in periods}}
    capacidade_teceirizada_dici =    {maquina: {period: getattr(form, f'capacidade_teceirizada_{period}') for period in periods}}
    ampliacoes_jet1_dici =           {maquina: {period: getattr(form, f'ampliacoes_jet1_{period}', None) for period in periods}}
    ampliacoes_jet2_dici =           {maquina: {period: getattr(form, f'ampliacoes_jet2_{period}', None) for period in periods}}
    ampliacoes_jet3_dici =           {maquina: {period: getattr(form, f'ampliacoes_jet3_{period}', None) for period in periods}}
    reducoes_jet1_dici =             {maquina: {period: getattr(form, f'reducoes_jet1_{period}', None) for period in periods}}
    reducoes_jet2_dici =             {maquina: {period: getattr(form, f'reducoes_jet2_{period}', None) for period in periods}}
    reducoes_jet3_dici =             {maquina: {period: getattr(form, f'reducoes_jet3_{period}', None) for period in periods}}
    quantidade_jet1_dici =           {maquina: {period: getattr(form, f'quantidade_jet1_{period}', None) for period in periods}}
    quantidade_jet2_dici =           {maquina: {period: getattr(form, f'quantidade_jet2_{period}', None) for period in periods}}
    quantidade_jet3_dici =           {maquina: {period: getattr(form, f'quantidade_jet3_{period}', None) for period in periods}}

    if request.method == 'POST':
        for period in periods:
            if period >= periodo_atual:
                # Obtenha os valores de produção planejada e demanda prevista para o período atual
                numero_turnos = numero_turnos_dici[maquina][period].data
                capacidade_disponivel = capacidade_disponivel_dici[maquina][period].data
                capacidade_necessaria = capacidade_necessaria_dici[maquina][period].data
                colmeia_horas = colmeia_horas_dici[maquina][period].data
                piquet_horas = piquet_horas_dici[maquina][period].data
                maxim_horas = maxim_horas_dici[maquina][period].data
                setup = setup_dici[maquina][period].data
                produtividade = produtividade_dici[maquina][period].data
                capacidade_instalada_jet1 = capacidade_instalada_jet1_dici[maquina][period].data
                capacidade_instalada_jet2 = capacidade_instalada_jet2_dici[maquina][period].data
                capacidade_instalada_jet3 = capacidade_instalada_jet3_dici[maquina][period].data
                capacidade_teceirizada = capacidade_teceirizada_dici[maquina][period].data
                ampliacoes_jet1 = ampliacoes_jet1_dici[maquina][period].data
                ampliacoes_jet2 = ampliacoes_jet2_dici[maquina][period].data
                ampliacoes_jet3 = ampliacoes_jet3_dici[maquina][period].data
                reducoes_jet1 = reducoes_jet1_dici[maquina][period].data
                reducoes_jet2 = reducoes_jet2_dici[maquina][period].data
                reducoes_jet3 = reducoes_jet3_dici[maquina][period].data
                quantidade_jet1 = quantidade_jet1_dici[maquina][period].data
                quantidade_jet2 = quantidade_jet2_dici[maquina][period].data
                quantidade_jet3 = quantidade_jet3_dici[maquina][period].data

                # Atualizar ou criar CapacidadeJets
                existing_plan = CapacidadeJets.query.filter_by(
                    periodo_numero=period, grupo_id=current_user.id
                ).order_by(CapacidadeJets.periodo_modificado.desc()).first()

                if existing_plan:
                    if existing_plan.periodo_modificado == periodo_atual:
                        # Atualizar o plano existente
                        existing_plan.numero_turnos = numero_turnos
                        existing_plan.capacidade_terceirizada = capacidade_teceirizada
                        existing_plan.ampliacoes_tipo1 = ampliacoes_jet1
                        existing_plan.ampliacoes_tipo2 = ampliacoes_jet2
                        existing_plan.ampliacoes_tipo3 = ampliacoes_jet3
                        existing_plan.reducoes_tipo1 = reducoes_jet1
                        existing_plan.reducoes_tipo2 = reducoes_jet2
                        existing_plan.reducoes_tipo3 = reducoes_jet3

                    else:
                        # Criar um novo plano
                        new_plan = CapacidadeJets(
                            grupo_id=current_user.id,
                            periodo_numero=period,
                            periodo_modificado=periodo_atual,

                           numero_turnos = numero_turnos,
                           capacidade_disponivel = capacidade_disponivel,
                           capacidade_necessaria = capacidade_necessaria,
                           colmeia_horas = colmeia_horas,
                           piquet_horas = piquet_horas,
                           maxim_horas = maxim_horas,
                           setup = setup,
                           produtividade = produtividade,
                           capacidade_instalada_tipo1 = capacidade_instalada_jet1,
                           capacidade_instalada_tipo2 = capacidade_instalada_jet2,
                           capacidade_instalada_tipo3 = capacidade_instalada_jet3,
                           capacidade_teceirizada = capacidade_teceirizada,
                           ampliacoes_tipo1 = ampliacoes_jet1,
                           ampliacoes_tipo2 = ampliacoes_jet2,
                           ampliacoes_tipo3 = ampliacoes_jet3,
                           reducoes_tipo1 = reducoes_jet1,
                           reducoes_tipo2 = reducoes_jet2,
                           reducoes_tipo3 = reducoes_jet3
                        )

                        db.session.add(new_plan)
        db.session.commit()
        flash('Plano de Purga/Tinturaria salvo com sucesso!', 'success')
        return redirect(url_for('dashboard'))


    elif request.method == 'GET':
        for period in periods:
            capacidade_jets = CapacidadeJets.query.filter_by(
                periodo_numero=period, grupo_id=current_user.id
            ).filter(CapacidadeJets.periodo_modificado <= periodo_atual).order_by(CapacidadeJets.periodo_modificado.desc()).first()

            if capacidade_jets:
                numero_turnos_dici[maquina][period].data = capacidade_jets.numero_turnos
                capacidade_disponivel_dici[maquina][period].data = capacidade_jets.capacidade_disponivel
                capacidade_necessaria_dici[maquina][period].data = capacidade_jets.capacidade_necessaria
                colmeia_horas_dici[maquina][period].data = capacidade_jets.colmeia
                piquet_horas_dici[maquina][period].data = capacidade_jets.piquet
                maxim_horas_dici[maquina][period].data = capacidade_jets.maxim
                setup_dici[maquina][period].data = capacidade_jets.setup
                produtividade_dici[maquina][period].data = capacidade_jets.produtividade
                capacidade_instalada_jet1_dici[maquina][period].data = capacidade_jets.capacidade_instalada_tipo1
                capacidade_instalada_jet2_dici[maquina][period].data = capacidade_jets.capacidade_instalada_tipo2
                capacidade_instalada_jet3_dici[maquina][period].data = capacidade_jets.capacidade_instalada_tipo3
                capacidade_teceirizada_dici[maquina][period].data = capacidade_jets.capacidade_terceirizada
                ampliacoes_jet1_dici[maquina][period].data = capacidade_jets.ampliacoes_tipo1
                ampliacoes_jet2_dici[maquina][period].data = capacidade_jets.ampliacoes_tipo2
                ampliacoes_jet3_dici[maquina][period].data = capacidade_jets.ampliacoes_tipo3
                reducoes_jet1_dici[maquina][period].data = capacidade_jets.reducoes_tipo1
                reducoes_jet2_dici[maquina][period].data = capacidade_jets.reducoes_tipo2
                reducoes_jet3_dici[maquina][period].data = capacidade_jets.reducoes_tipo3
                quantidade_jet1_dici[maquina][period].data = capacidade_jets.quantidade_tipo1
                quantidade_jet2_dici[maquina][period].data = capacidade_jets.quantidade_tipo2
                quantidade_jet3_dici[maquina][period].data = capacidade_jets.quantidade_tipo3

    return render_template('purga_tinturaria.html',
                           form=form,
                           periods=periods,
                           periodo_atual=periodo_atual,

                           numero_turnos = numero_turnos_dici,
                           capacidade_disponivel = capacidade_disponivel_dici,
                           capacidade_necessaria = capacidade_necessaria_dici,
                           colmeia_horas = colmeia_horas_dici,
                           piquet_horas = piquet_horas_dici,
                           maxim_horas = maxim_horas_dici,
                           setup = setup_dici,
                           produtividade = produtividade_dici,
                           capacidade_instalada_jet1 = capacidade_instalada_jet1_dici,
                           capacidade_instalada_jet2 = capacidade_instalada_jet2_dici,
                           capacidade_instalada_jet3 = capacidade_instalada_jet3_dici,
                           capacidade_teceirizada = capacidade_teceirizada_dici,
                           ampliacoes_jet1 = ampliacoes_jet1_dici,
                           ampliacoes_jet2 = ampliacoes_jet2_dici,
                           ampliacoes_jet3 = ampliacoes_jet3_dici,
                           reducoes_jet1 = reducoes_jet1_dici,
                           reducoes_jet2 = reducoes_jet2_dici,
                           reducoes_jet3 = reducoes_jet3_dici,
                           quantidade_jet1 = quantidade_jet1_dici,
                           quantidade_jet2 = quantidade_jet2_dici,
                           quantidade_jet3 = quantidade_jet3_dici)

# Fixação e Acabamento (Ramas)
@app.route('/fixacao_acabamento', methods=['GET', 'POST'])
@login_required
def fixacao_acabamento():
    form = FixacaoAcabamentoForm()
    maquina = "Ramas"

    periods = range(13, 25)
    periodo_atual = current_user.periodo_atual

 #                             'Fio Algodao': {period: getattr(form, f'fio_algodao_estoque_final_{period}', None) for period in periods}
    numero_turnos_dici =          {maquina: {period: getattr(form, f'numero_turnos_{period}', None) for period in periods}}
    capacidade_disponivel_dici =  {maquina: {period: getattr(form, f'capacidade_disponivel_{period}') for period in periods}}
    capacidade_necessaria_dici =  {maquina: {period: getattr(form, f'capacidade_necessaria_{period}') for period in periods}}
    colmeia_horas_dici =          {maquina: {period: getattr(form, f'colmeia_horas_{period}') for period in periods}}
    piquet_horas_dici =           {maquina: {period: getattr(form, f'piquet_horas_{period}') for period in periods}}
    maxim_horas_dici =            {maquina: {period: getattr(form, f'maxim_horas_{period}') for period in periods}}
    setup_dici =                  {maquina: {period: getattr(form, f'setup_{period}') for period in periods}}
    produtividade_dici =          {maquina: {period: getattr(form, f'produtividade_{period}') for period in periods}}
    capacidade_instalada_dici =   {maquina: {period: getattr(form, f'capacidade_instalada_{period}') for period in periods}}
    capacidade_teceirizada_dici = {maquina: {period: getattr(form, f'capacidade_teceirizada_{period}') for period in periods}}
    ampliacoes_dici =             {maquina: {period: getattr(form, f'ampliacoes_{period}', None) for period in periods}}
    reducoes_dici =               {maquina: {period: getattr(form, f'reducoes_{period}', None) for period in periods}}
    quantidade_dici =             {maquina: {period: getattr(form, f'quantidade_{period}', None) for period in periods}}

    if request.method == 'POST':
        for period in periods:
            if period >= periodo_atual:
                print("AQUI ####",numero_turnos_dici[maquina][period].data)
                #print("###", numero_turnos,"2 ####", numero_turnos[maquina])
                numero_turnos = numero_turnos_dici[maquina][period].data
                capacidade_disponivel = capacidade_disponivel_dici[maquina][period].data
                capacidade_necessaria = capacidade_necessaria_dici[maquina][period].data
                colmeia_horas = colmeia_horas_dici[maquina][period].data
                piquet_horas = piquet_horas_dici[maquina][period].data
                maxim_horas = maxim_horas_dici[maquina][period].data
                setup = setup_dici[maquina][period].data
                produtividade = produtividade_dici[maquina][period].data
                capacidade_instalada = capacidade_instalada_dici[maquina][period].data
                capacidade_teceirizada = capacidade_teceirizada_dici[maquina][period].data
                ampliacoes = ampliacoes_dici[maquina][period].data
                reducoes = reducoes_dici[maquina][period].data
                quantidade = quantidade_dici[maquina][period].data

                # Atualizar ou criar CapacidadeRamas
                existing_plan = CapacidadeRamas.query.filter_by(
                    periodo_numero=period, grupo_id=current_user.id
                ).order_by(CapacidadeRamas.periodo_modificado.desc()).first()

                if existing_plan:
                    if existing_plan.periodo_modificado == periodo_atual:
                        # Atualizar o plano existente
                        existing_plan.numero_turnos = numero_turnos
                        existing_plan.capacidade_terceirizada = capacidade_teceirizada
                        existing_plan.ampliacoes = ampliacoes
                        existing_plan.reducoes = reducoes

                    else:
                        # Criar um novo plano
                        new_plan = CapacidadeRamas(
                            grupo_id=current_user.id,
                            periodo_numero=period,
                            periodo_modificado=periodo_atual,

                           numero_turnos = numero_turnos,
                           capacidade_disponivel = capacidade_disponivel,
                           capacidade_necessaria = capacidade_necessaria,
                           colmeia_horas = colmeia_horas,
                           piquet_horas = piquet_horas,
                           maxim_horas = maxim_horas,
                           setup = setup,
                           produtividade = produtividade,
                           capacidade_instalada = capacidade_instalada,
                           capacidade_teceirizada = capacidade_teceirizada,
                           ampliacoes = ampliacoes,
                           reducoes = reducoes
                        )

                        db.session.add(new_plan)

        db.session.commit()
        flash('Plano de Fixação e Acabamento salvo com sucesso!', 'success')
        return redirect(url_for('dashboard'))


    elif request.method == 'GET':
        for period in periods:
            capacidade_teares = CapacidadeRamas.query.filter_by(
                periodo_numero=period, grupo_id=current_user.id
            ).filter(CapacidadeRamas.periodo_modificado <= periodo_atual).order_by(CapacidadeRamas.periodo_modificado.desc()).first()

            if capacidade_teares:
                numero_turnos_dici[maquina][period].data = capacidade_teares.numero_turnos
                capacidade_disponivel_dici[maquina][period].data = capacidade_teares.capacidade_disponivel
                capacidade_necessaria_dici[maquina][period].data = capacidade_teares.capacidade_necessaria
                colmeia_horas_dici[maquina][period].data = capacidade_teares.colmeia
                piquet_horas_dici[maquina][period].data = capacidade_teares.piquet
                maxim_horas_dici[maquina][period].data = capacidade_teares.maxim
                setup_dici[maquina][period].data = capacidade_teares.setup
                produtividade_dici[maquina][period].data = capacidade_teares.produtividade
                capacidade_instalada_dici[maquina][period].data = capacidade_teares.capacidade_instalada
                capacidade_teceirizada_dici[maquina][period].data = capacidade_teares.capacidade_terceirizada
                ampliacoes_dici[maquina][period].data = capacidade_teares.ampliacoes
                reducoes_dici[maquina][period].data = capacidade_teares.reducoes
                quantidade_dici[maquina][period].data = capacidade_teares.quantidade

    return render_template('fixacao_acabamento.html',
                           form=form,
                           periods=periods,
                           periodo_atual=periodo_atual,
                           numero_turnos = numero_turnos_dici,
                           capacidade_disponivel = capacidade_disponivel_dici,
                           capacidade_necessaria = capacidade_necessaria_dici,
                           colmeia_horas = colmeia_horas_dici,
                           piquet_horas = piquet_horas_dici,
                           maxim_horas = maxim_horas_dici,
                           setup = setup_dici,
                           produtividade = produtividade_dici,
                           capacidade_instalada = capacidade_instalada_dici,
                           capacidade_teceirizada = capacidade_teceirizada_dici,
                           ampliacoes=ampliacoes_dici,
                           reducoes=reducoes_dici,
                           quantidade=quantidade_dici)

@app.route('/financeiro', methods=['GET'])
@login_required
def financeiro():
    grupo_id = current_user.id
    period_list = range(13, 25)

    # Consultar dados de cada tabela e obter todos os registros
    custos_fixos = CustosFixos.query.filter_by(grupo_id=grupo_id).filter(CustosFixos.periodo.in_(period_list)).all()
    custos_compra_mp = CustosCompraMP.query.filter_by(grupo_id=grupo_id).filter(CustosCompraMP.periodo.in_(period_list)).all()
    custos_estoques = CustosEstoques.query.filter_by(grupo_id=grupo_id).filter(CustosEstoques.periodo.in_(period_list)).all()
    custos_terceirizacao = CustosTerceirizacao.query.filter_by(grupo_id=grupo_id).filter(CustosTerceirizacao.periodo.in_(period_list)).all()
    custos_capital = CustosCapital.query.filter_by(grupo_id=grupo_id).filter(CustosCapital.periodo.in_(period_list)).all()
    custos_vendas_perdidas = CustosVendasPerdidas.query.filter_by(grupo_id=grupo_id).filter(CustosVendasPerdidas.periodo.in_(period_list)).all()
    receitas_vendas = ReceitasVendas.query.filter_by(grupo_id=grupo_id).filter(ReceitasVendas.periodo.in_(period_list)).all()
    relatorio_financeiro = RelatorioFinanceiro.query.filter_by(grupo_id=grupo_id).filter(ReceitasVendas.periodo.in_(period_list)).all()

    tabelas = {
        'Relatorio Financeiro': relatorio_financeiro,
        'Custos Fixos': custos_fixos,
        'Custos Compra MP': custos_compra_mp,
        'Custos Estoques': custos_estoques,
        'Custos Terceirização': custos_terceirizacao,
        'Custos Capital': custos_capital,
        'Custos Vendas Perdidas': custos_vendas_perdidas,
        'Receitas Vendas': receitas_vendas
    }

    return render_template('financeiro.html', tabelas=tabelas)



@app.route('/simulate', methods=['POST', 'GET'])
@login_required
def simulate():
    periods = range(13, 25)
    # Pega o grupo completo do usuário autenticado
    grupo = current_user

    capacidade_teares_nao_validado = CapacidadeTeares.query.filter_by(grupo_id=grupo.id, validacao=False).first()
    capacidade_jets_nao_validado = CapacidadeJets.query.filter_by(grupo_id=grupo.id, validacao=False).first()
    capacidade_ramas_nao_validado = CapacidadeRamas.query.filter_by(grupo_id=grupo.id, validacao=False).first()

    if capacidade_teares_nao_validado or capacidade_jets_nao_validado or capacidade_ramas_nao_validado:
        flash("Existem configurações de capacidade necessária não atendidas. Verifique as tabelas das máquinas antes de continuar a simulação.", "warning")
        return redirect(url_for('dashboard'))

    # Se tudo OK executa a simulacao

    simulacao.executar_simulacao(grupo)

    # Cálculos da simulação para o período atual

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
    if grupo.periodo_atual > 12:
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

        # Reinicia o periodo_atual de todos os grupos para 12
        groups = Grupo.query.all()
        for grupo in groups:
            grupo.periodo_atual = 12

        db.session.commit()
        flash('Banco de dados resetado e período atual reiniciado para 12.', 'success')

    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(debug=True)
