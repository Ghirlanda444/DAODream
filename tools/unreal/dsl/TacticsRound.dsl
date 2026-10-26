(fn TacticsRound ()
  (Funzionedichiamata|ChooseTactic)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTacSlot) 0)
    (:then
      (Funzionedichiamata|DoTalent))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTacSlot) -2)
        (:else
          (Funzionedichiamata|StrikeFoe))))))
