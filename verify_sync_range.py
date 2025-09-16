#!/usr/bin/env python3
"""
Script para verificar sincronización específicamente en un rango de subtítulos
"""

import re
from typing import List, Optional
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
            print(f"Error parsing subtitle: {e}")
            continue
    
    return subtitles

def verify_range_sync(en_subs: List[Subtitle], es_subs: List[Subtitle], start_range: int, end_range: int):
    """Verifica sincronización en un rango específico"""
    
    # Crear mapas por índice
    en_by_index = {sub.index: sub for sub in en_subs}
    es_by_index = {sub.index: sub for sub in es_subs}
    
    print(f"\n=== VERIFICANDO SINCRONIZACIÓN RANGO {start_range}-{end_range} ===")
    
    errors = []
    warnings = []
    good_count = 0
    
    for i in range(start_range, end_range + 1):
        en_sub = en_by_index.get(i)
        es_sub = es_by_index.get(i)
        
        if not en_sub:
            errors.append(f"#{i}: FALTA EN INGLÉS")
            continue
            
        if not es_sub:
            errors.append(f"#{i}: FALTA EN ESPAÑOL")
            continue
        
        # Verificar que los tiempos coincidan (tolerancia de 100ms para exactitud)
        time_diff = abs(en_sub.timestamp_ms - es_sub.timestamp_ms)
        
        if time_diff > 100:
            errors.append(f"#{i}: DESYNC - Diferencia: {time_diff}ms")
            print(f"    EN: {en_sub.start_time} - {en_sub.text[:40]}...")
            print(f"    ES: {es_sub.start_time} - {es_sub.text[:40]}...")
        elif time_diff > 50:
            warnings.append(f"#{i}: Pequeña desviación: {time_diff}ms")
        else:
            good_count += 1
            
        # Verificar orden cronológico
        if i > start_range:
            prev_es = es_by_index.get(i-1)
            if prev_es and es_sub.timestamp_ms < prev_es.timestamp_ms:
                errors.append(f"#{i}: ORDEN CRONOLÓGICO INCORRECTO - tiempo anterior al previo")
    
    # Reporte
    total_checked = end_range - start_range + 1
    print(f"\n--- RESULTADO RANGO {start_range}-{end_range} ---")
    print(f"Subtítulos verificados: {total_checked}")
    print(f"Perfectamente sincronizados: {good_count}")
    print(f"Advertencias menores: {len(warnings)}")
    print(f"Errores críticos: {len(errors)}")
    
    if errors:
        print(f"\n--- ERRORES CRÍTICOS ---")
        for error in errors[:10]:  # Mostrar primeros 10
            print(f"  {error}")
            
    if warnings:
        print(f"\n--- ADVERTENCIAS ---") 
        for warning in warnings[:5]:  # Mostrar primeras 5
            print(f"  {warning}")
    
    # Verificar algunos ejemplos específicos
    print(f"\n--- EJEMPLOS DE VERIFICACIÓN ---")
    sample_indices = [start_range, start_range + 50, start_range + 100, end_range - 50, end_range]
    
    for idx in sample_indices:
        if start_range <= idx <= end_range:
            en_sub = en_by_index.get(idx)
            es_sub = es_by_index.get(idx)
            if en_sub and es_sub:
                diff = abs(en_sub.timestamp_ms - es_sub.timestamp_ms)
                status = "✓" if diff <= 100 else f"✗ ({diff}ms)"
                print(f"  #{idx}: {en_sub.start_time} <-> {es_sub.start_time} {status}")
    
    return len(errors) == 0

def main():
    print("Verificando sincronización en rango específico...")
    
    try:
        en_subs = parse_srt_file('en.srt')
        es_subs = parse_srt_file('es.srt')
    except Exception as e:
        print(f"Error: {e}")
        return
    
    print(f"Cargados: {len(en_subs)} subtítulos EN, {len(es_subs)} subtítulos ES")
    
    # Verificar rango 400-800 como pidió el usuario
    is_good = verify_range_sync(en_subs, es_subs, 400, 800)
    
    if is_good:
        print("\n🎉 RESULTADO: Sincronización CORRECTA en el rango verificado")
    else:
        print("\n⚠️  RESULTADO: Se encontraron problemas de sincronización")
    
    # También verificar el final actual del archivo español
    max_es_index = max(sub.index for sub in es_subs) if es_subs else 0
    print(f"\nÚltimo subtítulo en es.srt: #{max_es_index}")
    
    # Verificar los últimos 10 subtítulos para asegurar continuidad
    if max_es_index >= 10:
        print(f"\nVerificando últimos 10 subtítulos ({max_es_index-9} a {max_es_index}):")
        verify_range_sync(en_subs, es_subs, max_es_index-9, max_es_index)

if __name__ == "__main__":
    main()