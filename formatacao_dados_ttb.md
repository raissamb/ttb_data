
# Formatacao dos dados de TTB

ambiente folder: ttb_data
github: sim

## Ano 1964

Arquivos originais: dta files, um por mês

Problemas:

Na componente Z tem um spike em 25/06/1964:

- Linha original no dta file: ttb640625Z0813808139081410814008141081430814308136081270811608106081100811908126081280813008133**************081139081400813908139
- Erro: 81139 nT para Z

O que foi feito para resolver?

- Para essa mesma data, o registro esta bagunçado nos arquivos em formato WDC, então por agora o que foi feito: **np.nan** para este valor
- Seria bom procurar uma tabela de livro do ano, a cópia física presente no CPGf não possui as tabelas de HMV
