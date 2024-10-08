from models import Grupo, PlanoProducao, PlanoCompras, Custos, CapacidadeTeares, CapacidadeJets, CapacidadeRamas, TaxaProducao
from app import db
import time

def atualizar_plano_compras(grupo):
    periods = list(range(13, 25))
    periodo_atual = grupo.periodo_atual

    for material in ['Fio Algodao', 'Fio Sintetico', 'Corantes']:
        for period in periods:
            plano_compra = PlanoCompras.query.filter_by(grupo_id = grupo.id,
                                                periodo_numero = period,
                                                periodo_modificado = periodo_atual,
                                                material=material).order_by(
                                                    PlanoCompras.periodo_numero.asc()).first()

            consumo_previsto = calcular_consumo_previsto(grupo, material, period, periodo_atual)
            if plano_compra:
                plano_compra.consumo_previsto = consumo_previsto
            else:
                new_plan = PlanoCompras(
                                grupo_id=grupo.id,
                                periodo_numero=period,
                                periodo_modificado=periodo_atual,
                                material= material,

                                consumo_previsto = consumo_previsto
                            )

                db.session.add(new_plan)
    db.session.commit()


def atualizar_capacidade_maquinas(grupo):

    ### TEST
    start_time = time.time()

    periods = list(range(13, 25))
    periodo_atual = grupo.periodo_atual
    for familia in ['Colmeia', 'Piquet', 'Maxim']:
            for period in periods:
                plano_producao = PlanoProducao.query.filter_by(grupo_id=grupo.id,
                                                              familia=familia,
                                                              periodo_numero=period).order_by(
                                                                    PlanoProducao.periodo_modificado.desc()).first()
                capacidade_teares = CapacidadeTeares.query.filter_by(grupo_id = grupo.id,
                                                            periodo_numero = period,
                                                            periodo_modificado = periodo_atual).order_by(
                                                                CapacidadeTeares.periodo_numero.asc()).first()
                capacidade_ramas = CapacidadeRamas.query.filter_by(grupo_id = grupo.id,
                                                            periodo_numero = period,
                                                            periodo_modificado = periodo_atual).order_by(
                                                                CapacidadeRamas.periodo_numero.asc()).first()

                capacidade_jets = CapacidadeJets.query.filter_by(grupo_id = grupo.id,
                                           periodo_numero = period,
                                           periodo_modificado = periodo_atual).order_by(
                                               CapacidadeJets.periodo_numero.asc()).first()

                ### Taxas Máquinas/Processos ###
                # TODO: Fazer para Jets e otimizar
                taxa_tear = TaxaProducao.query.filter_by(tipo_equipamento="Teares", processo = "Malharia", familia=familia).first().taxa
                taxa_rama_1 = TaxaProducao.query.filter_by(tipo_equipamento="Ramas", processo = "Fixação", familia=familia).first().taxa
                taxa_rama_2 = TaxaProducao.query.filter_by(tipo_equipamento="Ramas", processo = "Acabamento", familia=familia).first().taxa


                if familia == "Colmeia":
                    t_tear = plano_producao.producao_planejada * taxa_tear
                    t_rama = plano_producao.producao_planejada * (taxa_rama_1 + taxa_rama_2)
                    t_jet = plano_producao.producao_planejada
                    capacidade_teares.colmeia = t_tear
                    capacidade_ramas.colmeia = t_rama
                    capacidade_jets.colmeia = t_jet
                if familia == "Piquet":
                    t_tear = plano_producao.producao_planejada * taxa_tear
                    t_rama = plano_producao.producao_planejada * (taxa_rama_1 + taxa_rama_2)
                    t_jet = plano_producao.producao_planejada
                    capacidade_teares.piquet = t_tear
                    capacidade_ramas.piquet =  t_rama
                    capacidade_jets.piquet = t_jet
                if familia == "Maxim":
                    t_tear = plano_producao.producao_planejada * taxa_tear
                    t_rama = plano_producao.producao_planejada * (taxa_rama_1 + taxa_rama_2)
                    t_jet = plano_producao.producao_planejada
                    capacidade_teares.maxim = t_tear
                    capacidade_ramas.maxim = t_rama
                    capacidade_jets.maxim = t_jet


    for period in periods: # Colocar dentro do outro loop de periodos depois
        capacidade_teares = CapacidadeTeares.query.filter_by(grupo_id = grupo.id,
                                                            periodo_numero = period,
                                                            periodo_modificado = periodo_atual).order_by(
                                                                CapacidadeTeares.periodo_numero.asc()).first()

        capacidade_ramas = CapacidadeRamas.query.filter_by(grupo_id = grupo.id,
                                                            periodo_numero = period,
                                                            periodo_modificado = periodo_atual).order_by(
                                                                CapacidadeRamas.periodo_numero.asc()).first()

        capacidade_jets = CapacidadeJets.query.filter_by(grupo_id = grupo.id,
                                           periodo_numero = period,
                                           periodo_modificado = periodo_atual).order_by(
                                               CapacidadeJets.periodo_numero.asc()).first()

        soma_teares = capacidade_teares.colmeia + capacidade_teares.piquet + capacidade_teares.maxim
        soma_ramas = capacidade_ramas.colmeia + capacidade_ramas.piquet + capacidade_ramas.maxim
        soma_jets = capacidade_jets.colmeia + capacidade_jets.piquet + capacidade_jets.maxim
        capacidade_teares.capacidade_necessaria = soma_teares + capacidade_teares.produtividade + capacidade_teares.setup
        capacidade_ramas.capacidade_necessaria = soma_ramas + capacidade_ramas.produtividade + capacidade_ramas.setup
        capacidade_jets.capacidade_necessaria = soma_jets + capacidade_jets.produtividade + capacidade_jets.setup

    db.session.commit()

    end_time = time.time()  # Tempo final
    execution_time = end_time - start_time  # Calcular o tempo de execução

    print(f"Tempo de execução: {execution_time:.4f} segundos")  # Exibir o tempo de execução


def calcular_consumo_previsto(grupo, material, periodo, periodo_atual):
    # #### Dicionario apenas para consulta manualmente
    dici_estrutura = {"Colmeia": {"Fio Algodao": 1,
                                  "Fio Sintetico": 0,
                                  "Corante": 0.02
                                  },
                      "Piquet":  {"Fio Algodao": 0.5,
                                  "Fio Sintetico": 0.5,
                                  "Corante": 0.02
                                  },
                      "Maxim":   {"Fio Algodao": 0,
                                  "Fio Sintetico": 1,
                                  "Corante": 0.02
                                  }}
    # ####
    if material == "Fio Algodao":
        consumo_previsto_fio_algodao = 0
        for familia in ["Colmeia", "Piquet"]:
            plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                        periodo_numero = periodo,
                                                        periodo_modificado = periodo_atual,
                                                        familia=familia).order_by(
                                                            PlanoProducao.periodo_numero.asc()).first()
            if familia == "Colmeia":
                consumo_previsto_fio_algodao += float(plano_producao.producao_planejada)
            if familia == "Piquet":
                consumo_previsto_fio_algodao += float(plano_producao.producao_planejada) * 0.5
        return consumo_previsto_fio_algodao

    if material == "Fio Sintetico":
        consumo_previsto_fio_sintetico = 0
        for familia in ["Piquet", "Maxim"]:
            plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                        periodo_numero = periodo,
                                                        periodo_modificado = periodo_atual,
                                                        familia=familia).order_by(
                                                            PlanoProducao.periodo_numero.asc()).first()
            if familia == "Maxim":
                consumo_previsto_fio_sintetico += float(plano_producao.producao_planejada)
            if familia == "Piquet":
                consumo_previsto_fio_sintetico += float(plano_producao.producao_planejada) * 0.5
        return consumo_previsto_fio_sintetico

    if material == "Corantes":
        consumo_previsto_corantes = 0
        for familia in ["Colmeia", "Piquet", "Maxim"]:
            plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                        periodo_numero = periodo,
                                                        periodo_modificado = periodo_atual,
                                                        familia=familia).order_by(
                                                            PlanoProducao.periodo_numero.asc()).first()
            if familia == "Colmeia":
                consumo_previsto_corantes += float(plano_producao.producao_planejada) * 0.02
            if familia == "Piquet":
                consumo_previsto_corantes += float(plano_producao.producao_planejada) * 0.02
            if familia == "Maxim":
                consumo_previsto_corantes += float(plano_producao.producao_planejada) * 0.02
        return consumo_previsto_corantes