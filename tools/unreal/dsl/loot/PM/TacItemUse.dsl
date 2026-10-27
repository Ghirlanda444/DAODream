(fn TacItemUse (Me)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTIt) 0)
    (:then
      (Funzionedichiamata|CdCheck :Who Me :Ab (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemStats) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniInv) (Variabili|Predefinito|OttieniTIt)) 6) 1)))
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniGBool)
    (:then
      (Funzionedichiamata|UseGo :Who Me :Slot (Variabili|Predefinito|OttieniTIt))
      (Variabili|Predefinito|ImpostaBF "true"))))))
