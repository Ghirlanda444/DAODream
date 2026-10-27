(fn TrFlag (B Fl)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica B 10) (Utility|Operatori|Aggiungi Fl 1)) (Utilità|Array|Length (Variabili|Predefinito|OttieniTBehaviors)))
    (:then
      (Variabili|Predefinito|ImpostaBF (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTBehaviors) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica B 10) (Utility|Operatori|Aggiungi Fl 1))) 0.0)))
    (:else
      (Variabili|Predefinito|ImpostaBF (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) Fl 0) (Utility|Operatori|Uguale(==) Fl 1)) (Utility|Operatori|Uguale(==) Fl 7)) (Utility|Operatori|Uguale(==) Fl 8))))))
