#!/usr/bin/env python3
"""
Script para analizar y reparar la sincronización entre archivos SRT en.srt y es.srt
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Subtitle:
    index: int
    start_time: str
    end_time: str
    text: str
    timestamp_ms: int  # para comparación

def parse_timestamp(time_str: str) -> int:
    """Convierte timestamp SRT a milisegundos"""
    # Formato: HH:MM:SS,mmm
    parts = time_str.replace(',', ':').split(':')
    hours, minutes, seconds, ms = map(int, parts)
    return ((hours * 3600 + minutes * 60 + seconds) * 1000) + ms

def parse_srt_file(filename: str) -> List[Subtitle]:
    """Parse archivo SRT y devuelve lista de subtítulos"""
    subtitles = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # Remover BOM si existe
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
            index = int(lines[0])
            time_line = lines[1]
            text_lines = lines[2:]
            
            # Parse tiempos
            if '-->' not in time_line:
                continue
                
            start_time, end_time = time_line.split(' --> ')
            start_ms = parse_timestamp(start_time.strip())
            
            text = '\n'.join(text_lines)
            
            subtitles.append(Subtitle(
                index=index,
                start_time=start_time.strip(),
                end_time=end_time.strip(), 
                text=text,
                timestamp_ms=start_ms
            ))
        except (ValueError, IndexError) as e:
            print(f"Error parseando bloque: {block[:50]}... - {e}")
            continue
    
    return subtitles

def find_sync_issues(en_subs: List[Subtitle], es_subs: List[Subtitle]) -> Dict:
    """Encuentra problemas de sincronización"""
    issues = {
        'missing_in_es': [],
        'duplicates_in_es': [],
        'time_drifts': [],
        'index_mismatches': []
    }
    
    # Crear mapas por tiempo
    es_by_time = {}
    for es_sub in es_subs:
        time_key = es_sub.timestamp_ms
        if time_key not in es_by_time:
            es_by_time[time_key] = []
        es_by_time[time_key].append(es_sub)
    
    print(f"Analizando {len(en_subs)} subtítulos en inglés vs {len(es_subs)} en español")
    
    # Verificar cada subtítulo en inglés
    for en_sub in en_subs:
        # Buscar coincidencia exacta por tiempo
        exact_match = es_by_time.get(en_sub.timestamp_ms, [])
        
        if not exact_match:
            # Buscar coincidencia cercana (±500ms)
            close_matches = []
            for es_time, es_list in es_by_time.items():
                if abs(es_time - en_sub.timestamp_ms) <= 500:
                    close_matches.extend(es_list)
            
            if not close_matches:
                issues['missing_in_es'].append(en_sub)
            else:
                # Hay coincidencias cercanas pero no exactas
                best_match = min(close_matches, key=lambda x: abs(x.timestamp_ms - en_sub.timestamp_ms))
                if abs(best_match.timestamp_ms - en_sub.timestamp_ms) > 200:
                    issues['time_drifts'].append((en_sub, best_match))
        else:
            # Hay coincidencia exacta - verificar si hay duplicados
            if len(exact_match) > 1:
                issues['duplicates_in_es'].extend(exact_match[1:])
            
            # Verificar si el índice coincide
            es_match = exact_match[0]
            if en_sub.index != es_match.index:
                issues['index_mismatches'].append((en_sub, es_match))
    
    return issues

def print_analysis(issues: Dict):
    """Imprime análisis de problemas"""
    print("\n=== ANÁLISIS DE SINCRONIZACIÓN ===")
    print(f"Subtítulos faltantes en español: {len(issues['missing_in_es'])}")
    print(f"Duplicados en español: {len(issues['duplicates_in_es'])}")
    print(f"Desviaciones de tiempo: {len(issues['time_drifts'])}")
    print(f"Índices no coincidentes: {len(issues['index_mismatches'])}")
    
    if issues['missing_in_es']:
        print("\n--- PRIMEROS 10 FALTANTES ---")
        for i, sub in enumerate(issues['missing_in_es'][:10]):
            print(f"#{sub.index} ({sub.start_time}): {sub.text[:50]}...")
    
    if issues['duplicates_in_es']:
        print("\n--- DUPLICADOS ENCONTRADOS ---")
        for sub in issues['duplicates_in_es'][:5]:
            print(f"#{sub.index} ({sub.start_time}): {sub.text[:50]}...")
    
    if issues['time_drifts']:
        print("\n--- DESVIACIONES DE TIEMPO ---")
        for en_sub, es_sub in issues['time_drifts'][:5]:
            drift_ms = abs(en_sub.timestamp_ms - es_sub.timestamp_ms)
            print(f"EN #{en_sub.index} ({en_sub.start_time}) vs ES #{es_sub.index} ({es_sub.start_time}) - Diferencia: {drift_ms}ms")

def main():
    print("Analizando sincronización entre en.srt y es.srt...")
    
    # Parse archivos
    try:
        en_subs = parse_srt_file('en.srt')
        es_subs = parse_srt_file('es.srt')
    except FileNotFoundError as e:
        print(f"Error: No se pudo encontrar archivo: {e}")
        return
    except Exception as e:
        print(f"Error parseando archivos: {e}")
        return
    
    # Verificar que se parsearon correctamente
    if not en_subs or not es_subs:
        print("Error: No se pudieron parsear los archivos SRT")
        return
    
    print(f"Parseados: {len(en_subs)} subtítulos en inglés, {len(es_subs)} en español")
    
    # Encontrar problemas
    issues = find_sync_issues(en_subs, es_subs)
    
    # Imprimir análisis
    print_analysis(issues)
    
    # Verificar punto específico de ruptura alrededor del #838
    print(f"\n=== VERIFICANDO ÁREA PROBLEMÁTICA (subtítulos 830-850) ===")
    for en_sub in en_subs:
        if 830 <= en_sub.index <= 850:
            # Buscar corresponsal español
            es_match = None
            for es_sub in es_subs:
                if abs(es_sub.timestamp_ms - en_sub.timestamp_ms) <= 100:
                    es_match = es_sub
                    break
            
            if es_match:
                sync_status = "✓" if en_sub.index == es_match.index else f"DESYNC (ES #{es_match.index})"
                print(f"EN #{en_sub.index} -> ES #{es_match.index if es_match else 'FALTA'} {sync_status}")
            else:
                print(f"EN #{en_sub.index} -> FALTA EN ESPAÑOL")

if __name__ == "__main__":
    main()