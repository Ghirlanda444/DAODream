(fn TrList ()
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniCL))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 1.0)
    (:then
      (Utilità|Array|Add (Variabili|Predefinito|OttieniCL) (Variabili|Predefinito|OttieniTMe)))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 2.0)
    (:then
      (Variabili|Predefinito|ImpostaCL (Variabili|Predefinito|OttieniAllyL)))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 3.0)
    (:then
      (Variabili|Predefinito|ImpostaCL (Variabili|Predefinito|OttieniEnL)))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 7.0)
    (:then
      (Funzionedichiamata|TrAddValid :A (Variabili|Predefinito|OttieniTMeHated)))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 5.0)
    (:then
      (Funzionedichiamata|TrAddValid :A (Gioco|GetPlayerPawn 0)))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 18.0)
    (:then
      (Funzionedichiamata|TrAddValid :A (Variabili|Predefinito|OttieniTCtrl)))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTT) 100.0)
    (:then
      (Funzionedichiamata|TrAddFollower :Idx (Matematica|Float|Truncate (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniTT) 100.0))))))))))))))))))
