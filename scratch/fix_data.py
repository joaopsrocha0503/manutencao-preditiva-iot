import os

def fix_file(file_path):
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return
    
    # Tentamos ler como utf-8, se falhar ou se tiver caracteres corrompidos, tratamos
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
            
    # Substituições de Mojibake comuns do Windows-1252 lido como UTF-8
    replacements = {
        'CrÃ­tico': 'Crítico',
        'CrÃtico': 'Crítico',
        'VibraÃ§Ã£o': 'Vibração',
        'VibraÃ§Ã£o': 'Vibração',
        'IntervenÃ§Ã£o': 'Intervenção',
        'ManutenÃ§Ã£o': 'Manutenção',
        'IntervenÃ§Ã£o': 'Intervenção',
        'ManutenÃ§Ã£o': 'Manutenção',
        'Ã­': 'í',
        'Ã§Ã£': 'çã'
    }
    
    original_content = content
    for bad, good in replacements.items():
        content = content.replace(bad, good)
        
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        print(f"Arquivo corrigido com sucesso: {file_path}")
    else:
        print(f"Nenhuma correção necessária para: {file_path}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'data', 'sensores_simulados.csv')
    ps1_path = os.path.join(base_dir, 'scripts', 'generate_data.ps1')
    
    fix_file(csv_path)
    fix_file(ps1_path)

if __name__ == '__main__':
    main()
