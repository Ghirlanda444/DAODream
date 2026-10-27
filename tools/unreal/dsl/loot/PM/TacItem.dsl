(fn TacItem (Me Cmd Sub)
  (Variabili|Predefinito|ImpostaBF "false")
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length (Variabili|Predefinito|OttieniEnAll)) 0)
    (:then
      (Funzionedichiamata|TacItem2 :Me Me :Cmd Cmd :Sub Sub))))
