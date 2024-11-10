# app.py
import math
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from forms import (LoginForm, ProductionForm, PurchaseForm,
                   TecelagemForm, PurgaTinturariaForm, FixacaoAcabamentoForm,
                   CadastroGrupoForm)
from models import (Grupo,PlanoProducao,PlanoCompras,PrevisaoDemanda,
                    CapacidadeJets,CapacidadeRamas,CapacidadeTeares,TaxaProducao,Custos,
                    RelatorioFinanceiro,CustosCapital,CustosCompraMP,CustosEstoques,
                    CustosFixos,CustosTerceirizacao,CustosVendasPerdidas,ReceitasVendas,
                    ControlePlanos, EstiloDemanda,
                    db)
from simulacao import simulacao
from utils.func_auxiliares import (atualizar_plano_compras, atualizar_capacidade_maquinas,
                                   atualizar_financeiro, set_flag_controle)
from flask import session
from utils_db import cadastrar_grupo_db
import time # Para Testes

app = Flask(__name__)
app.config.from_object('config.Config')
app.config['SESSION_SQLALCHEMY'] = db  # Define explicitamente o uso da instância existente


db.init_app(app)
Session(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Grupo.query.get(int(user_id))

@app.before_request
def before_request():
    # Tornar a sessão permanente (renovar a duração da sessão a cada requisição)
    session.permanent = True


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
            login_user(user, remember=False)  # 'remember=True' ativa o remember-me
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
    grupo_id = current_user.id

    # Filtrar dados de produção e demanda apenas para os períodos de 13 a 25
    planos_producao = PlanoProducao.query.filter_by(grupo_id=grupo_id).filter(
        PlanoProducao.periodo_numero.between(13, 25)
    ).all()

    producao_real_por_familia = {'Colmeia': [], 'Piquet': [], 'Maxim': []}
    producao_planejada_por_familia = {'Colmeia': [], 'Piquet': [], 'Maxim': []}
    demanda_prevista_por_familia = {'Colmeia': [], 'Piquet': [], 'Maxim': []}
    demanda_real_por_familia = {'Colmeia': [], 'Piquet': [], 'Maxim': []}
    periodos_producao = sorted({plano.periodo_numero for plano in planos_producao})

    # Coletar dados para os gráficos de produção e demanda
    for plano in planos_producao:
        familia = plano.familia
        if familia in producao_real_por_familia:
            producao_real_por_familia[familia].append(plano.producao_real)
            producao_planejada_por_familia[familia].append(plano.producao_planejada)
            demanda_prevista_por_familia[familia].append(plano.demanda_prevista)
            demanda_real_por_familia[familia].append(plano.demanda_real)

    # Gráficos de Produção e Demanda
    fig_producao_real = {
        "data": [
            {
                "x": periodos_producao,
                "y": producao_real_por_familia[familia],
                "mode": "lines+markers",
                "name": f"Produção Real {familia}"
            }
            for familia in producao_real_por_familia
        ],
        "layout": {
            "title": "Produção Real por Família",
            "xaxis": {"title": "Períodos"},
            "yaxis": {"title": "Produção (unidades)"}
        }
    }

    fig_producao_planejada = {
        "data": [
            {
                "x": periodos_producao,
                "y": producao_planejada_por_familia[familia],
                "mode": "lines+markers",
                "name": f"Produção Planejada {familia}"
            }
            for familia in producao_planejada_por_familia
        ],
        "layout": {
            "title": "Produção Planejada por Família",
            "xaxis": {"title": "Períodos"},
            "yaxis": {"title": "Produção (unidades)"}
        }
    }

    fig_demanda_prevista = {
        "data": [
            {
                "x": periodos_producao,
                "y": demanda_prevista_por_familia[familia],
                "mode": "lines+markers",
                "name": f"Demanda Prevista {familia}"
            }
            for familia in demanda_prevista_por_familia
        ],
        "layout": {
            "title": "Demanda Prevista por Família",
            "xaxis": {"title": "Períodos"},
            "yaxis": {"title": "Demanda (unidades)"}
        }
    }

    fig_demanda_real = {
        "data": [
            {
                "x": periodos_producao,
                "y": demanda_real_por_familia[familia],
                "mode": "lines+markers",
                "name": f"Demanda Real {familia}"
            }
            for familia in demanda_real_por_familia
        ],
        "layout": {
            "title": "Demanda Real por Família",
            "xaxis": {"title": "Períodos"},
            "yaxis": {"title": "Demanda (unidades)"}
        }
    }

    # Filtrar dados de compras apenas para os períodos de 13 a 25
    planos_compras = PlanoCompras.query.filter_by(grupo_id=grupo_id).filter(
        PlanoCompras.periodo_numero.between(13, 25)
    ).all()

    compras_reais_por_material = {'Fio Algodao': [], 'Fio Sintetico': [], 'Corantes': []}
    compras_planejadas_por_material = {'Fio Algodao': [], 'Fio Sintetico': [], 'Corantes': []}
    periodos_compras = sorted({plano.periodo_numero for plano in planos_compras})

    # Coletar dados para os gráficos de compras
    for plano in planos_compras:
        material = plano.material
        if material in compras_reais_por_material:
            compras_reais_por_material[material].append(plano.compra_real)
            compras_planejadas_por_material[material].append(plano.compra_planejada)

    fig_compras_reais = {
        "data": [
            {
                "x": periodos_compras,
                "y": compras_reais_por_material[material],
                "mode": "lines+markers",
                "name": f"Compras Reais {material}"
            }
            for material in compras_reais_por_material
        ],
        "layout": {
            "title": "Compras Reais por Material",
            "xaxis": {"title": "Períodos"},
            "yaxis": {"title": "Compras (unidades)"}
        }
    }

    fig_compras_planejadas = {
        "data": [
            {
                "x": periodos_compras,
                "y": compras_planejadas_por_material[material],
                "mode": "lines+markers",
                "name": f"Compras Planejadas {material}"
            }
            for material in compras_planejadas_por_material
        ],
        "layout": {
            "title": "Compras Planejadas por Material",
            "xaxis": {"title": "Períodos"},
            "yaxis": {"title": "Compras (unidades)"}
        }
    }

    # Dados de capacidade dos Teares (Permanece igual)
    capacidades_teares = CapacidadeTeares.query.filter_by(grupo_id=grupo_id).filter(
        CapacidadeTeares.periodo_numero.between(13, 25)
    ).all()
    capacidades_ramas = CapacidadeRamas.query.filter_by(grupo_id=grupo_id).filter(
        CapacidadeRamas.periodo_numero.between(13, 25)
    ).all()
    capacidades_jets = CapacidadeJets.query.filter_by(grupo_id=grupo_id).filter(
        CapacidadeJets.periodo_numero.between(13, 25)
    ).all()

    # Periodos 
    periodos_teares = [cap.periodo_numero for cap in capacidades_teares]
    periodos_ramas = [cap.periodo_numero for cap in capacidades_ramas]
    periodos_jets = [cap.periodo_numero for cap in capacidades_jets]
    # Capacidade instalada
    capacidade_instalada_teares = [cap.capacidade_instalada for cap in capacidades_teares]
    capacidade_instalada_ramas = [cap.capacidade_instalada for cap in capacidades_ramas]
    capacidade_instalada_jets = [cap.capacidade_instalada for cap in capacidades_jets]
    # Capacidade Terceirizada
    capacidade_terceirizada_teares = [cap.capacidade_terceirizada for cap in capacidades_teares]
    capacidade_terceirizada_ramas = [cap.capacidade_terceirizada for cap in capacidades_ramas]
    capacidade_terceirizada_jets = [cap.capacidade_terceirizada for cap in capacidades_jets]


    # capacidade_disponivel_teares = [cap.capacidade_disponivel for cap in capacidades_teares]
    # capacidade_disponivel_ramas = [cap.capacidade_disponivel for cap in capacidades_ramas]
    # capacidade_disponivel_jets_tipo1 = [cap.capacidade_tipo1 for cap in capacidades_jets]
    # capacidade_disponivel_jets_tipo2 = [cap.capacidade_tipo2 for cap in capacidades_jets]
    # capacidade_disponivel_jets_tipo3 = [cap.capacidade_tipo3 for cap in capacidades_jets]
    # capacidade_disponivel_jets = [cap.capacidade_disponivel for cap in capacidades_jets]




    fig_teares = {
        "data": [
            {
                "x": periodos_teares,
                "y": capacidade_instalada_teares,
                "type": "bar",
                "name": "Capacidade Instalada"
            },
            {
                "x": periodos_teares,
                "y": capacidade_terceirizada_teares,
                "type": "bar",
                "name": "Capacidade Terceirizada"
            }
        ],
        "layout": {
            "title": "Capacidade Disponível dos Teares",
            "xaxis": {"title": "Períodos"},
            "yaxis": {"title": "Capacidade"},
            "barmode": "overlay"
        }
    }

    fig_ramas = {
        "data": [
            {
                "x": periodos_ramas,
                "y": capacidade_instalada_ramas,
                "type": "bar",
                "name": "Capacidade Instalada"
            },
            {
                "x": periodos_ramas,
                "y": capacidade_terceirizada_ramas,
                "type": "bar",
                "name": "Capacidade Terceirizada"
            }
        ],
        "layout": {
            "title": "Capacidade Disponível dos Ramas",
            "xaxis": {"title": "Períodos"},
            "yaxis": {"title": "Capacidade"},
            "barmode": "overlay"
        }
    }

    fig_jets = {
        "data": [
            {
                "x": periodos_jets,
                "y": capacidade_instalada_jets,
                "type": "bar",
                "name": "Capacidade Instalada"
            },
            {
                "x": periodos_jets,
                "y": capacidade_terceirizada_jets,
                "type": "bar",
                "name": "Capacidade Terceirizada"
            }
        ],
        "layout": {
            "title": "Capacidade Disponível dos Jets",
            "xaxis": {"title": "Períodos"},
            "yaxis": {"title": "Capacidade"},
            "barmode": "overlay"
        }
    }



    # fig_jets = {
    #     "data": [
    #         {
    #             "x": periodos_jets,
    #             "y": capacidade_disponivel_jets_tipo1,
    #             "type": "bar",
    #             "name": "Capacidade Tipo 1"
    #         },
    #         {
    #             "x": periodos_jets,
    #             "y": capacidade_disponivel_jets_tipo2,
    #             "type": "bar",
    #             "name": "Capacidade Tipo 2"
    #         },
    #         {
    #             "x": periodos_jets,
    #             "y": capacidade_disponivel_jets_tipo3,
    #             "type": "bar",
    #             "name": "Capacidade Tipo 3"
    #         }
    #     ],
    #     "layout": {
    #         "title": "Capacidade Disponível dos Jets por Tipo",
    #         "xaxis": {"title": "Períodos"},
    #         "yaxis": {"title": "Capacidade"},
    #         "barmode": "overlay"  # Configura as barras como sobrepostas
    #     }
    # }


    return render_template(
        'dashboard.html',
        fig_producao_real=fig_producao_real,
        fig_producao_planejada=fig_producao_planejada,
        fig_demanda_prevista=fig_demanda_prevista,
        fig_demanda_real=fig_demanda_real,
        fig_compras_reais=fig_compras_reais,
        fig_compras_planejadas=fig_compras_planejadas,
        fig_teares=fig_teares,
        fig_ramas=fig_ramas,
        fig_jets=fig_jets
    )






@app.route('/production', methods=['GET', 'POST'])
@login_required
def production():
    form = ProductionForm()

    periodo_atual = current_user.periodo_atual
    estilo_demanda = current_user.estilo_demanda
    periods = list(range(13, 25))


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

        # Flag de controle
        set_flag_controle(current_user, "producao")

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
                    producao_planejada_por_familia[familia][period].data = math.ceil(plan.producao_planejada)
                    producao_real_por_familia[familia][period].data = math.ceil(plan.producao_real)
                    previsoes_por_familia[familia][period].data = math.ceil(plan.demanda_prevista)
                    demanda_real_por_familia[familia][period].data = math.ceil(plan.demanda_real)
                    estoques_iniciais_por_familia[familia][period].data = math.ceil(plan.estoques_iniciais)
                    estoques_finais_por_familia[familia][period].data = math.ceil(plan.estoques_finais)
                    vendas_perdidas_por_familia[familia][period].data = math.ceil(plan.vendas_perdidas)
                    vendas_por_familia[familia][period].data = math.ceil(plan.vendas)

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


        # TODO: Finalizar Implementação
        ####### Atualizar as outras TABELAS#####
        ### TEST
        start_time = time.time()

        atualizar_plano_compras(current_user)
        atualizar_capacidade_maquinas(current_user)
        atualizar_financeiro(current_user)

        set_flag_controle(current_user, "compras")

        end_time = time.time()  # Tempo final
        execution_time = end_time - start_time  # Calcular o tempo de execução
        print(f"Tempo de execução: {execution_time:.4f} segundos")  # Exibir o tempo de execução


        ####### Fim atualização ######

        db.session.commit()
        flash(f'Plano de compras salvo com sucesso! #Debug Time = {execution_time:.4f} segundos', 'success')
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
                    compras_por_material[material][period].data = math.ceil(plan.compra_planejada)
                    compras_real_por_material[material][period].data = math.ceil(plan.compra_real)
                    compras_emergencial_por_material[material][period].data = math.ceil(plan.compra_emergencial)
                    consumo_previsto_por_material[material][period].data = math.ceil(plan.consumo_previsto)
                    consumo_real_por_material[material][period].data = math.ceil(plan.consumo_real)
                    estoques_iniciais_por_material[material][period].data = math.ceil(plan.estoques_iniciais)
                    estoques_finais_por_material[material][period].data = math.ceil(plan.estoques_finais)


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

    periods = list(range(13, 25))
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
                        existing_plan.quantidade = quantidade

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

        # TODO: Finalizar Implementação
        ####### Atualizar as outras TABELAS#####
        ### TEST
        start_time = time.time()

        # atualizar_plano_compras(current_user)
        atualizar_capacidade_maquinas(current_user)
        atualizar_financeiro(current_user)

        end_time = time.time()  # Tempo final
        execution_time = end_time - start_time  # Calcular o tempo de execução
        print(f"Tempo de execução: {execution_time:.4f} segundos")  # Exibir o tempo de execução


        ####### Fim atualização ######


        db.session.commit()
        flash(f'Plano de Tecelagem salvo com sucesso! #Debug Time = {execution_time:.4f} segundos', 'success')
        return redirect(url_for('dashboard'))


    elif request.method == 'GET':
        for period in periods:
            capacidade_teares = CapacidadeTeares.query.filter_by(
                periodo_numero=period, grupo_id=current_user.id
            ).filter(CapacidadeTeares.periodo_modificado <= periodo_atual).order_by(CapacidadeTeares.periodo_modificado.desc()).first()

            if capacidade_teares:
                numero_turnos_dici[maquina][period].data = math.ceil(capacidade_teares.numero_turnos)
                capacidade_disponivel_dici[maquina][period].data = math.ceil(capacidade_teares.capacidade_disponivel)
                capacidade_necessaria_dici[maquina][period].data = math.ceil(capacidade_teares.capacidade_necessaria)
                colmeia_horas_dici[maquina][period].data = math.ceil(capacidade_teares.colmeia)
                piquet_horas_dici[maquina][period].data = math.ceil(capacidade_teares.piquet)
                maxim_horas_dici[maquina][period].data = math.ceil(capacidade_teares.maxim)
                setup_dici[maquina][period].data = math.ceil(capacidade_teares.setup)
                produtividade_dici[maquina][period].data = math.ceil(capacidade_teares.produtividade)
                capacidade_instalada_dici[maquina][period].data = math.ceil(capacidade_teares.capacidade_instalada)
                capacidade_teceirizada_dici[maquina][period].data = math.ceil(capacidade_teares.capacidade_terceirizada)
                ampliacoes_dici[maquina][period].data = math.ceil(capacidade_teares.ampliacoes)
                reducoes_dici[maquina][period].data = math.ceil(capacidade_teares.reducoes)
                quantidade_dici[maquina][period].data = math.ceil(capacidade_teares.quantidade)

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
    periods = list(range(13, 25))
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
                        existing_plan.ampliacoes_jet1 = ampliacoes_jet1
                        existing_plan.ampliacoes_jet2 = ampliacoes_jet2
                        existing_plan.ampliacoes_jet3 = ampliacoes_jet3
                        existing_plan.reducoes_jet1 = reducoes_jet1
                        existing_plan.reducoes_jet2 = reducoes_jet2
                        existing_plan.reducoes_jet3 = reducoes_jet3
                        existing_plan.quantidade_jet1 = quantidade_jet1
                        existing_plan.quantidade_jet2 = quantidade_jet2
                        existing_plan.quantidade_jet3 = quantidade_jet3

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
                            reducoes_tipo3 = reducoes_jet3,
                            quantidade_jet1 = quantidade_jet1,
                            quantidade_jet2 = quantidade_jet2,
                            quantidade_jet3 = quantidade_jet3
                        )

                        db.session.add(new_plan)

        # TODO: Finalizar Implementação
        ####### Atualizar as outras TABELAS#####
        ### TEST
        start_time = time.time()

        # atualizar_plano_compras(current_user)
        atualizar_capacidade_maquinas(current_user)
        atualizar_financeiro(current_user)

        end_time = time.time()  # Tempo final
        execution_time = end_time - start_time  # Calcular o tempo de execução
        print(f"Tempo de execução: {execution_time:.4f} segundos")  # Exibir o tempo de execução


        ####### Fim atualização ######

        db.session.commit()
        flash(f'Plano de Purga/Tinturaria salvo com sucesso! #Debug Time = {execution_time:.4f} segundos', 'success')
        return redirect(url_for('dashboard'))


    elif request.method == 'GET':
        for period in periods:
            capacidade_jets = CapacidadeJets.query.filter_by(
                periodo_numero=period, grupo_id=current_user.id
            ).filter(CapacidadeJets.periodo_modificado <= periodo_atual).order_by(CapacidadeJets.periodo_modificado.desc()).first()

            if capacidade_jets:
                numero_turnos_dici[maquina][period].data = math.ceil(capacidade_jets.numero_turnos)
                capacidade_disponivel_dici[maquina][period].data = math.ceil(capacidade_jets.capacidade_disponivel)
                capacidade_necessaria_dici[maquina][period].data = math.ceil(capacidade_jets.capacidade_necessaria)
                colmeia_horas_dici[maquina][period].data = math.ceil(capacidade_jets.colmeia)
                piquet_horas_dici[maquina][period].data = math.ceil(capacidade_jets.piquet)
                maxim_horas_dici[maquina][period].data = math.ceil(capacidade_jets.maxim)
                setup_dici[maquina][period].data = math.ceil(capacidade_jets.setup)
                produtividade_dici[maquina][period].data = math.ceil(capacidade_jets.produtividade)
                capacidade_instalada_jet1_dici[maquina][period].data = math.ceil(capacidade_jets.capacidade_instalada_tipo1)
                capacidade_instalada_jet2_dici[maquina][period].data = math.ceil(capacidade_jets.capacidade_instalada_tipo2)
                capacidade_instalada_jet3_dici[maquina][period].data = math.ceil(capacidade_jets.capacidade_instalada_tipo3)
                capacidade_teceirizada_dici[maquina][period].data = math.ceil(capacidade_jets.capacidade_terceirizada)
                ampliacoes_jet1_dici[maquina][period].data = math.ceil(capacidade_jets.ampliacoes_tipo1)
                ampliacoes_jet2_dici[maquina][period].data = math.ceil(capacidade_jets.ampliacoes_tipo2)
                ampliacoes_jet3_dici[maquina][period].data = math.ceil(capacidade_jets.ampliacoes_tipo3)
                reducoes_jet1_dici[maquina][period].data = math.ceil(capacidade_jets.reducoes_tipo1)
                reducoes_jet2_dici[maquina][period].data = math.ceil(capacidade_jets.reducoes_tipo2)
                reducoes_jet3_dici[maquina][period].data = math.ceil(capacidade_jets.reducoes_tipo3)
                quantidade_jet1_dici[maquina][period].data = math.ceil(capacidade_jets.quantidade_tipo1)
                quantidade_jet2_dici[maquina][period].data = math.ceil(capacidade_jets.quantidade_tipo2)
                quantidade_jet3_dici[maquina][period].data = math.ceil(capacidade_jets.quantidade_tipo3)

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

    periods = list(range(13, 25))
    periodo_atual = current_user.periodo_atual

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
                        existing_plan.quantidade = quantidade

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
                           reducoes = reducoes,
                           quantidade = quantidade
                        )

                        db.session.add(new_plan)

        # TODO: Finalizar Implementação
        ####### Atualizar as outras TABELAS#####
        ### TEST
        start_time = time.time()

        # atualizar_plano_compras(current_user)
        atualizar_capacidade_maquinas(current_user)
        atualizar_financeiro(current_user)

        end_time = time.time()  # Tempo final
        execution_time = end_time - start_time  # Calcular o tempo de execução
        print(f"Tempo de execução: {execution_time:.4f} segundos")  # Exibir o tempo de execução


        ####### Fim atualização ######


        db.session.commit()
        flash(f'Plano de Fixação e Acabamento salvo com sucesso! #Debug Time = {execution_time:.4f} segundos', 'success')
        return redirect(url_for('dashboard'))


    elif request.method == 'GET':
        for period in periods:
            capacidade_teares = CapacidadeRamas.query.filter_by(
                periodo_numero=period, grupo_id=current_user.id
            ).filter(CapacidadeRamas.periodo_modificado <= periodo_atual).order_by(CapacidadeRamas.periodo_modificado.desc()).first()

            if capacidade_teares:
                numero_turnos_dici[maquina][period].data = math.ceil(capacidade_teares.numero_turnos)
                capacidade_disponivel_dici[maquina][period].data = math.ceil(capacidade_teares.capacidade_disponivel)
                capacidade_necessaria_dici[maquina][period].data = math.ceil(capacidade_teares.capacidade_necessaria)
                colmeia_horas_dici[maquina][period].data = math.ceil(capacidade_teares.colmeia)
                piquet_horas_dici[maquina][period].data = math.ceil(capacidade_teares.piquet)
                maxim_horas_dici[maquina][period].data = math.ceil(capacidade_teares.maxim)
                setup_dici[maquina][period].data = math.ceil(capacidade_teares.setup)
                produtividade_dici[maquina][period].data = math.ceil(capacidade_teares.produtividade)
                capacidade_instalada_dici[maquina][period].data = math.ceil(capacidade_teares.capacidade_instalada)
                capacidade_teceirizada_dici[maquina][period].data = math.ceil(capacidade_teares.capacidade_terceirizada)
                ampliacoes_dici[maquina][period].data = math.ceil(capacidade_teares.ampliacoes)
                reducoes_dici[maquina][period].data = math.ceil(capacidade_teares.reducoes)
                quantidade_dici[maquina][period].data = math.ceil(capacidade_teares.quantidade)

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

    check_producao = ControlePlanos.filter_by(grupo_id=grupo.id, plano_producao_salvo=False)
    check_compras = ControlePlanos.filter_by(grupo_id=grupo.id, plano_producao_salvo=False)

    if check_producao or check_compras == False:
        if check_producao == False:
            flash("Você não salvou um Plano de Produção para o período atual. Por favor clique no botão para salvar o plano na página Plano de Produção.", "warning")
            return redirect(url_for('dashboard'))
        if check_compras == False:
            flash("Você não salvou um Plano de Compras para o período atual. Por favor clique no botão para salvar o plano na página Plano de Compras.", "warning")
            return redirect(url_for('dashboard'))

    if capacidade_teares_nao_validado or capacidade_jets_nao_validado or capacidade_ramas_nao_validado:
        flash("Existem configurações de capacidade necessária não atendidas. Verifique as tabelas das máquinas antes de continuar a simulação.", "warning")
        return redirect(url_for('dashboard'))



    # Se tudo OK executa a simulacao

    simulacao.executar_simulacao(grupo)

    atualizar_plano_compras(grupo)
    atualizar_capacidade_maquinas(grupo)
    atualizar_financeiro(grupo)
    # Cálculos da simulação para o período atual

    # Avançar para o próximo período
    # grupo.periodo_atual += 1  # Incrementa o período atual do grupo
    # db.session.commit()

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



@app.route('/consultar_usuarios', methods=['GET', 'POST'])
@login_required
def consultar_usuarios():
    if not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('dashboard'))

    # Inicializa a lista de usuários e resultados financeiros
    usuarios = []
    resultados_financeiros = []

    # Se o método for POST, realiza a consulta
    if request.method == 'POST':
        # Obtém os parâmetros do formulário
        criterio = request.form.get('criterio')
        grupo_nome = request.form.get('grupo_nome')
        periodo_inicio = request.form.get('periodo_inicio')
        periodo_fim = request.form.get('periodo_fim')

        # Realiza a consulta de usuários com base no critério selecionado
        if criterio == 'todos':
            usuarios = Grupo.query.all()
        # elif criterio == 'administradores':
        #     usuarios = Grupo.query.filter_by(is_admin=True).all()
        elif criterio == 'grupos' and grupo_nome:
            usuarios = Grupo.query.filter(Grupo.grupo_nome.ilike(f"%{grupo_nome}%")).all()

        # Realiza a consulta de resultados financeiros se os períodos forem fornecidos
        if periodo_inicio and periodo_fim:
            try:
                # Converte os períodos para inteiros
                periodo_inicio = int(periodo_inicio)
                periodo_fim = int(periodo_fim)

                # Consulta a tabela RelatorioFinanceiro para o intervalo de períodos
                resultados_financeiros = RelatorioFinanceiro.query.filter(
                    RelatorioFinanceiro.periodo.between(periodo_inicio, periodo_fim)
                ).all()
            except ValueError:
                flash('Os períodos devem ser números inteiros.')

    # Renderiza a página com os resultados da consulta
    return render_template(
        'consultar_usuarios.html',
        usuarios=usuarios,
        resultados_financeiros=resultados_financeiros
    )


@app.route('/cadastrar_grupos', methods=['GET', 'POST'])
@login_required
def cadastrar_grupos():
    if not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('dashboard'))

    form = CadastroGrupoForm()
    # Obter os estilos de demanda disponíveis
    estilos = EstiloDemanda.query.all()
    form.estilo_demanda.choices = [(estilo.id, estilo.nome_estilo) for estilo in estilos]

    if form.validate_on_submit():
        grupo_nome = form.grupo_nome.data
        password = form.password.data
        estilo_demanda_id = form.estilo_demanda.data

        # Verificar se o nome do grupo já existe
        existing_group = Grupo.query.filter_by(grupo_nome=grupo_nome).first()
        if existing_group:
            flash('Já existe um grupo com esse nome. Por favor, escolha outro nome.', 'danger')
        else:
            dados_grupo = {
                "Nome": grupo_nome,
                "Estilo": estilo_demanda_id,
                "Senha": password
            }

            cadastrar_grupo_db(dados_grupo)

            flash('Grupo cadastrado com sucesso!', 'success')
            return redirect(url_for('cadastrar_grupos'))

    return render_template('cadastrar_grupos.html', form=form)



import csv
from io import StringIO
from flask import make_response

@app.route('/baixar_csv', methods=['POST'])
@login_required
def baixar_csv():
    if not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('dashboard'))

    # Receber parâmetros da consulta do formulário
    criterio = request.form.get('criterio')
    grupo_nome = request.form.get('grupo_nome')
    periodo_inicio = request.form.get('periodo_inicio')
    periodo_fim = request.form.get('periodo_fim')

    # Consultar os dados conforme o critério
    usuarios = []
    resultados_financeiros = []

    if criterio == 'todos':
        usuarios = Grupo.query.all()
    elif criterio == 'grupos' and grupo_nome:
        usuarios = Grupo.query.filter(Grupo.grupo_nome.ilike(f"%{grupo_nome}%")).all()

    if periodo_inicio and periodo_fim:
        try:
            periodo_inicio = int(periodo_inicio)
            periodo_fim = int(periodo_fim)
            resultados_financeiros = RelatorioFinanceiro.query.filter(
                RelatorioFinanceiro.periodo.between(periodo_inicio, periodo_fim)
            ).all()
        except ValueError:
            flash('Os períodos devem ser números inteiros.')
            return redirect(url_for('consultar_usuarios'))

    # Criar o CSV na memória
    si = StringIO()
    writer = csv.writer(si)

    # Cabeçalho dos dados
    writer.writerow(["Grupo ID", "Nome do Grupo", "Período", "Custos Fixos", "Custos Compras MP", 
                     "Custos Terceirização", "Custos Capital", "Custos Vendas Perdidas", 
                     "Custos Totais", "Receitas Vendas", "Resultado Operacional", "Resultado Operacional Acumulado"])

    # Adicionar linhas dos dados financeiros
    for resultado in resultados_financeiros:
        writer.writerow([
            resultado.grupo_id, resultado.grupo.grupo_nome, resultado.periodo,
            resultado.custos_fixos, resultado.custos_compra_mp, resultado.custos_terceirizacao,
            resultado.custos_capital, resultado.custos_vendas_perdidas, resultado.custos_totais,
            resultado.receitas_vendas, resultado.resultado_operacional, resultado.ro_acumulado
        ])

    # Configurar o CSV para download
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=resultados_financeiros.csv"
    output.headers["Content-type"] = "text/csv"
    return output



if __name__ == '__main__':
    app.run(debug=True)
