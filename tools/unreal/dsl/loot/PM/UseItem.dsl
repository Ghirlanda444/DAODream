(fn UseItem (Who Slot)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemStats) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniInv) Slot) 6) 0)) 1.0) (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemStats) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniInv) Slot) 6) 0)) 2.0))
    (:then
      (Funzionedichiamata|CdCheck :Who Who :Ab (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemStats) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniInv) Slot) 6) 1)))
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniGBool)
    (:then
      (Funzionedichiamata|UseGo :Who Who :Slot Slot))
    (:else
      (Funzionedichiamata|ShowMsg :Txt "Not ready yet"))))
    (:else
      (Funzionedichiamata|ShowMsg :Txt "It cannot be used"))))
