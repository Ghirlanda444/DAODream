(fn PlayerAttackNow ()
  (Funzionedichiamata|MayAttack)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniTalking) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPStunUntil) (Utilità|Testo|GetGameTimeinSeconds))) (Utility|Operatori|Minore(<) (Utility|Operatori|Sottrai (Utilità|Testo|GetGameTimeinSeconds) (Variabili|Predefinito|OttieniLastAttack)) (Variabili|Predefinito|OttieniPInterval)))
    (:else
      (Variabili|Predefinito|ImpostaLastAttack (Utilità|Testo|GetGameTimeinSeconds))
      (Funzionedichiamata|SwingAnim)
      (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniBowOn)
        (:then
          (Funzionedichiamata|BowAttack))
        (:else
          (Funzionedichiamata|MeleeAttack))))))
