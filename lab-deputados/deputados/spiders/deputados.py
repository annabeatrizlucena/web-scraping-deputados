import scrapy
import csv
from scrapy import *

COLUNAS = [
      'nome', 'genero', 'presenca_plenario', 'ausencia_justificada_plenario',
      'ausencia_nao_justificada_plenario', 'presenca_comissao',
      'ausencia_justificada_comissao', 'ausencia_nao_justificada_comissao',
      'data_nascimento', 'quant_viagem', 'salario_bruto', 'gasto_total_par',
      'gasto_total_gab', 'gasto_jan_par', 'gasto_fev_par', 'gasto_mar_par',
      'gasto_abr_par', 'gasto_maio_par', 'gasto_junho_par', 'gasto_jul_par',
      'gasto_agosto_par', 'gasto_set_par', 'gasto_out_par', 'gasto_nov_par',
      'gasto_jan_gab', 'gasto_fev_gab', 'gasto_mar_gab', 'gasto_abr_gab',
      'gasto_maio_gab', 'gasto_junho_gab', 'gasto_jul_gab', 'gasto_agosto_gab',
      'gasto_set_gab', 'gasto_out_gab', 'gasto_nov_gab'
    ]

def get_nome(response):
    dep_nome = response.css(
      'div.l-identificacao-info>ul.informacoes-deputado li::text').getall(
      )[0].replace("\n", "").strip()
    return dep_nome

def get_nascimento(response):
  try:
    nascimento = response.css(
      'div.l-identificacao-info>ul.informacoes-deputado li::text').getall(
      )[4].replace("\n", "").strip()
  except:
    nascimento = response.css(
      'div.l-identificacao-info>ul.informacoes-deputado li::text').getall(
      )[1].replace("\n", "").strip()
  return nascimento

def get_presenca(response):
  presencas = response.css("div.list-table>ul.list-table__content>li").getall()
  if (presencas != []):
    body_plenario, body_comissao = presencas
    plenario = Selector(text=body_plenario).xpath("//dd/text()").getall()
    plenario = list(
      map(lambda x: x.replace("dias", "").replace("\n", "").replace(" ", ""),
          plenario))
    presenca_plenario = float(plenario[0])
    ausencia_jus_plenario = float(plenario[1])
    ausencia_nao_jus_plenario = float(plenario[2])

    comissao = Selector(text=body_comissao).xpath("//dd/text()").getall()
    comissao = list(
      map(
        lambda x: x.replace("reuniões", "").replace("\n", "").replace(" ", ""),
        comissao))
    presenca_comissao = float(comissao[0])
    ausencia_jus_comissao = float(comissao[1])
    ausencia_nao_jus_comissao = float(comissao[2])
    return presenca_plenario, ausencia_jus_plenario, ausencia_nao_jus_plenario, presenca_comissao, ausencia_jus_comissao, ausencia_nao_jus_comissao
  else:
    return [0, 0, 0, 0, 0, 0]

def get_gasto_total_parlamento(response):
  gasto = response.css(
    "table[id=percentualgastocotaparlamentar]>tbody>tr>td::text").getall()
  try:
    gasto_total_parlamentar = float(gasto[1].replace("\n", "").replace(
      " ", "").replace("R$", "").replace(".", "").replace(',', "."))
    return gasto_total_parlamentar
  except:
    return 0  


def get_gasto_total_gabinete(response):
  gasto = response.css(
    "table[id=percentualgastoverbagabinete]>tbody>tr>td::text").getall()
  gasto_total_gabinete = float(gasto[1].replace("\n", "").replace(
    " ", "").replace("R$", "").replace(".", "").replace(',', "."))
  return gasto_total_gabinete


def get_quant_viagens(response):
  viagens = response.css('div.beneficio__viagens>a::text').getall()
  if (viagens == []):
    return 0
  return int(viagens[0])

def get_salario_bruto(response):
  salario_bruto = response.css('a.beneficio__info::text').getall()
  salario_bruto = float(salario_bruto[1].replace("\n", "").replace(
    " ", "").replace("R$", "").replace(".", "").replace(',', "."))
  return salario_bruto

def get_salario_mensal(response):
  parl = response.css(
    "table[id=gastomensalcotaparlamentar]>tbody>tr>td::text").getall()
  meses_parl = {
    'JAN': 0,
    'FEV': 0,
    'MAR': 0,
    'ABR': 0,
    'MAI': 0,
    'JUN': 0,
    'JUL': 0,
    'AGO': 0,
    'SET': 0,
    'OUT': 0,
    'NOV': 0
  }
  for i in range(0, len(parl), 3):
    mes = parl[i]
    valor = float(parl[i + 1].replace("\n", "").replace(" ", "").replace(
      "R$", "").replace(".", "").replace(',', "."))
    meses_parl[mes] = valor
  meses_parl = list(meses_parl.values())

  gab = response.css(
    "table[id=gastomensalverbagabinete]>tbody>tr>td::text").getall()
  meses_gab = {
    'JAN': 0,
    'FEV': 0,
    'MAR': 0,
    'ABR': 0,
    'MAI': 0,
    'JUN': 0,
    'JUL': 0,
    'AGO': 0,
    'SET': 0,
    'OUT': 0,
    'NOV': 0
  }
  for i in range(0, len(gab), 3):
    mes = gab[i]
    valor = float(gab[i + 1].replace("\n", "").replace(" ", "").replace(
      "R$", "").replace(".", "").replace(',', "."))
    meses_gab[mes] = valor
  meses_gab = list(meses_gab.values())

  return meses_parl + meses_gab  

class DeputadosSpider(scrapy.Spider):
  name = "deputados"
  
  def start_requests(self):

    with open('data/deputados_deputadas.csv', 'w') as file:
      writer = csv.writer(file)
      writer.writerow(COLUNAS)

    with open('data/lista_deputados_string_list.txt') as f:
      urls = f.readlines()
      urls = list(
        map(lambda x: x.replace("\n", "").replace(",", "").replace('"', ""),
            urls))
      for url in urls:
        yield scrapy.Request(url=url,
                             callback=lambda res: self.parse(res, "deputados"))

    with open('data/lista_deputadas_string_list.txt') as f:
      urls = f.readlines()
      urls = list(
        map(lambda x: x.replace("\n", "").replace(",", "").replace('"', ""),
            urls))
      for url in urls:
        yield scrapy.Request(url=url,
                             callback=lambda res: self.parse(res, "deputadas"))

  def parse(self, response, caso):
    info_dep = []
    dep_nome = get_nome(response)
    presenca = get_presenca(response)
    nascimento = get_nascimento(response)
    gasto_total_parlamentar = get_gasto_total_parlamento(response)
    gasto_total_gabinete = get_gasto_total_gabinete(response)
    quant_viagem = get_quant_viagens(response)
    salario_bruto = get_salario_bruto(response)
    gastos_mensais = get_salario_mensal(response)

    info_dep += [dep_nome]
    if(caso == 'deputadas'):
      info_dep += ['M']
    else:
      info_dep += ['H']
    info_dep += presenca
    info_dep += [nascimento]
    info_dep += [quant_viagem]
    info_dep += [salario_bruto]
    info_dep += [gasto_total_parlamentar]
    info_dep += [gasto_total_gabinete]
    info_dep += gastos_mensais

    if (len(info_dep) != len(COLUNAS)):
      print(len(info_dep), len(COLUNAS))
      print(len(gastos_mensais))

    with open(f'data/deputados_deputadas.csv', 'a') as file:
      writer = csv.writer(file)
      writer.writerow(info_dep)
