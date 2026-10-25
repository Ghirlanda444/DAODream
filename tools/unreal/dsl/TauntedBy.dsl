(fn TauntedBy (Who Amount bTaunt)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniHostile) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead))) (Utility|Operatori|Minoreuguale(<=) (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) Who) 1000.0))
    (:then
      (Variabili|Predefinito|ImpostaTSwitched (Matematica|Float|SelectFloat -1000000000.0 (Variabili|Predefinito|OttieniTSwitched) bTaunt))
      (Funzionedichiamata|AddThreat :Who Who :Amount Amount))))
