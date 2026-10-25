(fn AddOwn (Slot)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTUntil) Slot) (Utilità|Testo|GetGameTimeinSeconds))
    (:then
      (Variabili|Predefinito|ImpostaOwnAtk (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniOwnAtk) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica Slot 16) 8))))
      (Variabili|Predefinito|ImpostaOwnPen (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniOwnPen) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica Slot 16) 9))))
      (Variabili|Predefinito|ImpostaOwnSpeed (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniOwnSpeed) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica Slot 16) 10))))
      (Variabili|Predefinito|ImpostaThreatenOn (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniThreatenOn) (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalents) (Utility|Operatori|Moltiplica Slot 16)) 808.0)))
      (Variabili|Predefinito|ImpostaFeign (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniFeign) (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalents) (Utility|Operatori|Moltiplica Slot 16)) 3023.0)))
      (Variabili|Predefinito|ImpostaOwnCrit (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniOwnCrit) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica Slot 16) 11)))))))
