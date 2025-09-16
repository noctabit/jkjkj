#!/usr/bin/env python3
"""
Script para traducción controlada y verificada desde subtítulo #211
"""

import re
import sys

def get_subtitle_block_from_en(start_index: int, end_index: int):
    """Extrae bloques de subtítulos específicos del archivo en.srt"""
    
    blocks_to_translate = []
    
    with open('en.srt', 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    if content.startswith('\ufeff'):
        content = content[1:]
    
    all_blocks = content.split('\n\n')
    
    for block in all_blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
            
        try:
            index = int(lines[0])
            if start_index <= index <= end_index:
                blocks_to_translate.append((index, block.strip()))
        except ValueError:
            continue
    
    return sorted(blocks_to_translate, key=lambda x: x[0])

def translate_text(english_text: str) -> str:
    """Traduce texto específico del inglés al español"""
    
    # Diccionario de traducciones comunes para consistencia
    translations = {
        "REEVES NARRATING": "REEVES NARRANDO",
        "MALE NEWSCASTER": "LOCUTOR MASCULINO", 
        "FEMALE NEWSCASTER": "LOCUTORA FEMENINA",
        "REPORTER": "REPORTERA",
        "WOMAN": "MUJER",
        "MAN": "HOMBRE",
        "Silk Road": "Silk Road",  # Mantener nombre propio
        "Bitcoin": "Bitcoin",  # Mantener término técnico
        "Dread Pirate Roberts": "Dread Pirate Roberts",  # Mantener nombre propio
        "FBI": "FBI",
        "DEA": "DEA",
    }
    
    # Lista de traducciones línea por línea basadas en contexto
    # Para casos específicos conocidos que requieren traducción precisa
    specific_translations = {
        "about the inner workings\nof the Silk Road and,": "sobre el funcionamiento interno\ndel Silk Road y,",
        "you know, his own identity,\nof course.": "ya sabes, su propia identidad,\npor supuesto.",
        "every law enforcement agency\nthat you can imagine.": "toda agencia de aplicación de la ley\nque puedas imaginar.",
        "is a collaborative effort.": "es un esfuerzo colaborativo.",
        "come from the community itself.": "vienen de la propia comunidad.",
        "But he did tell me like\nsome interesting things": "Pero él sí me dijo como\nalgunas cosas interesantes",
        "and the way that\nthe Silk Road works.": "y la forma en que\nfunciona el Silk Road.",
        "of anything that's main purpose\nis to harm innocent": "de cualquier cosa cuyo propósito principal\nsea dañar inocentes",
        "or that it was necessary": "o que fuera necesario",
        "to harm innocent people\nto bring to market.": "dañar gente inocente\npara llevar al mercado.",
    }
    
    # Buscar traducciones específicas primero
    for eng, spa in specific_translations.items():
        if eng.lower() in english_text.lower():
            return english_text.replace(eng, spa)
    
    # Aplicar traducciones de términos comunes
    spanish_text = english_text
    for eng, spa in translations.items():
        spanish_text = spanish_text.replace(eng, spa)
    
    # Traducciones generales por patrones
    general_patterns = [
        (r'\bthe\b', 'el/la'),  # Requiere contexto
        (r'\band\b', 'y'),
        (r'\bof\b', 'de'),
        (r'\bto\b', 'a/para'),  # Requiere contexto
        (r'\bthat\b', 'que/eso'),  # Requiere contexto
        (r'\bis\b', 'es'),
        (r'\bwas\b', 'era/estaba'),  # Requiere contexto
        (r'\bwere\b', 'eran/estaban'),  # Requiere contexto
        (r'\bwith\b', 'con'),
        (r'\bfrom\b', 'desde/de'),
        (r'\bthis\b', 'esto/este/esta'),
        (r'\bin\b', 'en'),
        (r'\bon\b', 'en/sobre'),
        (r'\bat\b', 'en/a'),
    ]
    
    # NOTA: Para este caso específico, necesitaríamos traducciones más complejas
    # Por ahora retornamos el texto marcado para traducción manual
    return f"[TRADUCIR]: {english_text}"

def append_translated_blocks(blocks_to_append: list):
    """Añade bloques traducidos al final de es.srt"""
    
    with open('es.srt', 'a', encoding='utf-8') as f:
        f.write('\n\n')  # Separador
        
        for i, (index, original_block) in enumerate(blocks_to_append):
            lines = original_block.split('\n')
            if len(lines) >= 3:
                # Mantener índice y tiempos exactos
                f.write(f"{lines[0]}\n")  # Índice
                f.write(f"{lines[1]}\n")  # Tiempos
                
                # Traducir texto
                text_lines = lines[2:]
                text = '\n'.join(text_lines)
                translated_text = translate_text(text)
                f.write(f"{translated_text}\n")
                
                # Añadir separador entre subtítulos (excepto el último)
                if i < len(blocks_to_append) - 1:
                    f.write('\n')

def main():
    if len(sys.argv) != 3:
        print("Uso: python3 controlled_translate.py <inicio> <fin>")
        print("Ejemplo: python3 controlled_translate.py 211 220")
        sys.exit(1)
    
    start_idx = int(sys.argv[1])
    end_idx = int(sys.argv[2])
    
    print(f"Extrayendo subtítulos {start_idx} a {end_idx} de en.srt...")
    
    blocks = get_subtitle_block_from_en(start_idx, end_idx)
    
    if not blocks:
        print("No se encontraron subtítulos en ese rango")
        sys.exit(1)
    
    print(f"Encontrados {len(blocks)} subtítulos para traducir")
    
    # Mostrar preview
    print("\n--- PREVIEW DE LOS PRIMEROS 2 SUBTÍTULOS ---")
    for i, (idx, block) in enumerate(blocks[:2]):
        lines = block.split('\n')
        text = '\n'.join(lines[2:])
        translated = translate_text(text)
        print(f"#{idx}: {lines[1]}")
        print(f"EN: {text[:50]}...")
        print(f"ES: {translated[:50]}...")
        print()
    
    response = input(f"¿Continuar con la traducción de {len(blocks)} subtítulos? (s/N): ")
    if response.lower() != 's':
        print("Cancelado por el usuario")
        sys.exit(0)
    
    print("Añadiendo traducciones a es.srt...")
    append_translated_blocks(blocks)
    
    print(f"✅ Completado: añadidos {len(blocks)} subtítulos ({start_idx}-{end_idx})")

if __name__ == "__main__":
    main()