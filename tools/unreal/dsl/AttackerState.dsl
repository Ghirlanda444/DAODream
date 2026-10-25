(fn AttackerState (Attacker)
  (Variabili|Predefinito|ImpostaAStunned "false")
  (Variabili|Predefinito|ImpostaAPen 0.0)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) Attacker (Gioco|GetPlayerPawn 0))
    (:then
      (Variabili|Predefinito|ImpostaAStunned (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPStunUntil) (Utilità|Testo|GetGameTimeinSeconds)))
      (Variabili|Predefinito|ImpostaAPen (Matematica|Float|SelectFloat (Variabili|Predefinito|OttieniPDisarmAmt) 0.0 (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPDisarmUntil) (Utilità|Testo|GetGameTimeinSeconds)))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid Attacker)
        (:then
          (Funzionedichiamata|NpcAttackerState :Attacker Attacker))))))
