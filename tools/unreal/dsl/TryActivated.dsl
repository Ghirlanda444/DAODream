(fn TryActivated ()
  (Variabili|Predefinito|ImpostaTCostNow (Matematica|Float|Truncate (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniTCost) (Utility|Operatori|Aggiungi (Utility|Operatori|Dividi (Variabili|Predefinito|OttieniPFatigue) 100.0) 1.0)) 0.5)))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Variabili|Predefinito|OttieniPStamina) (Variabili|Predefinito|OttieniTCostNow))
    (:then
      (Funzionedichiamata|ShowMsg :Txt "Not enough stamina"))
    (:else
      (Funzionedichiamata|ActivateTalent))))
