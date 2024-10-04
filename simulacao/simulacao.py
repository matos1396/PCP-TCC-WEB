# simulacao.py
from models import Grupo, PlanoProducao, PlanoCompras, Custos, CapacidadeTeares, CapacidadeJets, CapacidadeRamas
from app import db

# Função principal da simulação
def executar_simulacao(grupo):

    # Buscar os dados do grupo
    periodo_atual = grupo.periodo_atual
    periodo_simular = periodo_atual + 1
    print ("Periodo Atual = ", periodo_atual)  # DEBUG

    ### Para teste###
    # TODO: Implementar Lógica para demanda real
    data_demanda_real = 3500
    ########

    ##### INICIO PLANO PRODUCAO ####
    for familia in ["Colmeia", "Piquet", "Maxim"]:
        plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                       periodo_numero = periodo_simular,
                                                       periodo_modificado = periodo_atual,
                                                       familia=familia).order_by(
                                                           PlanoProducao.periodo_numero.asc()).first()

        # Para estoque inicial Futuro
        plano_producao_futuro = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                              periodo_numero = periodo_simular+1,
                                                              periodo_modificado = periodo_atual,
                                                              familia=familia).order_by(
                                                                  PlanoProducao.periodo_numero.asc()).first()

        ##### Para teste ####
        # TODO: Implementar Lógica para produção real
        data_producao_real = plano_producao.producao_planejada
        ########

        # Demanda real e Producao Real
        plano_producao.demanda_real = data_demanda_real
        plano_producao.producao_real = data_producao_real

        # Calculo para Vendas reais e perdidas
        vendas_perdidas, vendas = calculo_vendas(plano_producao.estoques_iniciais,
                                                 data_demanda_real,
                                                 data_producao_real)
        plano_producao.vendas_perdidas = vendas_perdidas
        plano_producao.vendas = vendas

        # Calculo para estoques
        estoque_final = calculo_estoques("producao", plano_producao.estoques_iniciais,
                                         data_demanda_real,
                                         data_producao_real)

        plano_producao.estoques_finais = estoque_final
        plano_producao_futuro.estoques_iniciais = estoque_final

    db.session.commit()
    ##### FIM PLANO PRODUCAO ####


    #### INICIO PLANO COMPRAS ####

    for material in ["Fio Algodao", "Fio Sintetico", "Corantes"]:
        plano_compra = PlanoCompras.query.filter_by(grupo_id = grupo.id,
                                                    periodo_numero = periodo_simular,
                                                    periodo_modificado = periodo_atual,
                                                    material=material).order_by(
                                                        PlanoCompras.periodo_numero.asc()).first()

        # Para estoque inicial Futuro
        plano_compra_futuro = PlanoCompras.query.filter_by(grupo_id = grupo.id,
                                                           periodo_numero = periodo_simular+1,
                                                           periodo_modificado = periodo_atual,
                                                           material=material).order_by(
                                                               PlanoCompras.periodo_numero.asc()).first()

         ##### Para teste ####
        # TODO: Implementar Lógica para consumo real e compra real
        data_consumo_real = plano_compra.consumo_previsto
        data_compra_real = plano_compra.compra_planejada
        ########

        # Consumo Real e Compra Real
        plano_compra.consumo_real = data_consumo_real
        plano_compra.compra_real = data_compra_real
        ### 

        plano_compra.compra_emergencial = calculo_compra_emergencial(plano_compra.estoques_iniciais,
                                                                     data_consumo_real,
                                                                     data_compra_real)

        # Calculo para estoques
        estoque_final = calculo_estoques("compra", plano_compra.estoques_iniciais,
                                         data_consumo_real,
                                         data_compra_real,
                                         plano_compra.compra_emergencial)

        plano_compra.estoques_finais = estoque_final
        plano_compra_futuro.estoques_iniciais = estoque_final

    db.session.commit()
    #### FIM PLANO COMPRAS






# Funcao calculo vendas
def calculo_vendas(estoque_inicial, demanda_real, producao_real):

    if producao_real + estoque_inicial <= demanda_real:
        vendas = producao_real + estoque_inicial
        vendas_perdidas = demanda_real - producao_real - estoque_inicial
    else:
        vendas = round(demanda_real)
        vendas_perdidas = 0

    return vendas_perdidas, vendas

# Funcao Calculo estoque
def calculo_estoques(tipo, estoque_inicial, demanda_real, producao_real, compra_emergencial = 0):

    if tipo == "producao":
        estoque_final = producao_real - demanda_real + estoque_inicial
        if estoque_final < 0:
            estoque_final = 0
        return estoque_final
    if tipo == "compra": 
        if compra_emergencial > 0:
            estoque_final = 0
        else:             #    compra     -   consumo    +    estoque
            estoque_final = producao_real - demanda_real + estoque_inicial
        return estoque_final

# Funcao Calculo compra emergencial
def calculo_compra_emergencial(estoque_inicial, consumo_real, compra_real):

    compra_emergencial = consumo_real - compra_real - estoque_inicial
    if compra_emergencial < 0:
        compra_emergencial = 0
    return compra_emergencial 

