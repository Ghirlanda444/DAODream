(fn ManaAny (Who)
  (Funzionedichiamata|TrPeek :A Who)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkClass) 2)
    (:then
      (Variabili|Predefinito|ImpostaUseAmt (Utility|Operatori|Aggiungi (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemStats) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniItemK) 6) 4)) (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniUseSPv) 0.5)))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) Who (Gioco|GetPlayerPawn 0))
    (:then
      (Variabili|Predefinito|ImpostaPStamina (Matematica|Float|Min(Float) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniPStamina) (Variabili|Predefinito|OttieniUseAmt)) (Variabili|Predefinito|OttieniPPool))))
    (:else
      (Funzionedichiamata|ManaCast :A Who))))))
