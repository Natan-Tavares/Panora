import json
import os

nome_arquivo = 'noticias.json'


with open(nome_arquivo, 'r', encoding='utf-8') as f:
    dados = json.load(f)

opcao = input("Digite sua opção (1 ou 2): ").strip()

if opcao == '1':
    for item in dados:
        item['img_nome'] = 'foto1.jpg'

elif opcao == '2':
    for i, item in enumerate(dados):
        item['img_nome'] = f'foto{i+1}.jpg'

try:
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Sucesso! O arquivo '{nome_arquivo}' foi atualizado.")
except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo: {e}")
