from models import Grupo, PlanoProducao, PlanoCompras, Custos, CapacidadeTeares, CapacidadeJets, CapacidadeRamas
from app import db


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


            print(grupo, material, period, periodo_atual)
            consumo_previsto = calcular_consumo_previsto(grupo, material, period, periodo_atual)
            print(consumo_previsto)
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






def calcular_consumo_previsto(grupo, material, periodo, periodo_atual):
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

    # for familia in ["Colmeia", "Piquet", "Maxim"]:
        # plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
        #                                             periodo_numero = periodo,
        #                                             periodo_modificado = periodo_atual,
        #                                             familia=familia).order_by(
        #                                                 PlanoProducao.periodo_numero.asc()).first()

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