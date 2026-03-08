import struct
import string

def is_printable_ascii(byte_data):
    """Verifica se todos os bytes formam uma string ASCII imprimível padrão."""
    # Permite letras, números, pontuações e espaços
    caracteres_validos = set(string.printable.encode('ascii'))
    return all(b in caracteres_validos for b in byte_data)

def analisar_arquivo_tlv(caminho_arquivo):
    print(f"--- Iniciando Parser TLV no arquivo: {caminho_arquivo} ---\n")
    
    with open(caminho_arquivo, 'rb') as f:
        dados = f.read()

    tamanho_total = len(dados)
    i = 0
    
    resultados = []

    # Percorre o arquivo byte a byte
    while i < tamanho_total - 4:
        # Lê 4 bytes e converte para um número inteiro (Little-Endian)
        # '<I' significa: '<' (little-endian), 'I' (unsigned int de 4 bytes)
        tamanho_string = struct.unpack('<I', dados[i:i+4])[0]
        
        # Filtro de Sanidade: Uma string de metadados aqui dificilmente terá 
        # menos de 2 ou mais de 150 caracteres. Isso evita ler 'lixo' binário.
        if 2 <= tamanho_string <= 150 and (i + 4 + tamanho_string) <= tamanho_total:
            
            # Pega os bytes que supostamente representam a string
            possivel_string_bytes = dados[i+4 : i+4+tamanho_string]
            
            # Se a string for perfeitamente legível...
            if is_printable_ascii(possivel_string_bytes):
                texto_extraido = possivel_string_bytes.decode('ascii').strip()
                
                # Vamos verificar se é uma Chave Simples ou uma Variante (Regra dos 12 bytes)
                # Para ser variante, precisamos olhar 8 bytes para trás do nosso índice atual 'i'
                tipo_dado = "Chave Fixa (4 bytes)"
                
                if i >= 8:
                    # Lê os dois inteiros anteriores para ver se formam o cabeçalho de Variante
                    # Ex: [Contexto: 0 ou 1] [Tipo: 1 ou 2]
                    contexto, tipo_variante = struct.unpack('<II', dados[i-8:i])
                    
                    if contexto in (0, 1) and tipo_variante in (1, 2, 3, 4, 8):
                        tipo_dado = f"Variante (Tipo: {tipo_variante})"
                
                resultados.append({
                    'offset': i,
                    'tipo': tipo_dado,
                    'tamanho': tamanho_string,
                    'valor': texto_extraido
                })
                
                # Como encontramos uma string válida, podemos pular o índice direto para o final dela!
                i += 4 + tamanho_string
                continue
                
        i += 1 # Avança 1 byte e tenta novamente

    # --- EXIBIÇÃO DOS RESULTADOS ---
    print(f"{'OFFSET (Hex)':<15} | {'ESTRUTURA':<25} | {'TAMANHO':<8} | {'VALOR EXTRAÍDO'}")
    print("-" * 80)
    for res in resultados:
        offset_hex = f"0x{res['offset']:08X}"
        print(f"{offset_hex:<15} | {res['tipo']:<25} | {res['tamanho']:<8} | {res['valor']}")

#Para testar com o seu ficheiro extraído:
analisar_arquivo_tlv(r'C:\Users\bruno\Documents\BSP_Reader\files_for_test\TempBin\0003F13F-690A06E8.bin')