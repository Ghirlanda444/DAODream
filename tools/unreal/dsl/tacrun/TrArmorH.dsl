(fn TrArmorH ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniTMeHated))
    (:then
      (Funzionedichiamata|TrPeek :A (Variabili|Predefinito|OttieniTMeHated))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniPkAlive) (Utility|Operatori|Maggiore(>) (Matematica|Intero|BitwiseAND (Variabili|Predefinito|OttieniPkArmor) (Matematica|Float|Truncate (Variabili|Predefinito|OttieniTP))) 0))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMeHated))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 1.0)
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMe)))))))))
