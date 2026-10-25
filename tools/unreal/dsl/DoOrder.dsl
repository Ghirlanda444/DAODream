(fn DoOrder ()
  (Variabili|Predefinito|ImpostaTFound (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniPendingSlot) 1))
  (Variabili|Predefinito|ImpostaPendingSlot 0)
  (Variabili|Predefinito|ImpostaTacSlot -1)
  (Variabili|Predefinito|ImpostaTacDone "false")
  (Funzionedichiamata|UsableCheck :bMode (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniTFound) 18) 1)) 2.0))
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniTacDone)
    (:then
      (Funzionedichiamata|DoTalent))
    (:else
      (Funzionedichiamata|SayText :Txt "Not now")
      (Funzionedichiamata|TacticsRound))))
