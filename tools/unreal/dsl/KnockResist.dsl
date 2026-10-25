(fn KnockResist (Seconds)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) (Variabili|Predefinito|OttieniResist))
    (:then
      (Funzionedichiamata|SayText :Txt "Resisted"))
    (:else
      (Funzionedichiamata|KnockFor :Seconds Seconds))))
