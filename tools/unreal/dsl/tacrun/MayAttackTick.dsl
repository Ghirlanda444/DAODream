(fn MayAttackTick ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniPartyMayAttack) (Utility|Operatori|Maggiore(>) (Utilità|Testo|GetGameTimeinSeconds) (Variabili|Predefinito|OttieniMayCheckAt)))
    (:then
      (Variabili|Predefinito|ImpostaMayCheckAt (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) 1.0))
      (Funzionedichiamata|TrCtrl)
      (Funzionedichiamata|TrGather :Me (Variabili|Predefinito|OttieniTCtrl))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Length (Variabili|Predefinito|OttieniEnL)) 0)
    (:then
      (Variabili|Predefinito|ImpostaPartyMayAttack "false"))))))
