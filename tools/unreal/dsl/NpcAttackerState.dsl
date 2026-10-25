(fn NpcAttackerState (Attacker)
  (bind _n (Utilità|Casting|CastToBP_DlgNPC Attacker))
  (Variabili|Predefinito|ImpostaAStunned (Utility|Operatori|Maggiore(>) (Matematica|Float|Max(Float) (Classe|BPDlgNPC|OttieniStunUntil _n) (Classe|BPDlgNPC|OttieniKnockUntil _n)) (Utilità|Testo|GetGameTimeinSeconds)))
  (Variabili|Predefinito|ImpostaAPen (Matematica|Float|SelectFloat (Classe|BPDlgNPC|OttieniDisarmAmt _n) 0.0 (Utility|Operatori|Maggiore(>) (Classe|BPDlgNPC|OttieniDisarmUntil _n) (Utilità|Testo|GetGameTimeinSeconds)))))
