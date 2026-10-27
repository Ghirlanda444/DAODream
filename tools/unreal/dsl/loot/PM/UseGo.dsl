(fn UseGo (Who Slot)
  (Variabili|Predefinito|ImpostaItemK (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniInv) Slot))
  (Funzionedichiamata|UseSP :Who Who)
  (Utilità|Array|Add (Variabili|Predefinito|OttieniCdWho) Who)
  (Utilità|Array|Add (Variabili|Predefinito|OttieniCdAb) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemStats) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniItemK) 6) 1)))
  (Utilità|Array|Add (Variabili|Predefinito|OttieniCdUntil) (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) 5.0))
  (Funzionedichiamata|InvTake :Slot Slot :N 1)
  (Funzionedichiamata|ShowMsg :Txt (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemNames) (Variabili|Predefinito|OttieniItemK)))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemStats) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniItemK) 6) 0)) 1.0)
    (:then
      (Variabili|Predefinito|ImpostaUseAmt (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniUseSPv) 50.0) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemStats) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniItemK) 6) 4))))
      (Funzionedichiamata|HealAny :Who Who))
    (:else
      (Funzionedichiamata|ManaAny :Who Who))))
