#!/usr/bin/env python3
"""
Script para reconstruir es.srt con solo los primeros 210 subtítulos correctos
"""

import re

def extract_first_n_subtitles(filename: str, n: int, output_filename: str):
    """Extrae los primeros n subtítulos de un archivo SRT"""
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # Remover BOM si existe
    if content.startswith('\ufeff'):
        content = content[1:]
    
    blocks = content.split('\n\n')
    good_blocks = []
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
            
        try:
            index = int(lines[0])
            if index <= n:
                good_blocks.append(block.strip())
            else:
                break
        except ValueError:
            continue
    
    # Escribir archivo limpio
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(good_blocks))
        if good_blocks:
            f.write('\n')
    
    print(f"Extraídos {len(good_blocks)} subtítulos a {output_filename}")
    return len(good_blocks)

def get_subtitle_block(filename: str, index: int) -> str:
    """Obtiene un bloque específico de subtítulo por índice"""
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    if content.startswith('\ufeff'):
        content = content[1:]
    
    blocks = content.split('\n\n')
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
            
        try:
            block_index = int(lines[0])
            if block_index == index:
                return block.strip()
        except ValueError:
            continue
    
    return None

def main():
    print("Creando archivo es.srt limpio con los primeros 210 subtítulos...")
    
    # Extraer primeros 210 subtítulos buenos
    count = extract_first_n_subtitles('es.srt.backup', 210, 'es_clean.srt')
    
    print(f"Archivo limpio creado con {count} subtítulos sincronizados")
    
    # Verificar algunos ejemplos al final
    print("\nVerificando últimos subtítulos extraídos:")
    for i in range(208, 211):
        block = get_subtitle_block('es_clean.srt', i)
        if block:
            lines = block.split('\n')
            print(f"#{i}: {lines[1]} - {lines[2][:40]}...")

if __name__ == "__main__":
    main()