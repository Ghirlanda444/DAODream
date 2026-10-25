(fn DamageThreat (Who Damage)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) Damage 0.0)
    (:then
      (Funzionedichiamata|AttackerMul :Who Who)
      (Funzionedichiamata|AddThreat :Who Who :Amount (Utility|Operatori|Moltiplica (Utility|Operatori|Moltiplica (Utility|Operatori|Dividi Damage (Matematica|Float|Max(Float) (Variabili|Predefinito|OttieniMaxHealth) 1.0)) 100.0) (Variabili|Predefinito|OttieniTMul))))))
