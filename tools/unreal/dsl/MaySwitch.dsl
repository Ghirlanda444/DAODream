(fn MaySwitch (Changed)
  (Funzionedichiamata|KeepWounded :Who Changed)
  (Funzionedichiamata|WhoUp :Who (Variabili|Predefinito|OttieniFoe))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniKeep)) (Matematica|Booleano|ORBoolean (Utility|Operatori|Maggioreuguale(>=) (Utility|Operatori|Sottrai (Utilità|Testo|GetGameTimeinSeconds) (Variabili|Predefinito|OttieniTSwitched)) (Variabili|Predefinito|OttieniTWait)) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniWhoOk))))
    (:then
      (Funzionedichiamata|SwitchTo))))
