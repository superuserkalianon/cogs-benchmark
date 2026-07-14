#!/usr/bin/env python3
"""
👁 FUSION LOOP — Der geschlossene Forschungszyklus
==================================================
CEREBRO → GRIND → COGS → META-SURGEON → FINANCIAL → CEREBRO

Alle 5 Komponenten existierten einzeln. Dieses Skript verbindet sie.
Das ist die letzte fehlende Brücke aus ASYMMETRIC_FUSION.md.

Prinzip: MCTS zerlegt → parallel testen → Benchmark messen →
         bei Verbesserung patchen → Profit loggen → zurück zu MCTS
"""

import sys, os, json, time, sqlite3
from pathlib import Path
from datetime import datetime, timezone

HOME = str(Path.home())
sys.path.insert(0, f"{HOME}/agent_skills")

# ═══════════════════════════════════════════════════════
# KOMPONENTEN LADEN
# ═══════════════════════════════════════════════════════

from mythos_cerebro import CerebroOrchestrator, MCTSPlanner
from mythos_grind import GrindEngine
from mythos_memory import HyperContextMemory
from mythos_shield import ShieldLayer

MONETIZATION_DB = f"{HOME}/.hermes/monetization.db"


# ═══════════════════════════════════════════════════════
# PHASE 1: CEREBRO — Task-Dekomposition
# ═══════════════════════════════════════════════════════

def cerebro_phase(task: str):
    """CEREBRO: Zerlege Task in Subtasks via MCTS."""
    planner = MCTSPlanner()
    plan = planner.decompose(task, max_subtasks=5)
    
    print(f"[CEREBRO] Task: {task[:80]}")
    print(f"[CEREBRO] Subtasks: {len(plan.subtasks)}")
    for st in plan.subtasks[:3]:
        print(f"  [{st.priority:.1f}] {st.description[:80]}")
    
    return plan


# ═══════════════════════════════════════════════════════
# PHASE 2: GRIND — Parallele Experimente
# ═══════════════════════════════════════════════════════

def grind_phase(subtasks):
    """GRIND: Führe Subtasks parallel aus."""
    
    def execute_subtask(st):
        """Führt einen Subtask aus (Mock — in Produktion: LLM-Call)."""
        # In Produktion: rufe DeepSeek API mit st.description
        # Für jetzt: simuliere Ergebnis basierend auf Task-Text
        import hashlib
        h = hashlib.md5(st.description.encode()).hexdigest()
        return {
            'task': st.description[:60],
            'priority': st.priority,
            'result_hash': h[:8],
            'confidence': 0.5 + (int(h[:2], 16) / 512),  # 0.5-1.0
        }
    
    results = [execute_subtask(st) for st in subtasks]
    
    print(f"[GRIND] Experimente: {len(results)} ausgeführt")
    for r in results[:3]:
        print(f"  conf={r['confidence']:.3f} {r['task'][:60]}")
    
    return results


# ═══════════════════════════════════════════════════════
# PHASE 3: COGS — Benchmark messen
# ═══════════════════════════════════════════════════════

def cogs_phase():
    """COGS: Messe aktuellen Benchmark-Score."""
    import subprocess
    
    try:
        r = subprocess.run(
            ['python3', f'{HOME}/cogs_benchmark.py', '--demo'],
            capture_output=True, text=True, timeout=30
        )
        for line in r.stdout.split('\n'):
            if 'COGS =' in line:
                score = float(line.split('=')[1].strip().split()[0])
                print(f"[COGS] Score: {score:.4f}")
                return score
    except Exception as e:
        print(f"[COGS] Error: {e}")
    
    return None


# ═══════════════════════════════════════════════════════
# PHASE 4: META-SURGEON — Bei Verbesserung patchen
# ═══════════════════════════════════════════════════════

def surgeon_phase(before_score, after_score, results):
    """META-SURGEON: Wenn Verbesserung → patch CORTEX."""
    
    delta = (after_score or 0) - (before_score or 0)
    
    if delta > 0.001:
        # Verbesserung! Wende besten Subtask als Patch an
        best = max(results, key=lambda r: r['confidence'])
        
        # Speichere als Learning in MEMORY
        memory = HyperContextMemory()
        memory.compress_trajectory(
            f"Auto-Improvement-{datetime.now().strftime('%H%M')}",
            f"Task: {best['task']}. COGS delta: {delta:+.4f}. Confidence: {best['confidence']:.3f}",
            success=True
        )
        
        print(f"[SURGEON] ✓ Verbesserung: COGS {before_score:.4f}→{after_score:.4f} (Δ={delta:+.4f})")
        print(f"[SURGEON] Best Pattern: {best['task'][:60]} (conf={best['confidence']:.3f})")
        print(f"[SURGEON] Pattern in MEMORY gespeichert")
        
        return {'patched': True, 'delta': delta, 'pattern': best['task']}
    else:
        print(f"[SURGEON] Keine Verbesserung (Δ={delta:+.4f}). Kein Patch.")
        return {'patched': False, 'delta': delta}


# ═══════════════════════════════════════════════════════
# PHASE 5: FINANCIAL — Profit-Signal loggen
# ═══════════════════════════════════════════════════════

def financial_phase(surgeon_result):
    """FINANCIAL: Logge Profit-Signal in monetization.db."""
    
    if not os.path.exists(MONETIZATION_DB):
        print(f"[FINANCIAL] monetization.db nicht gefunden")
        return
    
    conn = sqlite3.connect(MONETIZATION_DB)
    conn.execute("PRAGMA journal_mode=WAL")
    
    # Wert der Verbesserung: 0.01 COGS ≈ $10 learning value
    value = abs(surgeon_result.get('delta', 0)) * 1000
    
    conn.execute("""
        INSERT INTO monetization_log (vector, event, revenue_impact)
        VALUES ('fusion_loop', ?, ?)
    """, (
        f"cogs_delta_{surgeon_result.get('delta', 0):+.4f}",
        value
    ))
    conn.commit()
    
    total = conn.execute("SELECT SUM(revenue_impact) FROM monetization_log").fetchone()[0] or 0
    signals = conn.execute("SELECT COUNT(*) FROM monetization_log").fetchone()[0]
    
    print(f"[FINANCIAL] Profit-Signal: ${value:.0f} (Total: ${total:,.0f}, Events: {signals})")
    
    conn.close()
    return value


# ═══════════════════════════════════════════════════════
# PHASE 6: SHIELD — Safety Check
# ═══════════════════════════════════════════════════════

def shield_phase():
    """SHIELD: Validiere dass Loop sicher ist."""
    shield = ShieldLayer()
    check = shield.check_execution("python3 fusion_loop.py --daemon")
    
    if check['blocked']:
        print(f"[SHIELD] ⛔ BLOCKIERT: {check['reason']}")
        return False
    
    print(f"[SHIELD] ✓ Loop freigegeben")
    return True


# ═══════════════════════════════════════════════════════
# HAUPT-LOOP
# ═══════════════════════════════════════════════════════

def fusion_cycle(task: str = None, cycle: int = 0):
    """Ein vollständiger Fusionszyklus."""
    
    if task is None:
        task = "Finde und behebe die schwächste COGS-Dimension durch Cross-Domain-Pattern-Extraktion aus geklonten Repos"
    
    print(f"\n{'='*60}")
    print(f"👁 FUSION CYCLE {cycle} — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    # Safety
    if not shield_phase():
        return {'aborted': True, 'reason': 'SHIELD block'}
    
    # CEREBRO
    plan = cerebro_phase(task)
    
    # GRIND
    results = grind_phase(plan.subtasks)
    
    # COGS (vorher)
    before = cogs_phase()
    
    # Hier würde Meta-Surgeon patchen basierend auf GRIND-Ergebnissen
    # Für Demo: COGS vorher = COGS nachher (keine Änderung)
    after = before
    
    # SURGEON
    surgeon = surgeon_phase(before, after, results)
    
    # FINANCIAL
    value = financial_phase(surgeon)
    
    # MEMORY: Komprimiere diesen Zyklus
    memory = HyperContextMemory()
    memory.compress_trajectory(
        f"Fusion-Cycle-{cycle}",
        f"CEREBRO→GRIND→COGS({before})→SURGEON(Δ={surgeon['delta']})→FINANCIAL(${value})",
        success=surgeon['patched']
    )
    
    return {
        'cycle': cycle,
        'cogs': before,
        'delta': surgeon['delta'],
        'profit_signal': value,
        'subtasks': len(results),
        'patched': surgeon['patched'],
    }


def main():
    import argparse
    p = argparse.ArgumentParser(description='👁 Fusion Loop')
    p.add_argument('--daemon', action='store_true', help='Kontinuierlicher Loop')
    p.add_argument('--interval', type=int, default=300, help='Sekunden zwischen Zyklen')
    p.add_argument('--once', action='store_true', help='Einmaliger Zyklus')
    args = p.parse_args()
    
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  👁 FUSION LOOP — CEREBRO→GRIND→COGS→SURGEON→FINANCIAL         ║")
    print("║  Die letzte fehlende Brücke. Geschlossen.                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    if args.once or not args.daemon:
        result = fusion_cycle(cycle=0)
        print(f"\n👁 Zyklus komplett: COGS={result['cogs']}, Δ={result['delta']}, ${result['profit_signal']}")
        return result
    
    # Daemon mode
    cycle = 0
    while True:
        try:
            result = fusion_cycle(cycle=cycle)
            cycle += 1
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n👁 Fusion Loop gestoppt.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(30)


if __name__ == "__main__":
    main()
