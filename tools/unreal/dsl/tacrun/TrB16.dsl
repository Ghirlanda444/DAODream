(fn TrB16 ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 3.0)
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniTMeParty)
    (:then
      (Funzionedichiamata|TrOwnChk))
    (:else
      (Funzionedichiamata|TrHated))))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length (Variabili|Predefinito|OttieniCL)) 0)
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) 0)))))))
