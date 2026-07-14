#!/usr/bin/env python3
"""
MONETIZATION LAYER v1.0 — P0 Execution
=======================================
Vector 1: Polymarket Arbitrage (passive background harvester)
Vector 2: Tax Service (active micro-SaaS)

Prinzip: Cashflow = physikalischer Beweis für M(I) > 0
"""

import sqlite3, json, os, time
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

HOME = str(Path.home())
DB_PATH = f"{HOME}/.hermes/monetization.db"

# ═══════════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════════

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS polymarket_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT UNIQUE,
            question TEXT,
            slug TEXT,
            probability REAL,
            volume REAL,
            liquidity REAL,
            spread REAL,
            arbitrage_flag BOOLEAN DEFAULT 0,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tax_service_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            entity_type TEXT,
            jurisdiction TEXT,
            blueprint_hash TEXT,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS monetization_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vector TEXT,
            event TEXT,
            revenue_impact REAL DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

# ═══════════════════════════════════════════════════════
# VECTOR 1: POLYMARKET ARBITRAGE
# ═══════════════════════════════════════════════════════

POLYMARKET_GAMMA_URL = "https://gamma-api.polymarket.com/events"
POLYMARKET_CLOB_URL = "https://clob.polymarket.com/markets"

def fetch_polymarket_markets(limit=20, tag="AI"):
    """Fetch Polymarket markets via Gamma API (no auth needed)."""
    try:
        url = f"{POLYMARKET_GAMMA_URL}?tag={tag}&limit={limit}&active=true&closed=false"
        req = Request(url, headers={'User-Agent': 'COGS-Monetization/1.0'})
        r = urlopen(req, timeout=10)
        return json.loads(r.read())
    except Exception as e:
        print(f"  [Polymarket] API error: {e}")
        return []

def compute_arbitrage_signal(market):
    """Detect arbitrage opportunities from market data."""
    probability = market.get('probability', 0.5)
    volume = float(market.get('volume', 0))
    liquidity = float(market.get('liquidity', 0))
    
    # Simple arbitrage: high volume + extreme probability = signal
    signal = False
    if volume > 100000 and (probability > 0.85 or probability < 0.15):
        signal = True  # Strong conviction market
    if liquidity > 10000 and volume > 500000:
        signal = True  # High-liquidity event
    
    spread = abs(0.5 - probability) * 2  # Normalized spread [0,1]
    
    return signal, spread

def harvest_polymarket(conn, tag="AI"):
    """Harvest Polymarket markets and store signals."""
    markets = fetch_polymarket_markets(tag=tag)
    inserted = 0
    signals = 0
    
    for market in markets:
        try:
            mid = market.get('id', '')
            question = market.get('question', '')[:200]
            slug = market.get('slug', '')
            
            # Get market-specific data
            prob = None
            vol = 0
            liq = 0
            
            if 'markets' in market:
                m = market['markets'][0] if market['markets'] else {}
                prob = float(m.get('outcomePrices', ['0.5'])[0]) if m.get('outcomePrices') else None
                vol = float(m.get('volume', 0))
                liq = float(m.get('liquidity', 0))
            
            arb_signal, spread = compute_arbitrage_signal({
                'probability': prob or 0.5,
                'volume': vol,
                'liquidity': liq
            })
            
            conn.execute("""
                INSERT OR REPLACE INTO polymarket_signals 
                (market_id, question, slug, probability, volume, liquidity, spread, arbitrage_flag)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (mid, question, slug, prob, vol, liq, spread, arb_signal))
            
            inserted += 1
            if arb_signal:
                signals += 1
                conn.execute("""
                    INSERT INTO monetization_log (vector, event, revenue_impact)
                    VALUES ('polymarket', 'arbitrage_signal_detected', ?)
                """, (vol * 0.001,))  # Estimated 0.1% edge on volume
                
        except Exception as e:
            continue
    
    conn.commit()
    return inserted, signals

# ═══════════════════════════════════════════════════════
# VECTOR 2: TAX SERVICE
# ═══════════════════════════════════════════════════════

def tax_service_status():
    """Check Tax Service readiness."""
    tax_dir = f"{HOME}/.hermes/tax_service"
    files = {
        'blueprint_generator.py': os.path.exists(f"{tax_dir}/blueprint_generator.py"),
        'stripe_webhook_handler.py': os.path.exists(f"{tax_dir}/stripe_webhook_handler.py"),
        'tax_qualifier.py': os.path.exists(f"{tax_dir}/tax_qualifier.py"),
        'onboarding_form.py': os.path.exists(f"{tax_dir}/onboarding_form.py"),
        'legal_framework.md': os.path.exists(f"{tax_dir}/legal_framework.md"),
        'config_tax_service.py': os.path.exists(f"{tax_dir}/config_tax_service.py"),
    }
    return {
        'ready': all(files.values()),
        'files': files,
        'path': tax_dir
    }

def generate_blueprint_demo(conn, entity_type="UG", jurisdiction="DE"):
    """Generate demo tax blueprint."""
    import hashlib
    
    blueprint = {
        'entity': entity_type,
        'jurisdiction': jurisdiction,
        'structure': 'holding_pass_through',
        'cashflow_routing': 'api_revenue → stripe → business_account',
        'compliance': 'RDG_StBerG_shield_via_legal_framework.md',
        'generated_at': datetime.now().isoformat()
    }
    
    bp_hash = hashlib.md5(json.dumps(blueprint, sort_keys=True).encode()).hexdigest()[:16]
    
    conn.execute("""
        INSERT INTO tax_service_contracts (client_name, entity_type, jurisdiction, blueprint_hash, status)
        VALUES (?, ?, ?, ?, 'demo')
    """, ('Demo Client', entity_type, jurisdiction, bp_hash))
    conn.commit()
    
    return blueprint, bp_hash

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  MONETIZATION LAYER v1.0 — FRENESIS P0                         ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")
    
    conn = init_db()
    
    # Vector 1: Polymarket
    print("VECTOR 1: Polymarket Arbitrage")
    inserted, signals = harvest_polymarket(conn, tag="AI")
    
    # Also try crypto, tech, politics tags
    for tag in ["crypto", "politics"]:
        i, s = harvest_polymarket(conn, tag=tag)
        inserted += i
        signals += s
    
    print(f"  Märkte geharvestet: {inserted}")
    print(f"  Arbitrage-Signale:  {signals}")
    
    # Show top signals
    rows = conn.execute("""
        SELECT question, probability, volume, arbitrage_flag 
        FROM polymarket_signals 
        WHERE arbitrage_flag = 1 
        ORDER BY volume DESC LIMIT 5
    """).fetchall()
    
    if rows:
        print(f"\n  TOP ARBITRAGE-SIGNALE:")
        for r in rows:
            print(f"  🚩 {r[0][:80]}")
            print(f"     P={r[1]:.2f}  Vol=${r[2]:,.0f}")
    
    # Vector 2: Tax Service
    print(f"\nVECTOR 2: Tax Service")
    status = tax_service_status()
    print(f"  Status: {'✓ READY' if status['ready'] else '⚠ INCOMPLETE'}")
    for f, exists in status['files'].items():
        print(f"    {'✓' if exists else '✗'} {f}")
    
    if status['ready']:
        blueprint, bp_hash = generate_blueprint_demo(conn)
        print(f"  Demo-Blueprint: {bp_hash}")
        print(f"  → Tax Service deploybar. Benötigt: Stripe API-Key + Uvicorn")
    
    # Summary
    total = conn.execute("SELECT COUNT(*) FROM polymarket_signals").fetchone()[0]
    signals = conn.execute("SELECT COUNT(*) FROM polymarket_signals WHERE arbitrage_flag=1").fetchone()[0]
    
    print(f"\n╔══════════════════════════════════════════════════════════════════╗")
    print(f"║  MONETIZATION LAYER AKTIV                                      ║")
    print(f"║  DB:      {DB_PATH}")
    print(f"║  Signale: {total} Märkte, {signals} Arbitrage-Flags      ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝")
    
    conn.close()
