#!/usr/bin/env python3
"""
Script para encontrar hasta dónde la sincronización es correcta entre en.srt y es.srt
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Subtitle:
    index: int
    start_time: str
    end_time: str
    text: str
    timestamp_ms: int

def parse_timestamp(time_str: str) -> int:
    """Convierte timestamp SRT a milisegundos"""
    parts = time_str.replace(',', ':').split(':')
    hours, minutes, seconds, ms = map(int, parts)
    return ((hours * 3600 + minutes * 60 + seconds) * 1000) + ms

def parse_srt_file(filename: str) -> List[Subtitle]:
    """Parse archivo SRT y devuelve lista de subtítulos"""
    subtitles = []
    
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
            index = int(lines[0])
            time_line = lines[1]
            text_lines = lines[2:]
            
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
            continue
    
    return subtitles

def find_last_good_sync(en_subs: List[Subtitle], es_subs: List[Subtitle]) -> int:
    """Encuentra el último subtítulo que está bien sincronizado"""
    
    # Crear mapas por índice
    en_by_index = {sub.index: sub for sub in en_subs}
    es_by_index = {sub.index: sub for sub in es_subs}
    
    last_good = 0
    consecutive_good = 0
    
    print("Verificando sincronización subtítulo por subtítulo...")
    
    for i in range(1, min(max(en_by_index.keys()), max(es_by_index.keys())) + 1):
        en_sub = en_by_index.get(i)
        es_sub = es_by_index.get(i)
        
        if not en_sub or not es_sub:
            print(f"#{i}: FALTA ({'EN' if not en_sub else 'ES'})")
            consecutive_good = 0
            continue
        
        # Verificar que los tiempos coincidan (tolerancia de 500ms)
        time_diff = abs(en_sub.timestamp_ms - es_sub.timestamp_ms)
        
        if time_diff <= 500:
            consecutive_good += 1
            if consecutive_good >= 5:  # Necesitamos al menos 5 consecutivos buenos
                last_good = i
        else:
            print(f"#{i}: DESYNC - Diferencia de tiempo: {time_diff}ms")
            print(f"    EN: {en_sub.start_time} - {en_sub.text[:30]}...")
            print(f"    ES: {es_sub.start_time} - {es_sub.text[:30]}...")
            consecutive_good = 0
        
        # Reportar cada 50 subtítulos
        if i % 50 == 0:
            status = "✓" if consecutive_good > 0 else "✗"
            print(f"Progreso: {i} subtítulos verificados {status} (Último bueno: {last_good})")
    
    return last_good

def main():
    print("Buscando el último punto de sincronización correcta...")
    
    try:
        en_subs = parse_srt_file('en.srt')
        es_subs = parse_srt_file('es.srt')
    except Exception as e:
        print(f"Error: {e}")
        return
    
    print(f"Cargados: {len(en_subs)} subtítulos EN, {len(es_subs)} subtítulos ES")
    
    last_good = find_last_good_sync(en_subs, es_subs)
    
    print(f"\n=== RESULTADO ===")
    print(f"Último subtítulo bien sincronizado: #{last_good}")
    
    if last_good > 0:
        # Mostrar algunos detalles del último bueno
        en_by_index = {sub.index: sub for sub in en_subs}
        es_by_index = {sub.index: sub for sub in es_subs}
        
        for i in range(max(1, last_good - 2), last_good + 1):
            en_sub = en_by_index.get(i)
            es_sub = es_by_index.get(i)
            if en_sub and es_sub:
                print(f"#{i}: {en_sub.start_time} -> {es_sub.start_time}")
    
    # Calcular estadísticas
    total_en = len(en_subs)
    percentage_good = (last_good / total_en) * 100 if total_en > 0 else 0
    remaining = total_en - last_good
    
    print(f"\nEstadísticas:")
    print(f"- Porcentaje bien sincronizado: {percentage_good:.1f}%")
    print(f"- Subtítulos por reconstruir: {remaining}")
    print(f"- Total en inglés: {total_en}")

if __name__ == "__main__":
    main()