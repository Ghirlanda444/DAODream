(fn AddJumpOpt (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) K (Variabili|Predefinito|OttieniEditRow))
    (:else
      (Funzionedichiamata|AddOpt :Name (Utilità|Stringa|Append (Utilità|Stringa|Append (Variabili|Predefinito|OttieniJumpName) " ") (Utilità|Stringa|ToString(Integer) (Utility|Operatori|Aggiungi K 1))) :Cmd 10.0 :Sub (Matematica|Conversioni|ToFloat(Integer) (Utility|Operatori|Aggiungi K 1))))))
