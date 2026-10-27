(fn TacticAct (I)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 10.0)
    (:then
      (Variabili|Predefinito|ImpostaTacDone (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 4)) -1.0))
      (Variabili|Predefinito|ImpostaTacNext (Matematica|Float|Max(Float) (Variabili|Predefinito|OttieniTacNext) (Matematica|Float|SelectFloat (Utility|Operatori|Sottrai (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 4)) 1.0) 0.0 (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 4)) (Utility|Operatori|Aggiungi (Matematica|Conversioni|ToFloat(Integer) I) 1.0))))))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 4.0) (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 5.0))
    (:then
      (Funzionedichiamata|TacticUsable :Ability (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 4)) :bMode (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 5.0))
      (Funzionedichiamata|TacAim))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 9.0)
    (:then
      (Funzionedichiamata|TacticMove :Sub (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 4))))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 2.0)
    (:then
      (Variabili|Predefinito|ImpostaTacDone "true")
      (Funzionedichiamata|TacAim))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 3.0)
    (:then
      (Variabili|Predefinito|ImpostaTacDone "true")
      (Variabili|Predefinito|ImpostaTacSlot -2))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 6.0)
    (:then
      (Funzionedichiamata|ModeOff :Ability (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 4))))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 7.0) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 15.0) (Utility|Operatori|Minoreuguale(<=) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) 18.0)))
    (:then
      (Funzionedichiamata|TacItemRow :Cmd (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 3)) :Sub (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 4))))))))))))))))))
