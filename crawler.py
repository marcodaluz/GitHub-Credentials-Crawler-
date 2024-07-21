import os
import re
import requests
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter o token do GitHub da variável de ambiente
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Expressões regulares para encontrar credenciais de banco de dados
regex_patterns = {
    'mysql': r'(?i)(host|user|username|password|passwd|db|database)["\']?\s*[:=]\s*["\']([^"\']+?)["\']',
    'postgres': r'(?i)(host|user|username|password|passwd|db|database)["\']?\s*[:=]\s*["\']([^"\']+?)["\']',
    'mongodb': r'(?i)(host|user|username|password|passwd|db|database)["\']?\s*[:=]\s*["\']([^"\']+?)["\']',
    'sqlserver': r'(?i)(host|user|username|password|passwd|db|database)["\']?\s*[:=]\s*["\']([^"\']+?)["\']',
    'generic': r'(?i)(database|db|host|user|username|password|passwd)["\']?\s*[:=]\s*["\']([^"\']+?)["\']',
    'database_url': r'(?i)DATABASE_URL\s*=\s*["\']([^"\']+?)["\']',  # Novo padrão para DATABASE_URL
}

# Padrões de nomes de arquivos comuns para configuração de banco de dados
db_file_patterns = [
    r'^\.env$',             # .env
    r'^config(\.py|\.yaml|\.yml|\.json)?$',  # config.py, config.yaml, config.yml, config.json
    r'^settings(\.py|\.yaml|\.yml|\.json)?$',  # settings.py, settings.yaml, settings.yml, settings.json
    r'^database(\.yml|\.yaml|\.json)?$',  # database.yml, database.yaml, database.json
    r'^db_config(\.py|\.yaml|\.yml|\.json)?$',  # db_config.py, db_config.yaml, db_config.yml, db_config.json
    r'^application(\.properties|\.yaml|\.yml|\.json)?$',  # application.properties, application.yaml, application.yml, application.json
    r'^db(\.properties|\.yaml|\.yml|\.json)?$',  # db.properties, db.yaml, db.yml, db.json
    r'^database(\.ini|\.json)$',  # database.ini, database.json
]

def is_database_config_file(file_name):
    for pattern in db_file_patterns:
        if re.match(pattern, file_name, re.IGNORECASE):
            return True
    return False

def search_repository(repo_url):
    try:
        # Extrair o nome do repositório da URL
        repo_name = repo_url.rstrip('/').split('github.com/')[-1]
        print(f"Accessing repository: {repo_name}")
        
        api_url = f"https://api.github.com/repos/{repo_name}/contents"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {GITHUB_TOKEN}'
        }
        
        results = []
        process_directory(api_url, headers, results)
        return results
    except Exception as e:
        print(f"Error accessing repository: {str(e)}")
        return {'error': str(e)}

def process_directory(api_url, headers, results):
    response = requests.get(api_url, headers=headers)
    if response.status_code == 403:  # Rate limit exceeded
        print("Rate limit exceeded. Waiting for 60 seconds...")
        time.sleep(60)  # Esperar 60 segundos antes de tentar novamente
        response = requests.get(api_url, headers=headers)
    
    response.raise_for_status()
    contents = response.json()
    
    for file_content in contents:
        if file_content['type'] == "dir":
            dir_url = file_content['_links']['self']
            process_directory(dir_url, headers, results)
        else:
            file_name = file_content['name']
            if is_database_config_file(file_name):
                print(f"Checking file: {file_content['path']}")  # Log para verificação
                file_data_response = requests.get(file_content['download_url'], headers=headers)
                if file_data_response.status_code == 403:  # Rate limit exceeded
                    print("Rate limit exceeded. Waiting for 60 seconds...")
                    time.sleep(60)  # Esperar 60 segundos antes de tentar novamente
                    file_data_response = requests.get(file_content['download_url'], headers=headers)
                
                file_data_response.raise_for_status()
                file_data = file_data_response.text
                
                found_credentials = set()  # Usar um conjunto para evitar duplicatas
                file_result = {
                    'file_path': file_content['path'],
                    'file_url': file_content['html_url'],
                    'content': file_data,  # Adicionando o conteúdo do arquivo
                    'credentials': []
                }
                
                for db_type, pattern in regex_patterns.items():
                    matches = re.findall(pattern, file_data)
                    if matches:
                        for match in matches:
                            credential = match[1]  # Capturando o segundo grupo da regex que contém o valor das credenciais
                            # Verifica se este arquivo possui credenciais específicas de banco de dados
                            if credential.strip() != "" and db_type not in file_result['credentials']:  # Verifica se há credenciais válidas
                                file_result['credentials'].append(db_type)
                
                # Adicionar os resultados deste arquivo à lista principal apenas se houver credenciais
                if file_result['credentials']:
                    results.append(file_result)


# Modifiquei a estrutura para incluir o conteúdo completo de cada arquivo encontrado

# Agora precisamos ajustar a apresentação desses resultados no front-end
