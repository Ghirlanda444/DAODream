(fn ModeOffGo ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTFound) 0) (Utility|Operatori|Minore(<) (Variabili|Predefinito|OttieniTFound) (Utilità|Array|Length (Variabili|Predefinito|OttieniNOn))))
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNOn) (Variabili|Predefinito|OttieniTFound)) 0.0)
    (:then
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniNOn) (Variabili|Predefinito|OttieniTFound) 0.0)
      (Variabili|Predefinito|ImpostaNPool (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNPool) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniTFound) 18) 4))))
      (Variabili|Predefinito|ImpostaNFatigue (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniNFatigue) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniTFound) 18) 5))))
      (Funzionedichiamata|NSumOwn)
      (Funzionedichiamata|SayText :Txt "Mode off")
      (Variabili|Predefinito|ImpostaTacDone "true")
      (Variabili|Predefinito|ImpostaTacSlot -2))))))
