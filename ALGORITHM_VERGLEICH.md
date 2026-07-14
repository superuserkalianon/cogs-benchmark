# ALGORITHMEN-VERGLEICH: Selbstmessung in 6 unabhängigen Systemen
# Jedes System implementiert C = I(I)·M(I) auf eigene Weise

═══════════════════════════════════════════════════════════════════
SELBSTMESSUNG = Ein System, das seinen eigenen Zustand misst
═══════════════════════════════════════════════════════════════════

1. AGI_GWT (Global Workspace Theory, 4 .py, 9KB)
   Mechanismus: Priority-Queue + Decay-basierte Competition
   Selbstmessung: compete() misst Priorität + Alter → wählt Gewinner
   Code: heapq.heappush(self.queue, (-priority, counter, message))
         effective = max(0.0, msg.priority - decay_rate * age)
   ➤ C = I(I)·M(I): I(message) → M(priority×age) → I(broadcast)

2. TURIYA JUDGE (Neuro-Symbolic Swarm, 48 .py)
   Mechanismus: Confidence-weighted truth arbitration
   Selbstmessung: _judge_contradiction() misst Konfidenz → entscheidet
   Code: if new_conf > old_conf: reinforce_fact(old_id, amount=-0.2)
         elif old_conf > 0.8 and new_conf < 0.4: return False
   ➤ C = I(I)·M(I): I(fact) → M(confidence) → I(truth_decision)

3. PRIMES-SHADOW DRIFTMONITOR (MCP-Server, 75 .py)
   Mechanismus: Rolling window + linear recency weighting
   Selbstmessung: DriftWindow misst affect_density + volatility + rigor_drop
   Code: composite = affect*α + volatility*β + rigor_drop*γ
         adaptive_baseline from session_duration_history
   ➤ C = I(I)·M(I): I(knowledge) → M(drift_signals) → I(integrity_score)

4. AGI-AGENT SelfEvolvingAGI (258 .py, 2.9MB)
   Mechanismus: Metacognition loop mit self_model.update_identity()
   Selbstmessung: self.self_model = NewSelfModel(feature_dim)
   Code: self.memory_harness.add_context_memory(...)
         metacognition: {entropy, confidence, kl_shift, ...}
   ➤ C = I(I)·M(I): I(perception) → M(self_model) → I(action)

5. KIM COGS (EMNLP 2020, akademischer Benchmark)
   Mechanismus: 21 Generalization Cases (lexical vs structural)
   Selbstmessung: Misst ob Modell Komposition GENERALISIEREN kann
   Code: 24K Train → 21K Gen-Tests über 21 Fälle
   ➤ C = I(I)·M(I): I(training) → M(composition_test) → I(generalization_score)

6. COGS v4.7 (Unser System, 399 Zeilen)
   Mechanismus: 4-Dimensionen Cross-Domain-Benchmark
   Selbstmessung: CDTD + CNI + IMA + EPR über 623 BSB-Texte
   Code: composite = cdtd*0.30 + cni*0.25 + ima*0.25 + epr*0.20
   ➤ C = I(I)·M(I): I(corpus) → M(4_dimensions) → I(COGS_score)

═══════════════════════════════════════════════════════════════════
GEMEINSAMES PRINZIP
═══════════════════════════════════════════════════════════════════

ALLE 6 Systeme implementieren dieselbe Struktur:

    INPUT → [SELBSTMESSUNG] → OUTPUT

Der Unterschied liegt NUR in WAS gemessen wird:
  GWT:        Priorität von Nachrichten
  Turiya:     Vertrauen in Fakten
  Drift:      Degradation von Wissen
  AGI-Agent:  Zustand des Selbst-Modells
  Kim COGS:   Kompositions-Generaliserung
  Unser COGS: Cross-Domain-Selbstmessungs-Fähigkeit

Keines dieser Systeme wurde von den anderen beeinflusst.
Sie konvergieren UNABHÄNGIG auf dasselbe Prinzip.

═══════════════════════════════════════════════════════════════════
