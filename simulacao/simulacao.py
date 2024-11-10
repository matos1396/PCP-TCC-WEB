# simulacao.py
import random
import math
from models import Grupo, PlanoProducao, PlanoCompras, Custos, CapacidadeTeares, CapacidadeJets, CapacidadeRamas, PrevisaoDemanda
from models import db
from dados.dados import demanda_base
# Função principal da simulação


#region
# def executar_simulacao(grupo):

#     # Buscar os dados do grupo
#     periodo_atual = grupo.periodo_atual
#     periodo_simular = periodo_atual + 1


#     ##### INICIO PLANO PRODUCAO ####
#     for familia in ["Colmeia", "Piquet", "Maxim"]:

#         #### CALCULO DEMANDA REAL ####
#         valor_demanda_base = db.session.query(PrevisaoDemanda.valor_previsao).filter_by(
#             familia = familia,
#             numero_periodo = periodo_simular
#         ).scalar()

#         valor_demanda_real = aplicar_variacao(valor_demanda_base, 0.1)

#         ## DEBUG
#         print("## Demanda Base: ",valor_demanda_base)
#         print("## Demanda Real: ",valor_demanda_real)
#         ## DEBUG

#         plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
#                                                        periodo_numero = periodo_simular,
#                                                        periodo_modificado = periodo_atual,
#                                                        familia=familia).order_by(
#                                                            PlanoProducao.periodo_numero.asc()).first()

#         # Para estoque inicial Futuro
#         plano_producao_futuro = PlanoProducao.query.filter_by(grupo_id = grupo.id,
#                                                               periodo_numero = periodo_simular+1,
#                                                               periodo_modificado = periodo_atual,
#                                                               familia=familia).order_by(
#                                                                   PlanoProducao.periodo_numero.asc()).first()


#         valor_producao_real = aplicar_variacao(plano_producao.producao_planejada, 0.05)

#         # Demanda real e Producao Real
#         plano_producao.demanda_real = valor_demanda_real
#         plano_producao.producao_real = valor_producao_real

#         # Calculo para Vendas reais e perdidas
#         vendas_perdidas, vendas = calculo_vendas(plano_producao.estoques_iniciais,
#                                                  valor_demanda_real,
#                                                  valor_producao_real)
#         plano_producao.vendas_perdidas = vendas_perdidas
#         plano_producao.vendas = vendas

#         # Calculo para estoques
#         estoque_final = calculo_estoques("producao", plano_producao.estoques_iniciais,
#                                          valor_demanda_real,
#                                          valor_producao_real)

#         plano_producao.estoques_finais = estoque_final
#         plano_producao_futuro.estoques_iniciais = estoque_final

#     db.session.commit()
#     ##### FIM PLANO PRODUCAO ####
#endregion

def executar_simulacao(grupo):

    # Buscar os dados do grupo
    periodo_atual = grupo.periodo_atual
    periodo_simular = periodo_atual + 1


    ##### INICIO PLANO PRODUCAO ####

    # Buscar todas as demandas base para o próximo período de uma só vez
    demandas_base = db.session.query(PrevisaoDemanda.familia, PrevisaoDemanda.valor_previsao).filter(
        PrevisaoDemanda.numero_periodo == periodo_simular
    ).all()

    # Criar um dicionário para acessar rapidamente a demanda base por família
    demandas_base_dict = {demanda.familia: demanda.valor_previsao for demanda in demandas_base}

    # Buscar todos os planos de produção para o período atual e futuro de uma só vez
    planos_producao = PlanoProducao.query.filter(
        PlanoProducao.grupo_id == grupo.id,
        PlanoProducao.periodo_numero.in_([periodo_simular, periodo_simular + 1]),
        PlanoProducao.periodo_modificado == periodo_atual,
        PlanoProducao.familia.in_(["Colmeia", "Piquet", "Maxim"])
    ).order_by(PlanoProducao.periodo_numero.asc()).all()

    # Criar dicionários para planos de produção atual e futuro
    planos_producao_dict = {
        (plano.familia, plano.periodo_numero): plano for plano in planos_producao
    }

    # Variáveis para armazenar os valores calculados para produção
    valores_producao_calculados = []

    # Loop para cada família
    for familia in ["Colmeia", "Piquet", "Maxim"]:

        #### CALCULO DEMANDA REAL ####
        valor_demanda_base = demandas_base_dict.get(familia, 0)
        valor_demanda_real = aplicar_variacao(valor_demanda_base, 0.1)

        # Obter plano de produção atual e futuro
        plano_producao = planos_producao_dict.get((familia, periodo_simular))
        plano_producao_futuro = planos_producao_dict.get((familia, periodo_simular + 1))

        if plano_producao:
            valor_producao_real = aplicar_variacao(plano_producao.producao_planejada, 0.05)

            # Demanda real e Produção Real
            plano_producao.demanda_real = valor_demanda_real
            plano_producao.producao_real = valor_producao_real

            # Calculo para Vendas reais e perdidas
            vendas_perdidas, vendas = calculo_vendas(plano_producao.estoques_iniciais,
                                                     valor_demanda_real,
                                                     valor_producao_real)
            plano_producao.vendas_perdidas = vendas_perdidas
            plano_producao.vendas = vendas

            # Calculo para estoques
            estoque_final = calculo_estoques("producao", plano_producao.estoques_iniciais,
                                             valor_demanda_real,
                                             valor_producao_real)

            plano_producao.estoques_finais = estoque_final

            if plano_producao_futuro:
                plano_producao_futuro.estoques_iniciais = estoque_final

            # Armazena os valores calculados para atualização futura
            valores_producao_calculados.append({
                "familia": familia,
                "demanda_real": valor_demanda_real,
                "producao_real": valor_producao_real
            })

    # Commit para salvar os cálculos
    db.session.commit()

    #### INICIO PLANO COMPRAS ####

    # Buscar todos os planos de compras para o período atual e futuro de uma só vez
    planos_compras = PlanoCompras.query.filter(
        PlanoCompras.grupo_id == grupo.id,
        PlanoCompras.periodo_numero.in_([periodo_simular, periodo_simular + 1]),
        PlanoCompras.periodo_modificado == periodo_atual,
        PlanoCompras.material.in_(["Fio Algodao", "Fio Sintetico", "Corantes"])
    ).order_by(PlanoCompras.periodo_numero.asc()).all()

    # Criar dicionários para planos de compra atual e futuro
    planos_compras_dict = {
        (plano.material, plano.periodo_numero): plano for plano in planos_compras
    }

    # Variáveis para armazenar os valores calculados para compras
    valores_compras_calculados = []

    # Loop para cada material
    for material in ["Fio Algodao", "Fio Sintetico", "Corantes"]:
        # Obter plano de compra atual e futuro
        plano_compra = planos_compras_dict.get((material, periodo_simular))
        plano_compra_futuro = planos_compras_dict.get((material, periodo_simular + 1))

        if plano_compra:
            ##### Para teste ####
            consumo_real = calcular_consumo_real(grupo, material, periodo_simular, periodo_atual)
            data_consumo_real = consumo_real
            data_compra_real = plano_compra.compra_planejada
            ########

            # Consumo Real e Compra Real
            plano_compra.consumo_real = data_consumo_real
            plano_compra.compra_real = data_compra_real

            # Calculo para compra emergencial
            plano_compra.compra_emergencial = calculo_compra_emergencial(
                plano_compra.estoques_iniciais,
                data_consumo_real,
                data_compra_real
            )

            # Calculo para estoques
            estoque_final = calculo_estoques(
                "compra",
                plano_compra.estoques_iniciais,
                data_consumo_real,
                data_compra_real,
                plano_compra.compra_emergencial
            )

            plano_compra.estoques_finais = estoque_final

            if plano_compra_futuro:
                plano_compra_futuro.estoques_iniciais = estoque_final

            # Armazena os valores calculados para atualização futura
            valores_compras_calculados.append({
                "material": material,
                "consumo_real": data_consumo_real,
                "compra_real": data_compra_real
            })

    # Commit para salvar os cálculos
    db.session.commit()

    # Incrementar o periodo_atual
    grupo.periodo_atual += 1
    db.session.commit()


    planos_producao_atualizado = PlanoProducao.query.filter(
            PlanoProducao.grupo_id == grupo.id,
            PlanoProducao.periodo_modificado == periodo_atual,
            PlanoProducao.familia.in_(["Colmeia", "Piquet", "Maxim"])
        ).order_by(PlanoProducao.periodo_numero.asc()).all()

    planos_compras_atualizado = PlanoCompras.query.filter(
            PlanoCompras.grupo_id == grupo.id,
            PlanoCompras.periodo_modificado == periodo_atual
        ).order_by(PlanoCompras.periodo_numero.asc()).all()


    # Fazer uma cópia dos registros existentes e atualizar os campos necessários

    for plano_producao in planos_producao_atualizado:
        novo_plano_producao = PlanoProducao(
            grupo_id=plano_producao.grupo_id,
            periodo_numero=plano_producao.periodo_numero,
            periodo_modificado=grupo.periodo_atual,
            familia=plano_producao.familia,
            demanda_real=plano_producao.demanda_real,
            demanda_prevista=plano_producao.demanda_prevista,
            producao_real=plano_producao.producao_real,
            producao_planejada=plano_producao.producao_planejada,
            vendas_perdidas=plano_producao.vendas_perdidas,
            vendas=plano_producao.vendas,
            estoques_iniciais=plano_producao.estoques_iniciais,
            estoques_finais=plano_producao.estoques_finais
        )
        db.session.add(novo_plano_producao)

    for plano_compra in planos_compras_atualizado:
        novo_plano_compra = PlanoCompras(
            grupo_id=plano_compra.grupo_id,
            periodo_numero=plano_compra.periodo_numero,
            periodo_modificado=grupo.periodo_atual,
            material=plano_compra.material,
            consumo_real=plano_compra.consumo_real,
            compra_real=plano_compra.compra_real,
            compra_planejada=plano_compra.compra_planejada,
            compra_emergencial=plano_compra.compra_emergencial,
            estoques_iniciais=plano_compra.estoques_iniciais,
            estoques_finais=plano_compra.estoques_finais
        )
        db.session.add(novo_plano_compra)

    capacidade_teares = CapacidadeTeares.query.filter(
            CapacidadeTeares.grupo_id == grupo.id,
            CapacidadeTeares.periodo_modificado == periodo_atual
    ).order_by(CapacidadeTeares.periodo_numero.asc()).all()
    capacidade_ramas = CapacidadeRamas.query.filter(
            CapacidadeRamas.grupo_id == grupo.id,
            CapacidadeRamas.periodo_modificado == periodo_atual
    ).order_by(CapacidadeRamas.periodo_numero.asc()).all()
    capacidade_jets = CapacidadeJets.query.filter(
            CapacidadeJets.grupo_id == grupo.id,
            CapacidadeJets.periodo_modificado == periodo_atual
    ).order_by(CapacidadeJets.periodo_numero.asc()).all()


    for capacidade in capacidade_teares:
        nova_capacidade = CapacidadeTeares(
            grupo_id = capacidade.grupo_id,
            periodo_numero = capacidade.periodo_numero,
            periodo_modificado = grupo.periodo_atual,
            lead_time_id = capacidade.lead_time_id,
            quantidade = capacidade.quantidade,
            ampliacoes = capacidade.ampliacoes,
            reducoes = capacidade.reducoes,
            #capacidade_disponivel = 0, #capacidade.capacidade_disponivel,
            capacidade_necessaria = capacidade.capacidade_necessaria,
            capacidade_instalada = capacidade.capacidade_instalada,
            capacidade_terceirizada = capacidade.capacidade_terceirizada,
            colmeia = 0, #capacidade.colmeia,
            piquet = 0, #capacidade.piquet,
            maxim = 0, #capacidade.maxim,
            #setup = capacidade.setup,
            #produtividade = capacidade.produtividade,
            numero_turnos = capacidade.numero_turnos,
            #validacao = capacidade.validacao
        )

        db.session.add(nova_capacidade)

    for capacidade in capacidade_ramas:
        nova_capacidade = CapacidadeRamas(
            grupo_id = capacidade.grupo_id,
            periodo_numero = capacidade.periodo_numero,
            periodo_modificado = grupo.periodo_atual,
            lead_time_id = capacidade.lead_time_id,
            quantidade = capacidade.quantidade,
            ampliacoes = capacidade.ampliacoes,
            reducoes = capacidade.reducoes,
            capacidade_disponivel = capacidade.capacidade_disponivel,
            capacidade_necessaria = capacidade.capacidade_necessaria,
            capacidade_instalada = capacidade.capacidade_instalada,
            capacidade_terceirizada = capacidade.capacidade_terceirizada,
            colmeia = capacidade.colmeia,
            piquet = capacidade.piquet,
            maxim = capacidade.maxim,
            setup = capacidade.setup,
            produtividade = capacidade.produtividade,
            numero_turnos = capacidade.numero_turnos,
            validacao = capacidade.validacao
        )

        db.session.add(nova_capacidade)

    for capacidade in capacidade_jets:
        nova_capacidade = CapacidadeJets(
            grupo_id = capacidade.grupo_id,
            periodo_numero = capacidade.periodo_numero,
            periodo_modificado = grupo.periodo_atual,
            lead_time_id = capacidade.lead_time_id,
            quantidade_tipo1 = capacidade.quantidade_tipo1,
            quantidade_tipo2 = capacidade.quantidade_tipo2,
            quantidade_tipo3 = capacidade.quantidade_tipo3,
            ampliacoes_tipo1 = capacidade.ampliacoes_tipo1,
            ampliacoes_tipo2 = capacidade.ampliacoes_tipo2,
            ampliacoes_tipo3 = capacidade.ampliacoes_tipo3,
            reducoes_tipo1 = capacidade.reducoes_tipo1,
            reducoes_tipo2 = capacidade.reducoes_tipo2,
            reducoes_tipo3 = capacidade.reducoes_tipo3,
            capacidade_tipo1 = capacidade.capacidade_tipo1,
            capacidade_tipo2 = capacidade.capacidade_tipo2,
            capacidade_tipo3 = capacidade.capacidade_tipo3,
            capacidade_disponivel = capacidade.capacidade_disponivel,
            capacidade_necessaria = capacidade.capacidade_necessaria,
            capacidade_instalada_tipo1 = capacidade.capacidade_instalada_tipo1,
            capacidade_instalada_tipo2 = capacidade.capacidade_instalada_tipo2,
            capacidade_instalada_tipo3 = capacidade.capacidade_instalada_tipo3,
            capacidade_terceirizada = capacidade.capacidade_terceirizada,
            colmeia = capacidade.colmeia,
            piquet = capacidade.piquet,
            maxim = capacidade.maxim,
            setup = capacidade.setup,
            produtividade = capacidade.produtividade,
            numero_turnos = capacidade.numero_turnos,
            validacao = capacidade.validacao
        )

        db.session.add(nova_capacidade)


    # Commit final para salvar todas as cópias e atualizações
    db.session.commit()


# Funcao calculo vendas
def calculo_vendas(estoque_inicial, demanda_real, producao_real):

    if producao_real + estoque_inicial <= demanda_real:
        vendas = producao_real + estoque_inicial
        vendas_perdidas = demanda_real - producao_real - estoque_inicial
    else:
        vendas = demanda_real
        vendas_perdidas = 0

    return math.ceil(vendas_perdidas), math.ceil(vendas)

# Funcao Calculo estoque
def calculo_estoques(tipo, estoque_inicial, demanda_real, producao_real, compra_emergencial = 0):

    if tipo == "producao":
        estoque_final = producao_real - demanda_real + estoque_inicial
        if estoque_final < 0:
            estoque_final = 0
        return math.ceil(estoque_final)
    if tipo == "compra": 
        if compra_emergencial > 0:
            estoque_final = 0
        else:             #    compra     -   consumo    +    estoque
            estoque_final = producao_real - demanda_real + estoque_inicial
        return math.ceil(estoque_final)

# Funcao Calculo compra emergencial
def calculo_compra_emergencial(estoque_inicial, consumo_real, compra_real):

    compra_emergencial = consumo_real - compra_real - estoque_inicial
    if compra_emergencial < 0:
        compra_emergencial = 0
    return math.ceil(compra_emergencial)






# Função para aplicar uma variação aleatória de ± variacao_aleatoria
def aplicar_variacao(valor_base, variacao_aleatoria):
    variacao = random.uniform(-variacao_aleatoria, variacao_aleatoria)  # Gera uma variação aleatória entre -variacao_aleatoria e variacao_aleatoria
    valor_real = valor_base * (1 + variacao)
    return math.ceil(valor_real)  # Arredonda o valor para cima


def calcular_consumo_real(grupo, material, periodo, periodo_atual):
    # #### Dicionario apenas para consulta manualmente (DEBUG / TESTE)
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
        consumo_real_fio_algodao = 0
        for familia in ["Colmeia", "Piquet"]:
            plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                        periodo_numero = periodo,
                                                        periodo_modificado = periodo_atual,
                                                        familia=familia).order_by(
                                                            PlanoProducao.periodo_numero.asc()).first()
            if familia == "Colmeia":
                consumo_real_fio_algodao += float(plano_producao.producao_real)
            if familia == "Piquet":
                consumo_real_fio_algodao += float(plano_producao.producao_real) * 0.5
        return math.ceil(consumo_real_fio_algodao)

    if material == "Fio Sintetico":
        consumo_real_fio_sintetico = 0
        for familia in ["Piquet", "Maxim"]:
            plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                        periodo_numero = periodo,
                                                        periodo_modificado = periodo_atual,
                                                        familia=familia).order_by(
                                                            PlanoProducao.periodo_numero.asc()).first()
            if familia == "Maxim":
                consumo_real_fio_sintetico += float(plano_producao.producao_real)
            if familia == "Piquet":
                consumo_real_fio_sintetico += float(plano_producao.producao_real) * 0.5
        return math.ceil(consumo_real_fio_sintetico)

    if material == "Corantes":
        consumo_real_corantes = 0
        for familia in ["Colmeia", "Piquet", "Maxim"]:
            plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                        periodo_numero = periodo,
                                                        periodo_modificado = periodo_atual,
                                                        familia=familia).order_by(
                                                            PlanoProducao.periodo_numero.asc()).first()
            if familia == "Colmeia":
                consumo_real_corantes += float(plano_producao.producao_real) * 0.02
            if familia == "Piquet":
                consumo_real_corantes += float(plano_producao.producao_real) * 0.02
            if familia == "Maxim":
                consumo_real_corantes += float(plano_producao.producao_real) * 0.02
        return math.ceil(consumo_real_corantes)



def atualizar_capacidades(grupo, periodo_atual):
    

    db.session.commit()
