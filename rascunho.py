# if dfDias['date'].is_monotonic_increasing:
#     print("As datas estão em ordem crescente.")
# elif dfDias['date'].is_monotonic_decreasing:
#     print("As datas estão em ordem decrescente.")
# else:
#     print("As datas não estão em ordem.")

# # Crie um intervalo de datas que deve estar presente no DataFrame
# intervalo_datas = pd.date_range(start=dfDias['date'].min(), end=dfDias['date'].max())

# # Encontre as datas que estão ausentes no DataFrame
# datas_faltando = set(intervalo_datas) - set(dfDias['date'])

# # Se houver datas faltando, imprima-as
# if datas_faltando:
#     print("Datas faltando:")
#     for data in datas_faltando:
#         print(data)
# else:
#     print("Não há datas faltando.")
# print(dfDias.iloc[101])
# print(dfDias.iloc[102])

##################################################